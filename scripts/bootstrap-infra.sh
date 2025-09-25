#!/usr/bin/env bash
#
# Explainer: Bootstrap Terraform working directory for local validation.
# This script intentionally disables backend to avoid accidental remote state writes.
#
# Usage:
#   scripts/bootstrap-infra.sh [path]
#
# TODO(infra@plasma): Add backend wiring and auth bootstrap once decided.

set -euo pipefail
IFS=$'\n\t'

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="${1:-$ROOT_DIR/infra/terraform}"

echo "[bootstrap-infra] Terraform dir: $TF_DIR"

if ! command -v terraform >/dev/null 2>&1; then
  echo "[bootstrap-infra] ERROR: terraform CLI not found" >&2
  exit 1
fi

pushd "$TF_DIR" >/dev/null
terraform fmt -diff || true
terraform init -backend=false
terraform validate || true
popd >/dev/null

echo "[bootstrap-infra] Complete"

