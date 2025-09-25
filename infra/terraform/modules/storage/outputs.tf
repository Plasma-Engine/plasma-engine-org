/** Outputs for storage module */

output "storage_summary" {
  description = "High-level summary of storage configuration"
  value = {
    name                   = var.name
    enable_versioning      = var.enable_versioning
    lifecycle_days_to_glacier = var.lifecycle_days_to_glacier
  }
}

# TODO: Output provider-specific identifiers (bucket names/IDs, ARNs, etc.).

