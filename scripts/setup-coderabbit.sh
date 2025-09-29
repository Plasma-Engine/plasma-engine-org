#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Usage function
usage() {
  cat << EOF
Usage: $0 [OPTIONS]

Configure CodeRabbit for all Plasma Engine repositories.

OPTIONS:
  -d, --dir DIR     Base directory containing repositories
                    (default: current directory's parent, or CODEBASE_DIR env var)
  -h, --help        Show this help message

ENVIRONMENT:
  CODEBASE_DIR      Base directory for repositories (overridden by -d flag)

EXAMPLES:
  # Use current directory's parent
  $0

  # Use specific directory
  $0 -d /path/to/repositories

  # Use environment variable
  export CODEBASE_DIR=/path/to/repositories
  $0

EOF
  exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -d|--dir)
      BASE_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Set BASE_DIR with precedence: CLI arg > env var > default (parent directory)
if [[ -z "${BASE_DIR:-}" ]]; then
  if [[ -n "${CODEBASE_DIR:-}" ]]; then
    BASE_DIR="$CODEBASE_DIR"
  else
    # Default to parent directory of current repo
    BASE_DIR="$(dirname "$(pwd)")"
  fi
fi

# Ensure BASE_DIR is absolute
BASE_DIR="$(cd "$BASE_DIR" && pwd)" || {
  echo -e "${YELLOW}⚠${NC} Invalid base directory: $BASE_DIR"
  exit 1
}

echo -e "${BLUE}Using base directory: ${BASE_DIR}${NC}"

GITHUB_ORG="Plasma-Engine"
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
