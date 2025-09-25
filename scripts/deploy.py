#!/usr/bin/env python3
"""
Explainer:
  Deployment orchestrator. Delegates to Terraform or other tooling based on
  environment. This is a conservative placeholder that validates inputs and
  prints intended actions; extend to actually apply changes.

Usage:
  python scripts/deploy.py --env staging
  python scripts/deploy.py --env prod --rollback v1.2.3

# TODO: Integrate with Helm/EKS or desired platform and implement safe rollout.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERRAFORM_DIR = os.path.join(REPO_ROOT, "plasma-engine-infra", "infra", "terraform", "envs")


def run(cmd: List[str], cwd: str | None = None) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd, cwd=cwd)


def deploy(env: str) -> int:
    env_dir = os.path.join(TERRAFORM_DIR, env)
    if not os.path.isdir(env_dir):
        print(f"Unknown environment: {env_dir}", file=sys.stderr)
        return 2
    # Terraform plan/apply with manual approval gates recommended in CI
    rc = run(["terraform", "init", "-input=false"], cwd=env_dir)
    if rc != 0:
        return rc
    rc = run(["terraform", "plan"], cwd=env_dir)
    if rc != 0:
        return rc
    # NOTE: In CI, apply should be gated by environment approval
    print("# TODO: Apply step gated by environment approval")
    return 0


def rollback(env: str, target: str) -> int:
    # Placeholder: real rollback depends on deployment system
    print(f"Rollback requested for env={env} to target={target}")
    print("# TODO: Implement rollback mechanics (Helm release history / Terraform state)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--rollback")
    args = parser.parse_args()
    if args.rollback:
        return rollback(args.env, args.rollback)
    return deploy(args.env)


if __name__ == "__main__":
    raise SystemExit(main())

