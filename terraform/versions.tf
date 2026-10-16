# ==============================================================================
# versions.tf — Terraform and Provider Version Constraints
# WHY:  Pinning versions ensures every team member and CI run uses the exact
#       same Terraform core and provider binaries. Think of it like a lockfile.
# WHEN: Evaluated by `terraform init` before anything else runs.
# WHERE: terraform/ directory, checked into Git.
# ==============================================================================

terraform {
  # Minimum Terraform CLI version required to use this configuration
  required_version = ">= 1.7.0"

  required_providers {
    # AWS provider — provisions VPC, EKS, IAM, etc.
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}
