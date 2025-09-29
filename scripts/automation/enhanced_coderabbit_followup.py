#!/usr/bin/env python3
"""Enhanced CodeRabbit Follow-up with Intelligent Rate Limiting.

This is an enhanced version of the original coderabbit_follow_up.py that adds:
- Better rate limiting awareness
- Intelligent scheduling based on PR priority
- Integration with the broader self-healing system
- More sophisticated state management
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib import request, error, parse

# Import from the original script
sys.path.append(os.path.dirname(__file__))
from coderabbit_follow_up import (
    Configuration as BaseConfiguration,
    PullRequest,
    Review,
    github_request as base_github_request,
    choose_follow_up_label,
    update_labels_and_comment,
    trigger_coderabbit_if_needed,
    FOLLOW_UP_LABELS,
)


@dataclass
class EnhancedConfiguration(BaseConfiguration):
    """Enhanced configuration with additional options."""
    
    priority_mode: bool = False
    max_coderabbit_requests: int = 10
    backoff_multiplier: float = 1.5


def load_enhanced_configuration() -> EnhancedConfiguration:
    """Load enhanced configuration from environment."""
    
    repo_slug = os.environ.get("GITHUB_REPOSITORY")
    if not repo_slug:
        sys.exit("GITHUB_REPOSITORY is required")
    
    try:
        owner, repo = repo_slug.split("/", maxsplit=1)
    except ValueError as exc:
        raise SystemExit(
            f"Unexpected GITHUB_REPOSITORY format '{repo_slug}'; expected owner/repo"
        ) from exc
    
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required")
    
    raw_pr_number = os.environ.get("INPUT_PR_NUMBER")
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
        coderabbit_logins = {"coderabbitai[bot]", "coderabbitai"}
    
    # Enhanced options
    priority_mode = os.environ.get("PRIORITY_MODE", "").lower() in ("true", "1", "yes")
    max_requests = int(os.environ.get("MAX_CODERABBIT_REQUESTS", "10"))
    backoff_multiplier = float(os.environ.get("BACKOFF_MULTIPLIER", "1.5"))
    
    return EnhancedConfiguration(
        owner=owner,
        repo=repo,
        token=token,
        pr_number=pr_number,
        coderabbit_logins=coderabbit_logins,
        priority_mode=priority_mode,
        max_coderabbit_requests=max_requests,
        backoff_multiplier=backoff_multiplier,
    )


def update_rate_limit_state(config: EnhancedConfiguration) -> None:
    """Update rate limit state after CodeRabbit API usage."""
    
    state_file = os.environ.get("SELF_HEALING_STATE_FILE", ".github/state/rate-limits.json")
    
    if not os.path.exists(state_file):
        return
    
    try:
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        # Increment CodeRabbit request counter
        state_data["coderabbit_requests"] = state_data.get("coderabbit_requests", 0) + 1
        state_data["last_updated"] = datetime.utcnow().isoformat()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
            
    except Exception as exc:
        print(f"Warning: Failed to update rate limit state: {exc}")


def github_request_with_rate_limiting(
    *,
    config: EnhancedConfiguration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None,
    body: dict[str, t.Any] | None = None,
    accepted_status: set[int] | None = None,
) -> t.Any:
    """GitHub request wrapper with enhanced rate limiting."""
    
    # Use the base implementation but with enhanced backoff
    for attempt in range(5):
        try:
            result = base_github_request(
                config=config,
                method=method,
                path=path,
                query=query,
                body=body,
                accepted_status=accepted_status,
            )
            
            # Update rate limit state on successful request
            if method.upper() == "POST" and "coderabbit" in path.lower():
                update_rate_limit_state(config)
            
            return result
            
        except Exception as exc:
            if "rate limit" in str(exc).lower() or "429" in str(exc):
                # Enhanced backoff for rate limiting
                delay = (config.backoff_multiplier ** attempt) * 30  # Start at 30 seconds
                print(f"Rate limit detected, waiting {delay:.1f} seconds...")
                time.sleep(delay)
                continue
            raise
    
    raise RuntimeError("Exhausted retries with rate limiting")


def get_pr_priority_score(pr: PullRequest) -> float:
    """Calculate priority score for a PR based on various factors."""
    
    score = 0.0
    
    # Age factor
    try:
        updated = datetime.fromisoformat(pr.updated_at.replace('Z', '+00:00'))
        age_hours = (datetime.utcnow().replace(tzinfo=updated.tzinfo) - updated).total_seconds() / 3600
        
        # Older PRs get higher priority
        if age_hours > 168:  # 1 week
            score += 10
        elif age_hours > 72:  # 3 days
            score += 5
        elif age_hours > 24:  # 1 day
            score += 3
    except (ValueError, TypeError):
        pass
    
    # Label-based priority
    priority_labels = {
        "status:needs-coderabbit-review": 8,
        "status:needs-cursor-fix": 6,
        "priority:high": 15,
        "priority:critical": 25,
        "bug": 10,
        "security": 20,
    }
    
    for label in pr.labels:
        score += priority_labels.get(label, 0)
    
    # Recent activity bonus
    try:
        updated = datetime.fromisoformat(pr.updated_at.replace('Z', '+00:00'))
        hours_since_update = (datetime.utcnow().replace(tzinfo=updated.tzinfo) - updated).total_seconds() / 3600
        
        if hours_since_update < 2:  # Very recent
            score += 5
        elif hours_since_update < 6:  # Recent
            score += 3
    except (ValueError, TypeError):
        pass
    
    return score


def prioritized_pr_processing(config: EnhancedConfiguration) -> list[dict]:
    """Process PRs in priority order with rate limiting awareness."""
    
    # Get all open PRs
    pulls = github_request_with_rate_limiting(
        config=config,
        method="GET",
        path=f"/repos/{config.owner}/{config.repo}/pulls",
        query={"state": "open", "per_page": 50},
    )
    
    if not pulls:
        return []
    
    # Convert to PullRequest objects and calculate priority
    prs_with_priority = []
    for item in pulls:
        pr = PullRequest(
            number=item["number"],
            title=item["title"],
            head_sha=item["head"]["sha"],
            updated_at=item["updated_at"],
            labels=[label["name"] for label in item.get("labels", [])],
        )
        
        priority_score = get_pr_priority_score(pr)
        prs_with_priority.append((pr, priority_score))
    
    # Sort by priority (highest first)
    prs_with_priority.sort(key=lambda x: x[1], reverse=True)
    
    # Process up to max_coderabbit_requests PRs
    outcomes = []
    processed_count = 0
    
    for pr, priority_score in prs_with_priority:
        if processed_count >= config.max_coderabbit_requests:
            print(f"Reached maximum CodeRabbit requests limit ({config.max_coderabbit_requests})")
            break
        
        print(f"Processing PR #{pr.number} (priority: {priority_score:.1f})")
        
        # Get reviews for this PR
        reviews_data = github_request_with_rate_limiting(
            config=config,
            method="GET",
            path=f"/repos/{config.owner}/{config.repo}/pulls/{pr.number}/reviews",
            query={"per_page": 100},
        )
        
        reviews = [
            Review(
                state=review["state"],
                submitted_at=review.get("submitted_at"),
                commit_id=review["commit_id"],
                reviewer_login=(review.get("user") or {}).get("login", ""),
            )
            for review in (reviews_data or [])
        ]
        
        # Determine follow-up action
        label, reason = choose_follow_up_label(
            pr=pr,
            reviews=reviews,
            coderabbit_logins=config.coderabbit_logins,
        )
        
        # Update labels and comments
        comment_posted = update_labels_and_comment(
            config=config,
            pr=pr,
            new_label=label,
            reason=reason,
        )
        
        # Trigger CodeRabbit if needed (this counts toward rate limit)
        if label == "status:needs-coderabbit-review":
            try:
                trigger_coderabbit_if_needed(
                    config=config,
                    pr_number=pr.number,
                    new_label=label,
                    reason=reason,
                )
                processed_count += 1
            except Exception as exc:
                print(f"Failed to trigger CodeRabbit for PR #{pr.number}: {exc}")
        
        outcomes.append({
            "pr_number": pr.number,
            "priority_score": priority_score,
            "applied_label": label,
            "comment_posted": comment_posted,
            "reason": reason,
        })
        
        # Add small delay between requests
        time.sleep(1)
    
    return outcomes


def main() -> None:
    """Enhanced main entry point."""
    
    config = load_enhanced_configuration()
    
    print(f"🤖 Enhanced CodeRabbit Follow-up")
    print(f"   Priority mode: {config.priority_mode}")
    print(f"   Max requests: {config.max_coderabbit_requests}")
    print(f"   Backoff multiplier: {config.backoff_multiplier}")
    
    # Ensure follow-up labels exist
    try:
        existing_labels = github_request_with_rate_limiting(
            config=config,
            method="GET",
            path=f"/repos/{config.owner}/{config.repo}/labels",
            query={"per_page": 100},
        )
        present = {label["name"] for label in (existing_labels or [])}
        
        for label_name in FOLLOW_UP_LABELS - present:
            github_request_with_rate_limiting(
                config=config,
                method="POST",
                path=f"/repos/{config.owner}/{config.repo}/labels",
                body={
                    "name": label_name,
                    "color": "0e8a16" if "approved" in label_name else "d73a4a",
                    "description": "Enhanced autopilot coordination label",
                },
                accepted_status={201},
            )
    except Exception as exc:
        print(f"Warning: Failed to ensure labels exist: {exc}")
    
    # Process PRs
    if config.pr_number:
        # Single PR mode (backward compatibility)
        print(f"Processing single PR #{config.pr_number}")
        # Fall back to original implementation for single PR
        from coderabbit_follow_up import process_pull_requests
        outcomes = process_pull_requests(config)
    else:
        # Enhanced prioritized processing
        print("Processing PRs in priority order...")
        outcomes = prioritized_pr_processing(config)
    
    # Output results
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "single_pr" if config.pr_number else "prioritized",
        "max_requests": config.max_coderabbit_requests,
        "processed_count": len(outcomes),
        "outcomes": outcomes,
    }
    
    print(f"\\n✅ Enhanced CodeRabbit follow-up complete:")
    print(f"   Processed {len(outcomes)} PR(s)")
    
    if outcomes:
        print("\\n📋 Processing Results:")
        for outcome in outcomes:
            print(f"   PR #{outcome['pr_number']}: {outcome['applied_label']}")
            if 'priority_score' in outcome:
                print(f"      Priority: {outcome['priority_score']:.1f}")
            print(f"      Reason: {outcome['reason']}")
    
    print(f"\\n{json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()