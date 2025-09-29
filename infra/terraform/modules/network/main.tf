// Explainer: Minimal networking module (AWS). Creates a VPC and two public subnets.
// Inputs: cidr_block, azs, name_prefix, tags
// Outputs: vpc_id, public_subnet_ids
// Downstream: Compute modules (EKS/EC2/Lambda) will attach to these subnets.
// Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-vpc"
  })
}

resource "aws_subnet" "public" {
  count                   = length(var.azs)
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.cidr_block, 4, count.index)
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = true
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-public-${count.index}"
  })
}