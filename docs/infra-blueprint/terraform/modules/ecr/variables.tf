variable "repository_names" {
  description = "List of repository names to create."
  type        = list(string)
  default     = ["gateway", "agent", "brand", "content", "research"]
}

variable "tags" {
  description = "Common resource tags/labels."
  type        = map(string)
  default     = {}
}

