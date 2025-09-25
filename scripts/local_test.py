#!/usr/bin/env python3
"""
Local Testing Orchestrator

Purpose:
- Provide a simple, documented entrypoint for running lint and tests across services.

Behavior:
- Detects known service directories and prints the commands it will run.
- Executes best-effort checks; non-zero exit codes are surfaced at the end.

Extend:
- Add coverage thresholds or service-specific commands as repositories evolve.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Tuple

KNOWN_PY_SERVICES = [
    "plasma-engine-agent",
    "plasma-engine-brand",
    "plasma-engine-content",
    "plasma-engine-research",
]

KNOWN_NODE_SERVICES = [
    "plasma-engine-gateway",
]


def run(cmd: List[str], cwd: str | None = None) -> int:
    print(f"$ {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    exit_codes: List[int] = []

    # Node services
    for svc in KNOWN_NODE_SERVICES:
        if os.path.isdir(svc):
            exit_codes.append(run(["npm", "ci"], cwd=svc))
            exit_codes.append(run(["npm", "run", "lint", "--if-present"], cwd=svc))
            exit_codes.append(run(["npm", "test", "--if-present"], cwd=svc))

    # Python services
    for svc in KNOWN_PY_SERVICES:
        if os.path.isdir(svc):
            req_dev = os.path.join(svc, "requirements-dev.txt")
            req = os.path.join(svc, "requirements.txt")
            if os.path.isfile(req_dev):
                exit_codes.append(run(["python3", "-m", "pip", "install", "-r", "requirements-dev.txt"], cwd=svc))
            if os.path.isfile(req):
                exit_codes.append(run(["python3", "-m", "pip", "install", "-r", "requirements.txt"], cwd=svc))
            exit_codes.append(run(["ruff", "check", "."], cwd=svc))
            exit_codes.append(run(["black", "--check", "."], cwd=svc))
            exit_codes.append(run(["pytest", "-q"], cwd=svc))

    # Summarize
    failures = [c for c in exit_codes if c != 0]
    if failures:
        print(f"One or more commands failed: {failures}")
        return 1
    print("All checks completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())