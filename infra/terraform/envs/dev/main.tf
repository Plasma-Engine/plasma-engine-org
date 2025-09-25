/**
  Environment: dev

  Purpose: Wire reusable modules with development defaults and minimal capacity.
  Provider configuration is intentionally left as TODO until a cloud target is chosen.

  # TODO: Configure provider(s) and remote state backend for dev.
*/

# terraform {
#   required_version = ">= 1.6.0"
#   backend "s3" {
#     # TODO: Configure remote state for dev environment
#   }
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#   }
# }

# provider "aws" {
#   region = var.region
# }

module "networking" {
  source               = "../../modules/networking"
  name                 = var.name
  cidr_block           = var.cidr_block
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.enable_nat_gateway
}

module "security" {
  source         = "../../modules/security"
  name           = var.name
  secrets_engine = var.secrets_engine
  kms_key_alias  = var.kms_key_alias
}

module "observability" {
  source          = "../../modules/observability"
  name            = var.name
  enable_tracing  = true
  enable_metrics  = true
  enable_logging  = true
}

module "iam" {
  source             = "../../modules/iam"
  name               = var.name
  service_principals = ["gateway", "agent", "content", "research", "brand"]
}

module "storage" {
  source                    = "../../modules/storage"
  name                      = "${var.name}-data"
  enable_versioning         = true
  kms_key_id                = "" # TODO: wire to module.security when implemented
  lifecycle_days_to_glacier = 90
}

module "compute" {
  source          = "../../modules/compute"
  name            = var.name
  desired_count   = 2
  instance_type   = "" # TODO: set when provider chosen
  container_image = "ghcr.io/plasma-engine/gateway:dev" # TODO: adjust per service
  subnet_ids      = [] # TODO: pass from module.networking outputs
}

