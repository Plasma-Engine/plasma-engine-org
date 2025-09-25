/** Variables for compute module */

variable "name" {
  description = "Workload name/prefix"
  type        = string
}

variable "desired_count" {
  description = "Desired number of instances/pods"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "Instance/machine type (if applicable)"
  type        = string
  default     = ""
}

variable "container_image" {
  description = "Container image to deploy (if containerized)"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for compute placement (from networking module)"
  type        = list(string)
  default     = []
}

# TODO: Add CPU/memory settings, autoscaling policies, and IAM roles as needed.

