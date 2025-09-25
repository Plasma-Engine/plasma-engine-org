#!/bin/bash

# Plasma Engine GitHub Authentication Setup
# This script configures GitHub access for various development tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# GitHub Token (should be kept secure)
GITHUB_TOKEN="${GITHUB_TOKEN:?Set GITHUB_TOKEN env var before running this script}"
GITHUB_USER="${GITHUB_USER:-plasma-engine-bot}"
GITHUB_ORG="Plasma-Engine"

echo -e "${GREEN}Setting up GitHub authentication for Plasma Engine...${NC}"

# 1. Configure Git with token
echo -e "\n${YELLOW}Configuring Git...${NC}"
git config --global user.name "${GITHUB_USER}"
git config --global user.email "${GITHUB_USER}@users.noreply.github.com"

# Set up credential helper for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    git config --global credential.helper osxkeychain
    echo -e "${GREEN}✓ Git configured with macOS keychain${NC}"
else
    git config --global credential.helper store
    echo -e "${GREEN}✓ Git configured with credential store${NC}"
fi

# 2. Create .netrc for HTTPS authentication
echo -e "\n${YELLOW}Setting up .netrc for HTTPS authentication...${NC}"
cat > ~/.netrc << EOF
machine github.com
login ${GITHUB_USER}
password ${GITHUB_TOKEN}

machine api.github.com
login ${GITHUB_USER}
password ${GITHUB_TOKEN}
EOF
chmod 600 ~/.netrc
echo -e "${GREEN}✓ .netrc configured${NC}"

# 3. Set up GitHub CLI (if installed)
if command -v gh &> /dev/null; then
    echo -e "\n${YELLOW}Configuring GitHub CLI...${NC}"
    echo "${GITHUB_TOKEN}" | gh auth login --with-token
    gh auth status
    echo -e "${GREEN}✓ GitHub CLI configured${NC}"
else
    echo -e "\n${YELLOW}GitHub CLI not installed. Install with: brew install gh${NC}"
fi

# 4. Export environment variables for current session
echo -e "\n${YELLOW}Setting environment variables...${NC}"
export GITHUB_TOKEN="${GITHUB_TOKEN}"
export GITHUB_USER="${GITHUB_USER}"
export GITHUB_ORG="${GITHUB_ORG}"
export GH_TOKEN="${GITHUB_TOKEN}"

# 5. Create local config file
echo -e "\n${YELLOW}Creating local configuration...${NC}"
cat > .github-config << EOF
# GitHub Configuration for Plasma Engine
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_USER=${GITHUB_USER}
GITHUB_ORG=${GITHUB_ORG}
EOF
chmod 600 .github-config
echo -e "${GREEN}✓ Local config created${NC}"

# 6. Test GitHub access
echo -e "\n${YELLOW}Testing GitHub access...${NC}"
if curl -s -H "Authorization: token ${GITHUB_TOKEN}" https://api.github.com/user | grep -q "\"login\":"; then
    echo -e "${GREEN}✓ GitHub API access verified${NC}"
    echo -e "${GREEN}✓ Authenticated as: ${GITHUB_USER}${NC}"
else
    echo -e "${RED}✗ Failed to authenticate with GitHub${NC}"
    exit 1
fi

# 7. Set up git aliases for easier management
echo -e "\n${YELLOW}Setting up helpful git aliases...${NC}"
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.pl "pull --rebase"
git config --global alias.ps push
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

echo -e "${GREEN}✓ Git aliases configured${NC}"

# 8. Instructions for other tools
echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}GitHub Authentication Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}For Cursor IDE:${NC}"
echo "1. Open Cursor Settings (Cmd+,)"
echo "2. Search for 'GitHub'"
echo "3. Add token to GitHub: Personal Access Token field"
echo "   Token: <REDACTED – use GITHUB_TOKEN environment variable>"

echo -e "\n${YELLOW}For VS Code:${NC}"
echo "1. Install GitHub Pull Requests extension"
echo "2. Sign in with the token when prompted"
echo "3. Or use Command Palette: >GitHub: Set Personal Access Token"

echo -e "\n${YELLOW}For Warp Terminal:${NC}"
echo "1. Warp will automatically use the git credentials configured"
echo "2. The .netrc file enables HTTPS authentication"

echo -e "\n${YELLOW}Environment variables set for this session:${NC}"
echo "  GITHUB_TOKEN, GITHUB_USER, GITHUB_ORG, GH_TOKEN"

echo -e "\n${YELLOW}To make environment variables permanent, add to ~/.zshrc:${NC}"
echo "  export GITHUB_TOKEN='<YOUR_GITHUB_PAT>'"
echo "  export GITHUB_USER='${GITHUB_USER}'"
echo "  export GITHUB_ORG='${GITHUB_ORG}'"

echo -e "\n${GREEN}You can now clone private repos with:${NC}"
echo "  git clone https://github.com/${GITHUB_ORG}/plasma-engine-gateway.git"

echo -e "\n${YELLOW}Security Note:${NC}"
echo "  - Token stored in: ~/.netrc (permissions: 600)"
echo "  - Local config in: .github-config (permissions: 600)"
echo "  - Keep these files secure and don't commit them!"
