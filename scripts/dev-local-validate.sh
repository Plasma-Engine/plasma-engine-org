#!/usr/bin/env bash
# Explainer: Local validation script to run formatters/linters/tests where
# applicable. Safe to run repeatedly.

set -euo pipefail

echo "[validate] terraform fmt"
if command -v terraform >/dev/null 2>&1; then
  terraform fmt -recursive
else
  echo "[validate] terraform not installed. Skipping."
fi

echo "[validate] Done."

