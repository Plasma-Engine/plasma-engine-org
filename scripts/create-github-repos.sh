#!/bin/bash

# Script to create Plasma Engine repositories on GitHub

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# GitHub settings
GITHUB_USER="xkonjin"
GITHUB_TOKEN="${GITHUB_TOKEN}"
VISIBILITY="private"  # Change to "public" if needed

echo -e "${GREEN}Creating Plasma Engine repositories on GitHub...${NC}"

# List of repositories to create
REPOS=(
    "plasma-engine-gateway:API Gateway and GraphQL Federation"
    "plasma-engine-research:GraphRAG Knowledge Management System"
    "plasma-engine-brand:Brand Monitoring and Analytics Platform"
    "plasma-engine-content:AI Content Generation and Publishing"
    "plasma-engine-agent:Agent Orchestration and Automation"
    "plasma-engine-shared:Shared Libraries and Templates"
    "plasma-engine-infra:Infrastructure as Code and CI/CD"
)

# Function to create a repository
create_repo() {
    local repo_name=$1
    local description=$2
    
    echo -e "\n${YELLOW}Creating ${repo_name}...${NC}"
    
    # Check if repo exists
    if curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/repos/${GITHUB_USER}/${repo_name}" | grep -q "\"name\":"; then
        echo -e "${YELLOW}Repository ${repo_name} already exists, skipping...${NC}"
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
            \"private\": $([ "$VISIBILITY" = "private" ] && echo "true" || echo "false"),
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
        echo "$response"
        return 1
    fi
}

# Create each repository
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    create_repo "$repo_name" "$description"
done

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Repository creation complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Show repository URLs
echo -e "\n${YELLOW}Your repositories:${NC}"
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    echo "  https://github.com/${GITHUB_USER}/${repo_name}"
done
