# Module: vpc
# Purpose: Define the network foundation (VPC/VNet), subnets, routing, NAT, and basic security lists.
# Notes:
# - Keep this module cloud-agnostic via variable naming. Implementations may target AWS (VPC), GCP (VPC), or Azure (VNet).
# - Prefer separate public and private subnets across at least 2-3 AZs for HA.
# - Expose outputs for subnet IDs, route tables, NAT gateways/instances, and CIDR blocks.

terraform {
  required_version = ">= 1.5.0"
}

# Implementation sketch (provider-specific resources intentionally omitted):
# - Create VPC with CIDR var.vpc_cidr
# - Create private_subnets and public_subnets across availability zones
# - Attach Internet Gateway (for public) and NAT Gateways (for private)
# - Configure route tables per subnet tier

# Placeholders for future resources:
# resource "aws_vpc" "this" { }
# resource "aws_subnet" "private" { count = length(var.private_subnet_cidrs) }
# resource "aws_subnet" "public"  { count = length(var.public_subnet_cidrs) }
# resource "aws_nat_gateway" "this" { }

