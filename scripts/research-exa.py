#!/usr/bin/env python3
"""
Purpose: Demonstrate Exa-backed research query from CLI.
Behavior: Reads EXA_API_KEY from environment and prepares a sample request.
Notes: This is a stub; endpoints and schemas must be validated via Rube MCP.
"""
import json
import os
import sys
from typing import Any, Dict


def build_search_request(query: str, limit: int = 10) -> Dict[str, Any]:
    """Construct a search request payload.

    TODO: Validate fields and filters via Rube MCP Exa docs.
    """
    return {"query": query, "limit": limit, "filters": {"language": "en"}}


def main() -> None:
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        print("EXA_API_KEY not set; printing sample payload only.")
        payload = build_search_request("plasma engine exa")
        print(json.dumps(payload, indent=2))
        sys.exit(0)

    # TODO: Validate base URL and headers via Rube MCP before enabling request.
    print("EXA_API_KEY detected. # TODO: perform request after validating endpoint via MCP.")


if __name__ == "__main__":
    main()