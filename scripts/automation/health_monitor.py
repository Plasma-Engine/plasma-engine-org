#!/usr/bin/env python3
"""Health Monitor and Escalation System.

Monitors the health of the self-healing automation system and escalates
issues when the automation fails or gets stuck. Provides notifications
via Slack, Discord, and GitHub issues.
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib import request, error, parse


@dataclass
class HealthMetrics:
    """System health metrics."""
    
    total_prs_processed: int = 0
    coderabbit_success_rate: float = 0.0
    claude_repair_success_rate: float = 0.0
    cursor_dispatch_success_rate: float = 0.0
    stuck_prs: list[int] = None
    rate_limit_hits: int = 0
    error_count: int = 0
    last_successful_run: str = ""


@dataclass
class Configuration:
    """Health monitor configuration."""
    
    github_token: str
    repo_owner: str
    repo_name: str
    slack_webhook_url: str = ""
    discord_webhook_url: str = ""


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
        slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL", ""),
        discord_webhook_url=os.environ.get("DISCORD_WEBHOOK_URL", ""),
    )


def github_request(
    config: Configuration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None,
    body: dict[str, t.Any] | None = None
) -> t.Any:
    """Execute GitHub REST API request."""
    
    base_url = "https://api.github.com"
    url = parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{parse.urlencode(query)}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config.github_token}",
        "User-Agent": "plasma-engine-health-monitor",
    }
    
    payload: bytes | None = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = request.Request(url, data=payload, method=method.upper(), headers=headers)
    
    try:
        with request.urlopen(req) as response:
            data = response.read()
            if not data:
                return None
            return json.loads(data)
    except error.HTTPError as exc:
        print(f"GitHub API error ({exc.code}): {exc.read().decode()}")
        return None


def analyze_pr_health(config: Configuration) -> tuple[list[int], dict[str, t.Any]]:
    """Analyze PR health and identify stuck PRs."""
    
    # Get all open PRs
    pulls = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/pulls",
        {"state": "open", "per_page": 100}
    ) or []
    
    stuck_prs = []
    status_counts = {
        "needs-coderabbit-review": 0,
        "needs-cursor-fix": 0,
        "needs-claude-repair": 0,
        "coderabbit-approved": 0,
        "no-status": 0,
    }
    
    # Analyze each PR
    for pr in pulls:
        labels = [label["name"] for label in pr.get("labels", [])]
        updated_at = pr["updated_at"]
        
        # Check if PR is stuck (no updates in 48+ hours with pending status)
        try:
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            hours_since_update = (datetime.utcnow().replace(tzinfo=updated.tzinfo) - updated).total_seconds() / 3600
            
            pending_labels = ["status:needs-coderabbit-review", "status:needs-cursor-fix", "status:needs-claude-repair"]
            has_pending_status = any(label in labels for label in pending_labels)
            
            if hours_since_update > 48 and has_pending_status:
                stuck_prs.append(pr["number"])
        except (ValueError, TypeError):
            pass
        
        # Count status labels
        if "status:needs-coderabbit-review" in labels:
            status_counts["needs-coderabbit-review"] += 1
        elif "status:needs-cursor-fix" in labels:
            status_counts["needs-cursor-fix"] += 1
        elif "status:needs-claude-repair" in labels:
            status_counts["needs-claude-repair"] += 1
        elif "status:coderabbit-approved" in labels:
            status_counts["coderabbit-approved"] += 1
        else:
            status_counts["no-status"] += 1
    
    analysis = {
        "total_open_prs": len(pulls),
        "status_distribution": status_counts,
        "stuck_prs_count": len(stuck_prs),
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    return stuck_prs, analysis


def analyze_workflow_runs(config: Configuration) -> dict[str, t.Any]:
    """Analyze recent workflow runs for success/failure rates."""
    
    # Get recent workflow runs
    workflow_runs = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/actions/runs",
        {
            "created": f">={(datetime.utcnow() - timedelta(hours=24)).isoformat()}",
            "per_page": 50
        }
    ) or {}
    
    runs = workflow_runs.get("workflow_runs", [])
    
    # Analyze by workflow name
    workflow_stats = {}
    for run in runs:
        workflow_name = run.get("name", "unknown")
        conclusion = run.get("conclusion", "unknown")
        
        if workflow_name not in workflow_stats:
            workflow_stats[workflow_name] = {
                "total": 0,
                "success": 0,
                "failure": 0,
                "cancelled": 0,
                "in_progress": 0
            }
        
        workflow_stats[workflow_name]["total"] += 1
        
        if conclusion == "success":
            workflow_stats[workflow_name]["success"] += 1
        elif conclusion == "failure":
            workflow_stats[workflow_name]["failure"] += 1
        elif conclusion == "cancelled":
            workflow_stats[workflow_name]["cancelled"] += 1
        elif run.get("status") == "in_progress":
            workflow_stats[workflow_name]["in_progress"] += 1
    
    # Calculate success rates
    for workflow_name, stats in workflow_stats.items():
        if stats["total"] > 0:
            stats["success_rate"] = stats["success"] / stats["total"]
        else:
            stats["success_rate"] = 0.0
    
    return {
        "workflow_stats": workflow_stats,
        "total_runs": len(runs),
        "analysis_period": "24 hours",
        "timestamp": datetime.utcnow().isoformat(),
    }


def load_health_history() -> list[dict]:
    """Load health monitoring history from state file."""
    
    state_file = ".github/state/health-history.json"
    
    if not os.path.exists(state_file):
        return []
    
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_health_record(metrics: HealthMetrics, pr_analysis: dict, workflow_analysis: dict) -> None:
    """Save current health record to history."""
    
    state_file = ".github/state/health-history.json"
    state_dir = os.path.dirname(state_file)
    
    # Ensure directory exists
    os.makedirs(state_dir, exist_ok=True)
    
    # Load existing history
    history = load_health_history()
    
    # Add new record
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": asdict(metrics),
        "pr_analysis": pr_analysis,
        "workflow_analysis": workflow_analysis,
    }
    
    history.append(record)
    
    # Keep only last 168 records (1 week at hourly intervals)
    history = history[-168:]
    
    # Save back
    with open(state_file, 'w') as f:
        json.dump(history, f, indent=2)


def send_slack_notification(webhook_url: str, message: dict) -> bool:
    """Send notification to Slack."""
    
    if not webhook_url:
        return False
    
    payload = json.dumps(message).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with request.urlopen(req) as response:
            return response.getcode() == 200
    except Exception as exc:
        print(f"Failed to send Slack notification: {exc}")
        return False


def send_discord_notification(webhook_url: str, message: dict) -> bool:
    """Send notification to Discord."""
    
    if not webhook_url:
        return False
    
    payload = json.dumps(message).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with request.urlopen(req) as response:
            return response.getcode() in {200, 204}
    except Exception as exc:
        print(f"Failed to send Discord notification: {exc}")
        return False


def create_github_issue(config: Configuration, title: str, body: str, labels: list[str]) -> bool:
    """Create a GitHub issue for escalation."""
    
    issue_data = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    
    result = github_request(
        config,
        "POST",
        f"/repos/{config.repo_owner}/{config.repo_name}/issues",
        body=issue_data
    )
    
    return result is not None


def check_health_thresholds(
    metrics: HealthMetrics,
    pr_analysis: dict,
    workflow_analysis: dict
) -> list[dict[str, str]]:
    """Check if any health thresholds are breached."""
    
    alerts = []
    
    # Check for stuck PRs
    stuck_count = pr_analysis.get("stuck_prs_count", 0)
    if stuck_count > 3:
        alerts.append({
            "level": "warning",
            "type": "stuck_prs",
            "message": f"{stuck_count} PRs have been stuck for more than 48 hours",
            "details": f"Total open PRs: {pr_analysis.get('total_open_prs', 0)}"
        })
    
    # Check workflow success rates
    workflow_stats = workflow_analysis.get("workflow_stats", {})
    for workflow_name, stats in workflow_stats.items():
        success_rate = stats.get("success_rate", 0.0)
        if success_rate < 0.7 and stats.get("total", 0) >= 3:  # At least 3 runs
            alerts.append({
                "level": "error",
                "type": "workflow_failure",
                "message": f"Workflow '{workflow_name}' has low success rate: {success_rate:.1%}",
                "details": f"Success: {stats.get('success', 0)}, Failures: {stats.get('failure', 0)}"
            })
    
    # Check for rate limiting issues
    if metrics.rate_limit_hits > 10:
        alerts.append({
            "level": "warning",
            "type": "rate_limiting",
            "message": f"High rate limit hits: {metrics.rate_limit_hits}",
            "details": "Consider adjusting request frequency"
        })
    
    # Check for high error count
    if metrics.error_count > 5:
        alerts.append({
            "level": "error",
            "type": "high_errors",
            "message": f"High error count: {metrics.error_count}",
            "details": "Review logs for recurring issues"
        })
    
    return alerts


def escalate_alerts(config: Configuration, alerts: list[dict], metrics: HealthMetrics) -> None:
    """Escalate alerts through various channels."""
    
    if not alerts:
        return
    
    # Prepare summary
    error_alerts = [a for a in alerts if a["level"] == "error"]
    warning_alerts = [a for a in alerts if a["level"] == "warning"]
    
    summary = f"""🚨 **Self-Healing System Health Alert**

**Repository:** {config.repo_owner}/{config.repo_name}
**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

**Alerts Summary:**
• {len(error_alerts)} error(s)
• {len(warning_alerts)} warning(s)

**Error Alerts:**
"""
    
    for alert in error_alerts:
        summary += f"❌ **{alert['type']}**: {alert['message']}\\n   {alert['details']}\\n"
    
    summary += "\\n**Warning Alerts:**\\n"
    for alert in warning_alerts:
        summary += f"⚠️ **{alert['type']}**: {alert['message']}\\n   {alert['details']}\\n"
    
    # Send Slack notification
    if config.slack_webhook_url:
        slack_message = {
            "text": "Self-Healing System Alert",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Self-Healing System Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary
                    }
                }
            ]
        }
        send_slack_notification(config.slack_webhook_url, slack_message)
    
    # Send Discord notification
    if config.discord_webhook_url:
        discord_message = {
            "content": summary[:2000],  # Discord has a 2000 char limit
            "embeds": [
                {
                    "title": "Self-Healing System Health Alert",
                    "color": 0xff0000 if error_alerts else 0xffff00,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fields": [
                        {
                            "name": "Repository",
                            "value": f"{config.repo_owner}/{config.repo_name}",
                            "inline": True
                        },
                        {
                            "name": "Errors",
                            "value": str(len(error_alerts)),
                            "inline": True
                        },
                        {
                            "name": "Warnings",
                            "value": str(len(warning_alerts)),
                            "inline": True
                        }
                    ]
                }
            ]
        }
        send_discord_notification(config.discord_webhook_url, discord_message)
    
    # Create GitHub issue for critical errors
    critical_errors = [a for a in error_alerts if a["type"] in ["workflow_failure", "high_errors"]]
    if critical_errors:
        issue_title = f"🚨 Self-Healing System Alert: {len(critical_errors)} critical issue(s)"
        issue_body = f"""# Self-Healing System Health Alert

**Timestamp:** {datetime.utcnow().isoformat()}

## Critical Issues

"""
        for alert in critical_errors:
            issue_body += f"### {alert['type']}\n{alert['message']}\n\n**Details:** {alert['details']}\n\n"
        
        issue_body += """
## Next Steps

1. Review the workflow logs for the failing runs
2. Check rate limiting configuration
3. Verify API credentials and permissions
4. Consider temporary adjustment of automation frequency

This issue was automatically created by the health monitoring system.
"""
        
        create_github_issue(
            config,
            issue_title,
            issue_body,
            ["bug", "automation", "critical", "health-alert"]
        )


def main() -> None:
    """Main health monitoring logic."""
    
    config = load_configuration()
    
    print("🏥 Self-Healing System Health Monitor")
    
    # Analyze PR health
    stuck_prs, pr_analysis = analyze_pr_health(config)
    print(f"   PR Analysis: {pr_analysis['total_open_prs']} open, {len(stuck_prs)} stuck")
    
    # Analyze workflow health
    workflow_analysis = analyze_workflow_runs(config)
    total_runs = workflow_analysis.get("total_runs", 0)
    print(f"   Workflow Analysis: {total_runs} runs in last 24h")
    
    # Create health metrics
    metrics = HealthMetrics(
        total_prs_processed=pr_analysis["total_open_prs"],
        stuck_prs=stuck_prs or [],
        last_successful_run=datetime.utcnow().isoformat(),
    )
    
    # Calculate success rates from workflow stats
    workflow_stats = workflow_analysis.get("workflow_stats", {})
    if "Self-Healing Repository Orchestrator" in workflow_stats:
        orchestrator_stats = workflow_stats["Self-Healing Repository Orchestrator"]
        metrics.coderabbit_success_rate = orchestrator_stats.get("success_rate", 0.0)
    
    # Save health record
    save_health_record(metrics, pr_analysis, workflow_analysis)
    
    # Check for health threshold breaches
    alerts = check_health_thresholds(metrics, pr_analysis, workflow_analysis)
    
    if alerts:
        print(f"   ⚠️ {len(alerts)} alert(s) detected")
        escalate_alerts(config, alerts, metrics)
    else:
        print("   ✅ All health checks passed")
    
    # Output summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "health_status": "unhealthy" if alerts else "healthy",
        "alerts_count": len(alerts),
        "metrics": asdict(metrics),
        "pr_analysis": pr_analysis,
        "workflow_analysis": workflow_analysis,
    }
    
    print(f"\\n{json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()