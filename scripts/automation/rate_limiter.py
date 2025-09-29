#!/usr/bin/env python3
"""Rate limiting manager for self-healing automation.

Tracks API usage across CodeRabbit, Claude, and Cursor to prevent hitting
rate limits while maintaining system responsiveness. Uses GitHub Actions
cache and repository state to persist rate limit counters.
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from urllib import error, parse, request


@dataclass
class RateLimitState:
    """Tracks rate limit usage for each service."""
    
    coderabbit_requests: int = 0
    claude_requests: int = 0
    cursor_requests: int = 0
    window_start: str = ""
    last_updated: str = ""


@dataclass
class RateLimitConfig:
    """Rate limit configuration from environment."""
    
    coderabbit_max_per_hour: int
    claude_max_per_hour: int
    cursor_max_per_hour: int
    github_token: str


def load_config() -> RateLimitConfig:
    """Load rate limit configuration from environment variables."""
    
    return RateLimitConfig(
        coderabbit_max_per_hour=int(os.environ.get("CODERABBIT_MAX_REQUESTS_PER_HOUR", "60")),
        claude_max_per_hour=int(os.environ.get("CLAUDE_MAX_REQUESTS_PER_HOUR", "100")),
        cursor_max_per_hour=int(os.environ.get("CURSOR_MAX_REQUESTS_PER_HOUR", "50")),
        github_token=os.environ.get("GITHUB_TOKEN", ""),
    )


def load_rate_limit_state(config: RateLimitConfig) -> RateLimitState:
    """Load current rate limit state from GitHub repository or initialize new."""
    
    # Try to load from GitHub repository state file
    state_file = os.environ.get("SELF_HEALING_STATE_FILE", ".github/state/rate-limits.json")
    
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
                return RateLimitState(**data)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass  # Fall through to create new state
    
    # Initialize new state
    now = datetime.utcnow()
    return RateLimitState(
        window_start=now.isoformat(),
        last_updated=now.isoformat(),
    )


def save_rate_limit_state(state: RateLimitState, config: RateLimitConfig) -> None:
    """Save rate limit state to repository state file."""
    
    state_file = os.environ.get("SELF_HEALING_STATE_FILE", ".github/state/rate-limits.json")
    state_dir = os.path.dirname(state_file)
    
    # Ensure state directory exists
    os.makedirs(state_dir, exist_ok=True)
    
    # Update timestamp
    state.last_updated = datetime.utcnow().isoformat()
    
    # Save to file
    with open(state_file, 'w') as f:
        json.dump(asdict(state), f, indent=2)


def is_rate_limit_exceeded(
    current_requests: int, 
    max_requests: int, 
    window_start: str,
    service_name: str
) -> tuple[bool, str]:
    """Check if rate limit is exceeded for a service."""
    
    now = datetime.utcnow()
    window_start_dt = datetime.fromisoformat(window_start.replace('Z', '+00:00'))
    
    # Reset window if more than an hour has passed
    if now - window_start_dt > timedelta(hours=1):
        return False, f"{service_name} rate limit window reset"
    
    if current_requests >= max_requests:
        time_until_reset = (window_start_dt + timedelta(hours=1) - now).total_seconds()
        return True, f"{service_name} rate limit exceeded, resets in {int(time_until_reset)}s"
    
    remaining = max_requests - current_requests
    return False, f"{service_name} has {remaining} requests remaining in current window"


def reset_window_if_needed(state: RateLimitState) -> RateLimitState:
    """Reset the rate limit window if an hour has passed."""
    
    now = datetime.utcnow()
    window_start = datetime.fromisoformat(state.window_start.replace('Z', '+00:00'))
    
    if now - window_start > timedelta(hours=1):
        return RateLimitState(
            coderabbit_requests=0,
            claude_requests=0,
            cursor_requests=0,
            window_start=now.isoformat(),
            last_updated=now.isoformat(),
        )
    
    return state


def get_intelligent_schedule_factor() -> float:
    """Return scheduling factor based on time of day and repository activity.
    
    Returns multiplier for rate limits:
    - 1.0 = normal rate limits
    - 0.5 = more conservative (outside business hours)
    - 1.5 = more aggressive (high activity periods)
    """
    
    now = datetime.utcnow()
    
    # More conservative outside business hours (UTC)
    if now.hour < 8 or now.hour > 18:
        return 0.7
    
    # More conservative on weekends
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return 0.6
    
    # More aggressive during peak development hours
    if 10 <= now.hour <= 16:  # 10 AM - 4 PM UTC
        return 1.3
    
    return 1.0


def main() -> None:
    """Main rate limiting check - outputs GitHub Actions variables."""
    
    config = load_config()
    state = load_rate_limit_state(config)
    state = reset_window_if_needed(state)
    
    # Apply intelligent scheduling
    schedule_factor = get_intelligent_schedule_factor()
    
    adjusted_coderabbit_max = int(config.coderabbit_max_per_hour * schedule_factor)
    adjusted_claude_max = int(config.claude_max_per_hour * schedule_factor)
    adjusted_cursor_max = int(config.cursor_max_per_hour * schedule_factor)
    
    # Check rate limits
    coderabbit_exceeded, coderabbit_msg = is_rate_limit_exceeded(
        state.coderabbit_requests, adjusted_coderabbit_max, state.window_start, "CodeRabbit"
    )
    
    claude_exceeded, claude_msg = is_rate_limit_exceeded(
        state.claude_requests, adjusted_claude_max, state.window_start, "Claude"
    )
    
    cursor_exceeded, cursor_msg = is_rate_limit_exceeded(
        state.cursor_requests, adjusted_cursor_max, state.window_start, "Cursor"
    )
    
    # Output GitHub Actions variables
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"coderabbit_ok={'false' if coderabbit_exceeded else 'true'}\\n")
        f.write(f"claude_ok={'false' if claude_exceeded else 'true'}\\n")
        f.write(f"cursor_ok={'false' if cursor_exceeded else 'true'}\\n")
        f.write(f"schedule_factor={schedule_factor}\\n")
    
    # Save updated state
    save_rate_limit_state(state, config)
    
    # Log status
    print(f"🕒 Rate Limit Status (factor: {schedule_factor:.1f})")
    print(f"   CodeRabbit: {coderabbit_msg}")
    print(f"   Claude: {claude_msg}")
    print(f"   Cursor: {cursor_msg}")
    
    # Create summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "window_start": state.window_start,
        "schedule_factor": schedule_factor,
        "limits": {
            "coderabbit": {
                "used": state.coderabbit_requests,
                "max": adjusted_coderabbit_max,
                "available": not coderabbit_exceeded
            },
            "claude": {
                "used": state.claude_requests,
                "max": adjusted_claude_max,
                "available": not claude_exceeded
            },
            "cursor": {
                "used": state.cursor_requests,
                "max": adjusted_cursor_max,
                "available": not cursor_exceeded
            }
        }
    }
    
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()