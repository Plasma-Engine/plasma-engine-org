#!/usr/bin/env python3
"""Autopilot orchestration for Cursor agents and CodeRabbit reviews.

This module stitches together the repository's background automation so the
DevOps stack can advance without human babysitting:

- **CodeRabbit coordination** – We reuse ``coderabbit_follow_up`` to request
  fresh reviews, update status labels, and post explicit hand-off comments.
- **Cursor dispatch** – Whenever a pull request sits in the
  ``status:needs-cursor-fix`` state, we fan out the relevant ``agent:*``
  labels using the existing ``cursor_dispatch`` heuristics so specialised
  Cursor agents wake up.
- **Automerge on green** – Once CodeRabbit approves a pull request and all
  required status checks succeed, the orchestrator merges the branch using the
  configured strategy. This closes the loop by promoting agent-authored work
  into the target branch without manual intervention.

Every function below includes detailed inline commentary per the repository's
engineering guidelines. The goal is to let future maintainers reason about the
automation without reverse-engineering the call graph or spelunking through
API docs.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, TypedDict

from scripts.automation import coderabbit_follow_up, cursor_dispatch


# ---------------------------------------------------------------------------
# Data models used by the orchestrator
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class AutopilotSettings:
    """Runtime configuration parsed from environment variables.

    Attributes mirror the knobs exposed via GitHub Actions ``env`` or
    ``workflow_dispatch`` inputs so that operators can tune behaviour without
    editing code. Extensive docstrings explain why each value matters.
    """

    owner: str
    repo: str
    token: str
    target_branch: str = "main"
    merge_method: str = "squash"
    dry_run: bool = False
    classifier_override: dict[str, str] = field(default_factory=dict)
    coderabbit_logins: set[str] = field(default_factory=lambda: {"coderabbitai[bot]", "coderabbitai"})
    required_status_contexts: set[str] = field(default_factory=set)
    status_poll_delay: float = 5.0
    status_poll_attempts: int = 3


@dataclass(slots=True)
class PullRequestSnapshot:
    """Lightweight projection of pull request metadata needed for decisions."""

    number: int
    title: str
    head_sha: str
    base_ref: str
    labels: set[str]
    draft: bool
    html_url: str


class ActionLogEntry(TypedDict):
    """Structured record describing one autopilot action for reporting."""

    pr_number: int
    pr_title: str
    url: str
    actions: list[str]
    notes: list[str]


# ---------------------------------------------------------------------------
# Helpers for environment parsing and validation
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Fetch an environment variable or raise a descriptive error."""

    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Environment variable {name} must be set for autopilot orchestration")
    return value


def _parse_bool(value: str | None) -> bool:
    """Interpret common truthy/falsey strings as ``bool`` values.

    Accepting a broad range of inputs makes it easier to toggle behaviour via
    GitHub workflow inputs (which surface as strings) without introducing
    fragile casing/formatting requirements.
    """

    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> set[str]:
    """Turn a comma-separated string into a set of cleaned entries."""

    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def load_settings() -> AutopilotSettings:
    """Hydrate :class:`AutopilotSettings` from environment variables.

    We intentionally mirror the parsing logic used by the other automation
    scripts so option names stay consistent across workflows.
    """

    repo_slug = _require_env("GITHUB_REPOSITORY")
    try:
        owner, repo = repo_slug.split("/", maxsplit=1)
    except ValueError as exc:  # pragma: no cover - defensive guardrail
        raise SystemExit(f"GITHUB_REPOSITORY expected 'owner/repo', found '{repo_slug}'") from exc

    token = _require_env("GITHUB_TOKEN")

    target_branch = os.environ.get("AUTOPILOT_TARGET_BRANCH", "main")
    merge_method = os.environ.get("AUTOPILOT_MERGE_METHOD", "squash").lower()
    if merge_method not in {"merge", "squash", "rebase"}:
        raise SystemExit(
            "AUTOPILOT_MERGE_METHOD must be one of 'merge', 'squash', or 'rebase'"
        )

    classifier_override: dict[str, str] = {}
    if os.environ.get("CURSOR_AGENT_CLASSIFIERS"):
        for entry in os.environ["CURSOR_AGENT_CLASSIFIERS"].split(","):
            entry = entry.strip()
            if not entry:
                continue
            try:
                pattern, label = entry.split("=", maxsplit=1)
            except ValueError as exc:  # pragma: no cover - guard against invalid config
                raise SystemExit(
                    "CURSOR_AGENT_CLASSIFIERS entries must look like pattern=label"
                ) from exc
            classifier_override[pattern.strip()] = label.strip()

    coderabbit_logins_env = os.environ.get("CODERABBIT_LOGINS")
    if coderabbit_logins_env:
        coderabbit_logins = _parse_csv(coderabbit_logins_env)
    else:
        coderabbit_logins = {"coderabbitai[bot]", "coderabbitai"}

    required_status_contexts = _parse_csv(os.environ.get("AUTOPILOT_REQUIRED_STATUS_CONTEXTS"))

    dry_run = _parse_bool(os.environ.get("AUTOPILOT_DRY_RUN"))

    status_poll_delay_raw = os.environ.get("AUTOPILOT_STATUS_POLL_DELAY", "5")
    status_poll_attempts_raw = os.environ.get("AUTOPILOT_STATUS_POLL_ATTEMPTS", "3")

    try:
        status_poll_delay = float(status_poll_delay_raw)
    except ValueError as exc:
        raise SystemExit(
            f"AUTOPILOT_STATUS_POLL_DELAY must be numeric; received '{status_poll_delay_raw}'"
        ) from exc

    try:
        status_poll_attempts = int(status_poll_attempts_raw)
    except ValueError as exc:
        raise SystemExit(
            f"AUTOPILOT_STATUS_POLL_ATTEMPTS must be an integer; received '{status_poll_attempts_raw}'"
        ) from exc

    return AutopilotSettings(
        owner=owner,
        repo=repo,
        token=token,
        target_branch=target_branch,
        merge_method=merge_method,
        dry_run=dry_run,
        classifier_override=classifier_override,
        coderabbit_logins=coderabbit_logins,
        required_status_contexts=required_status_contexts,
        status_poll_delay=status_poll_delay,
        status_poll_attempts=status_poll_attempts,
    )


# ---------------------------------------------------------------------------
# GitHub REST plumbing (mirrors helper patterns from sibling scripts)
# ---------------------------------------------------------------------------


def github_request(
    *,
    settings: AutopilotSettings,
    method: str,
    path: str,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    accepted_status: Iterable[int] | None = None,
) -> Any:
    """Execute a GitHub REST request with retries and helpful errors."""

    import urllib.error
    import urllib.parse
    import urllib.request

    accepted = set(accepted_status or {200, 201, 202, 204})
    base_url = "https://api.github.com"
    url = urllib.parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.token}",
        "User-Agent": "plasma-engine-autopilot",
    }

    payload: bytes | None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        payload = None

    for attempt in range(5):
        request = urllib.request.Request(url, data=payload, method=method.upper(), headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                status = response.getcode()
                data = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            data = exc.read()
            if status in {429, 500, 502, 503, 504}:
                time.sleep(2 ** attempt + 0.1 * attempt)
                continue
            raise RuntimeError(
                f"GitHub API request failed ({status}): {data.decode('utf-8', 'ignore')}"
            ) from exc
        except urllib.error.URLError as exc:
            time.sleep(2 ** attempt + 0.1 * attempt)
            if attempt == 4:
                raise RuntimeError(f"Network error talking to GitHub: {exc}") from exc
            continue

        if status not in accepted:
            raise RuntimeError(
                f"Unexpected GitHub status {status}: {data.decode('utf-8', 'ignore')}"
            )

        if not data:
            return None
        return json.loads(data)

    raise RuntimeError("Exceeded retry budget for GitHub API call")


# ---------------------------------------------------------------------------
# Core orchestration steps
# ---------------------------------------------------------------------------


def fetch_open_pull_requests(settings: AutopilotSettings) -> list[PullRequestSnapshot]:
    """Return open pull requests with just the fields the orchestrator needs."""

    pulls: list[PullRequestSnapshot] = []
    page = 1

    while True:
        payload = github_request(
            settings=settings,
            method="GET",
            path=f"/repos/{settings.owner}/{settings.repo}/pulls",
            query={"state": "open", "per_page": 100, "page": page},
        )
        if not payload:
            break

        for item in payload:
            pulls.append(
                PullRequestSnapshot(
                    number=item["number"],
                    title=item["title"],
                    head_sha=item["head"]["sha"],
                    base_ref=item["base"]["ref"],
                    labels={label["name"] for label in item.get("labels", [])},
                    draft=item.get("draft", False),
                    html_url=item.get("html_url", ""),
                )
            )

        if len(payload) < 100:
            break
        page += 1

    return pulls


def fetch_pull_request_details(settings: AutopilotSettings, pr_number: int) -> dict[str, Any]:
    """Retrieve extended pull request metadata on-demand."""

    return github_request(
        settings=settings,
        method="GET",
        path=f"/repos/{settings.owner}/{settings.repo}/pulls/{pr_number}",
    )


def combined_status_success(settings: AutopilotSettings, sha: str) -> tuple[bool, list[str]]:
    """Check whether the commit's combined status signals success.

    Returns a tuple ``(is_success, notes)`` so callers can surface the reason
    a merge was skipped in the final report.
    """

    response = github_request(
        settings=settings,
        method="GET",
        path=f"/repos/{settings.owner}/{settings.repo}/commits/{sha}/status",
    )

    state = response.get("state", "")
    if state != "success":
        return False, [f"Combined status is '{state}'"]

    missing_contexts: list[str] = []
    if settings.required_status_contexts:
        success_contexts = {
            status.get("context")
            for status in response.get("statuses", [])
            if status.get("state") == "success"
        }
        missing_contexts = sorted(settings.required_status_contexts - success_contexts)

    if missing_contexts:
        return False, [
            "Missing required successful contexts: " + ", ".join(missing_contexts)
        ]

    return True, []


def dispatch_cursor_agents(
    *,
    settings: AutopilotSettings,
    pr: PullRequestSnapshot,
) -> tuple[bool, list[str]]:
    """Apply agent labels and post a summary comment for the given PR.

    Returns a tuple ``(changed, notes)`` where ``changed`` indicates whether
    labels were updated or a comment was posted. ``notes`` provides contextual
    breadcrumbs for the final report.
    """

    cursor_config = cursor_dispatch.Configuration(
        owner=settings.owner,
        repo=settings.repo,
        token=settings.token,
        pr_number=pr.number,
        classifier_override=settings.classifier_override,
    )

    classifier = cursor_dispatch.build_classifier(cursor_config)
    files = cursor_dispatch.list_changed_files(cursor_config)

    aggregated_labels: set[str] = set()
    summary: list[dict[str, Any]] = []

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

    if not aggregated_labels:
        aggregated_labels = {"agent:general"}

    current_labels = cursor_dispatch.get_current_labels(cursor_config)

    if settings.dry_run:
        notes = [
            "Dry-run: would set agent labels to " + ", ".join(sorted(aggregated_labels))
        ]
        if not summary:
            notes.append("No files detected by GitHub API; classifier skipped")
        return False, notes

    changed = cursor_dispatch.replace_agent_labels(
        config=cursor_config,
        current_labels=current_labels,
        desired_labels=aggregated_labels,
    )

    if changed:
        cursor_dispatch.post_dispatch_comment(
            config=cursor_config,
            labels=aggregated_labels,
            summary=summary,
        )
        return True, [
            "Agent labels updated",
            "Summary comment posted",
            "Active labels: " + ", ".join(sorted(aggregated_labels)),
        ]

    return False, ["Agent labels already up to date"]


def attempt_merge(
    *,
    settings: AutopilotSettings,
    pr: PullRequestSnapshot,
) -> tuple[bool, list[str]]:
    """If the PR is mergeable, perform the merge and return action notes."""

    detail = fetch_pull_request_details(settings, pr.number)

    notes: list[str] = []

    if detail.get("base", {}).get("ref") != settings.target_branch:
        return False, [
            f"Base branch '{detail.get('base', {}).get('ref')}' does not match target '{settings.target_branch}'"
        ]

    if detail.get("draft", False):
        return False, ["PR is marked as draft"]

    mergeable_state = detail.get("mergeable_state")
    if mergeable_state and mergeable_state not in {"clean", "has_hooks", "unstable"}:
        return False, [f"Mergeable state is '{mergeable_state}'"]

    status_ok, status_notes = combined_status_success(settings, pr.head_sha)
    if not status_ok:
        return False, status_notes

    if settings.dry_run:
        return False, [
            "Dry-run: would merge with method " + settings.merge_method,
        ]

    response = github_request(
        settings=settings,
        method="PUT",
        path=f"/repos/{settings.owner}/{settings.repo}/pulls/{pr.number}/merge",
        body={
            "merge_method": settings.merge_method,
            "commit_title": f"Autopilot merge: {pr.title}",
        },
        accepted_status={200},
    )

    if not response or not response.get("merged", False):
        notes.extend([
            "Merge API returned non-success payload",
            json.dumps(response, indent=2, sort_keys=True),
        ])
        return False, notes

    return True, [
        "Pull request merged successfully",
        f"Merge SHA: {response.get('sha', 'unknown')}",
    ]


def run() -> None:
    """Entrypoint executed by GitHub Actions or local maintainers."""

    settings = load_settings()

    # ------------------------------------------------------------------
    # Step 1: Reuse the CodeRabbit follow-up logic so labels are fresh and
    # any pending reviews are re-requested before we attempt merges.
    # ------------------------------------------------------------------
    coderabbit_config = coderabbit_follow_up.Configuration(
        owner=settings.owner,
        repo=settings.repo,
        token=settings.token,
        pr_number=None,
        coderabbit_logins=settings.coderabbit_logins,
    )

    coderabbit_outcomes = coderabbit_follow_up.process_pull_requests(coderabbit_config)

    # ------------------------------------------------------------------
    # Step 2: Inspect open pull requests and take appropriate actions.
    # ------------------------------------------------------------------
    pulls = fetch_open_pull_requests(settings)

    action_log: list[ActionLogEntry] = []

    for pr in pulls:
        actions: list[str] = []
        notes: list[str] = []

        if "status:needs-cursor-fix" in pr.labels:
            changed, dispatch_notes = dispatch_cursor_agents(settings=settings, pr=pr)
            if changed:
                actions.append("cursor_dispatch")
            notes.extend(dispatch_notes)

        if "status:coderabbit-approved" in pr.labels:
            merged, merge_notes = attempt_merge(settings=settings, pr=pr)
            if merged:
                actions.append("merged")
            notes.extend(merge_notes)

        if actions or notes:
            action_log.append(
                ActionLogEntry(
                    pr_number=pr.number,
                    pr_title=pr.title,
                    url=pr.html_url,
                    actions=actions,
                    notes=notes,
                )
            )

    report = {
        "settings": {
            "owner": settings.owner,
            "repo": settings.repo,
            "target_branch": settings.target_branch,
            "merge_method": settings.merge_method,
            "dry_run": settings.dry_run,
            "required_status_contexts": sorted(settings.required_status_contexts),
        },
        "coderabbit": coderabbit_outcomes,
        "pull_requests": action_log,
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()


