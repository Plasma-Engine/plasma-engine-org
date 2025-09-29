#!/usr/bin/env bash
# Explainer: Run Python CI steps locally (ruff, black, pytest with coverage).
# Usage: ./scripts/run_python_ci_local.sh [path]

set -euo pipefail
ROOT=${1:-.}

python -m pip install --upgrade pip >/dev/null
pip install ruff black pytest pytest-cov >/dev/null

ruff check "$ROOT"
black --check "$ROOT"
pytest -q "$ROOT" --junitxml=junit.xml --cov="$ROOT" --cov-report=xml

echo "Artifacts: junit.xml and coverage.xml (if coverage present)."

