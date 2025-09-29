#!/usr/bin/env python3
"""Coordinate autopilot workflow executions across Plasma Engine repositories.

This module exists so background agents (or human operators) can trigger the
`autopilot.yml` workflow in every service repo with a *single* command. The
automation keeps Cursor agents, CodeRabbit, and merge pipelines humming without
manual babysitting.

High-level behaviour:

* Read the multi-repo configuration from ``config/autopilot/targets.json``.
* Optionally filter the target list via ``--service`` or ``--repo`` arguments.
* For each target, hit the GitHub REST endpoint that dispatches a workflow run.
* Support dry-run mode so we can audit the plan before touching GitHub state.

Every function below carries thorough inline commentary per repository
standards. Future maintainers should not need to reverse-engineer the control
flow when wiring new services or changing execution cadence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


# TODO(jf-platform, 2025-09-26): Allow per-target secrets (e.g. alternate
# GitHub tokens) so the dispatcher can operate across organisations with stricter
# permission boundaries. The current implementation assumes the repository-scoped
# token works everywhere, which holds true for the Plasma Engine monorepo family.


@dataclass
class WorkflowTarget:
    """Describe one workflow we intend to trigger.

    Attributes mirror the shape of ``config/autopilot/targets.json`` so the
    configuration file stays human-readable while still mapping cleanly onto a
    structured Python object.
    """

    owner: str
    repo: str
    workflow: str
    ref: str
    inputs: dict[str, str]


@dataclass
class DispatchOutcome:
    """Capture the result of dispatching (or planning to dispatch) a workflow."""

    target: WorkflowTarget
    executed: bool
    message: str


def _require_env(name: str) -> str:
    """Look up an environment variable or bail with a descriptive message.

    The dispatcher leans on the GitHub fine-grained token that GitHub Actions
    exposes as ``GITHUB_TOKEN``. Exiting early with context helps automation
    troubleshoot missing credentials quickly.
    """

    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Environment variable {name} must be set for autopilot dispatch")
    return value


def load_targets(config_path: Path) -> list[WorkflowTarget]:
    """Parse the JSON configuration file into :class:`WorkflowTarget` objects."""

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - guardrail for ops mistakes
        raise SystemExit(
            f"Autopilot configuration file missing: {config_path}. Did you run onboarding?"
        ) from exc

    targets: list[WorkflowTarget] = []
    for entry in raw.get("targets", []):
        try:
            target = WorkflowTarget(
                owner=entry["owner"],
                repo=entry["repo"],
                workflow=entry["workflow"],
                ref=entry.get("ref", "main"),
                inputs={key: str(value) for key, value in entry.get("inputs", {}).items()},
            )
        except KeyError as exc:  # pragma: no cover - defensive guardrail
            raise SystemExit(
                f"Configuration entry is missing required field {exc!s}: {entry}"
            ) from exc
        targets.append(target)

    if not targets:
        raise SystemExit(
            "No workflow targets found in config/autopilot/targets.json. Add at least one entry."
        )

    return targets


def _filter_targets(targets: Iterable[WorkflowTarget], selectors: set[str]) -> list[WorkflowTarget]:
    """Limit the target list to entries whose repo slugs match the selectors.

    ``selectors`` can be either ``owner/repo`` pairs or bare repository names.
    Passing an empty set returns the original list.
    """

    if not selectors:
        return list(targets)

    filtered: list[WorkflowTarget] = []
    for target in targets:
        slug = f"{target.owner}/{target.repo}"
        if slug in selectors or target.repo in selectors:
            filtered.append(target)
    return filtered


def dispatch_workflow(*, token: str, target: WorkflowTarget, dry_run: bool) -> DispatchOutcome:
    """Invoke the GitHub REST API to start a workflow run for ``target``.

    The endpoint we call is ``POST /repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches``.
    We include ``ref`` (the branch/tag to run on) and any workflow inputs defined in the config.
    """

    if dry_run:
        return DispatchOutcome(
            target=target,
            executed=False,
            message="Dry-run: would dispatch workflow",
        )

    import urllib.error
    import urllib.request

    url = (
        f"https://api.github.com/repos/{target.owner}/{target.repo}/"
        f"actions/workflows/{target.workflow}/dispatches"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "plasma-engine-autopilot-dispatcher",
    }
    payload = json.dumps({"ref": target.ref, "inputs": target.inputs}).encode("utf-8")

    request = urllib.request.Request(url, data=payload, method="POST", headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            status = response.getcode()
            if status != 204:
                raise RuntimeError(f"Unexpected status code {status} when dispatching {target.repo}")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(
            f"GitHub API rejected dispatch for {target.owner}/{target.repo}: {exc.code} {details}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network failure while dispatching {target.owner}/{target.repo}: {exc.reason}"
        ) from exc

    return DispatchOutcome(target=target, executed=True, message="Workflow dispatched successfully")


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser so agents can customise dispatcher behaviour."""

    parser = argparse.ArgumentParser(
        description=(
            "Trigger cursor/CodeRabbit autopilot workflows across the Plasma Engine repo family."
        )
    )
    parser.add_argument(
        "--config",
        default=Path("config/autopilot/targets.json"),
        type=Path,
        help="Path to the autopilot target definition file",
    )
    parser.add_argument(
        "--target",
        "--service",
        action="append",
        dest="targets",
        default=[],
        help="Restrict dispatching to specific repos (owner/repo or repo name).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned dispatches without calling the GitHub API.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entrypoint used by both CLI invocations and GitHub Actions."""

    parser = build_parser()
    args = parser.parse_args(argv)

    token = _require_env("GITHUB_TOKEN")
    targets = load_targets(args.config)
    filtered = _filter_targets(targets, selectors={t for t in args.targets})

    outcomes: list[DispatchOutcome] = []
    for target in filtered:
        try:
            outcome = dispatch_workflow(token=token, target=target, dry_run=args.dry_run)
        except Exception as exc:  # pragma: no cover - guard against operational surprises
            outcomes.append(
                DispatchOutcome(target=target, executed=False, message=f"Failed: {exc}")
            )
        else:
            outcomes.append(outcome)

    summary = {
        "dry_run": args.dry_run,
        "attempted": len(outcomes),
        "executed": sum(1 for outcome in outcomes if outcome.executed),
        "results": [
            {
                "owner": outcome.target.owner,
                "repo": outcome.target.repo,
                "workflow": outcome.target.workflow,
                "executed": outcome.executed,
                "message": outcome.message,
            }
            for outcome in outcomes
        ],
    }

    print(json.dumps(summary, indent=2))

    failures = [outcome for outcome in outcomes if not outcome.executed and "Failed:" in outcome.message]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())



