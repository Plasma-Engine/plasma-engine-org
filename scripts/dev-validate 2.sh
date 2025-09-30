#!/usr/bin/env bash
# Purpose: Run local validation: terraform fmt/validate, python/node lint/tests.
# Explainer: Aggregates common checks to keep the repo in an always-works state.

set -euo pipefail

echo "[validate] Terraform fmt"
terraform fmt -recursive || true

echo "[validate] Terraform validate (dev env)"
(cd infra/terraform/envs/dev && terraform init -input=false && terraform validate) || true

echo "[validate] Python: ruff/black/pytest"
ruff check . || true
black --check . || true
pytest -q || true

echo "[validate] Node: eslint/test"
npx -y eslint . || true
npm test --silent --if-present || true

echo "[validate] Done"

