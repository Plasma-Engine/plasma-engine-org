variable "node_type" {
  description = "Instance/node type for Redis."
  type        = string
  default     = "cache.t3.small"
}

variable "subnet_ids" {
  description = "Private subnet IDs for Redis subnet group."
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "Security groups for Redis access."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common resource tags/labels."
  type        = map(string)
  default     = {}
}

