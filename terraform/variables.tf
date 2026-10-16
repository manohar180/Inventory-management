# ==============================================================================
# variables.tf — Input Variables for StockPilot Infrastructure
# WHY:  Keeping all tuneable values in one place means you never have to grep
#       through main.tf to change the cluster name or node count.
#       Think of variables like function parameters for your infrastructure.
# WHEN: Values are sourced from terraform.tfvars (local) or -var flags (CI).
# WHERE: terraform/ directory.
# ==============================================================================

# ── Region & Environment ──────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region where all resources will be created."
  type        = string
  default     = "ap-south-1" # Mumbai — lowest latency for India-based projects
}

variable "environment" {
  description = "Deployment environment label (dev / staging / prod)."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

# ── Networking ────────────────────────────────────────────────────────────────

variable "vpc_name" {
  description = "Name tag applied to the VPC and derived resources."
  type        = string
  default     = "stockpilot-vpc"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the VPC."
  type        = string
  default     = "10.30.0.0/16"
}

variable "availability_zones" {
  description = "List of AZs to use (must have at least 2 for EKS HA)."
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs for private subnets (one per AZ). Worker nodes live here."
  type        = list(string)
  default     = ["10.30.1.0/24", "10.30.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets (one per AZ). Load balancers live here."
  type        = list(string)
  default     = ["10.30.101.0/24", "10.30.102.0/24"]
}

# ── EKS Cluster ───────────────────────────────────────────────────────────────

variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
  default     = "stockpilot-eks"
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS control plane."
  type        = string
  default     = "1.31"
}

# ── Node Group ────────────────────────────────────────────────────────────────

variable "node_instance_type" {
  description = "EC2 instance type for EKS managed worker nodes."
  type        = string
  default     = "t3.medium" # 2 vCPU / 4 GB RAM — adequate for capstone demo
}

variable "node_min_size" {
  description = "Minimum number of worker nodes in the managed node group."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes (HPA + CA can scale up to this)."
  type        = number
  default     = 4
}

variable "node_desired_size" {
  description = "Desired number of worker nodes at baseline."
  type        = number
  default     = 2
}
