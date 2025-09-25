#!/usr/bin/env bash
# Explainer: Run Node CI steps locally (npm ci, eslint, tests).
# Usage: ./scripts/run_node_ci_local.sh [path] [test-script]

set -euo pipefail
ROOT=${1:-.}
TEST=${2:-test}

pushd "$ROOT" >/dev/null
if [ -f package.json ]; then
  npm ci
  npm run lint --if-present || echo "eslint not configured"
  npm run "$TEST" --if-present
else
  echo "No package.json in $ROOT"
fi
popd >/dev/null

