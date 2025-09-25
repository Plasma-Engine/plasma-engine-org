/** Outputs for observability module */

output "observability_summary" {
  description = "High-level summary of observability configuration"
  value = {
    name            = var.name
    enable_tracing  = var.enable_tracing
    enable_metrics  = var.enable_metrics
    enable_logging  = var.enable_logging
  }
}

# TODO: Output endpoints/URLs and credentials references as needed.

