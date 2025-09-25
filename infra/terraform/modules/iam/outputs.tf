/** Outputs for IAM module */

output "iam_summary" {
  description = "High-level summary of IAM configuration"
  value = {
    name               = var.name
    service_principals = var.service_principals
  }
}

# TODO: Output role ARNs/IDs and policy document references.

