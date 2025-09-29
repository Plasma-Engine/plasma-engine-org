#!/usr/bin/env python3
"""Pull Request Discovery for Self-Healing Automation.

Intelligently discovers pull requests that need attention from
CodeRabbit, Claude, or Cursor agents. Prioritizes based on:
- Age of PR
- Last activity
- Current status labels
- CI/CD status
- Review state
"""

from __future__ import annotations

import json
import os
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib import error, parse, request


@dataclass
class PullRequest:
    """Pull request data for processing priority."""
    
    number: int
    title: str
    head_sha: str
    updated_at: str
    labels: list[str]
    draft: bool
    state: str
    priority_score: float = 0.0


@dataclass  
class Configuration:
    """Runtime configuration from environment."""
    
    github_token: str
    repo_owner: str
    repo_name: str
    max_prs_per_run: int


def load_configuration() -> Configuration:
    """Load configuration from environment variables."""
    
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        sys.exit("GITHUB_TOKEN is required")
    
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo_slug or "/" not in repo_slug:
        sys.exit("GITHUB_REPOSITORY must be in format 'owner/repo'")
    
    owner, repo = repo_slug.split("/", 1)
    
    return Configuration(
        github_token=github_token,
        repo_owner=owner,
        repo_name=repo,
        max_prs_per_run=int(os.environ.get("MAX_PRS_PER_RUN", "5"))
    )


def github_request(
    config: Configuration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None
) -> t.Any:
    """Execute GitHub REST API request."""
    
    base_url = "https://api.github.com"
    url = parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{parse.urlencode(query)}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config.github_token}",
        "User-Agent": "plasma-engine-pr-discovery",
    }
    
    req = request.Request(url, method=method.upper(), headers=headers)
    
    try:
        with request.urlopen(req) as response:
            data = response.read()
            if not data:
                return None
            return json.loads(data)
    except error.HTTPError as exc:
        print(f"GitHub API error ({exc.code}): {exc.read().decode()}")
        return None


def fetch_open_pull_requests(config: Configuration) -> list[PullRequest]:
    """Fetch all open pull requests from the repository."""
    
    pulls = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/pulls",
        {"state": "open", "per_page": 100}
    )
    
    if not pulls:
        return []
    
    return [
        PullRequest(
            number=pr["number"],
            title=pr["title"],
            head_sha=pr["head"]["sha"],
            updated_at=pr["updated_at"],
            labels=[label["name"] for label in pr.get("labels", [])],
            draft=pr["draft"],
            state=pr["state"]
        )
        for pr in pulls
    ]


def calculate_priority_score(pr: PullRequest) -> float:
    """Calculate priority score for processing order.
    
    Higher scores = higher priority
    Factors:
    - Needs attention labels (+10 each)
    - Age (older = higher priority, up to +5)
    - Recent activity (more recent = higher priority, up to +3)
    - Draft status (-5)
    - Size indicators
    """
    
    score = 0.0
    
    # Status labels that indicate need for attention
    attention_labels = {
        "status:needs-coderabbit-review": 10,
        "status:needs-cursor-fix": 8,
        "status:needs-claude-repair": 12,
        "priority:high": 15,
        "priority:critical": 20,
        "bug": 8,
        "security": 15,
    }
    
    for label in pr.labels:
        score += attention_labels.get(label, 0)
    
    # Age factor (older PRs get higher priority)
    try:
        updated = datetime.fromisoformat(pr.updated_at.replace('Z', '+00:00'))
        age_hours = (datetime.utcnow().replace(tzinfo=updated.tzinfo) - updated).total_seconds() / 3600
        
        if age_hours > 168:  # 1 week
            score += 5
        elif age_hours > 72:  # 3 days
            score += 3
        elif age_hours > 24:  # 1 day
            score += 2
        elif age_hours > 6:  # 6 hours
            score += 1
    except (ValueError, TypeError):
        pass
    
    # Recent activity bonus (more recent activity = higher priority)
    try:
        updated = datetime.fromisoformat(pr.updated_at.replace('Z', '+00:00'))
        hours_since_update = (datetime.utcnow().replace(tzinfo=updated.tzinfo) - updated).total_seconds() / 3600
        
        if hours_since_update < 2:  # Very recent activity
            score += 3
        elif hours_since_update < 6:  # Recent activity
            score += 2
        elif hours_since_update < 24:  # Same day activity
            score += 1
    except (ValueError, TypeError):
        pass
    
    # Draft penalty
    if pr.draft:
        score -= 5
    
    # Special handling for automated PRs
    automated_indicators = ["dependabot", "renovate", "auto-", "chore:", "deps:"]
    if any(indicator in pr.title.lower() for indicator in automated_indicators):
        score -= 3  # Lower priority for automated PRs
    
    # Emergency indicators
    emergency_indicators = ["hotfix", "critical", "urgent", "breaking"]
    if any(indicator in pr.title.lower() for indicator in emergency_indicators):
        score += 10
    
    return max(score, 0.0)  # Ensure non-negative


def filter_eligible_prs(prs: list[PullRequest]) -> list[PullRequest]:
    """Filter PRs that are eligible for automation processing."""
    
    eligible = []
    
    for pr in prs:
        # Skip if already approved and doesn't need fixes
        if ("status:coderabbit-approved" in pr.labels and 
            "status:needs-cursor-fix" not in pr.labels and
            "status:needs-claude-repair" not in pr.labels):
            continue
        
        # Skip if marked to ignore automation
        if "automation:skip" in pr.labels or "no-automation" in pr.labels:
            continue
        
        # Skip if in specific states that shouldn't be automated
        blocked_states = ["status:on-hold", "status:blocked", "wip"]
        if any(state in pr.labels for state in blocked_states):
            continue
        
        eligible.append(pr)
    
    return eligible


def prioritize_pull_requests(prs: list[PullRequest], max_count: int) -> list[PullRequest]:
    """Sort PRs by priority and return top N."""
    
    # Calculate priority scores
    for pr in prs:
        pr.priority_score = calculate_priority_score(pr)
    
    # Sort by priority score (highest first)
    sorted_prs = sorted(prs, key=lambda x: x.priority_score, reverse=True)
    
    # Return top N
    return sorted_prs[:max_count]


def get_repository_activity_context(config: Configuration) -> dict[str, t.Any]:
    """Get repository activity context for intelligent scheduling."""
    
    # Get recent commits
    commits = github_request(
        config,
        "GET", 
        f"/repos/{config.repo_owner}/{config.repo_name}/commits",
        {"since": (datetime.utcnow() - timedelta(hours=24)).isoformat(), "per_page": 50}
    )
    
    # Get recent issues
    issues = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/issues", 
        {"state": "open", "since": (datetime.utcnow() - timedelta(hours=24)).isoformat(), "per_page": 50}
    )
    
    return {
        "recent_commits": len(commits) if commits else 0,
        "recent_issues": len(issues) if issues else 0,
        "high_activity": (len(commits) if commits else 0) > 10,
    }


def main() -> None:
    """Main PR discovery logic."""
    
    config = load_configuration()
    
    # Fetch all open PRs
    all_prs = fetch_open_pull_requests(config)
    print(f"Found {len(all_prs)} open pull requests")
    
    # Filter eligible PRs
    eligible_prs = filter_eligible_prs(all_prs)
    print(f"Filtered to {len(eligible_prs)} eligible PRs")
    
    # Get repository activity context
    activity_context = get_repository_activity_context(config)
    
    # Adjust max PRs based on activity
    max_prs = config.max_prs_per_run
    if activity_context["high_activity"]:
        max_prs = min(max_prs + 2, 10)  # Process more during high activity
    
    # Prioritize and limit PRs
    prioritized_prs = prioritize_pull_requests(eligible_prs, max_prs)
    
    # Output for GitHub Actions
    pr_numbers = [pr.number for pr in prioritized_prs]
    
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"pr_numbers={json.dumps(pr_numbers)}\\n")
        f.write(f"total_prs={len(pr_numbers)}\\n")
    
    # Log summary
    print(f"\\n🎯 PR Discovery Summary:")
    print(f"   Total open PRs: {len(all_prs)}")
    print(f"   Eligible PRs: {len(eligible_prs)}")
    print(f"   Selected for processing: {len(prioritized_prs)}")
    print(f"   Repository activity: {'High' if activity_context['high_activity'] else 'Normal'}")
    
    # Detailed PR list
    if prioritized_prs:
        print("\\n📋 Selected PRs (by priority):")
        for i, pr in enumerate(prioritized_prs, 1):
            status_labels = [label for label in pr.labels if label.startswith("status:")]
            print(f"   {i}. PR #{pr.number} (score: {pr.priority_score:.1f})")
            print(f"      Title: {pr.title}")
            print(f"      Status: {', '.join(status_labels) if status_labels else 'No status labels'}")
            print(f"      Draft: {pr.draft}")
    
    # Output detailed JSON for debugging
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "repository_activity": activity_context,
        "discovery_results": {
            "total_open": len(all_prs),
            "eligible": len(eligible_prs),
            "selected": len(prioritized_prs),
            "max_configured": config.max_prs_per_run,
            "max_adjusted": max_prs
        },
        "selected_prs": [
            {
                "number": pr.number,
                "title": pr.title,
                "priority_score": pr.priority_score,
                "labels": pr.labels,
                "draft": pr.draft,
                "updated_at": pr.updated_at
            }
            for pr in prioritized_prs
        ]
    }
    
    print(f"\\n{json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()