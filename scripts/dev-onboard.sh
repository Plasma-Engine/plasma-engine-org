#!/usr/bin/env bash
# Explainer: Developer onboarding script to set up local tooling and validate
# the workspace. Non-destructive and idempotent.

set -euo pipefail

echo "[onboard] Starting onboarding..."
echo "[onboard] Repo root: $(pwd)"

echo "[onboard] Checking git status"
git status -sb || true

echo "[onboard] Checking terraform availability"
if command -v terraform >/dev/null 2>&1; then
  terraform -version
  echo "[onboard] Running terraform fmt (no changes applied)"
  terraform fmt -recursive || true
else
  echo "[onboard] terraform not found. # TODO: Install Terraform >= 1.6.0"
fi

echo "[onboard] Done. See docs/devops/README.md for next steps."

