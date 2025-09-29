#!/usr/bin/env bash
 #
 # Script: local-test.sh
 # Purpose: Convenience wrapper to run tests for Python/Node projects if present.
 #
 set -euo pipefail

if compgen -G "**/pytest.ini" > /dev/null 2>&1 || compgen -G "**/pyproject.toml" > /dev/null 2>&1; then
   echo "[local-test] running pytest"
   python3 -m pip install --user pytest >/dev/null 2>&1 || true
   pytest -q || true
 else
   echo "[local-test] skipping Python tests (no config)"
 fi

 if [ -f package.json ]; then
   echo "[local-test] running node tests"
   npm ci || npm install
   npx --yes vitest run || npx --yes jest --ci || true
 else
   echo "[local-test] skipping Node tests (no package.json)"
 fi


