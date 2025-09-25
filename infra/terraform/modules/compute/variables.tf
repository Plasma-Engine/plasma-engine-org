variable "name_prefix" {
  description = "Prefix for naming compute resources"
  type        = string
}

variable "vpc_id" {
  description = "Target VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for compute resources"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}