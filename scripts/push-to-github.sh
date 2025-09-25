#!/bin/bash

# Script to initialize and push Plasma Engine repositories to GitHub

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# GitHub organization
GITHUB_ORG="Plasma-Engine"
BASE_DIR="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"

echo -e "${GREEN}Pushing Plasma Engine repositories to GitHub...${NC}"

# List of repositories
REPOS=(
    "plasma-engine-gateway"
    "plasma-engine-research"
    "plasma-engine-brand"
    "plasma-engine-content"
    "plasma-engine-agent"
    "plasma-engine-shared"
    "plasma-engine-infra"
)

# Function to initialize and push repository
push_repo() {
    local repo_name=$1
    local repo_dir="${BASE_DIR}/${repo_name}"
    
    echo -e "\n${YELLOW}Processing ${repo_name}...${NC}"
    
    if [ ! -d "$repo_dir" ]; then
        echo -e "${RED}Directory ${repo_dir} does not exist, skipping...${NC}"
        return 1
    fi
    
    cd "$repo_dir"
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        echo "Initializing git repository..."
        git init
        git branch -M main
    fi
    
    # Add remote if not exists
    if ! git remote | grep -q "origin"; then
        echo "Adding remote origin..."
        git remote add origin "https://github.com/${GITHUB_ORG}/${repo_name}.git"
    else
        echo "Remote origin already exists"
        # Update the remote URL in case it changed
        git remote set-url origin "https://github.com/${GITHUB_ORG}/${repo_name}.git"
    fi
    
    # Create .gitignore if not exists
    if [ ! -f ".gitignore" ]; then
        echo "Creating .gitignore..."
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Testing
coverage/
.coverage
.pytest_cache/
.nyc_output/

# Docker
*.pid
EOF
    fi
    
    # Add all files
    echo "Staging files..."
    git add -A
    
    # Commit if there are changes
    if ! git diff --staged --quiet; then
        echo "Committing changes..."
        git commit -m "Initial commit: ${repo_name} setup with organization structure"
    else
        echo "No changes to commit"
    fi
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    if git push -u origin main 2>/dev/null; then
        echo -e "${GREEN}✓ Successfully pushed ${repo_name}${NC}"
    else
        echo -e "${YELLOW}Attempting force push for ${repo_name}...${NC}"
        if git push -u origin main --force; then
            echo -e "${GREEN}✓ Force pushed ${repo_name}${NC}"
        else
            echo -e "${RED}✗ Failed to push ${repo_name}${NC}"
        fi
    fi
    
    cd "$BASE_DIR"
}

# Push each repository
for repo in "${REPOS[@]}"; do
    push_repo "$repo"
done

# Also push the main organization repository if needed
echo -e "\n${YELLOW}Creating organization overview repository...${NC}"
cd "$BASE_DIR"

# Initialize the main org repo
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# Create comprehensive .gitignore for org root
cat > .gitignore << 'EOF'
# Service repositories (managed separately)
plasma-engine-*/

# Environment
.env
.env.*
.github-token
.github-config

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp
EOF

# Add organization files
git add -A
git commit -m "feat: Plasma Engine organization structure and documentation" || true

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Repository push complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Show repository URLs
echo -e "\n${YELLOW}Your repositories are available at:${NC}"
for repo in "${REPOS[@]}"; do
    echo "  https://github.com/${GITHUB_ORG}/${repo}"
done

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Visit https://github.com/${GITHUB_ORG} to view your organization"
echo "2. Configure branch protection rules for main branches"
echo "3. Set up team access and permissions"
echo "4. Enable GitHub Actions for CI/CD"
echo "5. Configure CodeRabbit for automated reviews"
