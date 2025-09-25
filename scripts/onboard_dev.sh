#!/usr/bin/env bash
# Explainer: Developer onboarding helper. Verifies core tooling and suggests install commands.
# Usage: ./scripts/onboard_dev.sh

set -euo pipefail

echo "Checking core tooling..."
command -v python3 >/dev/null || echo "# TODO: Install Python 3.11+"
command -v pip >/dev/null || echo "# TODO: Install pip"
command -v node >/dev/null || echo "# TODO: Install Node 20+"
command -v npm >/dev/null || echo "# TODO: Install npm"
command -v terraform >/dev/null || echo "# TODO: Install Terraform >=1.6"
command -v ruff >/dev/null || echo "# TODO: pipx install ruff"
command -v black >/dev/null || echo "# TODO: pipx install black"
command -v pytest >/dev/null || echo "# TODO: pipx install pytest"
command -v eslint >/dev/null || echo "# TODO: npm i -g eslint"
command -v tflint >/dev/null || echo "# TODO: Install tflint"
command -v pre-commit >/dev/null || echo "# TODO: pipx install pre-commit"

echo "Onboarding check complete. See docs/devops/README.md for standards."

