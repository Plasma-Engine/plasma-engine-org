/** Outputs for security module */

output "security_summary" {
  description = "High-level summary of security configuration"
  value = {
    name           = var.name
    secrets_engine = var.secrets_engine
    kms_key_alias  = var.kms_key_alias
  }
}

# TODO: Output key IDs/ARNs and secrets paths when implemented.

