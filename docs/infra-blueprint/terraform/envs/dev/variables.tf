# Feature flags (disabled by default to allow safe planning)
variable "enable_vpc" { description = "Provision VPC resources" type = bool default = false }
variable "enable_eks" { description = "Provision EKS resources" type = bool default = false }
variable "enable_ecr" { description = "Provision container registries" type = bool default = false }
variable "enable_postgres" { description = "Provision Postgres" type = bool default = false }
variable "enable_redis" { description = "Provision Redis" type = bool default = false }
variable "enable_observability" { description = "Install observability stack via Helm" type = bool default = false }

# Shared
variable "extra_tags" { description = "Extra resource tags" type = map(string) default = {} }

# VPC
variable "vpc_cidr" { description = "VPC CIDR" type = string default = "10.0.0.0/16" }
variable "public_subnet_cidrs" { description = "Public subnet CIDRs" type = list(string) default = ["10.0.0.0/24", "10.0.1.0/24"] }
variable "private_subnet_cidrs" { description = "Private subnet CIDRs" type = list(string) default = ["10.0.10.0/24", "10.0.11.0/24"] }

# EKS
variable "cluster_name" { description = "Cluster name" type = string default = "plasma-dev" }
variable "kubernetes_version" { description = "K8s version" type = string default = "1.30" }
variable "node_instance_types" { description = "Node instance types" type = list(string) default = ["t3.medium"] }
variable "min_size" { description = "Min nodes" type = number default = 1 }
variable "max_size" { description = "Max nodes" type = number default = 3 }
variable "desired_size" { description = "Desired nodes" type = number default = 2 }

# ECR
variable "repository_names" { description = "Container repositories" type = list(string) default = ["gateway", "agent", "brand", "content", "research"] }

# Postgres
variable "db_name" { description = "DB name" type = string default = "plasma_engine" }
variable "engine_version" { description = "Postgres version" type = string default = "15" }
variable "instance_class" { description = "DB instance class" type = string default = "db.t3.medium" }

# Redis
variable "redis_node_type" { description = "Redis node type" type = string default = "cache.t3.small" }

# Observability
variable "obsv_namespace" { description = "Observability namespace" type = string default = "observability" }
variable "kps_chart_version" { description = "kube-prometheus-stack chart version" type = string default = "60.0.0" }
variable "kps_values_file" { description = "Values file path for kube-prometheus-stack" type = string default = "" }
variable "loki_values_file" { description = "Values file path for Loki" type = string default = "" }
variable "tempo_or_jaeger_values_file" { description = "Values file path for Tempo/Jaeger" type = string default = "" }
variable "otelcol_values_file" { description = "Values file path for OpenTelemetry Collector" type = string default = "" }

