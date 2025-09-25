/**
  Networking module (provider-agnostic scaffold)

  This module is responsible for core network primitives: VPC/VNet, subnets,
  routing, gateways, and security groups or firewall rules. It intentionally
  contains no provider-specific resources by default to allow organizations to
  swap in preferred upstream modules.

  References:
  - Terraform Modules: https://developer.hashicorp.com/terraform/language/modules
  - Example AWS VPC module: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws

  # TODO: Implement with chosen provider or re-export upstream module.
*/

locals {
  module_purpose = "Establishes baseline networking constructs for environment"
}

# Example (commented):
# module "vpc" {
#   source  = "terraform-aws-modules/vpc/aws"
#   version = "~> 5.0"
#   name    = var.name
#   cidr    = var.cidr_block
#   azs     = var.availability_zones
#   public_subnets  = var.public_subnet_cidrs
#   private_subnets = var.private_subnet_cidrs
#   enable_nat_gateway = var.enable_nat_gateway
# }

