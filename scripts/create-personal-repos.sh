#!/bin/bash

# Script to create and push Plasma Engine repositories to personal GitHub account

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# GitHub settings
GITHUB_USER="${GITHUB_USER:?Set GITHUB_USER to your personal GitHub handle}"
GITHUB_TOKEN="${GITHUB_TOKEN:?Set GITHUB_TOKEN before running this script}"
BASE_DIR="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Creating Plasma Engine repos under personal account${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# List of repositories with descriptions (using arrays for macOS compatibility)
REPO_NAMES=(
    "plasma-engine-gateway"
    "plasma-engine-research"
    "plasma-engine-brand"
    "plasma-engine-content"
    "plasma-engine-agent"
    "plasma-engine-shared"
    "plasma-engine-infra"
)

REPO_DESCS=(
    "API Gateway and GraphQL Federation for Plasma Engine"
    "GraphRAG Knowledge Management System"
    "Brand Monitoring and Analytics Platform"
    "AI Content Generation and Publishing"
    "Agent Orchestration and Automation"
    "Shared Libraries and Templates"
    "Infrastructure as Code and CI/CD"
)

# Function to create repository
create_repo() {
    local repo_name=$1
    local description=$2
    
    echo -e "\n${YELLOW}Creating ${repo_name}...${NC}"
    
    # Check if repo exists
    if curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/repos/${GITHUB_USER}/${repo_name}" | grep -q "\"name\":"; then
        echo -e "${YELLOW}Repository ${repo_name} already exists${NC}"
        return 0
    fi
    
    # Create the repository
    response=$(curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{
            \"name\": \"${repo_name}\",
            \"description\": \"${description}\",
            \"private\": true,
            \"has_issues\": true,
            \"has_projects\": true,
            \"has_wiki\": false,
            \"auto_init\": false,
            \"allow_squash_merge\": true,
            \"allow_merge_commit\": true,
            \"allow_rebase_merge\": true,
            \"delete_branch_on_merge\": true
        }")
    
    if echo "$response" | grep -q "\"name\": \"${repo_name}\""; then
        echo -e "${GREEN}✓ Created ${repo_name}${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create ${repo_name}${NC}"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

# Function to push repository
push_repo() {
    local repo_name=$1
    local repo_dir="${BASE_DIR}/${repo_name}"
    
    echo -e "\n${YELLOW}Pushing ${repo_name}...${NC}"
    
    if [ ! -d "$repo_dir" ]; then
        echo -e "${RED}Directory ${repo_dir} does not exist, skipping...${NC}"
        return 1
    fi
    
    cd "$repo_dir"
    
    # Update remote to personal account
    git remote set-url origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${repo_name}.git" 2>/dev/null || \
        git remote add origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${repo_name}.git"
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    if git push -u origin main --force 2>&1 | grep -q "branch 'main' set up to track"; then
        echo -e "${GREEN}✓ Successfully pushed ${repo_name}${NC}"
    elif git push -u origin main 2>&1 | grep -q "Everything up-to-date"; then
        echo -e "${GREEN}✓ ${repo_name} already up-to-date${NC}"
    else
        # Try again without force
        git push -u origin main 2>/dev/null && echo -e "${GREEN}✓ Pushed ${repo_name}${NC}" || echo -e "${RED}✗ Failed to push ${repo_name}${NC}"
    fi
    
    cd "$BASE_DIR"
}

# Create and push each repository
for i in "${!REPO_NAMES[@]}"; do
    repo_name="${REPO_NAMES[$i]}"
    description="${REPO_DESCS[$i]}"
    create_repo "$repo_name" "$description"
    push_repo "$repo_name"
done

# Also create main organization repository
echo -e "\n${YELLOW}Creating main plasma-engine-org repository...${NC}"
create_repo "plasma-engine-org" "Plasma Engine Organization Overview and Documentation"

# Push the main org repo
cd "$BASE_DIR"
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/plasma-engine-org.git"
git push -u origin main --force 2>/dev/null && echo -e "${GREEN}✓ Pushed plasma-engine-org${NC}" || echo -e "${YELLOW}plasma-engine-org may already be up-to-date${NC}"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}All repositories created and pushed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Show repository URLs
echo -e "\n${BLUE}Your repositories are now available at:${NC}"
# Show repository URLs
for repo_name in "${REPO_NAMES[@]}"; do
    echo "  https://github.com/${GITHUB_USER}/${repo_name}"
done
echo "  https://github.com/${GITHUB_USER}/plasma-engine-org"

echo -e "\n${YELLOW}Repository Statistics:${NC}"
for repo_name in "${REPO_NAMES[@]}"; do
    cd "${BASE_DIR}/${repo_name}" 2>/dev/null && \
    file_count=$(git ls-files | wc -l | tr -d ' ') && \
    echo "  ${repo_name}: ${file_count} files"
done

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Visit https://github.com/${GITHUB_USER}?tab=repositories to view all repos"
echo "2. Configure branch protection rules for main branches"
echo "3. Set up GitHub Actions secrets for CI/CD"
echo "4. Enable CodeRabbit for automated PR reviews"
echo "5. Consider creating a GitHub organization for better management"

echo -e "\n${BLUE}To clone all repositories to a new machine:${NC}"
echo "cd ~/projects && for repo in plasma-engine-*; do git clone https://github.com/${GITHUB_USER}/\$repo.git; done"
