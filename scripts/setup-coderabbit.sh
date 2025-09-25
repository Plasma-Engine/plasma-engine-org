#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GITHUB_ORG="Plasma-Engine"
BASE_DIR="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"
REPOS=(
  plasma-engine-gateway
  plasma-engine-research
  plasma-engine-brand
  plasma-engine-content
  plasma-engine-agent
  plasma-engine-shared
  plasma-engine-infra
)

CODERABBIT_CONTENT=$(cat <<'YAML'
# CodeRabbit Configuration
# Documentation: https://docs.coderabbit.ai/guides/configure-coderabbit

language: "en-US"
early_access: false

reviews:
  high_level_summary: true
  review_status: true
  collapse_walkthrough: false
  auto_review:
    enabled: true
    drafts: false
  tools:
    ruff:
      enabled: true
    mypy:
      enabled: true
    eslint:
      enabled: true
    prettier:
      enabled: true
  path_filters:
    - "!**/*.md"
    - "!**/*.txt"
    - "!**/package-lock.json"
    - "!**/yarn.lock"
  instructions: |
    - Focus on correctness, security, and performance impacts
    - Require tests or explain why coverage is not needed
    - Verify logging, telemetry, and error handling paths
    - Validate API contracts, schemas, and migrations
    - Flag missing docs or runbooks for operational work

chat:
  auto_reply: true

knowledge_base:
  learnings:
    scope: auto
  issues:
    scope: auto
YAML
)

echo -e "${BLUE}Adding .coderabbit.yaml to repositories${NC}"

for repo in "${REPOS[@]}"; do
  repo_dir="${BASE_DIR}/${repo}"
  echo -e "\n${YELLOW}Repository: ${repo}${NC}"

  if [[ ! -d "${repo_dir}" ]]; then
    echo -e "  ${YELLOW}⚠${NC} Skipping missing repo"
    continue
  fi

  pushd "$repo_dir" >/dev/null
  echo "$CODERABBIT_CONTENT" > .coderabbit.yaml
  git add .coderabbit.yaml

  if git diff --cached --quiet; then
    echo -e "  ${YELLOW}•${NC} No changes to commit"
    popd >/dev/null
    continue
  fi

  git commit -m "chore: add CodeRabbit configuration" >/dev/null
  if git push >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Pushed CodeRabbit config"
  else
    echo -e "  ${YELLOW}⚠${NC} Failed to push"
  fi
  popd >/dev/null
done

echo -e "\n${GREEN}CodeRabbit configuration complete.${NC}"
