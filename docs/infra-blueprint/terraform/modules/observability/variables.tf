variable "namespace" {
  description = "Kubernetes namespace for observability components."
  type        = string
  default     = "observability"
}

variable "kps_chart_version" {
  description = "kube-prometheus-stack chart version."
  type        = string
  default     = "60.0.0"
}

variable "kps_values_file" {
  description = "Values YAML file path for kube-prometheus-stack."
  type        = string
  default     = ""
}

variable "loki_values_file" {
  description = "Values YAML file path for Loki."
  type        = string
  default     = ""
}

variable "tempo_or_jaeger_values_file" {
  description = "Values YAML for Tempo or Jaeger."
  type        = string
  default     = ""
}

variable "otelcol_values_file" {
  description = "Values YAML for OpenTelemetry Collector."
  type        = string
  default     = ""
}

