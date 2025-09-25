/** Outputs for compute module */

output "compute_summary" {
  description = "High-level summary of compute configuration"
  value = {
    name           = var.name
    desired_count  = var.desired_count
    instance_type  = var.instance_type
    container_image = var.container_image
  }
}

# TODO: Output runtime-specific values (service URLs, instance IDs, etc.).

