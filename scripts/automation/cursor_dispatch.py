#!/usr/bin/env python3
"""Dispatch specialized Cursor agents based on pull-request content.

The automation loops in tandem with the CodeRabbit follow-up pipeline:

1. CodeRabbit requests changes, which causes the `status:needs-cursor-fix`
   label to appear on the pull request.
2. This script inspects the head commit, classifies the changed files, and
   applies one or more `agent:*` labels that map to distinct Cursor agents.
3. Each agent watches for its label and can autonomously triage follow-up work
   (fix tests, update docs, refresh Terraform, etc.).

Lots of inline comments are included per the repository's engineering
guidelines so that future maintainers can reason about the automation without
reverse-engineering it.
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass
from urllib import error, parse, request


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Configuration:
    """Runtime configuration derived from GitHub Actions environment."""

    owner: str
    repo: str
    token: str
    pr_number: int
    classifier_override: dict[str, str]


@dataclass
class PRFile:
    """Represents one file entry returned by the PR files API."""

    filename: str
    status: str
    additions: int
    deletions: int


# ---------------------------------------------------------------------------
# Environment parsing helpers
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Fetch an environment variable or abort with a descriptive message."""

    value = os.environ.get(name)
    if not value:
        sys.exit(f"Environment variable {name} must be set for cursor dispatch")
    return value


def load_configuration() -> Configuration:
    """Hydrate configuration for downstream API calls."""

    repo_slug = _require_env("GITHUB_REPOSITORY")
    try:
        owner, repo = repo_slug.split("/", maxsplit=1)
    except ValueError as exc:  # pragma: no cover - defensive guardrail
        raise SystemExit(
            f"GITHUB_REPOSITORY expected 'owner/repo', found '{repo_slug}'"
        ) from exc

    token = _require_env("GITHUB_TOKEN")

    raw_number = os.environ.get("INPUT_PR_NUMBER") or os.environ.get(
        "GITHUB_PR_NUMBER"
    )
    if not raw_number:
        sys.exit(
            "Provide the pull request number using INPUT_PR_NUMBER or GITHUB_PR_NUMBER"
        )
    try:
        pr_number = int(raw_number)
    except ValueError as exc:
        raise SystemExit(
            f"Pull request number must be an integer; received '{raw_number}'"
        ) from exc

    classifier_override_raw = os.environ.get("CURSOR_AGENT_CLASSIFIERS")
    classifier_override: dict[str, str] = {}
    if classifier_override_raw:
        for entry in classifier_override_raw.split(","):
            if not entry.strip():
                continue
            try:
                pattern, label = entry.split("=", maxsplit=1)
            except ValueError as exc:
                raise SystemExit(
                    "CURSOR_AGENT_CLASSIFIERS entries must look like pattern=label"
                ) from exc
            classifier_override[pattern.strip()] = label.strip()

    return Configuration(
        owner=owner,
        repo=repo,
        token=token,
        pr_number=pr_number,
        classifier_override=classifier_override,
    )


# ---------------------------------------------------------------------------
# GitHub REST API helper
# ---------------------------------------------------------------------------


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API returns an unexpected response."""


def github_request(
    *,
    config: Configuration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None,
    body: dict[str, t.Any] | None = None,
    accepted_status: set[int] | None = None,
) -> t.Any:
    """Execute a GitHub REST request with retry-friendly plumbing."""

    accepted_status = accepted_status or {200, 201, 202, 204}
    base_url = "https://api.github.com"
    url = parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{parse.urlencode(query)}"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config.token}",
        "User-Agent": "plasma-engine-cursor-dispatch",
    }

    payload: bytes | None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        payload = None

    for attempt in range(5):
        req = request.Request(url, data=payload, method=method.upper(), headers=headers)
        try:
            with request.urlopen(req) as response:
                status = response.getcode()
                data = response.read()
        except error.HTTPError as exc:
            status = exc.code
            data = exc.read()
            if status in {429, 502, 503, 504}:
                time.sleep(2 ** attempt + 0.1 * attempt)
                continue
            raise GitHubAPIError(
                f"GitHub API call failed ({status}): {data.decode('utf-8', 'ignore')}"
            ) from exc
        except error.URLError as exc:
            time.sleep(2 ** attempt + 0.1 * attempt)
            if attempt == 4:
                raise GitHubAPIError(f"Network error talking to GitHub: {exc}") from exc
            continue

        if status not in accepted_status:
            raise GitHubAPIError(
                f"Unexpected GitHub status {status}: {data.decode('utf-8', 'ignore')}"
            )

        if not data:
            return None
        return json.loads(data)

    raise GitHubAPIError("Exceeded retry budget for GitHub API call")


# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------


AGENT_LABELS = {
    "agent:infra",
    "agent:python",
    "agent:javascript",
    "agent:docs",
    "agent:content",
    "agent:ops",
    "agent:security",
    "agent:general",
}


def default_classifier(path: str) -> set[str]:
    """Return agent labels inferred from the changed file path."""

    labels: set[str] = set()
    lowered = path.lower()

    if lowered.endswith(('.md', '.rst')) or lowered.startswith('docs/'):
        labels.add("agent:docs")

    if any(segment in lowered for segment in ["content", "marketing"]):
        labels.add("agent:content")

    if lowered.endswith(".tf") or "infra" in lowered or "terraform" in lowered:
        labels.add("agent:infra")

    if lowered.endswith(('.py', '.pyi')):
        labels.add("agent:python")

    if lowered.endswith(('.ts', '.tsx', '.js', '.jsx')):
        labels.add("agent:javascript")

    if "security" in lowered or "policies" in lowered:
        labels.add("agent:security")

    if "ops" in lowered or "runbook" in lowered or "playbook" in lowered:
        labels.add("agent:ops")

    if not labels:
        labels.add("agent:general")

    return labels


def build_classifier(config: Configuration) -> t.Callable[[str], set[str]]:
    """Combine default heuristics with optional overrides."""

    if not config.classifier_override:
        return default_classifier

    def classify(path: str) -> set[str]:
        for prefix, label in config.classifier_override.items():
            if path.startswith(prefix):
                return {label}
        return default_classifier(path)

    return classify


# ---------------------------------------------------------------------------
# GitHub operations
# ---------------------------------------------------------------------------


def list_changed_files(config: Configuration) -> list[PRFile]:
    """Fetch up to 300 changed files by paging the PR files API."""

    files: list[PRFile] = []
    page = 1
    while True:
        payload = github_request(
            config=config,
            method="GET",
            path=f"/repos/{config.owner}/{config.repo}/pulls/{config.pr_number}/files",
            query={"page": page, "per_page": 100},
        )
        if not payload:
            break
        files.extend(
            PRFile(
                filename=item["filename"],
                status=item["status"],
                additions=item.get("additions", 0),
                deletions=item.get("deletions", 0),
            )
            for item in payload
        )
        if len(payload) < 100:
            break
        page += 1
    return files


def get_current_labels(config: Configuration) -> set[str]:
    """Retrieve existing labels on the pull request."""

    pull = github_request(
        config=config,
        method="GET",
        path=f"/repos/{config.owner}/{config.repo}/pulls/{config.pr_number}",
    )
    return {label["name"] for label in pull.get("labels", [])}


def replace_agent_labels(
    *,
    config: Configuration,
    current_labels: set[str],
    desired_labels: set[str],
) -> bool:
    """Mutate GitHub labels so agent labels match our desired set.

    Returns ``True`` if a change was performed so callers can emit commentary.
    """

    changed = False

    tracked = AGENT_LABELS | desired_labels

    for label in tracked:
        if label in current_labels and label not in desired_labels:
            github_request(
                config=config,
                method="DELETE",
                path=(
                    f"/repos/{config.owner}/{config.repo}/issues/{config.pr_number}/labels/"
                    f"{parse.quote(label)}"
                ),
                accepted_status={200, 204},
            )
            changed = True

    missing = [label for label in desired_labels if label not in current_labels]
    if missing:
        github_request(
            config=config,
            method="POST",
            path=f"/repos/{config.owner}/{config.repo}/issues/{config.pr_number}/labels",
            body={"labels": missing},
            accepted_status={200},
        )
        changed = True

    return changed


def post_dispatch_comment(
    *,
    config: Configuration,
    labels: set[str],
    summary: list[dict[str, t.Any]],
) -> None:
    """Leave a PR comment summarising the dispatch decision."""

    markdown_lines = [
        "🤖 **Cursor Dispatch**",
        "",
        "| File | Status | Agents |",
        "| --- | --- | --- |",
    ]
    for entry in summary:
        markdown_lines.append(
            f"| `{entry['filename']}` | {entry['status']} | {', '.join(sorted(entry['labels']))} |"
        )

    markdown_lines.append("")
    markdown_lines.append(
        "Active agent labels: " + ", ".join(f"`{label}`" for label in sorted(labels))
    )
    markdown_lines.append(
        "Agents should pick up tasks associated with their label and update the PR when complete."
    )

    github_request(
        config=config,
        method="POST",
        path=f"/repos/{config.owner}/{config.repo}/issues/{config.pr_number}/comments",
        body={"body": "\n".join(markdown_lines)},
        accepted_status={201},
    )


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------


def main() -> None:
    """Entrypoint executed in the GitHub Action."""

    config = load_configuration()
    classifier = build_classifier(config)

    files = list_changed_files(config)
    summary: list[dict[str, t.Any]] = []
    aggregated_labels: set[str] = set()

    for file in files:
        labels = classifier(file.filename)
        aggregated_labels.update(labels)
        summary.append(
            {
                "filename": file.filename,
                "status": file.status,
                "labels": sorted(labels),
                "additions": file.additions,
                "deletions": file.deletions,
            }
        )

    current_labels = get_current_labels(config)
    if not aggregated_labels:
        aggregated_labels = {"agent:general"}

    changed = replace_agent_labels(
        config=config, current_labels=current_labels, desired_labels=aggregated_labels
    )

    if changed:
        post_dispatch_comment(config=config, labels=aggregated_labels, summary=summary)

    print(
        json.dumps(
            {
                "pr_number": config.pr_number,
                "labels": sorted(aggregated_labels),
                "changed": changed,
                "files": summary,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


