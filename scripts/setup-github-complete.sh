#!/bin/bash
set -euo pipefail

# One-shot orchestrator to align Plasma Engine GitHub artefacts.
# It chains the modular scripts in this directory and tightens org defaults.
# Requirements: gh auth login (scopes: repo, workflow, admin:org).

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_ORG="${GITHUB_ORG:-Plasma-Engine}"

run_step() {
  local description="$1"
  shift
  echo -e "\n${BLUE}${description}${NC}"
  "$@"
}

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Plasma Engine – GitHub bootstrap${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

run_step "Step 1 ▸ Synchronizing label taxonomy" \
  "${SCRIPT_DIR}/setup-labels.sh"

run_step "Step 2 ▸ Seeding Phase 1 backlog" \
  "${SCRIPT_DIR}/create-phase1-issues.sh"

run_step "Step 3 ▸ Enforcing branch protection" \
  "${SCRIPT_DIR}/setup-branch-protection.sh"

run_step "Step 4 ▸ Verifying CodeRabbit configuration" \
  "${SCRIPT_DIR}/setup-coderabbit.sh"

run_step "Step 5 ▸ Ensuring organization project exists" \
  bash -c 'gh project list --owner "'"${GITHUB_ORG}"'" --limit 100 | grep -q "Plasma Engine – Automation Streams" || gh project create --owner "'"${GITHUB_ORG}"'" --title "Plasma Engine – Automation Streams" --description "Program roadmap and sprint tracker"'

run_step "Step 6 ▸ Hardening organization defaults" \
  bash -c 'gh api orgs/"'"${GITHUB_ORG}"'" --method PATCH --input - <<JSON
{
  "default_repository_permission": "read",
  "members_allowed_repository_creation_type": "none",
  "members_can_create_public_repositories": false,
  "members_can_create_private_repositories": false,
  "has_organization_projects": true,
  "has_repository_projects": true,
  "members_can_delete_repositories": false,
  "members_can_invite_outside_collaborators": true,
  "members_can_fork_private_repositories": false
}
JSON'

echo -e "\n${GREEN}✅ GitHub bootstrap finished.${NC}"
echo -e "${YELLOW}Next:\n  - Configure Actions secrets per service\n  - Install the CodeRabbit GitHub App (if not already installed)\n  - Link new issues to the Automation Streams project board${NC}"
