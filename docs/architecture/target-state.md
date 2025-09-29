## Plasma Engine – Target-State Architecture (Draft)

This document captures the target deployable architecture for the Plasma Engine platform. Diagrams are provided in Mermaid for portability. All components and decisions are commentary-rich to support handoff to engineers.

### High-level context

```mermaid
flowchart LR
  subgraph Clients
    U1[Web
    UI]
    U2[CLI]
    U3[Automation/
    Schedulers]
  end

  U1-- HTTPS --> G[API Gateway]
  U2-- HTTPS --> G
  U3-- HTTPS --> G

  subgraph Kubernetes Cluster (EKS/GKE/AKS)
    G
    A[plasma-engine-agent]
    B[plasma-engine-brand]
    C[plasma-engine-content]
    R[plasma-engine-research]

    Q[Async Queue
    (SQS/RabbitMQ/Kafka)]
    W[Workers]
  end

  DB[(Postgres)]
  Cache[(Redis)]
  Obj[(Object Storage
  e.g., S3)]

  G <--> A
  G <--> B
  G <--> C
  G <--> R

  A <--> Q
  B <--> Q
  C <--> Q
  R <--> Q
  W <--> Q

  A <--> DB
  B <--> DB
  C <--> DB
  R <--> DB

  A <--> Cache
  B <--> Cache
  C <--> Cache
  R <--> Cache

  A --- Obj
  B --- Obj
  C --- Obj
  R --- Obj

  subgraph Observability
    P[Prometheus Operator]
    L[Loki]
    T[Tempo/Jaeger]
    O[OpenTelemetry Collector]
    Gr[Grafana]
  end

  O <-- OTLP --> A
  O <-- OTLP --> B
  O <-- OTLP --> C
  O <-- OTLP --> R
  O <-- OTLP --> G
  O --> P
  O --> L
  O --> T
  Gr <--> P
  Gr <--> L
  Gr <--> T
```

Notes:
- API Gateway provides routing, authz/authn, rate-limits, and observability headers.
- Core services run in a managed Kubernetes cluster. Async jobs are handled via a queue + worker pool.
- Data plane includes Postgres, Redis, and Object Storage. Replace with cloud provider equivalents as required.
- Observability follows OpenTelemetry-first collection with Prometheus/Loki/Tempo (or Jaeger) backends and Grafana dashboards.

### Kubernetes deployment view

```mermaid
flowchart TB
  subgraph Namespace: plasma
    subgraph Deployment: gateway
      GPod1(Pod)
      GPod2(Pod)
    end
    subgraph Deployment: agent
      APod1(Pod)
      APod2(Pod)
    end
    subgraph Deployment: brand
      BPod1(Pod)
    end
    subgraph Deployment: content
      CPod1(Pod)
      CPod2(Pod)
    end
    subgraph Deployment: research
      RPod1(Pod)
    end
    subgraph Stateful: postgres
      PSts(StatefulSet)
      PV(Managed Storage)
    end
    subgraph Cache: redis
      RSts(StatefulSet)
    end
    SVCG[(Service
    gateway)]
    SVCA[(Service
    agent)]
    SVCB[(Service
    brand)]
    SVCC[(Service
    content)]
    SVCR[(Service
    research)]
  end

  Ingress((Ingress/ALB)) --> SVCG
  SVCG --> GPod1
  SVCG --> GPod2
  SVCA --> APod1
  SVCA --> APod2
  SVCB --> BPod1
  SVCC --> CPod1
  SVCC --> CPod2
  SVCR --> RPod1

  APod1 -.-> PSts
  APod2 -.-> PSts
  BPod1 -.-> PSts
  CPod1 -.-> PSts
  CPod2 -.-> PSts
  RPod1 -.-> PSts

  APod1 -.-> RSts
  APod2 -.-> RSts
  BPod1 -.-> RSts
  CPod1 -.-> RSts
  CPod2 -.-> RSts
  RPod1 -.-> RSts
```

Assumptions:
- Managed database/cache services are preferred in production. For local/dev clusters, use Helm charts for Postgres/Redis with persistence classes.
- Ingress is backed by cloud ALB/NLB depending on need. TLS termination at the ingress with mTLS used internally for sensitive services.

### Deployment pipeline overview

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant GH as GitHub Actions
  participant REG as Container Registry
  participant TF as Terraform
  participant K8s as Helm/Kubernetes

  Dev->>GH: PR opens/updates
  GH->>GH: Lint/Test/Security (matrix per service)
  GH->>TF: Terraform plan (staging)
  GH->>Dev: Status checks (required)
  Dev->>GH: Merge to main
  GH->>REG: Build & push images (tag+sha)
  GH->>K8s: Helm upgrade --install (staging)
  Note over GH,K8s: Prod deploy requires manual approval via environment gate
  GH->>TF: Terraform apply (prod) upon approval
  GH->>K8s: Helm deploy to prod upon approval
```

References:
- OpenTelemetry Collector and OTLP: `https://opentelemetry.io/docs/collector/`
- Prometheus Operator (kube-prometheus-stack): `https://github.com/prometheus-operator/kube-prometheus`
- Loki/Tempo/Grafana: `https://grafana.com/oss/`
- CNCF TAG Observability best practices: `https://github.com/cncf/tag-observability`

