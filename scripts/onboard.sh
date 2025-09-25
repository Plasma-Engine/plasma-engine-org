#!/usr/bin/env bash
# Purpose: Developer onboarding automation for Plasma Engine repos
# Behavior: Checks prerequisites, clones repos, and prints next steps.
# Notes: Non-interactive; safe to re-run. Uses Makefile targets when available.
# TODO: Extend to install language toolchains via asdf/pyenv/nvm as per org policy.
set -euo pipefail

command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v make >/dev/null || { echo "make is required"; exit 1; }

echo "[onboard] Cloning all repositories (idempotent)"
make clone-all || true

echo "[onboard] Pulling latest changes"
make pull-all || true

echo "[onboard] Showing status"
make status-all || true

echo "[onboard] Next steps:"
echo " - make setup (starts infra and installs deps)"
echo " - make run-all (runs services in tmux)"
echo " - Review docs/devops/ and runbooks"