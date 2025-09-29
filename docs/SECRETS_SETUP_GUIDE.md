# 🔐 GitHub Secrets Setup Guide

## Overview
This guide explains how to properly configure secrets for GitHub Actions and automated deployments.

## 🎯 Method 1: GitHub Web Interface (Easiest)

1. **Navigate to Repository Settings**
   ```
   https://github.com/Plasma-Engine/plasma-engine-org/settings/secrets/actions
   ```

2. **Add Repository Secrets**
   - Click "New repository secret"
   - Add each secret one by one
   - These are encrypted and only exposed to GitHub Actions

## 🖥️ Method 2: GitHub CLI (Fastest for Multiple Secrets)

### Quick Setup Script
```bash
#!/bin/bash
# Run this from your local machine

REPO="Plasma-Engine/plasma-engine-org"

# Core API Keys (REQUIRED)
gh secret set OPENAI_API_KEY --repo $REPO
gh secret set APIFY_TOKEN --repo $REPO
gh secret set JWT_SECRET --repo $REPO

# Optional but Recommended
gh secret set ANTHROPIC_API_KEY --repo $REPO
gh secret set SENTRY_DSN --repo $REPO

# Database Credentials (for staging/prod)
gh secret set POSTGRES_PASSWORD --repo $REPO
gh secret set REDIS_PASSWORD --repo $REPO
gh secret set NEO4J_PASSWORD --repo $REPO
```

## 🏢 Method 3: Organization Secrets (For Multiple Repos)

If you have multiple repositories, set organization-level secrets:

1. Go to: https://github.com/organizations/Plasma-Engine/settings/secrets/actions
2. Add secrets that all repositories can use
3. Control access per repository

## 🔄 Method 4: GitHub Environments (Best for Staging/Production)

### Create Environments with Specific Secrets

1. **Create Environments**
   ```
   Repository Settings → Environments → New Environment
   ```
   - Create: `development`, `staging`, `production`

2. **Add Environment-Specific Secrets**
   ```yaml
   # In your workflow file
   jobs:
     deploy:
       environment: production
       steps:
         - name: Deploy
           env:
             API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

3. **Configure Protection Rules**
   - Require reviews for production
   - Restrict deployment branches

## 📁 Method 5: Encrypted Files (For Complex Configs)

### Store Encrypted Configuration Files

1. **Install git-crypt or SOPS**
   ```bash
   brew install git-crypt
   # or
   brew install sops
   ```

2. **Encrypt Sensitive Files**
   ```bash
   # Using SOPS
   sops --encrypt --in-place .env.production
   ```

3. **Store Decryption Key in GitHub Secrets**
   ```bash
   gh secret set SOPS_AGE_KEY --repo $REPO
   ```

4. **Decrypt in GitHub Actions**
   ```yaml
   - name: Decrypt secrets
     run: |
       echo "${{ secrets.SOPS_AGE_KEY }}" | sops --decrypt --input-type yaml .env.production.enc > .env
   ```

## 🐳 Method 6: Docker Secrets (For Container Deployments)

### Using Docker BuildKit Secrets

```dockerfile
# Dockerfile
# syntax=docker/dockerfile:1
FROM node:20

# Mount secret during build only
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm install
```

```yaml
# GitHub Actions workflow
- name: Build with secrets
  uses: docker/build-push-action@v4
  with:
    secrets: |
      "npm_token=${{ secrets.NPM_TOKEN }}"
```

## 🚀 Recommended Setup for Plasma Engine

### Step 1: Create Core Secrets Script
```bash
#!/bin/bash
# save as: scripts/github-secrets-setup.sh

echo "🔐 Setting up GitHub Secrets for Plasma Engine"

# Function to safely set secrets
set_secret() {
    local name=$1
    local prompt=$2

    echo -n "$prompt: "
    read -s value
    echo ""

    if [ -n "$value" ]; then
        gh secret set "$name" --repo "Plasma-Engine/plasma-engine-org" --body "$value"
        echo "✅ $name configured"
    else
        echo "⏭️  Skipped $name"
    fi
}

# Required Secrets
echo "📌 REQUIRED SECRETS"
set_secret "OPENAI_API_KEY" "Enter OpenAI API Key (sk-...)"
set_secret "APIFY_TOKEN" "Enter Apify Token"
set_secret "JWT_SECRET" "Enter JWT Secret (generate random 256-bit string)"

# Database Secrets
echo "📌 DATABASE SECRETS"
set_secret "POSTGRES_PASSWORD" "Enter PostgreSQL Password"
set_secret "REDIS_PASSWORD" "Enter Redis Password (or press enter for none)"
set_secret "NEO4J_PASSWORD" "Enter Neo4j Password"

# Optional API Keys
echo "📌 OPTIONAL API KEYS"
set_secret "ANTHROPIC_API_KEY" "Enter Anthropic API Key (optional)"
set_secret "SENTRY_DSN" "Enter Sentry DSN (optional)"

# Docker Registry
echo "📌 DOCKER REGISTRY"
set_secret "DOCKER_USERNAME" "Enter Docker Hub Username"
set_secret "DOCKER_PASSWORD" "Enter Docker Hub Password"

echo "✅ Secrets configuration complete!"
```

### Step 2: Create GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Services

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Deploy
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          APIFY_TOKEN: ${{ secrets.APIFY_TOKEN }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
          REDIS_PASSWORD: ${{ secrets.REDIS_PASSWORD }}
          NEO4J_PASSWORD: ${{ secrets.NEO4J_PASSWORD }}
        run: |
          docker-compose build
          docker-compose push
          # Deploy to your platform
```

### Step 3: Local Development with .env Files

```bash
# Create local .env that's gitignored
cat > .env.local << 'EOF'
# Local Development Secrets (DO NOT COMMIT)
OPENAI_API_KEY=sk-...
APIFY_TOKEN=apify_api_...
JWT_SECRET=local-dev-secret-key
POSTGRES_PASSWORD=postgres
REDIS_PASSWORD=
NEO4J_PASSWORD=neo4j
EOF

# Add to .gitignore
echo ".env.local" >> .gitignore
echo "*.env" >> .gitignore
```

## 🔒 Security Best Practices

### 1. Never Commit Secrets
```bash
# Install pre-commit hooks
pip install pre-commit detect-secrets
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF
pre-commit install
```

### 2. Rotate Secrets Regularly
```yaml
# .github/workflows/rotate-secrets.yml
name: Rotate Secrets Reminder

on:
  schedule:
    - cron: '0 0 1 */3 *' # Every 3 months

jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - name: Create Issue
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🔐 Time to Rotate Secrets',
              body: 'Quarterly reminder to rotate API keys and passwords.',
              labels: ['security', 'maintenance']
            })
```

### 3. Use Least Privilege
- Create service-specific API keys
- Use read-only credentials where possible
- Implement IP allowlisting for production

### 4. Audit Access
```bash
# Check who has access to secrets
gh api /repos/Plasma-Engine/plasma-engine-org/actions/secrets
```

## 🚨 Emergency Secret Rotation

If a secret is exposed:

```bash
#!/bin/bash
# emergency-rotate.sh

# 1. Immediately revoke the compromised key
echo "⚠️  Revoking compromised keys..."

# 2. Generate new secrets
NEW_JWT_SECRET=$(openssl rand -base64 32)
echo "Generated new JWT secret"

# 3. Update GitHub secrets
gh secret set JWT_SECRET --body "$NEW_JWT_SECRET" --repo "Plasma-Engine/plasma-engine-org"

# 4. Trigger redeploy
gh workflow run deploy.yml

# 5. Audit logs
echo "📋 Check audit logs for unauthorized access"
```

## 📊 Secrets Required by Service

| Service | Required Secrets | Optional Secrets |
|---------|-----------------|------------------|
| Gateway | JWT_SECRET | SENTRY_DSN |
| Research | OPENAI_API_KEY, POSTGRES_PASSWORD | ANTHROPIC_API_KEY |
| Brand | APIFY_TOKEN, POSTGRES_PASSWORD | SENTRY_DSN |
| Content | OPENAI_API_KEY, POSTGRES_PASSWORD | ANTHROPIC_API_KEY |
| Agent | OPENAI_API_KEY | ANTHROPIC_API_KEY |

## 🔄 Automated Setup Script

```bash
#!/bin/bash
# Complete automated setup

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    brew install gh
fi

# Authenticate
gh auth login

# Run setup
./scripts/github-secrets-setup.sh

# Verify
echo "Verifying secrets..."
gh secret list --repo "Plasma-Engine/plasma-engine-org"

echo "✅ Setup complete!"
```

## 📝 Next Steps

1. Run the setup script to add all secrets
2. Create environment-specific configurations
3. Set up branch protection rules
4. Configure secret scanning alerts
5. Enable Dependabot security updates

---

**Remember**: Secrets in GitHub Actions are encrypted and only available during workflow runs. They're never exposed in logs or to users without repository access.