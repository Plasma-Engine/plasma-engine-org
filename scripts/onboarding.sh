 #!/usr/bin/env bash
 #
 # Script: onboarding.sh
 # Purpose: Developer onboarding helper to set up local environment quickly.
 # Notes: Non-destructive; idempotent where possible.
 # TODO: Validate against org setup via Rube MCP.

 set -euo pipefail

 echo "[onboarding] verifying toolchain versions"
 command -v python3 && python3 --version || echo "python3 not found"
 command -v node && node --version || echo "node not found"
 command -v npm && npm --version || echo "npm not found"
 command -v terraform && terraform version || echo "terraform not found"

 echo "[onboarding] installing optional Python tools (ruff, black, pytest)"
 python3 -m pip install --user --upgrade pip >/dev/null 2>&1 || true
 python3 -m pip install --user ruff black pytest >/dev/null 2>&1 || true

 echo "[onboarding] done"


