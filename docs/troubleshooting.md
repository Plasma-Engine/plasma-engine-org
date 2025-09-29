# Plasma Engine - Troubleshooting Guide

## Overview

This guide covers common issues, diagnostic procedures, and solutions for the Plasma Engine platform. Use this as your first reference when encountering problems during development, deployment, or production operations.

## Quick Diagnostic Commands

### Health Check Commands

```bash
# Overall system health
make health-check

# Individual service health
curl http://localhost:3000/health    # Gateway
curl http://localhost:8000/health    # Research
curl http://localhost:8001/health    # Brand
curl http://localhost:8002/health    # Content
curl http://localhost:8003/health    # Agent

# Infrastructure health
make ps                              # Check running containers
make logs                           # View all logs
```

### Service Status Commands

```bash
# Check all service status
make status-all

# Check specific service
cd plasma-engine-<service>
npm run health-check    # TypeScript services
python -m app.health    # Python services

# Check database connections
make db-health
```

## Common Development Issues

### 1. Port Already in Use

**Symptoms:**
- Error: `EADDRINUSE: address already in use :::3000`
- Services fail to start

**Diagnosis:**
```bash
# Find processes using ports
lsof -i :3000
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Check all Plasma Engine processes
ps aux | grep plasma-engine
ps aux | grep node
ps aux | grep python
```

**Solutions:**
```bash
# Kill specific process
kill -9 <PID>

# Kill all Node.js processes
killall node

# Kill all Python processes (be careful!)
pkill -f "python.*plasma-engine"

# Use different ports (development)
PORT=3001 npm run dev
```

### 2. Database Connection Issues

**Symptoms:**
- Connection timeouts
- `could not connect to server`
- Authentication failures

**Diagnosis:**
```bash
# Check if database is running
docker ps | grep postgres
docker ps | grep redis
docker ps | grep neo4j

# Test database connectivity
pg_isready -h localhost -p 5432
redis-cli -h localhost -p 6379 ping
```

**Solutions:**
```bash
# Restart database services
make restart-infra

# Reset databases
make reset-db

# Check database logs
docker logs <postgres_container_id>
docker logs <redis_container_id>

# Verify environment variables
env | grep DATABASE_URL
env | grep REDIS_URL
```

### 3. Node.js / npm Issues

**Symptoms:**
- `Module not found` errors
- TypeScript compilation errors
- Package installation failures

**Diagnosis:**
```bash
# Check Node.js and npm versions
node --version
npm --version

# Check package.json consistency
npm ls
npm audit

# Check TypeScript configuration
npx tsc --noEmit
```

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Remove and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Update packages
npm update

# Fix security vulnerabilities
npm audit fix

# Use correct Node.js version (if using nvm)
nvm use 20.10.0
```

### 4. Python Virtual Environment Issues

**Symptoms:**
- Import errors
- Package not found
- Version conflicts

**Diagnosis:**
```bash
# Check Python version
python --version

# Check virtual environment
which python
which pip

# Check installed packages
pip list
pip show <package_name>
```

**Solutions:**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Update pip
pip install --upgrade pip

# Fix package conflicts
pip install --upgrade --force-reinstall <package_name>
```

### 5. Docker Issues

**Symptoms:**
- Container won't start
- Image build failures
- Volume mount issues

**Diagnosis:**
```bash
# Check Docker status
docker --version
docker-compose --version
docker system info

# Check running containers
docker ps -a

# Check images
docker images

# Check logs
docker logs <container_name>
```

**Solutions:**
```bash
# Restart Docker daemon
sudo systemctl restart docker  # Linux
# or restart Docker Desktop      # Mac/Windows

# Clean Docker system
docker system prune -f
docker volume prune -f

# Rebuild images
docker-compose build --no-cache

# Reset Docker Compose
docker-compose down -v
docker-compose up -d
```

## Service-Specific Issues

### Gateway Service (TypeScript)

**Common Issues:**

1. **GraphQL Schema Federation Errors**
```bash
# Symptoms
Error: Cannot find type "User" in schema

# Diagnosis
npm run schema:validate

# Solutions
# Check service schemas are accessible
curl http://localhost:8000/graphql/schema
curl http://localhost:8001/graphql/schema

# Restart gateway after service changes
npm run dev
```

2. **Authentication Issues**
```bash
# Symptoms
JWT token validation failed

# Diagnosis
# Check JWT secret configuration
echo $JWT_SECRET

# Verify Auth0 configuration
curl -X POST https://$AUTH0_DOMAIN/oauth/token

# Solutions
# Update Auth0 configuration
# Regenerate JWT secrets for development
```

### Research Service (Python)

**Common Issues:**

1. **Neo4j Connection Problems**
```bash
# Symptoms
Failed to establish connection to Neo4j

# Diagnosis
# Check Neo4j is running
docker ps | grep neo4j
curl http://localhost:7474

# Test connection
echo "RETURN 'Hello World' as message" | cypher-shell -u neo4j -p password

# Solutions
# Reset Neo4j data
docker-compose restart neo4j
# or
rm -rf neo4j_data
docker-compose up -d neo4j
```

2. **Vector Database Issues**
```bash
# Symptoms
Embedding search failures
Timeout connecting to Pinecone

# Diagnosis
# Check API keys
echo $PINECONE_API_KEY
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Api-Key: $PINECONE_API_KEY" https://api.pinecone.io/actions/whoami

# Solutions
# Update API keys
# Switch to pgvector for local development
VECTOR_STORE=pgvector python -m app.main
```

3. **Document Processing Issues**
```bash
# Symptoms
Document parsing fails
OCR not working

# Diagnosis
# Check file permissions
ls -la storage/documents/

# Check dependencies
pip show pytesseract
pip show pypdf2

# Solutions
# Install system dependencies (macOS)
brew install tesseract

# Install system dependencies (Ubuntu)
sudo apt-get install tesseract-ocr

# Check file formats
file storage/documents/problematic_file.pdf
```

### Brand Service (Python)

**Common Issues:**

1. **Social Media API Issues**
```bash
# Symptoms
Twitter API rate limit exceeded
Authentication failed

# Diagnosis
# Check API credentials
echo $TWITTER_BEARER_TOKEN
echo $LINKEDIN_CLIENT_ID

# Test API connectivity
curl -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" \
  "https://api.twitter.com/2/users/me"

# Solutions
# Update API credentials
# Implement exponential backoff
# Use different API tiers
```

2. **Sentiment Analysis Issues**
```bash
# Symptoms
Model loading failures
Slow inference times

# Diagnosis
# Check model files
ls -la models/
du -sh models/

# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Solutions
# Download models
python -c "import transformers; transformers.AutoModel.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment-latest')"

# Use smaller models for development
MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english python -m app.main
```

### Content Service (Python)

**Common Issues:**

1. **AI API Rate Limits**
```bash
# Symptoms
OpenAI API rate limit exceeded
Anthropic API quota exceeded

# Diagnosis
# Check API usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/usage"

# Solutions
# Implement request queuing
# Use multiple API keys
# Add retry logic with exponential backoff
```

2. **Content Generation Issues**
```bash
# Symptoms
Generated content doesn't match brand voice
Content is repetitive

# Diagnosis
# Check prompt templates
cat prompts/brand_voice_template.txt

# Check model parameters
grep -r "temperature" app/services/

# Solutions
# Update prompt engineering
# Adjust model parameters
# Implement content diversity checks
```

### Agent Service (Python)

**Common Issues:**

1. **Workflow Execution Failures**
```bash
# Symptoms
Workflows stuck in "running" state
Agent timeouts

# Diagnosis
# Check Celery workers
celery -A app.tasks inspect active

# Check Redis queue
redis-cli llen celery

# Solutions
# Restart Celery workers
celery -A app.tasks worker --loglevel=info

# Purge stuck tasks
celery -A app.tasks purge

# Increase timeout settings
CELERY_TASK_TIME_LIMIT=1800 celery worker
```

2. **Browser Automation Issues**
```bash
# Symptoms
Playwright browser won't start
Headless browser crashes

# Diagnosis
# Check Playwright installation
playwright install --dry-run

# Check system dependencies
ldd $(which chromium-browser)

# Solutions
# Reinstall Playwright browsers
playwright install chromium

# Install system dependencies
sudo apt-get install -y \
  libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
  libgtk-3-0 libatspi2.0-0 libjpeg-turbo8

# Use different browser
PLAYWRIGHT_BROWSER=firefox python -m app.main
```

## Production Issues

### 1. High CPU Usage

**Symptoms:**
- Slow response times
- Service timeouts
- High load average

**Diagnosis:**
```bash
# Check CPU usage
top -o cpu
htop

# Check specific processes
ps aux --sort=-%cpu | head -10

# Check service metrics
kubectl top pods -n plasma-engine
```

**Solutions:**
```bash
# Scale horizontally
kubectl scale deployment plasma-engine-gateway --replicas=5

# Optimize code
# Profile slow endpoints
# Add caching layers
# Implement connection pooling

# Vertical scaling
# Increase CPU limits in Kubernetes
# Use faster instance types
```

### 2. Memory Issues

**Symptoms:**
- Out of memory errors
- Pod restarts
- Slow garbage collection

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check container memory
docker stats

# Check Kubernetes pod memory
kubectl top pods -n plasma-engine
kubectl describe pod <pod-name> -n plasma-engine
```

**Solutions:**
```bash
# Increase memory limits
# In Kubernetes deployment:
resources:
  limits:
    memory: "4Gi"
  requests:
    memory: "2Gi"

# Optimize memory usage
# Implement proper connection pooling
# Add memory profiling
# Use streaming for large datasets
```

### 3. Database Performance Issues

**Symptoms:**
- Slow query performance
- Connection pool exhaustion
- Lock timeouts

**Diagnosis:**
```bash
# PostgreSQL diagnostics
psql -h localhost -U postgres -c "SELECT * FROM pg_stat_activity;"
psql -h localhost -U postgres -c "SELECT * FROM pg_stat_database;"

# Check slow queries
psql -h localhost -U postgres -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Redis diagnostics
redis-cli info memory
redis-cli info clients
redis-cli slowlog get 10
```

**Solutions:**
```bash
# Database optimization
# Add missing indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

# Optimize queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';

# Increase connection pool
# In database configuration:
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB

# Redis optimization
# Increase memory limit
# Configure appropriate eviction policy
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 4. Network Issues

**Symptoms:**
- Intermittent connectivity
- DNS resolution failures
- SSL/TLS errors

**Diagnosis:**
```bash
# Test connectivity between services
kubectl exec -it <pod-name> -- curl http://other-service:8000/health

# Check DNS resolution
kubectl exec -it <pod-name> -- nslookup other-service
kubectl exec -it <pod-name> -- dig other-service

# Check SSL certificates
openssl s_client -connect api.plasma-engine.com:443 -servername api.plasma-engine.com
```

**Solutions:**
```bash
# Fix DNS issues
# Check Kubernetes DNS
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Update SSL certificates
# Using cert-manager
kubectl get certificates -n plasma-engine
kubectl describe certificate plasma-engine-tls -n plasma-engine

# Network policy issues
kubectl get networkpolicies -n plasma-engine
```

## Monitoring and Alerting

### Setting Up Monitoring

**Prometheus Configuration:**
```yaml
# prometheus.yml
scrape_configs:
- job_name: 'plasma-engine-services'
  static_configs:
  - targets: ['gateway:3000', 'research:8000', 'brand:8001', 'content:8002', 'agent:8003']
```

**Key Metrics to Monitor:**
- Response time percentiles (50th, 95th, 99th)
- Error rates
- Request throughput
- Database connection pool usage
- Memory and CPU usage
- Queue depth (Celery/Redis)

### Log Analysis

**Centralized Logging:**
```bash
# ELK Stack setup
docker-compose -f logging/docker-compose.yml up -d

# View logs
kubectl logs -l app=plasma-engine-gateway -n plasma-engine --tail=100
kubectl logs -l app=plasma-engine-research -n plasma-engine --tail=100

# Search logs
grep -i "error" logs/gateway.log
grep -i "timeout" logs/research.log
```

**Structured Log Queries:**
```bash
# Using jq for JSON logs
cat logs/application.log | jq '.level == "ERROR"'
cat logs/application.log | jq 'select(.response_time > 1000)'
```

## Emergency Procedures

### 1. Service Outage Response

```bash
# Quick assessment
make health-check-all
kubectl get pods -n plasma-engine

# Identify failing services
kubectl describe pod <failing-pod> -n plasma-engine
kubectl logs <failing-pod> -n plasma-engine

# Quick fixes
kubectl rollout restart deployment/<service-name> -n plasma-engine
kubectl scale deployment <service-name> --replicas=0 -n plasma-engine
kubectl scale deployment <service-name> --replicas=3 -n plasma-engine
```

### 2. Database Emergency

```bash
# Check database health
kubectl exec -it postgres-0 -- pg_isready

# Create database backup
kubectl exec postgres-0 -- pg_dump plasma_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restart database
kubectl rollout restart statefulset postgres -n plasma-engine-infra

# Restore from backup (if needed)
kubectl exec -i postgres-0 -- psql plasma_production < backup_20240115_140000.sql
```

### 3. Security Incident Response

```bash
# Rotate API keys immediately
kubectl create secret generic plasma-engine-secrets-new \
  --from-literal=jwt-secret=new-jwt-secret \
  --from-literal=database-password=new-db-password

# Update deployments to use new secrets
kubectl patch deployment gateway -p '{"spec":{"template":{"spec":{"containers":[{"name":"gateway","env":[{"name":"JWT_SECRET","valueFrom":{"secretKeyRef":{"name":"plasma-engine-secrets-new","key":"jwt-secret"}}}]}]}}}}'

# Review access logs
grep -i "unauthorized\|forbidden\|suspicious" logs/gateway.log
```

## Performance Optimization

### 1. Query Optimization

```sql
-- Identify slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_brand_mentions_created_at ON brand_mentions(created_at);
CREATE INDEX CONCURRENTLY idx_users_email_active ON users(email) WHERE active = true;
```

### 2. Caching Strategy

```python
# Redis caching implementation
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache_with_ttl(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute and cache
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result, default=str))

            return result
        return wrapper
    return decorator
```

### 3. Connection Pooling

```python
# SQLAlchemy connection pooling
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Additional connections when needed
    pool_pre_ping=True,        # Validate connections before use
    pool_recycle=300,          # Recycle connections every 5 minutes
    connect_args={
        "connect_timeout": 10,  # Connection timeout
        "application_name": "plasma-engine-research"
    }
)
```

## Getting Help

### 1. Documentation Resources

- [Architecture Documentation](architecture.md)
- [API Reference](api-reference.md)
- [Development Guide](development.md)
- [Deployment Guide](deployment.md)

### 2. Support Channels

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/plasma-engine/plasma-engine-org/issues)
- **Development Team**: Contact the platform engineering team
- **Community**: Join the developer Slack workspace
- **Emergency**: Use the on-call escalation procedure

### 3. Diagnostic Information to Provide

When reporting issues, include:

```bash
# System information
uname -a
docker --version
kubectl version --client

# Service information
make status-all
kubectl get pods -n plasma-engine -o wide

# Logs (last 100 lines)
kubectl logs <pod-name> -n plasma-engine --tail=100

# Resource usage
kubectl top pods -n plasma-engine
kubectl describe node <node-name>

# Configuration
kubectl get configmap plasma-engine-config -n plasma-engine -o yaml
```

---

This troubleshooting guide covers the most common issues encountered with the Plasma Engine platform. Keep this document updated as new issues and solutions are discovered. For issues not covered here, don't hesitate to reach out to the development team for assistance.