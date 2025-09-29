# Plasma Engine - Deployment Guide

## Overview

This guide covers deployment strategies for the Plasma Engine platform across different environments, from local development to production-ready Kubernetes clusters.

## Prerequisites

### System Requirements

#### Development Environment
- **OS**: macOS, Linux, or Windows with WSL2
- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB available space
- **Network**: Stable internet connection

#### Production Environment
- **CPU**: 8+ cores per service instance
- **RAM**: 32GB+ per node
- **Storage**: SSD with 200GB+ available
- **Network**: High-bandwidth, low-latency connection

### Required Software

```bash
# Development tools
docker --version          # >= 24.0.0
docker-compose --version  # >= 2.20.0
kubectl version          # >= 1.28.0
node --version           # >= 20.10.0
python --version         # >= 3.11.0

# Optional but recommended
helm version             # >= 3.12.0
terraform --version     # >= 1.5.0
```

## Local Development Deployment

### Quick Start

1. **Clone and Setup**
```bash
# Clone the main repository
git clone https://github.com/plasma-engine/plasma-engine-org.git
cd plasma-engine-org

# Run complete setup
make setup
```

2. **Start Infrastructure**
```bash
# Start databases and Redis
make start-infra

# Verify infrastructure is running
make ps
```

3. **Start All Services**
```bash
# Start all services in development mode
make run-all

# Or start services individually
make run-gateway      # http://localhost:3000
make run-research     # http://localhost:8000
make run-brand        # http://localhost:8001
make run-content      # http://localhost:8002
make run-agent        # http://localhost:8003
```

### Docker Compose Configuration

The `docker-compose.yml` provides complete local infrastructure:

```yaml
version: '3.8'

services:
  # Databases
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: plasma_engine
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data

  # Elasticsearch for search
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  elasticsearch_data:
```

### Environment Configuration

Each service requires environment variables:

```bash
# Gateway Service (.env)
NODE_ENV=development
PORT=3000
JWT_SECRET=your-super-secret-jwt-key
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your_client_id
REDIS_URL=redis://localhost:6379

# Python Services (.env)
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/plasma_engine
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Staging Deployment

### Docker Registry Setup

1. **Build and Tag Images**
```bash
# Build all service images
make build-all

# Tag for registry
docker tag plasma-engine-gateway:latest your-registry.com/plasma-engine-gateway:staging
docker tag plasma-engine-research:latest your-registry.com/plasma-engine-research:staging
# ... repeat for all services

# Push to registry
make push-staging
```

2. **Staging Docker Compose**
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  gateway:
    image: your-registry.com/plasma-engine-gateway:staging
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=staging
      - DATABASE_URL=postgresql://user:pass@postgres:5432/plasma_staging
    depends_on:
      - postgres
      - redis

  research:
    image: your-registry.com/plasma-engine-research:staging
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://user:pass@postgres:5432/plasma_staging
    depends_on:
      - postgres
      - redis
      - neo4j

  # ... other services
```

3. **Deploy to Staging**
```bash
# Deploy to staging environment
docker-compose -f docker-compose.staging.yml up -d

# Run database migrations
make migrate-staging

# Run health checks
make health-check-staging
```

## Production Deployment

### Kubernetes Deployment

#### Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: plasma-engine
  labels:
    name: plasma-engine
---
apiVersion: v1
kind: Namespace
metadata:
  name: plasma-engine-infra
  labels:
    name: plasma-engine-infra
```

#### ConfigMaps and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: plasma-engine-config
  namespace: plasma-engine
data:
  NODE_ENV: "production"
  REDIS_HOST: "redis-service"
  POSTGRES_HOST: "postgres-service"
  NEO4J_HOST: "neo4j-service"
---
apiVersion: v1
kind: Secret
metadata:
  name: plasma-engine-secrets
  namespace: plasma-engine
type: Opaque
stringData:
  jwt-secret: "your-production-jwt-secret"
  database-password: "your-database-password"
  openai-api-key: "your-openai-key"
  anthropic-api-key: "your-anthropic-key"
```

#### Gateway Service Deployment

```yaml
# k8s/gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: plasma-engine-gateway
  namespace: plasma-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: plasma-engine-gateway
  template:
    metadata:
      labels:
        app: plasma-engine-gateway
    spec:
      containers:
      - name: gateway
        image: your-registry.com/plasma-engine-gateway:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: plasma-engine-config
              key: NODE_ENV
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: plasma-engine-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: gateway-service
  namespace: plasma-engine
spec:
  selector:
    app: plasma-engine-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

#### Research Service Deployment

```yaml
# k8s/research-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: plasma-engine-research
  namespace: plasma-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: plasma-engine-research
  template:
    metadata:
      labels:
        app: plasma-engine-research
    spec:
      containers:
      - name: research
        image: your-registry.com/plasma-engine-research:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgres-service:5432/plasma_production"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: plasma-engine-secrets
              key: database-password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: plasma-engine-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        volumeMounts:
        - name: document-storage
          mountPath: /app/storage
      volumes:
      - name: document-storage
        persistentVolumeClaim:
          claimName: document-storage-pvc
```

#### Database Deployments

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: plasma-engine-infra
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "plasma_production"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: plasma-engine-secrets
              key: database-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
      storageClassName: fast-ssd
```

#### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: plasma-engine-ingress
  namespace: plasma-engine
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.plasma-engine.com
    secretName: plasma-engine-tls
  rules:
  - host: api.plasma-engine.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gateway-service
            port:
              number: 80
```

### Helm Chart Deployment

#### Helm Chart Structure

```
charts/plasma-engine/
├── Chart.yaml
├── values.yaml
├── values.prod.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── hpa.yaml
└── charts/
    ├── postgresql/
    ├── redis/
    └── neo4j/
```

#### Values Configuration

```yaml
# values.prod.yaml
global:
  environment: production
  imageRegistry: your-registry.com
  imageTag: v1.0.0

gateway:
  replicaCount: 3
  image:
    repository: plasma-engine-gateway
  resources:
    requests:
      memory: 512Mi
      cpu: 250m
    limits:
      memory: 1Gi
      cpu: 500m
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

research:
  replicaCount: 2
  image:
    repository: plasma-engine-research
  resources:
    requests:
      memory: 1Gi
      cpu: 500m
    limits:
      memory: 4Gi
      cpu: 2

postgresql:
  enabled: true
  auth:
    database: plasma_production
  primary:
    persistence:
      size: 100Gi
      storageClass: fast-ssd

redis:
  enabled: true
  auth:
    enabled: true
  master:
    persistence:
      size: 10Gi

ingress:
  enabled: true
  hostname: api.plasma-engine.com
  tls: true
  certManager: true
```

#### Deployment Commands

```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install/upgrade Plasma Engine
helm upgrade --install plasma-engine ./charts/plasma-engine \
  --namespace plasma-engine \
  --create-namespace \
  --values ./charts/plasma-engine/values.prod.yaml

# Monitor deployment
kubectl rollout status deployment/plasma-engine-gateway -n plasma-engine
kubectl rollout status deployment/plasma-engine-research -n plasma-engine
```

## Infrastructure as Code (Terraform)

### AWS Infrastructure

```hcl
# terraform/main.tf
provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "plasma-engine-vpc"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Environment = var.environment
    Project     = "plasma-engine"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "plasma-engine-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  node_groups = {
    main = {
      desired_size = 3
      max_size     = 10
      min_size     = 3

      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = {
    Environment = var.environment
    Project     = "plasma-engine"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "plasma-engine-${var.environment}"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "plasma_engine"
  username = "postgres"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.postgres.name

  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"
  backup_retention_period = 7

  skip_final_snapshot = var.environment != "production"

  tags = {
    Environment = var.environment
    Project     = "plasma-engine"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "plasma-engine-redis-${var.environment}"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id         = "plasma-engine-${var.environment}"
  description                  = "Redis cluster for Plasma Engine"

  node_type                    = "cache.r6g.large"
  port                         = 6379
  parameter_group_name         = "default.redis7"

  num_cache_clusters           = 2
  at_rest_encryption_enabled   = true
  transit_encryption_enabled   = true

  subnet_group_name            = aws_elasticache_subnet_group.redis.name
  security_group_ids           = [aws_security_group.redis.id]

  tags = {
    Environment = var.environment
    Project     = "plasma-engine"
  }
}
```

### Deployment Pipeline

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/prod.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/prod.tfvars"

# Get cluster credentials
aws eks update-kubeconfig --region us-west-2 --name plasma-engine-production

# Deploy application
helm upgrade --install plasma-engine ./charts/plasma-engine \
  --namespace plasma-engine \
  --create-namespace \
  --values ./charts/plasma-engine/values.prod.yaml
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: plasma-engine

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [gateway, research, brand, content, agent]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ./plasma-engine-${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2

    - name: Update kubeconfig
      run: aws eks update-kubeconfig --name plasma-engine-production

    - name: Deploy with Helm
      run: |
        helm upgrade --install plasma-engine ./charts/plasma-engine \
          --namespace plasma-engine \
          --create-namespace \
          --values ./charts/plasma-engine/values.prod.yaml \
          --set global.imageTag=${{ github.sha }}

    - name: Wait for deployment
      run: |
        kubectl rollout status deployment/plasma-engine-gateway -n plasma-engine
        kubectl rollout status deployment/plasma-engine-research -n plasma-engine
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'plasma-engine-services'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['plasma-engine']
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: plasma-engine.*
```

### Grafana Dashboards

```bash
# Install monitoring stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Import Plasma Engine dashboards
kubectl apply -f k8s/dashboards/
```

## Troubleshooting

### Common Deployment Issues

1. **Image Pull Errors**
```bash
# Check image registry access
kubectl get pods -n plasma-engine
kubectl describe pod <pod-name> -n plasma-engine

# Verify registry credentials
kubectl get secret -n plasma-engine
```

2. **Database Connection Issues**
```bash
# Check database connectivity
kubectl exec -it <pod-name> -n plasma-engine -- nc -zv postgres-service 5432

# Check environment variables
kubectl exec -it <pod-name> -n plasma-engine -- env | grep DATABASE
```

3. **Resource Issues**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n plasma-engine

# Check resource limits
kubectl describe pod <pod-name> -n plasma-engine
```

### Health Check Endpoints

All services provide health check endpoints:

- `GET /health` - Basic health check
- `GET /ready` - Readiness check (dependencies ready)
- `GET /metrics` - Prometheus metrics

### Log Analysis

```bash
# View service logs
kubectl logs -f deployment/plasma-engine-gateway -n plasma-engine
kubectl logs -f deployment/plasma-engine-research -n plasma-engine

# View all logs with labels
kubectl logs -l app=plasma-engine-gateway -n plasma-engine --tail=100
```

---

This deployment guide provides comprehensive coverage for deploying the Plasma Engine platform across all environments. For additional support, consult the troubleshooting section or contact the platform engineering team.