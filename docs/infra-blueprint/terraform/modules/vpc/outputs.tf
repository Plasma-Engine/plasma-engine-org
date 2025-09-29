# Outputs expose IDs and key attributes to consuming modules

output "vpc_id" {
  description = "ID of the created VPC/VNet."
  value       = null # replace with resource id when implemented
}

output "public_subnet_ids" {
  description = "IDs of public subnets."
  value       = []
}

output "private_subnet_ids" {
  description = "IDs of private subnets."
  value       = []
}

