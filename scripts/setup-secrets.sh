#!/bin/bash

# Setup GitHub Secrets for Plasma Engine
# This script helps configure all required secrets for the project

set -e

REPO="Plasma-Engine/plasma-engine-org"

echo "🔐 Plasma Engine - GitHub Secrets Setup"
echo "======================================="
echo ""
echo "This script will help you set up all required GitHub secrets."
echo "You'll need to have your API keys and credentials ready."
echo ""

# Function to prompt for secret
prompt_secret() {
    local secret_name=$1
    local description=$2
    local required=$3

    echo ""
    echo "📌 $secret_name"
    echo "   $description"

    if [ "$required" = "required" ]; then
        echo "   ⚠️  REQUIRED for basic functionality"
    else
        echo "   ℹ️  Optional - press Enter to skip"
    fi

    read -s -p "   Enter value: " secret_value
    echo ""

    if [ -n "$secret_value" ]; then
        gh secret set "$secret_name" --body "$secret_value" --repo "$REPO"
        echo "   ✅ $secret_name configured"
    else
        if [ "$required" = "required" ]; then
            echo "   ⚠️  WARNING: $secret_name is required but was skipped"
        else
            echo "   ⏭️  Skipped $secret_name"
        fi
    fi
}

echo "🚀 Starting secret configuration..."
echo "===================================="

# Core API Keys
echo ""
echo "1️⃣ CORE API KEYS"
echo "-----------------"
prompt_secret "OPENAI_API_KEY" "OpenAI API key for GPT-4 and embeddings (get from https://platform.openai.com/api-keys)" "required"
prompt_secret "ANTHROPIC_API_KEY" "Anthropic API key for Claude models (get from https://console.anthropic.com/)" "optional"
prompt_secret "APIFY_TOKEN" "Apify API token for web scraping (get from https://console.apify.com/account/integrations)" "required"

# Database Credentials
echo ""
echo "2️⃣ DATABASE CREDENTIALS"
echo "----------------------"
echo "ℹ️  For local development, you can use default values"
prompt_secret "POSTGRES_PASSWORD" "PostgreSQL password (default: postgres)" "optional"
prompt_secret "REDIS_PASSWORD" "Redis password (leave empty for no auth)" "optional"
prompt_secret "NEO4J_PASSWORD" "Neo4j password (default: neo4j)" "optional"

# Authentication
echo ""
echo "3️⃣ AUTHENTICATION"
echo "-----------------"
prompt_secret "JWT_SECRET" "JWT secret key (256-bit random string)" "required"

# External Services
echo ""
echo "4️⃣ EXTERNAL SERVICES (Optional)"
echo "-------------------------------"
prompt_secret "SENTRY_DSN" "Sentry DSN for error tracking" "optional"
prompt_secret "DOCKER_USERNAME" "Docker Hub username" "optional"
prompt_secret "DOCKER_PASSWORD" "Docker Hub password" "optional"

# GitHub
echo ""
echo "5️⃣ GITHUB INTEGRATION"
echo "--------------------"
echo "ℹ️  GitHub token is already configured via gh CLI"

echo ""
echo "======================================="
echo "📊 Secret Configuration Summary"
echo "======================================="
echo ""
echo "Checking configured secrets..."
gh secret list --repo "$REPO"

echo ""
echo "🎯 Next Steps:"
echo "============="
echo ""
echo "1. Critical services to set up:"
echo "   □ Create Apify account: https://console.apify.com/"
echo "   □ Get OpenAI API key: https://platform.openai.com/"
echo "   □ Install CodeRabbit: https://github.com/marketplace/coderabbitai"
echo ""
echo "2. Start local infrastructure:"
echo "   docker-compose -f docker-compose.infrastructure.yml up -d"
echo ""
echo "3. Create local .env files:"
echo "   for service in gateway research brand content agent; do"
echo "     cp plasma-engine-\$service/.env.example plasma-engine-\$service/.env"
echo "   done"
echo ""
echo "4. Verify services are running:"
echo "   curl http://localhost:8000/health  # Research service"
echo "   curl http://localhost:8001/health  # Brand service"
echo "   curl http://localhost:8002/health  # Content service"
echo "   curl http://localhost:8003/health  # Agent service"
echo "   curl http://localhost:7000/health  # Gateway service"
echo ""
echo "✅ Secret setup complete!"