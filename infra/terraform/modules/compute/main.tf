// Explainer: Compute module placeholder. Choose one: ECS on Fargate, EKS, or EC2 ASG.
// Inputs: vpc_id, subnet_ids, name_prefix, tags
// Outputs: security_group_id (placeholder)
// Downstream: Service deployments will consume compute outputs.
// TODO: Owner=Platform: Decide preferred compute substrate per ADRs (EKS likely).

resource "aws_security_group" "service" {
  name        = "${var.name_prefix}-svc-sg"
  description = "Security group for services"
  vpc_id      = var.vpc_id

  // TODO: Tighten rules per service needs
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name_prefix}-svc-sg" })
}