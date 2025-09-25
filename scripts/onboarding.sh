#!/usr/bin/env bash
# Purpose: Developer onboarding helper for Plasma Engine
# Explainer: This script checks for required tools, sets up Git auth, and prints next steps.
# References: docs/devops/README.md, docs/devops/playbooks/ci-cd.md

set -euo pipefail

echo "[onboarding] Checking required tools..."
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1"; exit 1; }; }
need git
need gh || true
need terraform || true

echo "[onboarding] Suggested next steps:"
echo "- Configure credentials for your cloud provider (# TODO)"
echo "- Copy config/rube/mcp-config.template.json and set environment tokens"
echo "- Run scripts/dev-validate.sh to verify tooling"

