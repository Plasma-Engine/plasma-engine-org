/** Variables for storage module */

variable "name" {
  description = "Name/prefix for storage resources"
  type        = string
}

variable "enable_versioning" {
  description = "Enable object versioning if supported"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key identifier for encryption at rest (if applicable)"
  type        = string
  default     = ""
}

variable "lifecycle_days_to_glacier" {
  description = "After how many days to transition objects to cold storage"
  type        = number
  default     = 90
}

