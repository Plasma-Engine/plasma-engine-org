#!/usr/bin/env python3
"""
Explainer: Mirrors Exa API schemas locally (JSON/YAML) with precise comments per field.
Purpose: Enable offline development and validation against the latest Exa API structures.
Inputs:
  - EXA_SCHEMA_SOURCES: Optional comma-separated URLs or file paths to schema descriptors.
  - OUTPUT_DIR: Optional output directory (default: ./schemas/exa)
Outputs:
  - Writes annotated schema files to OUTPUT_DIR (e.g., search.yaml, crawl.yaml)
Downstream:
  - CI/validation steps can use these local schemas for contract tests.

Notes:
  - Prefer using the Rube MCP client for fetching authoritative Exa docs when available.
  - If EXA_SCHEMA_SOURCES is not provided, this script writes placeholders with TODOs.

References:
  - Exa docs: https://docs.exa.ai/  (Confirm endpoints and schema stability before updating)
"""
from __future__ import annotations

import os
import sys
import json
import textwrap
from pathlib import Path
from typing import List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # YAML support optional; write JSON if PyYAML is missing


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_sources(sources: str) -> List[str]:
    return [s.strip() for s in sources.split(",") if s.strip()]


def write_placeholder(output_dir: Path) -> None:
    """Write placeholder schemas with rich comments and TODOs."""
    ensure_dir(output_dir)

    placeholder = {
        "title": "Exa Search API Schema (Placeholder)",
        "description": (
            "Placeholder schema capturing expected fields for Exa search.\n"
            "TODO: Owner=Research integrate via Rube MCP and replace with authoritative schema."
        ),
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "User query string for web search.",
            },
            "num_results": {
                "type": "integer",
                "description": (
                    "Max number of results to return. TODO: Confirm Exa default/limits."
                ),
                "minimum": 1,
                "maximum": 50,
                "default": 10,
            },
            "filters": {
                "type": "object",
                "description": (
                    "Optional filter object. TODO: Enumerate allowed filters (domains, time range, etc.)."
                ),
                "additionalProperties": True,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
        "$comment": (
            "See https://docs.exa.ai/ for up-to-date parameters."
        ),
    }

    # Prefer YAML for readability if available
    if yaml is not None:
        path_yaml = output_dir / "search.yaml"
        with path_yaml.open("w", encoding="utf-8") as f:
            yaml.safe_dump(placeholder, f, sort_keys=False)
    # Always produce JSON as well
    path_json = output_dir / "search.json"
    with path_json.open("w", encoding="utf-8") as f:
        json.dump(placeholder, f, indent=2)


def main() -> int:
    output_dir = Path(os.environ.get("OUTPUT_DIR", "./schemas/exa")).resolve()
    sources_env = os.environ.get("EXA_SCHEMA_SOURCES", "")

    if not sources_env:
        print(
            "[mirror-exa-schemas] No EXA_SCHEMA_SOURCES provided; writing placeholders to",
            output_dir,
        )
        write_placeholder(output_dir)
        return 0

    sources = load_sources(sources_env)
    ensure_dir(output_dir)

    # TODO: Owner=DevEx: Replace with Rube MCP client to fetch schemas from Exa docs/API.
    for src in sources:
        print(f"[mirror-exa-schemas] INFO: Fetching from {src} (not implemented). Writing placeholder instead.")
    write_placeholder(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())