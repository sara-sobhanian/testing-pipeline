terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  # Uncomment and configure this for state management
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "prod/eks/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}

data "aws_eks_cluster_auth" "eks_auth" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.eks_auth.token
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name                   = "${var.environment}-${var.cluster_name}"
  cluster_version               = var.cluster_version
  cluster_endpoint_public_access = true
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      name = "${var.environment}-${var.cluster_name}-general"

      instance_types = var.node_instance_types
      capacity_type  = "ON_DEMAND"

      min_size     = var.min_nodes
      max_size     = var.max_nodes
      desired_size = var.desired_nodes

      vpc_security_group_ids = [aws_security_group.node_group.id]

      update_config = {
        max_unavailable_percentage = 33
      }
    }
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  )
}

# vpc.tf
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 4.0"

  name = "${var.environment}-${var.cluster_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = false  # Multiple NAT gateways for production
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  flow_log_max_aggregation_interval    = 60

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  )
}