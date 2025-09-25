## Observability Stack (Metrics, Logging, Tracing)

This blueprint outlines a practical, vendor-neutral observability stack following CNCF best practices with OpenTelemetry-first instrumentation.

### Principles
- Prefer OpenTelemetry SDKs/semantic conventions for all services (metrics, traces, logs).
- Centralize collection with the OpenTelemetry Collector; export to Prometheus (metrics), Loki (logs), and Tempo/Jaeger (traces).
- Treat observability as code: values files, dashboards, and alerts committed alongside services.

### Components
- Metrics: Prometheus Operator (`kube-prometheus-stack`) for scraping, recording rules, Alertmanager; Grafana for visualization.
- Logging: Loki (log aggregation) with Promtail or OTel Collector as log receiver; JSON logs with correlation IDs.
- Tracing: Tempo or Jaeger; OTLP ingest via OTel Collector; Grafana Tempo integrates well with Grafana UI.
- Collector: OTel Collector runs as DaemonSet + gateway mode; receives OTLP from apps and exports to backends.

### Ingestion paths
- App → OTLP → OTel Collector (gRPC 4317/HTTP 4318)
- Collector → Prometheus remote-write OR scrape via ServiceMonitor (metrics)
- Collector → Loki (logs) via `loki` exporter
- Collector → Tempo/Jaeger (traces) via `otlp` or specific exporter

### Kubernetes deployment patterns
- Use `ServiceMonitor`/`PodMonitor` for metrics discovery; avoid annotations-only in production.
- Namespaces: `plasma` for apps, `observability` for O11y components.
- Resource requests/limits tuned to avoid eviction during incidents.

### Alerting
- Ship minimal default alerts (node, API server, etc.).
- Add SLO-based multi-window, multi-burn-rate alerting for services. Reference: `https://sre.google/workbook/alerting-on-slos/`

### Dashboards
- Start with curated dashboards from kube-prometheus-stack.
- Add service dashboards with RED/USE methods and expose high-cardinality labels cautiously.

### Security and retention
- TLS in transit for OTel traffic inside the cluster (mTLS recommended via cert-manager/Istio if available).
- Log retention tuned by environment (e.g., 7-14 days dev, 30-90 days prod). Use object storage for durable backends if needed.

### References
- OpenTelemetry Collector: `https://opentelemetry.io/docs/collector/`
- kube-prometheus-stack: `https://github.com/prometheus-operator/kube-prometheus`
- Grafana Loki/Tempo: `https://grafana.com/oss/`
- CNCF TAG Observability: `https://github.com/cncf/tag-observability`

