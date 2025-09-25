#!/usr/bin/env python3
"""
Developer Onboarding Helper

Purpose:
- Provide a guided checklist and quick checks for local environment setup.
- Keep commentary detailed so this can be handed off to engineers directly.

What this script does:
- Prints required tool versions and verifies presence (Node, Python, Git, Terraform optional).
- Outlines recommended next steps and links to repo docs.

Note:
- This script is safe to run locally; it does not modify system state.
- Add organization-specific steps as needed (e.g., SSO, secrets retrieval).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str]) -> Tuple[int, str]:
    """Run a shell command and capture its output without raising exceptions.

    Returns a tuple of (exit_code, stdout+stderr_text).
    """
    try:
        result = subprocess.run(
            command, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        return 127, f"Command not found: {' '.join(command)}"


def check_binary(name: str) -> Tuple[bool, str]:
    """Check if a binary is available on PATH and return its version output if possible."""
    path = shutil.which(name)
    if not path:
        return False, f"{name}: not found on PATH"

    # Attempt to query a conventional version flag; fall back gracefully
    for flag in ("--version", "-v", "version"):
        code, output = run_command([name, flag])
        if code == 0:
            return True, f"{name}: {output}"
    return True, f"{name}: installed (version unknown)"


def print_heading(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> int:
    print_heading("Plasma Engine - Developer Onboarding")

    print("Repository Docs:")
    print("- docs/devops-process.md (process)")
    print("- docs/devops (runbooks, playbooks, release)")
    print("- docs/exa (API references)")

    print_heading("Toolchain Checks")
    for tool in ("node", "npm", "python3", "git", "terraform"):
        ok, msg = check_binary(tool)
        status = "OK" if ok else "MISSING"
        print(f"[{status}] {msg}")

    print_heading("Next Steps (Suggested)")
    print("1) If Terraform is missing, install v1.6+.")
    print("2) For Python projects, create a virtualenv and install requirements.")
    print("3) For Node projects, run `npm ci` and `npm test`.")
    print("4) Review CI workflows in .github/workflows and playbooks under docs/devops/playbooks.")

    # TODO: Add organization SSO/bootstrap instructions (e.g., GH CLI auth, cloud creds)

    return 0


if __name__ == "__main__":
    sys.exit(main())