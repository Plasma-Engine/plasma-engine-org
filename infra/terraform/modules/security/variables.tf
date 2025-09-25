/** Variables for security module */

variable "name" {
  description = "Name/prefix for security resources"
  type        = string
}

variable "secrets_engine" {
  description = "Secrets manager to integrate with (e.g., AWS Secrets Manager, Vault)"
  type        = string
  default     = ""
}

variable "kms_key_alias" {
  description = "KMS key alias for encryption"
  type        = string
  default     = ""
}

