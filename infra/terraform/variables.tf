//
// Explainer: Input variables with conservative defaults. Avoid secret values.
// Prefer environment variables and CI secret stores for sensitive inputs.
//

variable "environment" {
  description = "Deployment environment name (e.g., dev, stage, prod)"
  type        = string
  default     = "dev"
}

// AWS examples
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Local AWS profile for developer use only (not used in CI)."
  type        = string
  default     = null
}

// GCP examples
variable "gcp_project" {
  description = "GCP project id"
  type        = string
  default     = null
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = null
}

// Azure examples
variable "azure_subscription_id" {
  description = "Azure subscription id"
  type        = string
  default     = null
}

