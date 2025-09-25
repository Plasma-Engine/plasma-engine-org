# Module: observability
# Purpose: Install and configure the core observability stack in Kubernetes via Helm provider.
# Components:
# - kube-prometheus-stack (Prometheus Operator, Alertmanager, Grafana)
# - Loki for logs
# - Tempo or Jaeger for traces
# - OpenTelemetry Collector for OTLP ingestion and export to backends
# Notes:
# - This module expects an existing Kubernetes provider context and permissions.
# - Values should be externally configurable for storage classes, retention, resource limits, and dashboards.

terraform {
  required_version = ">= 1.5.0"
}

# Example resources (commented – provider specifics omitted):
# resource "helm_release" "kps" {
#   name       = "kube-prometheus-stack"
#   repository = "https://prometheus-community.github.io/helm-charts"
#   chart      = "kube-prometheus-stack"
#   version    = var.kps_chart_version
#   values     = [file(var.kps_values_file)]
#   namespace  = var.namespace
# }

