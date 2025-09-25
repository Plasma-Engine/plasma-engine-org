variable "name_prefix" {
  description = "Prefix for naming resources in dev"
  type        = string
  default     = "plasma-dev"
}

variable "cidr_block" {
  description = "CIDR block for the dev VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "azs" {
  description = "Availability zones to use in dev"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "tags" {
  description = "Tags to apply to dev resources"
  type        = map(string)
  default = {
    environment = "dev"
    project     = "plasma-engine"
  }
}