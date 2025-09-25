# Networking Module

Purpose: Provision core networking primitives (VPC/VNet, subnets, route tables, gateways, security groups/firewall rules).

Notes:
- Provider-agnostic scaffold; wire to a specific cloud provider module or resources as needed.
- See variables and outputs for required inputs and published values.

References:
- AWS VPC: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- Azure Virtual Network: https://registry.terraform.io/modules/Azure/network/azurerm/latest
- GCP VPC: https://registry.terraform.io/modules/terraform-google-modules/network/google/latest

# TODO: Select provider and finalize resource implementations.
