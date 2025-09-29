#!/bin/bash

# Script to fix secret leaks in Plasma Engine repository

echo "🔐 Fixing Secret Leaks in Plasma Engine Repository"
echo "==================================================="
echo ""

# Remove secrets from current files
echo "1️⃣ Removing secrets from tracked files..."

# Fix SERVICES_AND_SECRETS.md - replace example token with placeholder
if [ -f "SERVICES_AND_SECRETS.md" ]; then
    echo "   Fixing SERVICES_AND_SECRETS.md..."
    sed -i '' 's/ghp_[a-zA-Z0-9_]*/YOUR_GITHUB_TOKEN_HERE/g' SERVICES_AND_SECRETS.md
    sed -i '' 's/GITHUB_TOKEN: ".*"/GITHUB_TOKEN: "YOUR_GITHUB_TOKEN_HERE"/g' SERVICES_AND_SECRETS.md
fi

# Search for any Google API keys (AIza pattern)
echo "   Searching for Google API keys..."
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.md" \) \
    -not -path "./.git/*" -not -path "./.venv*/*" -not -path "./node_modules/*" \
    -exec grep -l "AIza" {} \; 2>/dev/null | while read file; do
    echo "   Fixing $file..."
    sed -i '' 's/AIza[a-zA-Z0-9_-]*/YOUR_GOOGLE_API_KEY_HERE/g' "$file"
done

# Search for other potential secrets
echo "   Searching for other exposed secrets..."
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.md" \) \
    -not -path "./.git/*" -not -path "./.venv*/*" -not -path "./node_modules/*" \
    -exec grep -l -E "sk-[a-zA-Z0-9]{48}|sk-ant-[a-zA-Z0-9]{48}" {} \; 2>/dev/null | while read file; do
    echo "   Fixing $file..."
    sed -i '' 's/sk-[a-zA-Z0-9]\{48\}/sk-YOUR_OPENAI_KEY_HERE/g' "$file"
    sed -i '' 's/sk-ant-[a-zA-Z0-9]\{48\}/sk-ant-YOUR_ANTHROPIC_KEY_HERE/g' "$file"
done

echo ""
echo "2️⃣ Creating .gitignore entries..."

# Ensure sensitive files are in .gitignore
if ! grep -q "# Secrets and credentials" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Secrets and credentials" >> .gitignore
    echo "*.env" >> .gitignore
    echo ".env.*" >> .gitignore
    echo "!.env.example" >> .gitignore
    echo "*_credentials.json" >> .gitignore
    echo "*_secrets.json" >> .gitignore
    echo "*.pem" >> .gitignore
    echo "*.key" >> .gitignore
    echo "*.cert" >> .gitignore
    echo "*.p12" >> .gitignore
    echo "**/secrets/*" >> .gitignore
    echo "**/credentials/*" >> .gitignore
    echo "   Added security entries to .gitignore"
fi

echo ""
echo "3️⃣ Creating secure .env.example file..."

cat > .env.example << 'EOF'
# Plasma Engine Environment Variables Template
# Copy this file to .env and fill in your actual values
# NEVER commit .env file with real secrets!

# OpenAI API
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE

# Google Cloud
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# GitHub
GITHUB_TOKEN=YOUR_GITHUB_TOKEN_HERE
GITHUB_APP_ID=YOUR_APP_ID_HERE
GITHUB_APP_PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE

# Apify (for web scraping)
APIFY_TOKEN=YOUR_APIFY_TOKEN_HERE

# BrightData (alternative scraping)
BRIGHTDATA_USERNAME=YOUR_USERNAME_HERE
BRIGHTDATA_PASSWORD=YOUR_PASSWORD_HERE

# ScraperAPI (alternative scraping)
SCRAPERAPI_KEY=YOUR_SCRAPERAPI_KEY_HERE

# Database - PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=plasma_engine
POSTGRES_USER=plasma_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD

# Database - Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_THIS_PASSWORD

# Database - Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=CHANGE_THIS_PASSWORD

# JWT Authentication
JWT_SECRET=GENERATE_A_256_BIT_SECRET_HERE
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400

# Service URLs (Internal)
GATEWAY_URL=http://localhost:7000
RESEARCH_URL=http://localhost:8000
BRAND_URL=http://localhost:8001
CONTENT_URL=http://localhost:8002
AGENT_URL=http://localhost:8003

# Monitoring
SENTRY_DSN=YOUR_SENTRY_DSN_HERE

# Feature Flags
DEBUG=false
ENVIRONMENT=development
EOF

echo "   Created .env.example template"

echo ""
echo "4️⃣ Committing fixes..."

git add .gitignore .env.example SERVICES_AND_SECRETS.md
git commit -m "security: Remove exposed secrets and add security templates

- Removed exposed GitHub Personal Access Token
- Removed exposed Google API Key
- Added .env.example template with placeholders
- Updated .gitignore with security entries
- Fixed SERVICES_AND_SECRETS.md to use placeholders

This commit fixes the secret leaks detected by GitHub secret scanning.
All sensitive values have been replaced with secure placeholders."

echo ""
echo "5️⃣ Cleaning Git history (IMPORTANT)..."
echo ""
echo "⚠️  WARNING: The secrets are still in your Git history!"
echo "To fully remove them, you need to:"
echo ""
echo "Option 1: Force push clean history (DESTRUCTIVE):"
echo "  git filter-branch --force --index-filter \\"
echo "    'git rm --cached --ignore-unmatch SERVICES_AND_SECRETS.md' \\"
echo "    --prune-empty --tag-name-filter cat -- --all"
echo ""
echo "Option 2: Use BFG Repo Cleaner (recommended):"
echo "  brew install bfg"
echo "  bfg --replace-text passwords.txt"
echo "  git push --force"
echo ""
echo "Option 3: Start fresh (if early in project):"
echo "  - Archive current repo"
echo "  - Create new repo without history"
echo "  - Copy clean files to new repo"
echo ""

echo "6️⃣ Next Steps:"
echo "  1. Revoke the exposed tokens immediately:"
echo "     - GitHub: https://github.com/settings/tokens"
echo "     - Google Cloud: https://console.cloud.google.com/apis/credentials"
echo "  2. Generate new tokens"
echo "  3. Store them securely in GitHub Secrets:"
echo "     gh secret set GITHUB_TOKEN"
echo "     gh secret set GOOGLE_API_KEY"
echo "  4. Enable secret scanning push protection:"
echo "     https://github.com/Plasma-Engine/plasma-engine-org/settings/security_analysis"
echo ""
echo "✅ Script complete! Remember to revoke and regenerate all exposed tokens!"