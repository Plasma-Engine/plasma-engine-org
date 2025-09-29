# Environment: dev
# Purpose: Demonstrate how to wire modules together using feature flags so this file is safe to plan without provisioning anything by default.

terraform {
  required_version = ">= 1.5.0"
}

locals {
  common_tags = merge(
    {
      "project"   = "plasma-engine"
      "env"       = "dev"
      "managedBy" = "terraform"
    },
    var.extra_tags
  )
}

module "vpc" {
  source   = "../../modules/vpc"
  count    = var.enable_vpc ? 1 : 0
  vpc_cidr = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  tags = local.common_tags
}

module "eks" {
  source  = "../../modules/eks"
  count   = var.enable_eks ? 1 : 0
  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  private_subnet_ids = module.vpc[0].private_subnet_ids
  node_instance_types = var.node_instance_types
  min_size = var.min_size
  max_size = var.max_size
  desired_size = var.desired_size
  tags = local.common_tags
}

module "ecr" {
  source = "../../modules/ecr"
  count  = var.enable_ecr ? 1 : 0
  repository_names = var.repository_names
  tags = local.common_tags
}

module "postgres" {
  source = "../../modules/postgres"
  count  = var.enable_postgres ? 1 : 0
  db_name                 = var.db_name
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  subnet_ids              = module.vpc[0].private_subnet_ids
  vpc_security_group_ids  = []
  tags = local.common_tags
}

module "redis" {
  source = "../../modules/redis"
  count  = var.enable_redis ? 1 : 0
  node_type               = var.redis_node_type
  subnet_ids              = module.vpc[0].private_subnet_ids
  vpc_security_group_ids  = []
  tags = local.common_tags
}

module "observability" {
  source = "../../modules/observability"
  count  = var.enable_observability ? 1 : 0
  namespace             = var.obsv_namespace
  kps_chart_version     = var.kps_chart_version
  kps_values_file       = var.kps_values_file
  loki_values_file      = var.loki_values_file
  tempo_or_jaeger_values_file = var.tempo_or_jaeger_values_file
  otelcol_values_file   = var.otelcol_values_file
}

