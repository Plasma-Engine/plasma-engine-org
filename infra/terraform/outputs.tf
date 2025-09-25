//
// Explainer: Outputs consumed by downstream stacks and CI.
// Provide minimally sensitive data; never output secrets.
//

output "environment" {
  description = "Effective environment name"
  value       = var.environment
}

