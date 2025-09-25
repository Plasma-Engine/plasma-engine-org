/**
  Observability module (provider/tool-agnostic scaffold)

  Purpose: Set up logging, metrics, tracing sinks and alert channels.

  # TODO: Integrate with chosen stack (e.g., OpenTelemetry collector, Prometheus, Grafana).
*/

locals {
  module_purpose = "Provision observability primitives and alerting"
}

