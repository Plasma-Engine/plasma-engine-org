#!/bin/bash

# 🔐 Quick GitHub Secrets Setup for Plasma Engine
# This script adds all required secrets to your GitHub repository

set -e

REPO="Plasma-Engine/plasma-engine-org"

echo "🔐 Plasma Engine - GitHub Secrets Quick Setup"
echo "============================================="
echo ""
echo "This will add secrets to: $REPO"
echo ""

# Check if gh CLI is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated. Running 'gh auth login'..."
    gh auth login
fi

# Function to add a secret
add_secret() {
    local name=$1
    local prompt=$2
    local required=$3

    echo ""
    echo "📌 $name"
    if [ "$required" = "true" ]; then
        echo "   ⚠️  REQUIRED - This secret is critical for the system to work"
    else
        echo "   ℹ️  Optional - Press Enter to skip"
    fi
    echo "   $prompt"

    read -s -p "   Value: " value
    echo ""

    if [ -n "$value" ]; then
        echo "$value" | gh secret set "$name" --repo "$REPO"
        echo "   ✅ $name added successfully"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "   ⚠️  WARNING: $name is required but was skipped!"
            return 1
        else
            echo "   ⏭️  Skipped $name"
            return 0
        fi
    fi
}

# Track if all required secrets are set
all_required_set=true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  CRITICAL API KEYS (Required)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

add_secret "OPENAI_API_KEY" "Get from: https://platform.openai.com/api-keys" "true" || all_required_set=false
add_secret "APIFY_TOKEN" "Get from: https://console.apify.com/account/integrations" "true" || all_required_set=false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  AUTHENTICATION (Required)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate a random JWT secret if not provided
echo ""
echo "📌 JWT_SECRET"
echo "   ⚠️  REQUIRED - Used for authentication"
echo "   Press Enter to auto-generate a secure random key, or paste your own"
read -s -p "   Value: " jwt_value
echo ""

if [ -z "$jwt_value" ]; then
    jwt_value=$(openssl rand -base64 32)
    echo "   🔑 Generated random JWT secret"
fi

echo "$jwt_value" | gh secret set "JWT_SECRET" --repo "$REPO"
echo "   ✅ JWT_SECRET added successfully"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  OPTIONAL API KEYS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

add_secret "ANTHROPIC_API_KEY" "Get from: https://console.anthropic.com/" "false"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  DATABASE PASSWORDS (Optional for local dev)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

add_secret "POSTGRES_PASSWORD" "Default: postgres (press Enter to skip)" "false"
add_secret "REDIS_PASSWORD" "Usually empty for local (press Enter to skip)" "false"
add_secret "NEO4J_PASSWORD" "Default: neo4j (press Enter to skip)" "false"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  MONITORING (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

add_secret "SENTRY_DSN" "Get from: https://sentry.io/" "false"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Current secrets in repository:"
gh secret list --repo "$REPO"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$all_required_set" = true ]; then
    echo "✅ All required secrets have been configured!"
    echo ""
    echo "Your GitHub Actions workflows can now:"
    echo "  • Use OpenAI API for AI features"
    echo "  • Use Apify for social media monitoring"
    echo "  • Authenticate users with JWT"
else
    echo "⚠️  Some required secrets are missing!"
    echo ""
    echo "Missing secrets will cause failures in:"
    echo "  • GitHub Actions workflows"
    echo "  • Automated deployments"
    echo "  • CI/CD pipelines"
    echo ""
    echo "Please run this script again to add missing secrets."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Secrets are now available in GitHub Actions:"
echo "   \${{ secrets.OPENAI_API_KEY }}"
echo "   \${{ secrets.APIFY_TOKEN }}"
echo "   \${{ secrets.JWT_SECRET }}"
echo ""
echo "2. Use in your workflows:"
echo "   - name: Deploy"
echo "     env:"
echo "       OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}"
echo ""
echo "3. For local development, create .env files:"
echo "   cp plasma-engine-*/.env.example plasma-engine-*/.env"
echo "   # Then add the same values to your local .env files"
echo ""
echo "4. View secrets at:"
echo "   https://github.com/$REPO/settings/secrets/actions"
echo ""
echo "✅ Setup complete!"