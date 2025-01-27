resource "aws_security_group" "node_group" {
  name_prefix = "${var.environment}-${var.cluster_name}-node"
  description = "Security group for EKS node group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = var.api_access_cidrs
  }

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = var.api_access_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.cluster_name}-node"
      Environment = var.environment
    }
  )
}