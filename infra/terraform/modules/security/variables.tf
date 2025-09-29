/** Variables for security module */

variable "name" {
  description = "Name/prefix for security resources"
  type        = string
  validation {
    condition     = length(trim(var.name)) > 0
    error_message = "name must be non-empty."
  }
}

variable "secrets_engine" {
  description = "Secrets manager to integrate with (e.g., AWS Secrets Manager, Vault)"
  type        = string
  default     = null
  validation {
    condition     = var.secrets_engine == null || length(trim(var.secrets_engine)) > 0
    error_message = "secrets_engine must be null or a non-empty string."
  }
}

variable "kms_key_alias" {
  description = "KMS key alias for encryption"
  type        = string
  default     = null
  validation {
    condition     = var.kms_key_alias == null || length(trim(var.kms_key_alias)) > 0
    error_message = "kms_key_alias must be null or a non-empty string."
  }
}

