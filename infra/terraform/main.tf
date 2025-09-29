//
// Explainer: Compose modules and resources here. This is a placeholder that
// demonstrates how to wire modules with labels/tags and environment context.
//

locals {
  // Standardized labels for tagging resources across providers
  labels = {
    project     = "plasma-engine"
    environment = var.environment
    managed_by  = "terraform"
    owner       = "infra@plasma"
  }
}

// Example module wiring (uncomment and replace with real modules)
// module "network" {
//   source = "./modules/network"
//   labels = local.labels
// }

