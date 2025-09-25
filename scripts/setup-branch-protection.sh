#!/bin/bash
set -euo pipefail

# Enforces opinionated branch protection on main branches for all repos.
# Requires: gh auth login (scopes: repo, admin:org for org repos).

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

GITHUB_ORG="${GITHUB_ORG:-Plasma-Engine}"
DEFAULT_REPOS=(
  plasma-engine-gateway
  plasma-engine-research
  plasma-engine-brand
  plasma-engine-content
  plasma-engine-agent
  plasma-engine-shared
  plasma-engine-infra
  plasma-engine-org
)

if [[ $# -gt 0 ]]; then
  REPOS=("$@")
else
  REPOS=("${DEFAULT_REPOS[@]}")
fi

read -r -d '' PAYLOAD <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "block_creations": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "allow_fork_syncing": true,
  "required_linear_history": true,
  "required_conversation_resolution": true
}
JSON

TMP_FILE="$(mktemp)"
trap 'rm -f "${TMP_FILE}"' EXIT
printf '%s' "${PAYLOAD}" > "${TMP_FILE}"

echo -e "${BLUE}Applying branch protection to main branches${NC}"

for repo in "${REPOS[@]}"; do
  echo -e "\n${YELLOW}Repository: ${repo}${NC}"
  if gh api "repos/${GITHUB_ORG}/${repo}/branches/main/protection" \
       --method PUT \
       -H "Accept: application/vnd.github+json" \
       --input "${TMP_FILE}" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Protection updated"
  else
    echo -e "  ${YELLOW}⚠${NC} Failed to update protection"
  fi
done

echo -e "\n${GREEN}Branch protection applied.${NC}"
