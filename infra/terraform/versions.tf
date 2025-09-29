//
// Explainer: Pin Terraform and provider versions for reproducibility.
// Adjust constraints intentionally and record changes in the activity log.
//

terraform {
  required_version = ">= 1.5.0, < 2.0.0" // TODO(infra@plasma): Align with team standard

  required_providers {
    // Example providers — uncomment and pin as needed
    // aws = {
    //   source  = "hashicorp/aws"
    //   version = "~> 5.0"
    // }
    // google = {
    //   source  = "hashicorp/google"
    //   version = "~> 5.0"
    // }
    // azurerm = {
    //   source  = "hashicorp/azurerm"
    //   version = "~> 3.0"
    // }
  }
}

