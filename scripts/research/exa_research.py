#!/usr/bin/env python3
"""
Explainer: Exa-backed research helper.

Purpose:
    Demonstrates how we would query the Exa API from Python to support
    research workflows. This is a placeholder: endpoints, payloads, and
    models must be updated after syncing with official docs via Rube MCP.

Usage:
    EXA_API_KEY=... ./scripts/research/exa_research.py "query string"

Notes:
    - Prefer environment variables for secrets.
    - Inline comments explain why decisions are made for clarity.
"""

import json
import os
import sys
from typing import Any, Dict

import urllib.request


def build_request_url(query: str) -> str:
    """Construct the placeholder search URL with proper encoding."""
    from urllib.parse import urlencode

    params = urlencode({"q": query})
    return f"https://api.exa.example.invalid/search?{params}"


def perform_request(url: str, api_key: str) -> Dict[str, Any]:
    """Perform a GET request using Bearer auth. Returns parsed JSON.

    In production, replace urllib with `requests` and add retries with
    exponential backoff.
    """
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        charset = resp.headers.get_content_charset() or "utf-8"
        data = resp.read().decode(charset)
        return json.loads(data)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: exa_research.py <query>")
        sys.exit(2)

    query = sys.argv[1]
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        # Explicit guidance to developers helps avoid silent failures
        raise SystemExit("EXA_API_KEY is not set. See docs/exa/auth.md")

    url = build_request_url(query)
    # For transparency, print the URL being requested (without secrets)
    print(f"[exa] GET {url}")
    try:
        result = perform_request(url, api_key)
    except Exception as exc:  # noqa: BLE001
        # Clear error message and next steps
        raise SystemExit(f"Request failed: {exc}\n# TODO: Update endpoint once schema is synced.")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

