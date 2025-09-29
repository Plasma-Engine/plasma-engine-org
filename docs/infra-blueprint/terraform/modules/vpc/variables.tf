# Variables for VPC module

variable "vpc_cidr" {
  description = "Primary CIDR block for the VPC (e.g., 10.0.0.0/16)."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets (one per AZ)."
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets (one per AZ)."
  type        = list(string)
  default     = []
}

variable "enable_nat_gateways" {
  description = "Whether to provision NAT gateways for private egress."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common resource tags/labels."
  type        = map(string)
  default     = {}
}

