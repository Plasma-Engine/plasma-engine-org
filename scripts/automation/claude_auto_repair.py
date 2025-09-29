#!/usr/bin/env python3
"""Claude AI Auto-Repair for CodeRabbit Issues.

Analyzes CodeRabbit feedback and automatically generates fixes using Claude AI.
Integrates with GitHub to:
1. Parse CodeRabbit review comments
2. Generate contextual fixes using Claude
3. Create commits with fixes
4. Update PR status and comments

This is the secondary repair mechanism after CodeRabbit identifies issues.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import typing as t
from dataclasses import dataclass
from datetime import datetime
from urllib import error, parse, request


@dataclass
class Configuration:
    """Runtime configuration for Claude auto-repair."""
    
    github_token: str
    anthropic_api_key: str
    repo_owner: str
    repo_name: str
    pr_number: int
    force_repair: bool


@dataclass
class ReviewComment:
    """CodeRabbit review comment to be processed."""
    
    id: int
    body: str
    path: str
    line: int | None
    diff_hunk: str
    created_at: str
    user_login: str


@dataclass
class RepairTask:
    """A single repair task generated from CodeRabbit feedback."""
    
    file_path: str
    original_content: str
    suggested_fix: str
    line_number: int | None
    context: str
    confidence: float


def load_configuration() -> Configuration:
    """Load configuration from environment variables."""
    
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        sys.exit("GITHUB_TOKEN is required")
    
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not anthropic_api_key:
        sys.exit("ANTHROPIC_API_KEY is required")
    
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo_slug or "/" not in repo_slug:
        sys.exit("GITHUB_REPOSITORY must be in format 'owner/repo'")
    
    owner, repo = repo_slug.split("/", 1)
    
    pr_number_str = os.environ.get("INPUT_PR_NUMBER", "")
    if not pr_number_str:
        sys.exit("INPUT_PR_NUMBER is required")
    
    try:
        pr_number = int(pr_number_str)
    except ValueError:
        sys.exit(f"INPUT_PR_NUMBER must be numeric, got: {pr_number_str}")
    
    force_repair = os.environ.get("FORCE_REPAIR", "").lower() in ("true", "1", "yes")
    
    return Configuration(
        github_token=github_token,
        anthropic_api_key=anthropic_api_key,
        repo_owner=owner,
        repo_name=repo,
        pr_number=pr_number,
        force_repair=force_repair
    )


def github_request(
    config: Configuration,
    method: str,
    path: str,
    query: dict[str, t.Any] | None = None,
    body: dict[str, t.Any] | None = None,
    accepted_status: set[int] | None = None
) -> t.Any:
    """Execute GitHub REST API request."""
    
    accepted_status = accepted_status or {200, 201, 202, 204}
    base_url = "https://api.github.com"
    url = parse.urljoin(base_url, path)
    if query:
        url = f"{url}?{parse.urlencode(query)}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config.github_token}",
        "User-Agent": "plasma-engine-claude-repair",
    }
    
    payload: bytes | None = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = request.Request(url, data=payload, method=method.upper(), headers=headers)
    
    try:
        with request.urlopen(req) as response:
            status = response.getcode()
            data = response.read()
            
            if status not in accepted_status:
                raise RuntimeError(f"GitHub API error {status}: {data.decode()}")
            
            if not data:
                return None
            return json.loads(data)
    except error.HTTPError as exc:
        print(f"GitHub API error ({exc.code}): {exc.read().decode()}")
        raise


def get_coderabbit_reviews(config: Configuration) -> list[ReviewComment]:
    """Fetch CodeRabbit review comments from the PR."""
    
    # Get PR reviews
    reviews = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/pulls/{config.pr_number}/reviews"
    ) or []
    
    # Get PR review comments (line-level comments)
    review_comments = github_request(
        config,
        "GET",
        f"/repos/{config.repo_owner}/{config.repo_name}/pulls/{config.pr_number}/comments"
    ) or []
    
    coderabbit_logins = {"coderabbitai[bot]", "coderabbitai"}
    coderabbit_comments = []
    
    # Process review-level comments
    for review in reviews:
        user = review.get("user", {})
        if user.get("login", "").lower() in {login.lower() for login in coderabbit_logins}:
            if review.get("body") and review.get("state") == "CHANGES_REQUESTED":
                coderabbit_comments.append(ReviewComment(
                    id=review["id"],
                    body=review["body"],
                    path="",  # Review-level comment
                    line=None,
                    diff_hunk="",
                    created_at=review["submitted_at"],
                    user_login=user.get("login", "")
                ))
    
    # Process line-level comments
    for comment in review_comments:
        user = comment.get("user", {})
        if user.get("login", "").lower() in {login.lower() for login in coderabbit_logins}:
            coderabbit_comments.append(ReviewComment(
                id=comment["id"],
                body=comment["body"],
                path=comment.get("path", ""),
                line=comment.get("line"),
                diff_hunk=comment.get("diff_hunk", ""),
                created_at=comment["created_at"],
                user_login=user.get("login", "")
            ))
    
    return coderabbit_comments


def should_attempt_repair(config: Configuration, comments: list[ReviewComment]) -> bool:
    """Determine if we should attempt automated repair."""
    
    if config.force_repair:
        return True
    
    if not comments:
        print("No CodeRabbit comments found, skipping repair")
        return False
    
    # Check for recent CodeRabbit activity
    recent_threshold = datetime.utcnow().timestamp() - (2 * 3600)  # 2 hours
    recent_comments = [
        c for c in comments
        if datetime.fromisoformat(c.created_at.replace('Z', '+00:00')).timestamp() > recent_threshold
    ]
    
    if not recent_comments:
        print("No recent CodeRabbit comments, skipping repair")
        return False
    
    # Check for explicit repair requests or changes requested
    repair_indicators = [
        "fix", "correct", "change", "update", "modify", 
        "remove", "add", "refactor", "improve"
    ]
    
    has_actionable_feedback = False
    for comment in recent_comments:
        body_lower = comment.body.lower()
        if any(indicator in body_lower for indicator in repair_indicators):
            has_actionable_feedback = True
            break
    
    return has_actionable_feedback


def call_claude_api(
    config: Configuration,
    system_prompt: str,
    user_prompt: str
) -> str | None:
    """Call Claude API for code analysis and repair."""
    
    # Using direct HTTP request to Anthropic API
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config.anthropic_api_key,
        "anthropic-version": "2023-06-01"
    }
    
    body = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 4000,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }
    
    payload = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=payload, headers=headers, method="POST")
    
    try:
        with request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get("content", [{}])[0].get("text", "")
    except error.HTTPError as exc:
        print(f"Claude API error ({exc.code}): {exc.read().decode()}")
        return None
    except Exception as exc:
        print(f"Claude API error: {exc}")
        return None


def generate_repair_tasks(
    config: Configuration,
    comments: list[ReviewComment]
) -> list[RepairTask]:
    """Generate repair tasks using Claude AI."""
    
    repair_tasks = []
    
    # Group comments by file
    comments_by_file = {}
    for comment in comments:
        if comment.path:
            if comment.path not in comments_by_file:
                comments_by_file[comment.path] = []
            comments_by_file[comment.path].append(comment)
    
    # Process each file
    for file_path, file_comments in comments_by_file.items():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
        except Exception as exc:
            print(f"Error reading {file_path}: {exc}")
            continue
        
        # Prepare Claude prompt
        system_prompt = """You are an expert software engineer helping to fix code issues identified by CodeRabbit.

Your task is to:
1. Analyze the CodeRabbit feedback
2. Understand the current code
3. Provide specific, minimal fixes that address the issues
4. Ensure the fixes maintain code quality and functionality

Return your response in JSON format with the following structure:
{
  "confidence": 0.8,
  "suggested_fix": "the exact code to replace the problematic section",
  "explanation": "brief explanation of the fix",
  "line_range": [start_line, end_line]
}

If you cannot provide a confident fix, set confidence to 0.0."""
        
        comment_summaries = []
        for comment in file_comments:
            comment_summaries.append(f"Line {comment.line}: {comment.body}")
        
        user_prompt = f"""File: {file_path}

CodeRabbit Feedback:
{chr(10).join(comment_summaries)}

Current File Content:
```
{file_content}
```

Please analyze the feedback and provide fixes for the identified issues."""
        
        claude_response = call_claude_api(config, system_prompt, user_prompt)
        if not claude_response:
            print(f"Failed to get Claude response for {file_path}")
            continue
        
        # Parse Claude response
        try:
            fix_data = json.loads(claude_response)
            confidence = fix_data.get("confidence", 0.0)
            
            if confidence >= 0.6:  # Only apply high-confidence fixes
                repair_tasks.append(RepairTask(
                    file_path=file_path,
                    original_content=file_content,
                    suggested_fix=fix_data.get("suggested_fix", ""),
                    line_number=fix_data.get("line_range", [None])[0],
                    context=fix_data.get("explanation", ""),
                    confidence=confidence
                ))
            else:
                print(f"Low confidence fix for {file_path}, skipping (confidence: {confidence})")
                
        except json.JSONDecodeError:
            print(f"Failed to parse Claude response for {file_path}")
            continue
    
    return repair_tasks


def apply_repairs(config: Configuration, repair_tasks: list[RepairTask]) -> bool:
    """Apply the generated repairs to the files."""
    
    if not repair_tasks:
        print("No repair tasks to apply")
        return False
    
    applied_repairs = []
    
    for task in repair_tasks:
        print(f"Applying repair to {task.file_path} (confidence: {task.confidence:.1f})")
        print(f"Context: {task.context}")
        
        try:
            # For now, create a simple replacement
            # In a more sophisticated version, we'd do precise line-based replacements
            with open(task.file_path, 'w') as f:
                f.write(task.suggested_fix)
            
            applied_repairs.append(task)
            
        except Exception as exc:
            print(f"Failed to apply repair to {task.file_path}: {exc}")
            continue
    
    if not applied_repairs:
        return False
    
    # Commit the changes
    try:
        # Configure git
        subprocess.run(["git", "config", "user.name", "Claude Auto-Repair Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "claude-repair@plasma-engine.org"], check=True)
        
        # Add all changed files
        for task in applied_repairs:
            subprocess.run(["git", "add", task.file_path], check=True)
        
        # Create commit message
        commit_message = f"🤖 Claude auto-repair: Fix {len(applied_repairs)} issue(s)\\n\\n"
        for i, task in enumerate(applied_repairs, 1):
            commit_message += f"{i}. {task.file_path}: {task.context}\\n"
        commit_message += "\\nGenerated by Claude AI based on CodeRabbit feedback"
        
        # Commit changes
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Committed {len(applied_repairs)} repair(s)")
            return True
        else:
            print(f"Failed to commit repairs: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as exc:
        print(f"Git operation failed: {exc}")
        return False


def update_pr_status(config: Configuration, repair_attempted: bool, repair_count: int) -> None:
    """Update PR with repair status."""
    
    if repair_attempted and repair_count > 0:
        comment_body = f"""🤖 **Claude Auto-Repair Complete**

Applied **{repair_count}** automated fix(es) based on CodeRabbit feedback.

The changes have been committed to this PR. Please review the fixes and trigger a new CodeRabbit review if needed.

*Generated by Claude AI Auto-Repair System*"""
        
        # Add comment to PR
        github_request(
            config,
            "POST",
            f"/repos/{config.repo_owner}/{config.repo_name}/issues/{config.pr_number}/comments",
            body={"body": comment_body}
        )
        
        # Update labels
        # Remove needs-claude-repair, add needs-coderabbit-review
        labels_to_remove = ["status:needs-claude-repair"]
        labels_to_add = ["status:needs-coderabbit-review", "claude:auto-repaired"]
        
        # Remove old labels
        for label in labels_to_remove:
            try:
                github_request(
                    config,
                    "DELETE",
                    f"/repos/{config.repo_owner}/{config.repo_name}/issues/{config.pr_number}/labels/{parse.quote(label)}",
                    accepted_status={200, 204, 404}
                )
            except:
                pass  # Label might not exist
        
        # Add new labels
        if labels_to_add:
            github_request(
                config,
                "POST",
                f"/repos/{config.repo_owner}/{config.repo_name}/issues/{config.pr_number}/labels",
                body={"labels": labels_to_add}
            )
    
    elif repair_attempted:
        comment_body = """🤖 **Claude Auto-Repair Attempted**

Attempted automated repair based on CodeRabbit feedback, but no high-confidence fixes were generated.

The issues may require manual intervention or the feedback may be too complex for automated repair.

*Generated by Claude AI Auto-Repair System*"""
        
        github_request(
            config,
            "POST",
            f"/repos/{config.repo_owner}/{config.repo_name}/issues/{config.pr_number}/comments",
            body={"body": comment_body}
        )


def main() -> None:
    """Main Claude auto-repair logic."""
    
    config = load_configuration()
    
    print(f"🔧 Claude Auto-Repair for PR #{config.pr_number}")
    
    # Fetch CodeRabbit comments
    coderabbit_comments = get_coderabbit_reviews(config)
    print(f"Found {len(coderabbit_comments)} CodeRabbit comment(s)")
    
    # Check if we should attempt repair
    if not should_attempt_repair(config, coderabbit_comments):
        print("Skipping auto-repair (no actionable feedback)")
        return
    
    print("Attempting automated repair...")
    
    # Generate repair tasks using Claude
    repair_tasks = generate_repair_tasks(config, coderabbit_comments)
    print(f"Generated {len(repair_tasks)} repair task(s)")
    
    # Apply repairs
    repair_successful = False
    if repair_tasks:
        repair_successful = apply_repairs(config, repair_tasks)
    
    # Update PR status
    update_pr_status(config, True, len(repair_tasks) if repair_successful else 0)
    
    print(f"✅ Claude auto-repair complete: {len(repair_tasks) if repair_successful else 0} repair(s) applied")


if __name__ == "__main__":
    main()