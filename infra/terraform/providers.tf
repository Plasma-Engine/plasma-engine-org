// Explainer: Configures the AWS provider. This is the default provider until the cloud decision is finalized.
// Inputs: variables.tf (aws_region, default_tags)
// Outputs: n/a
// Downstream: Used by modules to provision resources in the specified region and with default tags.
// Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.default_tags
  }
}

// TODO: Owner=DevOps: If GCP/Azure is selected, add matching provider blocks and conditionally configure via variables.