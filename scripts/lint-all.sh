#!/usr/bin/env bash
# Explainer: Runs linters/formatters across the repository and appends outputs to the DevOps activity log.
# Inputs: none
# Outputs: Appends command outputs to docs/devops/activity-log.md under a dated section.
# Downstream: Acts as a quick gate locally; CI uses reusable workflows in ci/github/workflows.
set -euo pipefail

LOG_FILE="/workspace/docs/devops/activity-log.md"
DATE=$(date +%F)

append_log() {
  echo -e "$1" >> "$LOG_FILE"
}

append_log "\n## ${DATE} (lint/format run)\n"

# Python: ruff + black
if command -v ruff >/dev/null 2>&1; then
  echo "[lint-all] ruff check ." | tee /dev/stderr
  OUTPUT=$(ruff check . 2>&1 || true)
  append_log "#### ruff check\n\n\`\`\`\n${OUTPUT}\n\`\`\`\n"
else
  append_log "- ruff: not installed"
fi

if command -v black >/dev/null 2>&1; then
  echo "[lint-all] black --check ." | tee /dev/stderr
  OUTPUT=$(black --check . 2>&1 || true)
  append_log "#### black --check\n\n\`\`\`\n${OUTPUT}\n\`\`\`\n"
else
  append_log "- black: not installed"
fi

# Node: eslint + prettier (if package.json exists)
if [ -f package.json ] || [ -d plasma-engine-gateway ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "[lint-all] eslint ." | tee /dev/stderr
    OUTPUT=$(npx -y eslint@9 . 2>&1 || true)
    append_log "#### eslint\n\n\`\`\`\n${OUTPUT}\n\`\`\`\n"

    echo "[lint-all] prettier -c ." | tee /dev/stderr
    OUTPUT=$(npx -y prettier@3 -c . 2>&1 || true)
    append_log "#### prettier --check\n\n\`\`\`\n${OUTPUT}\n\`\`\`\n"
  else
    append_log "- Node tooling: npm not installed"
  fi
else
  append_log "- Node: no package.json found at repo root"
fi

append_log "\n### Summary\n- Ran available linters/formatters. Missing tools are noted above.\n"

echo "[lint-all] Outputs appended to ${LOG_FILE}"