/**
  Variables for networking module

  # TODO: Finalize defaults and validation according to org standards.
*/

variable "name" {
  description = "Human-readable name/prefix for networking resources"
  type        = string
}

variable "cidr_block" {
  description = "Primary CIDR block for VPC/VNet (e.g., 10.0.0.0/16)"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones/regions to spread subnets across"
  type        = list(string)
  default     = []
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets"
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "CIDRs for private subnets"
  type        = list(string)
  default     = []
}

variable "enable_nat_gateway" {
  description = "Whether to provision NAT for private egress"
  type        = bool
  default     = true
}

