# ==============================================================================
# outputs.tf — Terraform Output Values
# WHY:  After `terraform apply`, you need several values to configure kubectl,
#       Helm, and other tools. Outputs surface these without digging through
#       the AWS console.
# WHEN: Printed at the end of every `terraform apply` run.
# WHERE: terraform/ directory.
# ==============================================================================

# ── VPC Outputs ───────────────────────────────────────────────────────────────

output "vpc_id" {
  description = "ID of the StockPilot VPC."
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC."
  value       = module.vpc.vpc_cidr_block
}

output "private_subnet_ids" {
  description = "IDs of the private subnets (worker nodes live here)."
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "IDs of the public subnets (load balancers live here)."
  value       = module.vpc.public_subnets
}

# ── EKS Outputs ───────────────────────────────────────────────────────────────

output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "API server endpoint URL for the EKS cluster."
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version running on the cluster."
  value       = module.eks.cluster_version
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded certificate authority data for the cluster."
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true # Marked sensitive so it is not printed in plain CI logs
}

output "node_group_arn" {
  description = "ARN of the managed node group."
  value       = module.eks.eks_managed_node_groups["stockpilot_nodes"].node_group_arn
}

# ── Convenience Outputs ───────────────────────────────────────────────────────

output "kubeconfig_command" {
  description = <<-EOT
    Run this command to update your local ~/.kube/config so that kubectl
    points at the newly created EKS cluster.
  EOT
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "helm_install_hint" {
  description = "Quick-start hint for deploying StockPilot via Helm after kubeconfig is configured."
  value       = <<-EOT
    helm upgrade --install stockpilot ./helm/stockpilot \
      --namespace stockpilot \
      --create-namespace \
      --values helm/stockpilot/values-prod.yaml
  EOT
}
