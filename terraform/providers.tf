# ==============================================================================
# providers.tf — AWS Provider Configuration
# WHY:  Tells Terraform which cloud account and region to target.
#       The region is read from a variable so it can be overridden without
#       touching this file.
# WHEN: Loaded at `terraform init` / every plan-apply cycle.
# WHERE: terraform/ directory.
# ==============================================================================

provider "aws" {
  region = var.aws_region

  # Propagate default tags to every AWS resource — useful for cost allocation
  # and for quickly identifying resources that belong to this project.
  default_tags {
    tags = {
      Project     = "stockpilot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
