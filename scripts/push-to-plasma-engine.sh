#!/bin/bash

# Script to push all repositories to Plasma-Engine organization using GitHub CLI

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
GITHUB_ORG="Plasma-Engine"
BASE_DIR="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Pushing repositories to Plasma-Engine organization${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# List of repositories
REPOS=(
    "plasma-engine-gateway:API Gateway and GraphQL Federation"
    "plasma-engine-research:GraphRAG Knowledge Management System"
    "plasma-engine-brand:Brand Monitoring and Analytics Platform"
    "plasma-engine-content:AI Content Generation and Publishing"
    "plasma-engine-agent:Agent Orchestration and Automation"
    "plasma-engine-shared:Shared Libraries and Templates"
    "plasma-engine-infra:Infrastructure as Code and CI/CD"
)

# Function to create or verify repository exists
ensure_repo_exists() {
    local repo_name=$1
    local description=$2
    
    echo -e "\n${YELLOW}Checking ${repo_name}...${NC}"
    
    # Check if repo exists in organization
    if gh repo view "${GITHUB_ORG}/${repo_name}" --json name >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Repository ${repo_name} exists${NC}"
    else
        echo "Creating ${repo_name}..."
        if gh repo create "${GITHUB_ORG}/${repo_name}" \
            --private \
            --description "${description}" \
            --enable-issues \
            --enable-wiki=false \
            2>/dev/null; then
            echo -e "${GREEN}✓ Created ${repo_name}${NC}"
        else
            echo -e "${YELLOW}Repository might already exist or there was an error${NC}"
        fi
    fi
}

# Function to push repository
push_repo() {
    local repo_name=$1
    local repo_dir="${BASE_DIR}/${repo_name}"
    
    echo -e "${YELLOW}Pushing ${repo_name}...${NC}"
    
    if [ ! -d "$repo_dir" ]; then
        echo -e "${RED}Directory ${repo_dir} does not exist, skipping...${NC}"
        return 1
    fi
    
    cd "$repo_dir"
    
    # Update remote to organization
    echo "Setting remote..."
    git remote set-url origin "https://github.com/${GITHUB_ORG}/${repo_name}.git" 2>/dev/null || \
        git remote add origin "https://github.com/${GITHUB_ORG}/${repo_name}.git"
    
    # Configure git to use gh auth
    gh auth setup-git >/dev/null 2>&1
    
    # Try to push
    echo "Pushing to GitHub..."
    if git push -u origin main 2>&1 | tee /tmp/push_output.txt | grep -q "Everything up-to-date\|new branch\|set up to track"; then
        echo -e "${GREEN}✓ Successfully pushed ${repo_name}${NC}"
    elif grep -q "rejected" /tmp/push_output.txt; then
        echo "Attempting to pull and merge..."
        git pull origin main --allow-unrelated-histories --no-edit 2>/dev/null || true
        if git push -u origin main 2>/dev/null; then
            echo -e "${GREEN}✓ Pushed after merge ${repo_name}${NC}"
        else
            echo -e "${YELLOW}Force pushing ${repo_name}...${NC}"
            git push -u origin main --force && echo -e "${GREEN}✓ Force pushed ${repo_name}${NC}"
        fi
    else
        echo -e "${YELLOW}Force pushing ${repo_name}...${NC}"
        git push -u origin main --force && echo -e "${GREEN}✓ Force pushed ${repo_name}${NC}"
    fi
    
    cd "$BASE_DIR"
}

# Process each repository
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    ensure_repo_exists "$repo_name" "$description"
    push_repo "$repo_name"
done

# Set up organization repository
echo -e "\n${YELLOW}Setting up organization overview repository...${NC}"
cd "$BASE_DIR"

if gh repo view "${GITHUB_ORG}/plasma-engine-org" --json name >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Organization repo exists${NC}"
else
    echo "Creating organization overview repository..."
    gh repo create "${GITHUB_ORG}/plasma-engine-org" \
        --private \
        --description "Plasma Engine Organization Overview and Documentation" \
        --enable-issues \
        --enable-wiki=false
fi

# Push org repo
git remote set-url origin "https://github.com/${GITHUB_ORG}/plasma-engine-org.git" 2>/dev/null || \
    git remote add origin "https://github.com/${GITHUB_ORG}/plasma-engine-org.git"
git push -u origin main --force 2>/dev/null && echo -e "${GREEN}✓ Pushed organization repo${NC}"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}All repositories pushed to Plasma-Engine organization!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Show repository URLs
echo -e "\n${BLUE}Your repositories are now available at:${NC}"
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    echo "  https://github.com/${GITHUB_ORG}/${repo_name}"
done
echo "  https://github.com/${GITHUB_ORG}/plasma-engine-org"

# Show repository stats
echo -e "\n${YELLOW}Repository Statistics:${NC}"
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    if [ -d "${BASE_DIR}/${repo_name}" ]; then
        cd "${BASE_DIR}/${repo_name}"
        file_count=$(git ls-files 2>/dev/null | wc -l | tr -d ' ')
        commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
        echo "  ${repo_name}: ${file_count} files, ${commit_count} commits"
    fi
done

cd "$BASE_DIR"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Visit https://github.com/orgs/${GITHUB_ORG}/repositories to manage repos"
echo "2. Configure branch protection rules"
echo "3. Set up GitHub Actions secrets"
echo "4. Enable CodeRabbit for PR reviews"
echo "5. Configure team access and permissions"

echo -e "\n${BLUE}Quick commands:${NC}"
echo "  Clone all: gh repo list ${GITHUB_ORG} --limit 100 | awk '{print \$1}' | xargs -I {} gh repo clone {}"
echo "  View org: gh browse --repo ${GITHUB_ORG}/plasma-engine-org"
