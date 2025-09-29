#!/usr/bin/env bash
# Purpose: Run local linting and tests across all repos
# Behavior: Delegates to Makefile targets; best-effort and non-interactive
# TODO: Add coverage thresholds and SARIF export when tools are installed
set -euo pipefail

command -v make >/dev/null || { echo "make is required"; exit 1; }

echo "[test] Running linters"
make lint-all || true

echo "[test] Running tests"
make test-all || true

echo "[test] Done"