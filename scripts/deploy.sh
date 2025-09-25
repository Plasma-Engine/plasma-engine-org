#!/usr/bin/env bash
# Purpose: Orchestrate Terraform plan/apply for dev environment
# Behavior: Non-interactive apply with clear TODOs for credentials and backends
# References: plasma-engine-infra/infra/terraform/envs/dev
set -euo pipefail

TF_DIR="plasma-engine-infra/infra/terraform/envs/dev"

if ! command -v terraform >/dev/null; then
  echo "terraform not installed. # TODO: Install Terraform or run in CI runner"
  exit 0
fi

pushd "$TF_DIR" >/dev/null

echo "[deploy] terraform init"
terraform init -input=false -no-color || true

echo "[deploy] terraform fmt (check)"
terraform fmt -recursive -check -no-color || true

echo "[deploy] terraform validate"
terraform validate -no-color || true

echo "[deploy] terraform plan"
terraform plan -input=false -no-color -out=tfplan || true

echo "[deploy] terraform apply (auto-approve)"
terraform apply -input=false -no-color -auto-approve tfplan || true

popd >/dev/null