// Explainer: Root variables used across the Terraform stack for provider configuration and tagging.
// Inputs: Provided by CI or env-specific tfvars
// Outputs: n/a
// Downstream: Referenced by providers and modules for consistent configuration.

variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1" // TODO: Confirm default region
}

variable "default_tags" {
  description = "Default resource tags applied to all resources"
  type        = map(string)
  default = {
    project     = "plasma-engine"
    environment = "dev"
    owner       = "devops"
  }
}