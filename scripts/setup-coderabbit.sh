#!/bin/bash
set -euo pipefail

# Verifies (and optionally provisions) CodeRabbit configuration across repos.
# Usage: ./scripts/setup-coderabbit.sh [--apply]
# --apply will open a working tree commit in each local repo when the config is missing.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITHUB_ORG="${GITHUB_ORG:-Plasma-Engine}"
APPLY=false

if [[ $# -gt 0 ]]; then
  if [[ "$1" == "--apply" ]]; then
    APPLY=true
  else
    echo "Unknown option: $1" >&2
    exit 1
  fi
fi

REPOS=(
  plasma-engine-gateway
  plasma-engine-research
  plasma-engine-brand
  plasma-engine-content
  plasma-engine-agent
  plasma-engine-shared
  plasma-engine-infra
)

CODERABBIT_TEMPLATE="${ROOT_DIR}/.automation/.coderabbit-template.yaml"

if [[ ! -f "${CODERABBIT_TEMPLATE}" ]]; then
  mkdir -p "${ROOT_DIR}/.automation"
  cat <<'TEMPLATE' > "${CODERABBIT_TEMPLATE}"
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
    - Verify logging, telemetry, and error handling paths
    - Require tests or justify gaps in coverage
    - Validate API contracts, schemas, and migrations
    - Flag missing docs or runbooks for operational work

chat:
  auto_reply: true

knowledge_base:
  learnings:
    scope: auto
  issues:
    scope: auto
TEMPLATE
fi

TEMPLATE_CONTENT="$(cat "${CODERABBIT_TEMPLATE}")"

function ensure_local_clone() {
  local repo="$1"
  local repo_dir="${ROOT_DIR}/${repo}"
  if [[ ! -d "${repo_dir}/.git" ]]; then
    echo -e "  ${YELLOW}•${NC} Cloning ${repo} locally"
    gh repo clone "${GITHUB_ORG}/${repo}" "${repo_dir}" -- --depth=1 >/dev/null
  fi
}

echo -e "${BLUE}Validating CodeRabbit configuration${NC}"

for repo in "${REPOS[@]}"; do
  echo -e "\n${YELLOW}Repository: ${repo}${NC}"
  if gh api "repos/${GITHUB_ORG}/${repo}/contents/.coderabbit.yaml" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} .coderabbit.yaml present"
    continue
  fi

  echo -e "  ${YELLOW}⚠${NC} Missing .coderabbit.yaml"
  if [[ "${APPLY}" == true ]]; then
    ensure_local_clone "${repo}"
    repo_dir="${ROOT_DIR}/${repo}"
    cd "${repo_dir}"
    branch="automation/coderabbit-$(date +%Y%m%d%H%M%S)"
    git checkout -b "${branch}" >/dev/null 2>&1 || git checkout "${branch}" >/dev/null 2>&1
    printf '%s\n' "${TEMPLATE_CONTENT}" > .coderabbit.yaml
    git add .coderabbit.yaml
    if git commit -m "chore: add CodeRabbit configuration" >/dev/null 2>&1; then
      echo -e "  ${GREEN}✓${NC} Committed template locally on ${branch}"
      echo -e "  ${YELLOW}•${NC} Run: git push -u origin ${branch} && gh pr create --fill"
    else
      echo -e "  ${YELLOW}⚠${NC} Could not commit (check repository state)"
    fi
    cd "${ROOT_DIR}"
  else
    echo -e "  ${YELLOW}•${NC} Run with --apply to create a template branch"
  fi
done

echo -e "\n${GREEN}CodeRabbit verification complete.${NC}"
