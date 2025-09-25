#!/usr/bin/env bash
#
# Explainer: Run linters across languages in this monorepo.
# - Python: ruff (lint)
# - Python: black (format check)
# - JS/TS: eslint
#
# Behavior: Non-fatal by default to enable partial adoption; emits summaries.
# TODO(devx@plasma): Tighten to fail-on-error once baseline is clean.

set -euo pipefail
IFS=$'\n\t'

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[lint-all] Root: $ROOT_DIR"

PY_STATUS=0
JS_STATUS=0

echo "[lint-all] Python: ruff"
if command -v ruff >/dev/null 2>&1; then
  ruff check . || PY_STATUS=$?
else
  echo "[lint-all] WARN: ruff not installed"
  PY_STATUS=2
fi

echo "[lint-all] Python: black --check"
if command -v black >/dev/null 2>&1; then
  black --check . || PY_STATUS=${PY_STATUS:-0}
else
  echo "[lint-all] WARN: black not installed"
  PY_STATUS=2
fi

echo "[lint-all] JS/TS: eslint"
if command -v eslint >/dev/null 2>&1; then
  eslint . || JS_STATUS=$?
else
  if [ -f package.json ]; then
    npx --yes eslint . || JS_STATUS=$?
  else
    echo "[lint-all] WARN: eslint not installed"
    JS_STATUS=2
  fi
fi

echo "[lint-all] Summary: PY_STATUS=$PY_STATUS JS_STATUS=$JS_STATUS"
exit 0

