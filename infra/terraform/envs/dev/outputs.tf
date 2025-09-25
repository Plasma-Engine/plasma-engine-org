output "vpc_id" {
  description = "Dev VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Dev public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "service_sg_id" {
  description = "Service security group ID in dev"
  value       = module.compute.security_group_id
}