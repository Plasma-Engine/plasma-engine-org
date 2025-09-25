/** Variables for IAM module */

variable "name" {
  description = "Name/prefix for IAM resources"
  type        = string
}

variable "service_principals" {
  description = "List of services that require roles/policies"
  type        = list(string)
  default     = []
}

variable "admin_users" {
  description = "Admin users or groups that need elevated permissions"
  type        = list(string)
  default     = []
}

# TODO: Add policy definitions and bindings per service.

