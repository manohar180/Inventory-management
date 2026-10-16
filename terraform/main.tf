# ==============================================================================
# main.tf — StockPilot Core AWS Infrastructure
#
# WHY:  We need a production-grade network and a managed Kubernetes cluster.
#       - VPC isolates our traffic from other AWS customers.
#       - Public subnets host internet-facing Load Balancers.
#       - Private subnets host worker nodes (they cannot be directly reached
#         from the internet — much safer).
#       - A NAT gateway lets private nodes reach the internet (to pull images,
#         send logs, etc.) without exposing them.
#       Think of it like an office building: the lobby (public subnet) is
#       open to visitors, but the server room (private subnet) is locked.
#
# WHEN: `terraform apply` — runs once. Changes trigger incremental updates.
# WHERE: terraform/ directory. Uses two community modules to avoid writing
#        hundreds of lines of low-level resource definitions.
# ==============================================================================

# ── VPC Module ────────────────────────────────────────────────────────────────
# The terraform-aws-modules/vpc module creates:
#   • The VPC itself
#   • 2 public subnets  (internet-reachable — for ALB / Ingress controllers)
#   • 2 private subnets (internet-blocked — for EKS worker nodes)
#   • 1 Internet Gateway (public traffic in/out)
#   • 1 NAT Gateway in ONE public subnet (cost-saving: single NAT vs. one per AZ)
#   • Route tables wiring everything together
#   • Subnet tags required by EKS and AWS Load Balancer Controller

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = var.vpc_name
  cidr = var.vpc_cidr

  # Spread subnets across two Availability Zones for high availability
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  # ONE NAT gateway shared across both private subnets — saves ~$32/month
  # vs. one NAT per AZ. Acceptable trade-off for a dev/capstone cluster.
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  # These tags are REQUIRED by EKS so it knows which subnets to use for
  # internal load balancers (private) and internet-facing ones (public).
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  tags = {
    Name = var.vpc_name
  }
}

# ── EKS Cluster Module ────────────────────────────────────────────────────────
# The terraform-aws-modules/eks module provisions:
#   • The EKS control plane (managed by AWS — no master nodes to maintain)
#   • IAM roles and policies for the cluster and node groups
#   • A managed node group running EC2 instances as worker nodes
#   • Security groups for cluster ↔ node communication

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.37.1"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  # Place the control plane in the VPC we created above
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets # Worker nodes go in private subnets

  # Allow kubectl access from anywhere and allow worker nodes to talk to API privately
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Automatically grant the Terraform caller admin access to the cluster
  # (avoids having to manually add a ConfigMap entry after apply).
  enable_cluster_creator_admin_permissions = true

  # Disable custom KMS key, CloudWatch log group, and IRSA OIDC provider to avoid SCP policy restrictions
  create_kms_key              = false
  cluster_encryption_config   = {}
  create_cloudwatch_log_group = false
  enable_irsa                 = false

  # ── Managed Node Group ──────────────────────────────────────────────────────
  # A managed node group means AWS handles node patching, replacement, and
  # lifecycle — we just declare the desired state.
  eks_managed_node_groups = {
    stockpilot_nodes = {
      instance_types = [var.node_instance_type]

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      # For Kubernetes 1.31, Amazon Linux 2023 is required
      ami_type = "AL2023_x86_64_STANDARD"

      # Nodes need this policy to pull images from ECR / GHCR (via VPC endpoint
      # or internet via NAT gateway)
      iam_role_additional_policies = {
        AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
      }

      labels = {
        role = "worker"
        app  = "stockpilot"
      }

      tags = {
        Name = "${var.cluster_name}-node"
      }
    }
  }

  # Add-ons managed by EKS — keeps core cluster components up to date
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  tags = {
    Name = var.cluster_name
  }
}
