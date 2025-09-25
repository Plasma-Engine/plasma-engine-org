/** Outputs for dev environment */

output "dev_summary" {
  description = "High-level summary of dev environment"
  value = {
    name   = var.name
    region = var.region
  }
}

