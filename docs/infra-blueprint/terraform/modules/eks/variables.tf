variable "cluster_name" {
  description = "Name of the Kubernetes cluster."
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes control plane version (e.g., 1.30)."
  type        = string
  default     = "1.30"
}

variable "private_subnet_ids" {
  description = "Subnet IDs where nodes should run (usually private)."
  type        = list(string)
  default     = []
}

variable "node_instance_types" {
  description = "List of instance types for node groups."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "min_size" {
  description = "Minimum nodes in the default node group."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum nodes in the default node group."
  type        = number
  default     = 4
}

variable "desired_size" {
  description = "Desired nodes in the default node group."
  type        = number
  default     = 2
}

variable "tags" {
  description = "Common resource tags/labels."
  type        = map(string)
  default     = {}
}

