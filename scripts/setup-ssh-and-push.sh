#!/bin/bash

# Script to set up SSH and push to Plasma-Engine organization

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
echo -e "${BLUE}Setting up SSH and pushing to Plasma-Engine organization${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Check if SSH key exists
SSH_KEY="$HOME/.ssh/id_ed25519"
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${YELLOW}No SSH key found. Creating one...${NC}"
    ssh-keygen -t ed25519 -C "platform-eng@plasma.engine" -f "$SSH_KEY" -N ""
    echo -e "${GREEN}✓ SSH key created${NC}"
fi

# Add SSH key to ssh-agent
echo -e "${YELLOW}Adding SSH key to ssh-agent...${NC}"
eval "$(ssh-agent -s)" > /dev/null 2>&1
ssh-add "$SSH_KEY" 2>/dev/null || ssh-add -K "$SSH_KEY" 2>/dev/null || true

# Display public key
echo -e "\n${YELLOW}Your SSH public key:${NC}"
cat "$SSH_KEY.pub"

echo -e "\n${RED}IMPORTANT: Add this SSH key to your GitHub account:${NC}"
echo "1. Go to https://github.com/settings/keys"
echo "2. Click 'New SSH key'"
echo "3. Paste the key above"
echo -e "4. Press Enter when done...\n"
read -r

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection to GitHub...${NC}"
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo -e "${GREEN}✓ SSH authentication successful${NC}"
else
    echo -e "${YELLOW}SSH test output:${NC}"
    ssh -T git@github.com 2>&1 || true
fi

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

# Function to update remote and push
update_and_push() {
    local repo_name=$1
    local repo_dir="${BASE_DIR}/${repo_name}"
    
    echo -e "\n${YELLOW}Processing ${repo_name}...${NC}"
    
    if [ ! -d "$repo_dir" ]; then
        echo -e "${RED}Directory ${repo_dir} does not exist, skipping...${NC}"
        return 1
    fi
    
    cd "$repo_dir"
    
    # Update remote to use SSH
    echo "Updating remote to SSH..."
    git remote set-url origin "git@github.com:${GITHUB_ORG}/${repo_name}.git"
    
    # Try to push
    echo "Attempting to push..."
    if git push -u origin main 2>/dev/null; then
        echo -e "${GREEN}✓ Successfully pushed ${repo_name}${NC}"
    elif git push -u origin main --force 2>/dev/null; then
        echo -e "${GREEN}✓ Force pushed ${repo_name}${NC}"
    else
        echo -e "${RED}✗ Failed to push ${repo_name}${NC}"
        echo "Trying to fetch and merge first..."
        git fetch origin main || true
        git merge origin/main --allow-unrelated-histories -m "Merge remote with local" || true
        if git push -u origin main; then
            echo -e "${GREEN}✓ Pushed after merge ${repo_name}${NC}"
        else
            echo -e "${RED}✗ Still failed to push ${repo_name}${NC}"
        fi
    fi
    
    cd "$BASE_DIR"
}

# Update and push each repository
for repo in "${REPOS[@]}"; do
    update_and_push "$repo"
done

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Process complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Show repository URLs
echo -e "\n${YELLOW}Your repositories:${NC}"
for repo in "${REPOS[@]}"; do
    echo "  https://github.com/${GITHUB_ORG}/${repo}"
done

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Visit https://github.com/${GITHUB_ORG} to view your organization"
echo "2. Configure branch protection rules"
echo "3. Set up CodeRabbit for automated reviews"
echo "4. Enable GitHub Actions for CI/CD"
