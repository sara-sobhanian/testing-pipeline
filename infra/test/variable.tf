variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}


variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "deals-eks"  # Shortened from dealsdeals-cluster
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "min_nodes" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum number of nodes"
  type        = number
  default     = 3
}

variable "desired_nodes" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "test"
    Application = "dealsdeals"
    Terraform   = "true"
  }
}