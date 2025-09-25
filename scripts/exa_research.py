#!/usr/bin/env python3
"""
Explainer:
  Exa-backed research helper. Queries the Exa Search API to retrieve samples.
  This is a placeholder pending authoritative schema from Rube MCP / exa.ai docs.

Usage:
  python scripts/exa_research.py --query "vector databases" --limit 5

# TODO: Replace BASE_URL, endpoints, and fields with official Exa API spec.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

import urllib.request

BASE_URL = os.environ.get("EXA_BASE_URL", "https://api.exa.ai")  # TODO
API_KEY = os.environ.get("EXA_API_KEY", "")  # TODO: Provide via secrets


def http_post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: EXA_API_KEY not set", file=sys.stderr)
        return 2

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",  # TODO: Confirm auth scheme
    }
    payload = {"query": args.query, "num_results": args.limit}  # TODO: Confirm fields

    try:
        resp = http_post_json(f"{BASE_URL}/search", payload, headers)  # TODO: Confirm path
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(resp, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

