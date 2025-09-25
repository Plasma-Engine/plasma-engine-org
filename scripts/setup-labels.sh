#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GITHUB_ORG="Plasma-Engine"
REPOS=(
  plasma-engine-gateway
  plasma-engine-research
  plasma-engine-brand
  plasma-engine-content
  plasma-engine-agent
  plasma-engine-shared
  plasma-engine-infra
  plasma-engine-org
)

LABELS=(
  "priority:critical|b60205|Issues that need immediate attention"
  "priority:high|d73a4a|High priority issues"
  "priority:medium|fbca04|Medium priority issues"
  "priority:low|0e8a16|Low priority issues"
  "type:bug|d73a4a|Something isn't working"
  "type:feature|a2eeef|New feature or request"
  "type:enhancement|84b6eb|Improvement to existing functionality"
  "type:documentation|0075ca|Documentation updates"
  "type:infrastructure|c5def5|Infrastructure & DevOps"
  "type:security|b60205|Security related issues"
  "status:in-progress|fbca04|Currently being worked on"
  "status:blocked|b60205|Blocked by another issue"
  "status:ready-for-review|7057ff|Ready for review"
  "service:gateway|1d76db|Gateway service"
  "service:research|1d76db|Research service"
  "service:brand|1d76db|Brand service"
  "service:content|1d76db|Content service"
  "service:agent|1d76db|Agent service"
  "service:shared|1d76db|Shared libraries"
  "service:infra|1d76db|Infrastructure"
  "phase:0|c2e0c6|Phase 0 planning"
  "phase:1|c2e0c6|Phase 1 implementation"
  "phase:2|c2e0c6|Phase 2 implementation"
  "ai:llm|ff6b6b|LLM / AI work"
  "ai:graphrag|ff6b6b|GraphRAG work"
)

echo -e "${BLUE}Creating standard labels for Plasma Engine repos${NC}"

for repo in "${REPOS[@]}"; do
  echo -e "\n${YELLOW}Repository: ${repo}${NC}"
  for entry in "${LABELS[@]}"; do
    IFS='|' read -r name color description <<< "$entry"
    if gh label create "$name" --color "$color" --description "$description" -R "${GITHUB_ORG}/${repo}" --force >/dev/null 2>&1; then
      echo -e "  ${GREEN}✓${NC} ${name}"
    else
      echo -e "  ${YELLOW}⚠${NC} Failed to create ${name}"
    fi
  done
done

echo -e "\n${GREEN}Label setup complete.${NC}"
