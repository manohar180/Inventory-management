# StockPilot — Terraform Infrastructure

This directory provisions the AWS cloud infrastructure required to run StockPilot on Kubernetes.

> ⚠️ **AWS COST WARNING**
> Running this infrastructure costs approximately **$5–8 per day** (2× t3.medium nodes + 1 NAT gateway + EKS control plane fee).
> **Always run `terraform destroy` when you are done with the evaluation to avoid unexpected AWS charges.**

---

## What Gets Provisioned

| Resource | Details |
|----------|---------|
| **VPC** | `10.30.0.0/16`, 2 public + 2 private subnets across 2 AZs |
| **Internet Gateway** | Enables public subnets to reach the internet |
| **NAT Gateway** | Single NAT (cost-saving) lets private nodes pull images |
| **EKS Cluster** | Kubernetes 1.31, public endpoint |
| **Managed Node Group** | 2× t3.medium worker nodes (scales to 4) |
| **EKS Add-ons** | CoreDNS, kube-proxy, vpc-cni |

---

## Prerequisites

1. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
2. [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.7.0
3. An AWS account with sufficient IAM permissions (AdministratorAccess or a scoped EKS/VPC policy)

**Authenticate with AWS (choose one):**
```bash
# Option A — AWS SSO (recommended)
aws sso login --profile your-profile

# Option B — Environment variables (never commit these!)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="ap-southeast-2"
```

---

## Usage

### 1. Prepare your variables

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars if you want to change region, instance type, etc.
```

### 2. Initialise Terraform (downloads providers & modules)

```bash
terraform init
```

### 3. Preview the changes (no AWS resources created yet)

```bash
terraform plan
# Screenshot this output for M7 submission
```

### 4. Apply (creates all AWS resources — costs money!)

```bash
terraform apply
# Type 'yes' when prompted
# This takes approximately 15–20 minutes
```

### 5. Configure kubectl

After apply completes, run the printed `kubeconfig_command` output:

```bash
aws eks update-kubeconfig --region ap-southeast-2 --name stockpilot-eks
kubectl get nodes   # Should show 2 Ready nodes
```

### 6. Deploy StockPilot via Helm

```bash
helm upgrade --install stockpilot ../helm/stockpilot \
  --namespace stockpilot \
  --create-namespace \
  --values ../helm/stockpilot/values-prod.yaml
```

---

## ⚠️ DESTROY WHEN DONE (avoid AWS charges)

```bash
# First delete any Kubernetes resources that created AWS Load Balancers
# (otherwise ELBs may block VPC deletion)
kubectl delete ingress --all -n stockpilot
kubectl delete svc --all -n stockpilot

# Then destroy all Terraform resources
terraform destroy
# Type 'yes' when prompted
# Screenshot the completion for M7 submission
```

---

## Required Screenshots (M7 Submission)

| # | Screenshot | Where to capture |
|---|-----------|-----------------|
| 1 | `terraform plan` output | Terminal |
| 2 | AWS Console → VPC → Your VPC | ap-southeast-2 console |
| 3 | AWS Console → EKS → stockpilot-eks cluster | ap-southeast-2 console |
| 4 | `kubectl get nodes` (2 Ready) | Terminal after `update-kubeconfig` |
| 5 | `terraform destroy` completion | Terminal |

---

## File Structure

```
terraform/
├── versions.tf          # Terraform & provider version pins
├── providers.tf         # AWS provider config with default tags
├── variables.tf         # All input variables with descriptions
├── main.tf              # VPC + EKS module calls (core infrastructure)
├── outputs.tf           # Useful values printed after apply
├── terraform.tfvars.example  # Copy → terraform.tfvars, fill in your values
├── .gitignore           # Excludes *.tfstate, *.tfvars, .terraform/
└── README.md            # This file
```
