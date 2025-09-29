output "security_group_id" {
  description = "Security group ID for services"
  value       = aws_security_group.service.id
}