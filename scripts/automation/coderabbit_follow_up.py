#!/usr/bin/env python3
"""GitHub-facing automation that coordinates CodeRabbit follow-up actions.

This helper is executed inside GitHub Actions to keep pull requests flowing
through an autonomous loop:

1. Cursor agents (or humans) push code to a pull request.
2. CodeRabbit reviews the changes and either approves or requests updates.
3. This script interprets CodeRabbit's state and updates pull request labels
   so downstream automations (Cursor background agents, chatops, etc.) know
   what to do next.

Why so many comments? The repository owner requested exhaustive in-code
documentation so future automation engineers can hand the system over without
oral context. Every function therefore includes detailed commentary on the
intent, assumptions, and edge cases.
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass
from urllib import request, error, parse


# ---------------------------------------------------------------------------
# Data models and configuration
# ---------------------------------------------------------------------------


@dataclass
class PullRequest:
    """Minimal projection of a pull request returned by the GitHub REST API."""

    number: int
    title: str
    head_sha: str
    updated_at: str
    labels: list[str]


@dataclass
class Review:
    """Represents a single review event on a pull request."""

    state: str
    submitted_at: str | None
    commit_id: str
    reviewer_login: str


class FollowUpOutcome(t.TypedDict):
    """Structured summary emitted for each processed pull request."""

    pr_number: int
    applied_label: str
    comment_posted: bool
    reason: str


class Configuration:
    """Runtime configuration derived from environment variables."""

    # GitHub exposes the `owner/repo` tuple via the `GITHUB_REPOSITORY`
    # environment variable inside Actions. We split once and re-use everywhere.
    owner: str
    repo: str
    token: str
    pr_number: int | None
    coderabbit_logins: set[str]


def load_configuration() -> Configuration:
    """Hydrate a ``Configuration`` object from process environment.

    Raises ``SystemExit`` with a descriptive message when mandatory variables
    are absent. The exit surfaces inside GitHub Actions as a failing step,
    giving operators immediate feedback.
    """

    repo_slug = os.environ.get("GITHUB_REPOSITORY")
    if not repo_slug:
        sys.exit("GITHUB_REPOSITORY is required to route API requests")

    try:
        owner, repo = repo_slug.split("/", maxsplit=1)
    except ValueError as exc:  # pragma: no cover - defensive guardrail
        raise SystemExit(
            f"Unexpected GITHUB_REPOSITORY format '{repo_slug}'; expected owner/repo"
        ) from exc

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is mandatory so we can call GitHub's REST API")

    raw_pr_number = os.environ.get("INPUT_PR_NUMBER") or os.environ.get(
        "GITHUB_PR_NUMBER"
    )
    pr_number: int | None
    if raw_pr_number and raw_pr_number.strip():
        try:
            pr_number = int(raw_pr_number)
        except ValueError as exc:
            raise SystemExit(
                f"INPUT_PR_NUMBER must be numeric; received '{raw_pr_number}'"
            ) from exc
    else:
        pr_number = None

    coderabbit_logins_override = os.environ.get("CODERABBIT_LOGINS")
    if coderabbit_logins_override:
        coderabbit_logins = {
            slug.strip()
            for slug in coderabbit_logins_override.split(",")
            if slug.strip()
        }
    else:
        # ``coderabbitai[bot]`` is the canonical login of the GitHub App. The
        # bare ``coderabbitai`` variant appears in some enterprise installs.
        coderabbit_logins = {"coderabbitai[bot]", "coderabbitai"}

    return Configuration(
        owner=owner,
        repo=repo,
        token=token,
        pr_number=pr_number,
        coderabbit_logins=coderabbit_logins,
    )


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


class GitHubAPIError(RuntimeError):
    """Raised when GitHub returns a non-successful HTTP response."""


def github_request(
    *,
    config: Configuration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None,
    body: dict[str, t.Any] | None = None,
    accepted_status: set[int] | None = None,
) -> t.Any:
    """Execute a REST request against GitHub and return the decoded payload.

    The helper hides repetitive plumbing (auth headers, retry backoff, JSON
    parsing). A conservative exponential backoff handles transient rate-limit
    responses without hammering GitHub.
    """

    accepted_status = accepted_status or {200, 201, 202, 204}
    base_url = "https://api.github.com"
    url = parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{parse.urlencode(query)}"

    payload: bytes | None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config.token}",
        "User-Agent": "plasma-engine-coderabbit-follow-up",
    }

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
            if status == 429 or status >= 500:
                # Trivial exponential backoff with jitter keeps us polite.
                time.sleep(2 ** attempt + 0.1 * attempt)
                continue
            raise GitHubAPIError(
                f"GitHub API request failed ({status}): {data.decode('utf-8', 'ignore')}"
            ) from exc
        except error.URLError as exc:
            time.sleep(2 ** attempt + 0.1 * attempt)
            if attempt == 4:
                raise GitHubAPIError(f"Network error talking to GitHub: {exc}") from exc
            continue

        if status not in accepted_status:
            decoded = data.decode("utf-8", "ignore")
            raise GitHubAPIError(f"Unexpected GitHub status {status}: {decoded}")

        if not data:
            return None
        return json.loads(data)

    raise GitHubAPIError("Exhausted retries contacting GitHub")


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------


FOLLOW_UP_LABELS = {
    "status:needs-coderabbit-review",
    "status:needs-cursor-fix",
    "status:coderabbit-approved",
}


def ensure_labels_exist(config: Configuration) -> None:
    """Create the tracking labels on-demand if the repository lacks them."""

    existing_labels: list[dict[str, t.Any]] = github_request(
        config=config,
        method="GET",
        path=f"/repos/{config.owner}/{config.repo}/labels",
        query={"per_page": 100},
    )
    present = {label["name"] for label in existing_labels}

    for label_name in FOLLOW_UP_LABELS - present:
        github_request(
            config=config,
            method="POST",
            path=f"/repos/{config.owner}/{config.repo}/labels",
            body={
                "name": label_name,
                "color": "0e8a16" if "approved" in label_name else "d73a4a",
                "description": "Autopilot coordination label managed by CodeRabbit follow-up script",
            },
            accepted_status={201},
        )


def list_open_pull_requests(config: Configuration) -> list[PullRequest]:
    """Fetch open pull requests (optionally filtered to a specific PR number)."""

    if config.pr_number is not None:
        pr = github_request(
            config=config,
            method="GET",
            path=f"/repos/{config.owner}/{config.repo}/pulls/{config.pr_number}",
        )
        return [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                head_sha=pr["head"]["sha"],
                updated_at=pr["updated_at"],
                labels=[label["name"] for label in pr.get("labels", [])],
            )
        ]

    pulls = github_request(
        config=config,
        method="GET",
        path=f"/repos/{config.owner}/{config.repo}/pulls",
        query={"state": "open", "per_page": 100},
    )

    return [
        PullRequest(
            number=item["number"],
            title=item["title"],
            head_sha=item["head"]["sha"],
            updated_at=item["updated_at"],
            labels=[label["name"] for label in item.get("labels", [])],
        )
        for item in pulls
    ]


def list_reviews(config: Configuration, pr_number: int) -> list[Review]:
    """Return every review associated with a pull request."""

    reviews = github_request(
        config=config,
        method="GET",
        path=f"/repos/{config.owner}/{config.repo}/pulls/{pr_number}/reviews",
        query={"per_page": 100},
    )

    return [
        Review(
            state=review["state"],
            submitted_at=review.get("submitted_at"),
            commit_id=review["commit_id"],
            reviewer_login=(review.get("user") or {}).get("login", ""),
        )
        for review in reviews
    ]


def choose_follow_up_label(
    *,
    pr: PullRequest,
    reviews: list[Review],
    coderabbit_logins: set[str],
) -> tuple[str, str]:
    """Decide which label best describes the PR's CodeRabbit state.

    Returns a tuple of ``(label, reason)``. The reason is later bubbled into
    the GitHub Action logs and optional PR comments so humans can follow the
    automation trail.
    """

    # Filter only CodeRabbit-authored reviews.
    robot_reviews = [
        review
        for review in reviews
        if review.reviewer_login.lower() in {login.lower() for login in coderabbit_logins}
    ]

    if not robot_reviews:
        return (
            "status:needs-coderabbit-review",
            "No CodeRabbit reviews detected; requesting a fresh analysis.",
        )

    # The most recent CodeRabbit review typically lives at the end of the list.
    latest = robot_reviews[-1]

    if latest.commit_id != pr.head_sha:
        return (
            "status:needs-coderabbit-review",
            "CodeRabbit review predates the latest commit; requesting re-review.",
        )

    state = latest.state.upper()
    if state == "CHANGES_REQUESTED":
        return (
            "status:needs-cursor-fix",
            "CodeRabbit requested changes on the latest commit.",
        )
    if state == "APPROVED":
        return (
            "status:coderabbit-approved",
            "CodeRabbit approved the pull request for the current head commit.",
        )

    # For COMMENTED, DISMISSED, or other states we stay conservative and ask
    # for another automatic review so the autopilot remains deterministic.
    return (
        "status:needs-coderabbit-review",
        f"Latest CodeRabbit review state '{state}' does not finalize the PR.",
    )


def update_labels_and_comment(
    *,
    config: Configuration,
    pr: PullRequest,
    new_label: str,
    reason: str,
) -> bool:
    """Ensure the PR carries exactly one follow-up label and optionally comment.

    Returns ``True`` when a comment was posted (i.e., the status changed) so the
    caller can include that fact in the terminal summary.
    """

    # Determine whether anything actually changed to avoid noisy churn.
    existing_labels = set(pr.labels)
    label_changed = new_label not in existing_labels or bool(
        FOLLOW_UP_LABELS.intersection(existing_labels - {new_label})
    )

    if not label_changed:
        return False

    # Remove any stale follow-up labels so exactly one remains.
    for label in FOLLOW_UP_LABELS:
        if label != new_label and label in existing_labels:
            github_request(
                config=config,
                method="DELETE",
                path=(
                    f"/repos/{config.owner}/{config.repo}/issues/{pr.number}/labels/"
                    f"{parse.quote(label)}"
                ),
                accepted_status={200, 204},
            )

    if new_label not in existing_labels:
        github_request(
            config=config,
            method="POST",
            path=f"/repos/{config.owner}/{config.repo}/issues/{pr.number}/labels",
            body={"labels": [new_label]},
            accepted_status={200},
        )

    comment_body = (
        "🤖 **Autopilot update:** "
        f"{reason} Current coordination label set to `{new_label}`."
    )

    github_request(
        config=config,
        method="POST",
        path=f"/repos/{config.owner}/{config.repo}/issues/{pr.number}/comments",
        body={"body": comment_body},
        accepted_status={201},
    )

    return True


def trigger_coderabbit_if_needed(
    *,
    config: Configuration,
    pr_number: int,
    new_label: str,
    reason: str,
) -> None:
    """Kick CodeRabbit when we need a (re)review.

    We purposely re-use the same request body we relied on manually so
    notifications remain consistent.
    """

    if new_label != "status:needs-coderabbit-review":
        return

    github_request(
        config=config,
        method="POST",
        path=f"/repos/{config.owner}/{config.repo}/pulls/{pr_number}/reviews",
        body={"event": "COMMENT", "body": "@coderabbit review"},
        accepted_status={200},
    )


def process_pull_requests(config: Configuration) -> list[FollowUpOutcome]:
    """Main orchestration routine invoked by ``main``."""

    ensure_labels_exist(config)
    outcomes: list[FollowUpOutcome] = []

    for pr in list_open_pull_requests(config):
        reviews = list_reviews(config, pr.number)
        label, reason = choose_follow_up_label(
            pr=pr, reviews=reviews, coderabbit_logins=config.coderabbit_logins
        )

        comment_posted = update_labels_and_comment(
            config=config, pr=pr, new_label=label, reason=reason
        )
        trigger_coderabbit_if_needed(
            config=config, pr_number=pr.number, new_label=label, reason=reason
        )

        outcomes.append(
            FollowUpOutcome(
                pr_number=pr.number,
                applied_label=label,
                comment_posted=comment_posted,
                reason=reason,
            )
        )

    return outcomes


def main() -> None:
    """Entry point executed by GitHub Actions."""

    config = load_configuration()
    outcomes = process_pull_requests(config)

    print(json.dumps({"outcomes": outcomes}, indent=2))


if __name__ == "__main__":
    main()


