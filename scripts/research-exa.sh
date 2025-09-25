#!/usr/bin/env bash
# Purpose: Query Exa references via Rube MCP first; fallback to curl when MCP unavailable.
# Explainer: Centralized entrypoint for research tasks to ensure provenance.

set -euo pipefail

QUERY=${1:-"plasma engine"}

echo "[exa] Attempting Rube MCP (not configured in this workspace)"
echo "# TODO: Integrate with Rube MCP CLI once available"

if [[ -n "${EXA_API_TOKEN:-}" ]]; then
  echo "[exa] Fallback: curl search (placeholder endpoint)"
  curl -sS -H "Authorization: Bearer ${EXA_API_TOKEN}" "https://api.exa.example.com/v1/search?q=${QUERY}" || true
else
  echo "[exa] No EXA_API_TOKEN set. Skipping."
fi

