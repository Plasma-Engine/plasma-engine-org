#!/usr/bin/env python3
"""Enhanced Cursor Agent Dispatch System.

Enhanced version of cursor_dispatch.py that integrates better with the
self-healing automation system and provides more intelligent fallback
behavior when CodeRabbit and Claude fail to resolve issues.
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
from cursor_dispatch import (
    Configuration as BaseConfiguration,
    PRFile,
    load_configuration as base_load_configuration,
    github_request as base_github_request,
    list_changed_files,
    get_current_labels,
    default_classifier,
    AGENT_LABELS,
)


@dataclass
class EnhancedConfiguration(BaseConfiguration):
    """Enhanced configuration with additional options."""
    
    fallback_mode: bool = False
    max_retry_attempts: int = 3
    escalation_threshold_hours: int = 48


def load_enhanced_configuration() -> EnhancedConfiguration:
    """Load enhanced configuration from environment."""
    
    # Start with base configuration
    base_config = base_load_configuration()
    
    # Enhanced options
    fallback_mode = os.environ.get("CURSOR_FALLBACK_MODE", "").lower() in ("true", "1", "yes")
    max_retry_attempts = int(os.environ.get("MAX_RETRY_ATTEMPTS", "3"))
    escalation_threshold = int(os.environ.get("ESCALATION_THRESHOLD_HOURS", "48"))
    
    return EnhancedConfiguration(
        owner=base_config.owner,
        repo=base_config.repo,
        token=base_config.token,
        pr_number=base_config.pr_number,
        classifier_override=base_config.classifier_override,
        fallback_mode=fallback_mode,
        max_retry_attempts=max_retry_attempts,
        escalation_threshold_hours=escalation_threshold,
    )


def should_trigger_cursor_agents(config: EnhancedConfiguration, pr_labels: list[str]) -> tuple[bool, str]:
    """Determine if Cursor agents should be triggered for this PR."""
    
    # Check for explicit cursor dispatch request
    if "status:needs-cursor-fix" in pr_labels:
        return True, "CodeRabbit requested changes that need Cursor agent attention"
    
    # Check for Claude repair failure
    if "claude:repair-failed" in pr_labels:
        return True, "Claude auto-repair failed, escalating to Cursor agents"
    
    # Check for stuck PR in fallback mode
    if config.fallback_mode and "status:stuck" in pr_labels:
        return True, "PR appears stuck, attempting Cursor agent intervention"
    
    # Check for high-priority issues that need immediate attention
    priority_labels = ["priority:critical", "priority:high", "security", "bug"]
    if any(label in pr_labels for label in priority_labels):
        return True, f"High-priority PR with labels: {[l for l in priority_labels if l in pr_labels]}"
    
    return False, "No conditions met for Cursor agent dispatch"


def analyze_pr_complexity(files: list[PRFile]) -> dict[str, t.Any]:
    """Analyze PR complexity to determine appropriate Cursor agent strategy."""
    
    total_changes = sum(f.additions + f.deletions for f in files)
    file_count = len(files)
    
    # Categorize by file types
    file_types = {}
    for f in files:
        ext = f.filename.split('.')[-1].lower() if '.' in f.filename else 'unknown'
        file_types[ext] = file_types.get(ext, 0) + 1
    
    # Determine complexity
    complexity = "low"
    if total_changes > 500 or file_count > 10:
        complexity = "high"
    elif total_changes > 100 or file_count > 5:
        complexity = "medium"
    
    return {
        "total_changes": total_changes,
        "file_count": file_count,
        "file_types": file_types,
        "complexity": complexity,
        "recommended_agents": _recommend_agents_for_complexity(complexity, file_types),
    }


def _recommend_agents_for_complexity(complexity: str, file_types: dict) -> list[str]:
    """Recommend specific agents based on complexity and file types."""
    
    agents = []
    
    # Add agents based on file types
    if any(ext in file_types for ext in ['py', 'pyi']):
        agents.append("agent:python")
    
    if any(ext in file_types for ext in ['ts', 'tsx', 'js', 'jsx']):
        agents.append("agent:javascript")
    
    if any(ext in file_types for ext in ['tf', 'tfvars']):
        agents.append("agent:infra")
    
    if any(ext in file_types for ext in ['md', 'rst', 'txt']):
        agents.append("agent:docs")
    
    # Add general agent for high complexity or mixed file types
    if complexity == "high" or len(file_types) > 3:
        agents.append("agent:general")
    
    # Ensure at least one agent is assigned
    if not agents:
        agents.append("agent:general")
    
    return agents


def enhanced_agent_classification(
    config: EnhancedConfiguration,
    files: list[PRFile],
    pr_labels: list[str]
) -> set[str]:
    """Enhanced agent classification with context awareness."""
    
    # Start with default classification
    all_labels = set()
    for file in files:
        labels = default_classifier(file.filename)
        all_labels.update(labels)
    
    # Apply overrides from configuration
    for file in files:
        for prefix, label in config.classifier_override.items():
            if file.filename.startswith(prefix):
                all_labels.discard("agent:general")  # Remove general if we have specific
                all_labels.add(label)
                break
    
    # Analyze complexity for additional context
    complexity_analysis = analyze_pr_complexity(files)
    recommended_agents = complexity_analysis.get("recommended_agents", [])
    
    # Add recommended agents based on complexity
    for agent in recommended_agents:
        if agent not in all_labels:
            all_labels.add(agent)
    
    # Special handling for security issues
    if any(label in pr_labels for label in ["security", "vulnerability", "cve"]):
        all_labels.add("agent:security")
    
    # Special handling for operational issues
    if any(label in pr_labels for label in ["ops", "deployment", "infrastructure"]):
        all_labels.add("agent:ops")
    
    # Remove general agent if we have specific agents (unless complexity is high)
    if len(all_labels) > 1 and "agent:general" in all_labels and complexity_analysis.get("complexity") != "high":
        all_labels.discard("agent:general")
    
    return all_labels


def update_rate_limit_state(config: EnhancedConfiguration) -> None:
    """Update rate limit state after Cursor API usage."""
    
    state_file = os.environ.get("SELF_HEALING_STATE_FILE", ".github/state/rate-limits.json")
    
    if not os.path.exists(state_file):
        return
    
    try:
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        # Increment Cursor request counter
        state_data["cursor_requests"] = state_data.get("cursor_requests", 0) + 1
        state_data["last_updated"] = datetime.utcnow().isoformat()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
            
    except Exception as exc:
        print(f"Warning: Failed to update rate limit state: {exc}")


def create_enhanced_dispatch_comment(
    config: EnhancedConfiguration,
    labels: set[str],
    complexity_analysis: dict,
    dispatch_reason: str
) -> dict[str, t.Any]:
    """Create enhanced dispatch comment with more context."""
    
    markdown_lines = [
        "🤖 **Enhanced Cursor Agent Dispatch**",
        "",
        f"**Dispatch Reason:** {dispatch_reason}",
        "",
        "## Complexity Analysis",
        f"- **Total Changes:** {complexity_analysis.get('total_changes', 0):,}",
        f"- **Files Changed:** {complexity_analysis.get('file_count', 0)}",
        f"- **Complexity:** {complexity_analysis.get('complexity', 'unknown').title()}",
        "",
        "## File Types",
    ]
    
    file_types = complexity_analysis.get('file_types', {})
    for ext, count in sorted(file_types.items()):
        markdown_lines.append(f"- **{ext}:** {count} file(s)")
    
    markdown_lines.extend([
        "",
        "## Active Cursor Agents",
        f"**Assigned Labels:** {', '.join(f'`{label}`' for label in sorted(labels))}",
        "",
        "### Next Steps",
        "1. Cursor agents will analyze the changes and PR context",
        "2. Agents will apply specialized fixes based on their domain expertise", 
        "3. Changes will be committed and the PR will be updated",
        "4. If issues persist, the PR will be escalated for manual review",
        "",
        "*This dispatch was generated by the Enhanced Cursor Agent System*"
    ])
    
    return {"body": "\\n".join(markdown_lines)}


def post_enhanced_dispatch_comment(
    config: EnhancedConfiguration,
    labels: set[str],
    complexity_analysis: dict,
    dispatch_reason: str
) -> None:
    """Post enhanced dispatch comment to PR."""
    
    comment_data = create_enhanced_dispatch_comment(
        config, labels, complexity_analysis, dispatch_reason
    )
    
    try:
        base_github_request(
            config=config,
            method="POST",
            path=f"/repos/{config.owner}/{config.repo}/issues/{config.pr_number}/comments",
            body=comment_data,
            accepted_status={201}
        )
        update_rate_limit_state(config)
    except Exception as exc:
        print(f"Failed to post enhanced dispatch comment: {exc}")


def main() -> None:
    """Enhanced Cursor dispatch main logic."""
    
    config = load_enhanced_configuration()
    
    print(f"🔧 Enhanced Cursor Agent Dispatch for PR #{config.pr_number}")
    print(f"   Fallback mode: {config.fallback_mode}")
    print(f"   Max retry attempts: {config.max_retry_attempts}")
    
    # Get current PR labels and files
    current_labels = get_current_labels(config)
    files = list_changed_files(config)
    
    print(f"   Found {len(files)} changed file(s)")
    print(f"   Current labels: {', '.join(current_labels) if current_labels else 'None'}")
    
    # Check if we should trigger Cursor agents
    should_dispatch, reason = should_trigger_cursor_agents(config, list(current_labels))
    
    if not should_dispatch:
        print(f"   Skipping dispatch: {reason}")
        return
    
    print(f"   Dispatching agents: {reason}")
    
    # Analyze PR complexity
    complexity_analysis = analyze_pr_complexity(files)
    print(f"   Complexity: {complexity_analysis['complexity']} ({complexity_analysis['total_changes']} changes)")
    
    # Classify files and determine agents
    agent_labels = enhanced_agent_classification(config, files, list(current_labels))
    
    if not agent_labels:
        agent_labels = {"agent:general"}
    
    print(f"   Assigned agents: {', '.join(sorted(agent_labels))}")
    
    # Update PR labels (this is similar to the original but with enhanced logic)
    from cursor_dispatch import replace_agent_labels
    
    try:
        changed = replace_agent_labels(
            config=config,
            current_labels=current_labels,
            desired_labels=agent_labels
        )
        
        if changed:
            print("   ✅ Updated PR labels successfully")
        else:
            print("   📋 No label changes needed")
            
    except Exception as exc:
        print(f"   ❌ Failed to update labels: {exc}")
        return
    
    # Post enhanced dispatch comment
    post_enhanced_dispatch_comment(config, agent_labels, complexity_analysis, reason)
    
    # Create summary output
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "pr_number": config.pr_number,
        "dispatch_reason": reason,
        "assigned_agents": sorted(agent_labels),
        "complexity_analysis": complexity_analysis,
        "labels_changed": changed if 'changed' in locals() else False,
        "mode": "fallback" if config.fallback_mode else "standard",
    }
    
    print(f"\\n✅ Enhanced Cursor dispatch complete:")
    print(f"   Agents assigned: {len(agent_labels)}")
    print(f"   Complexity: {complexity_analysis['complexity']}")
    print(f"   Labels updated: {'Yes' if changed else 'No'}")
    
    print(f"\\n{json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()