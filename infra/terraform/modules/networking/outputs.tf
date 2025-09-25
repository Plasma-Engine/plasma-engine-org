/**
  Outputs for networking module
*/

output "networking_summary" {
  description = "High-level summary of networking configuration"
  value = {
    name                  = var.name
    cidr_block            = var.cidr_block
    public_subnet_cidrs   = var.public_subnet_cidrs
    private_subnet_cidrs  = var.private_subnet_cidrs
    enable_nat_gateway    = var.enable_nat_gateway
  }
}

# TODO: Export provider-specific outputs when implemented (e.g., vpc_id, subnet_ids)

