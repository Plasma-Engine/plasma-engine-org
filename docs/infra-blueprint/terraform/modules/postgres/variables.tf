variable "db_name" {
  description = "Primary database name."
  type        = string
  default     = "plasma_engine"
}

variable "engine_version" {
  description = "Postgres engine version."
  type        = string
  default     = "15"
}

variable "instance_class" {
  description = "Instance size/class."
  type        = string
  default     = "db.t3.medium"
}

variable "subnet_ids" {
  description = "Subnet IDs for DB subnet group (private)."
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "Security groups to attach to the DB."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common resource tags/labels."
  type        = map(string)
  default     = {}
}

