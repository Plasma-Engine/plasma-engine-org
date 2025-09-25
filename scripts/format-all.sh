#!/usr/bin/env bash
#
# Explainer: Apply formatters across the repo.
# - Python: black
# - (Optional) JS/TS: prettier if configured in the future
#
# Behavior: Best-effort; prints next-steps if tools are missing.

set -euo pipefail
IFS=$'\n\t'

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[format-all] Root: $ROOT_DIR"

if command -v black >/dev/null 2>&1; then
  black .
else
  echo "[format-all] WARN: black not installed"
fi

# TODO(devx@plasma): Add prettier once JS/TS projects are standardized.
echo "[format-all] Done"

