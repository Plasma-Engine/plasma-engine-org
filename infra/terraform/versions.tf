// Explainer: Defines Terraform core and provider version constraints to ensure reproducible builds.
// Inputs: none (static constraints)
// Outputs: n/a
// Downstream: All Terraform configs in this root and child modules inherit these constraints.

terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    // TODO: Consider adding google/azurerm providers when cloud choice is finalized.
  }
}