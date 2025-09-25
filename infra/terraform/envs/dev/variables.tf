/** Variables for dev environment composition */

variable "name" {
  description = "Environment name/prefix"
  type        = string
  default     = "pe-dev"
}

variable "region" {
  description = "Cloud region for resources"
  type        = string
  default     = "us-east-1"
}

variable "cidr_block" {
  description = "Primary CIDR for the VPC/VNet"
  type        = string
  default     = "10.10.0.0/16"
}

variable "availability_zones" {
  description = "Zones for subnet spread"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs"
  type        = list(string)
  default     = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT for private egress"
  type        = bool
  default     = true
}

variable "secrets_engine" {
  description = "Secrets manager to use"
  type        = string
  default     = ""
}

variable "kms_key_alias" {
  description = "KMS key alias for encryption"
  type        = string
  default     = ""
}

