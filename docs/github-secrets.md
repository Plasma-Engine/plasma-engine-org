# GitHub Secrets Configuration

This document outlines the required GitHub Secrets for the Plasma Engine CI/CD pipeline.

## Required Secrets

### Container Registry
- **GITHUB_TOKEN**: Automatically provided by GitHub Actions for GHCR access

### External Services
- **SNYK_TOKEN**: Token for Snyk security scanning
- **CODECOV_TOKEN**: Token for code coverage reporting
- **OPENAI_API_KEY**: OpenAI API key for CodeRabbit AI reviews

### Deployment Secrets (Production)
- **PRODUCTION_DEPLOY_KEY**: SSH key for production deployment
- **STAGING_DEPLOY_KEY**: SSH key for staging deployment
- **DATABASE_URL**: Production database connection string
- **REDIS_URL**: Redis connection string for caching

### Environment Configuration
- **SECRET_KEY**: Application secret key for JWT and encryption
- **POSTGRES_PASSWORD**: Database password
- **POSTGRES_USER**: Database username
- **POSTGRES_DB**: Database name

## Setting Up Secrets

### 1. Repository Secrets
Navigate to your repository → Settings → Secrets and variables → Actions

### 2. Required Repository Secrets

```bash
# Snyk security scanning
SNYK_TOKEN="your-snyk-token-here"

# Code coverage
CODECOV_TOKEN="your-codecov-token-here"

# AI code reviews
OPENAI_API_KEY="your-openai-api-key-here"

# Database configuration
DATABASE_URL="postgresql://user:password@host:5432/dbname"
POSTGRES_PASSWORD="secure-password"
POSTGRES_USER="plasma_engine"
POSTGRES_DB="plasma_engine"

# Application secrets
SECRET_KEY="your-secret-key-256-bits"

# Deployment keys
PRODUCTION_DEPLOY_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----"

STAGING_DEPLOY_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----"
```

### 3. Environment-Specific Secrets

#### Staging Environment
- Environment name: `staging`
- URL: `https://staging.plasma-engine.dev`
- Secrets:
  - `STAGING_DATABASE_URL`
  - `STAGING_SECRET_KEY`

#### Production Environment
- Environment name: `production`
- URL: `https://plasma-engine.dev`
- Secrets:
  - `PRODUCTION_DATABASE_URL`
  - `PRODUCTION_SECRET_KEY`

## Environment Variables per Service

### Gateway Service (Node.js)
```env
NODE_ENV=production
PORT=3000
DATABASE_URL=${{ secrets.DATABASE_URL }}
JWT_SECRET=${{ secrets.SECRET_KEY }}
LOG_LEVEL=info
```

### Python Services (Research, Brand, Content, Agent)
```env
ENVIRONMENT=production
DATABASE_URL=${{ secrets.DATABASE_URL }}
SECRET_KEY=${{ secrets.SECRET_KEY }}
LOG_LEVEL=info
REDIS_URL=${{ secrets.REDIS_URL }}
```

## Security Best Practices

### 1. Secret Rotation
- Rotate secrets every 90 days
- Use GitHub's secret scanning alerts
- Never commit secrets to code

### 2. Access Control
- Use environment-specific secrets
- Limit secret access to required workflows
- Use OIDC for cloud provider authentication when possible

### 3. Monitoring
- Enable secret scanning
- Monitor for secret exposure in logs
- Set up alerts for failed authentication

## Validation Scripts

### Check Required Secrets
```bash
#!/bin/bash
# Check if all required secrets are set

required_secrets=(
  "SNYK_TOKEN"
  "CODECOV_TOKEN"
  "OPENAI_API_KEY"
  "DATABASE_URL"
  "SECRET_KEY"
)

for secret in "${required_secrets[@]}"; do
  if [[ -z "${!secret}" ]]; then
    echo "❌ Missing required secret: $secret"
    exit 1
  else
    echo "✅ $secret is set"
  fi
done

echo "🎉 All required secrets are configured!"
```

### Test Database Connection
```bash
#!/bin/bash
# Test database connectivity with secrets

if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
  echo "✅ Database connection successful"
else
  echo "❌ Database connection failed"
  exit 1
fi
```

## Troubleshooting

### Common Issues
1. **Invalid database URL format**
   - Format: `postgresql://user:password@host:port/database`

2. **Secret not accessible in workflow**
   - Check environment configuration
   - Verify secret name spelling

3. **Token authentication failures**
   - Verify token is not expired
   - Check token permissions/scopes

### Debug Mode
Enable debug logging by setting:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## Contact
For issues with secret configuration, contact the DevOps team or create an issue in the repository.