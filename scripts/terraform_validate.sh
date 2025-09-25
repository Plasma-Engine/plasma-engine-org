#!/usr/bin/env bash
# Explainer: Validate Terraform (fmt, init, validate) for a given directory.
# Usage: ./scripts/terraform_validate.sh [path]

set -euo pipefail
ROOT=${1:-.}

pushd "$ROOT" >/dev/null
terraform fmt -recursive
terraform init -input=false
terraform validate
popd >/dev/null

