#!/usr/bin/env python3
"""Deployment validation script for self-healing automation system."""

import json
import os
import sys
from pathlib import Path


def validate_files():
    """Validate all required files are present."""
    required_files = [
        ".github/workflows/self-healing-orchestrator.yml",
        ".github/workflows/coderabbit-follow-up.yml", 
        ".github/workflows/cursor-agent-dispatch.yml",
        "scripts/automation/rate_limiter.py",
        "scripts/automation/pr_discovery.py",
        "scripts/automation/enhanced_coderabbit_followup.py",
        "scripts/automation/claude_auto_repair.py",
        "scripts/automation/enhanced_cursor_dispatch.py",
        "scripts/automation/health_monitor.py",
        "scripts/automation/state_cleanup.py",
        "SELF_HEALING_AUTOMATION.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return missing_files


def validate_permissions():
    """Check that automation scripts are executable."""
    script_files = [
        "scripts/automation/rate_limiter.py",
        "scripts/automation/pr_discovery.py", 
        "scripts/automation/enhanced_coderabbit_followup.py",
        "scripts/automation/claude_auto_repair.py",
        "scripts/automation/enhanced_cursor_dispatch.py",
        "scripts/automation/health_monitor.py",
        "scripts/automation/state_cleanup.py"
    ]
    
    non_executable = []
    for script in script_files:
        path = Path(script)
        if path.exists() and not os.access(path, os.X_OK):
            non_executable.append(script)
    
    return non_executable


def create_initial_state():
    """Create initial state directory and files."""
    state_dir = Path(".github/state")
    state_dir.mkdir(exist_ok=True)
    
    # Create initial rate limit state
    rate_limit_file = state_dir / "rate-limits.json"
    if not rate_limit_file.exists():
        initial_state = {
            "coderabbit_requests": 0,
            "claude_requests": 0,
            "cursor_requests": 0,
            "window_start": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T00:00:00"
        }
        with open(rate_limit_file, 'w') as f:
            json.dump(initial_state, f, indent=2)
    
    return state_dir.exists()


def check_environment_setup():
    """Check recommended environment setup."""
    recommendations = []
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        recommendations.append("⚠️  Not in a git repository - deployment may not work correctly")
    
    # Check if README mentions the automation
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        if "self-healing" not in content.lower():
            recommendations.append("💡 Consider adding self-healing automation info to README.md")
    
    return recommendations


def main():
    """Main validation logic."""
    print("🔍 Validating Self-Healing Automation Deployment")
    print("=" * 50)
    
    # Check required files
    missing_files = validate_files()
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    else:
        print("✅ All required files present")
    
    # Check permissions
    non_executable = validate_permissions()
    if non_executable:
        print("⚠️  Non-executable script files:")
        for script in non_executable:
            print(f"   - {script}")
        print("   Run: chmod +x scripts/automation/*.py")
    else:
        print("✅ All scripts have correct permissions")
    
    # Create initial state
    if create_initial_state():
        print("✅ State directory initialized")
    else:
        print("❌ Failed to create state directory")
        sys.exit(1)
    
    # Environment recommendations
    recommendations = check_environment_setup()
    if recommendations:
        print("\\n📝 Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
    
    # Final summary
    print("\\n🎉 Deployment Validation Complete!")
    print("\\n📋 Next Steps:")
    print("   1. Commit and push all files to GitHub")
    print("   2. Set up required secrets in GitHub repository:")
    print("      - ANTHROPIC_API_KEY (for Claude integration)")
    print("      - SLACK_WEBHOOK_URL (optional)")
    print("      - DISCORD_WEBHOOK_URL (optional)")
    print("   3. Install CodeRabbit GitHub App")
    print("   4. Monitor first workflow runs in Actions tab")
    print("\\n🤖 Your repository will be self-healing within minutes!")


if __name__ == "__main__":
    main()