#!/bin/bash

# Test Cursor Agent Dispatch System
# This script helps test the cursor agent dispatch workflow

set -e

echo "🧪 Testing Cursor Agent Dispatch System"

# Check if we have gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is required but not installed"
    exit 1
fi

# Check if we're authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run 'gh auth login'"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# Get current repository info
REPO_INFO=$(gh repo view --json owner,name)
OWNER=$(echo "$REPO_INFO" | jq -r '.owner.login')
REPO=$(echo "$REPO_INFO" | jq -r '.name')

echo "📍 Repository: $OWNER/$REPO"

# Function to create a test PR
create_test_pr() {
    echo "🔧 Creating test branch and PR..."
    
    # Create a test branch
    TEST_BRANCH="test/cursor-dispatch-$(date +%s)"
    git checkout -b "$TEST_BRANCH"
    
    # Create a test Python file with some issues
    cat > test_cursor_agent.py << 'EOF'
import os,sys
import json

def test_function( x,y ):
    """Test function with formatting issues."""
    result=x+y
    
    # TODO: Fix this function
    if result>10:
        print( "Result is greater than 10" )
    else:
        print("Result is less than or equal to 10")
        
    return result


class TestClass:
    def __init__(self,name):
        self.name=name
        
    def get_name( self ):
        return self.name   


if __name__=="__main__":
    test_function(5,7)
EOF
    
    # Create a test markdown file
    cat > TEST_README.md << 'EOF'
# Test Documentation

This is a test file to trigger the cursor agents.

## Issues to Fix
- Inconsistent formatting
- Missing proper spacing
- TODO items need attention


### Python Code Issues
The accompanying Python file has several formatting issues that the cursor agent should fix:
- Import formatting
- Function parameter spacing
- Inconsistent whitespace
- Missing proper line endings
EOF
    
    git add test_cursor_agent.py TEST_README.md
    git commit -m "Add test files to trigger cursor agents

This commit adds test files with intentional formatting issues
to test the cursor agent dispatch system."
    
    git push origin "$TEST_BRANCH"
    
    # Create PR
    PR_URL=$(gh pr create \
        --title "🧪 Test Cursor Agent Dispatch System" \
        --body "This is a test PR to verify the cursor agent dispatch system works correctly.

The PR includes:
- A Python file with formatting issues (should trigger \`agent:python\`)
- A Markdown file with formatting issues (should trigger \`agent:docs\`)

Expected behavior:
1. The cursor-agent-dispatch workflow should classify the files
2. It should apply \`agent:python\` and \`agent:docs\` labels
3. Individual cursor agent workflows should process the files
4. The agents should commit formatting fixes
5. The agent labels should be removed when complete

Manual testing steps:
- [ ] Verify agent labels are applied
- [ ] Verify Python agent applies formatting fixes
- [ ] Verify Docs agent applies formatting fixes
- [ ] Verify labels are removed after processing" \
        --draft)
    
    PR_NUMBER=$(echo "$PR_URL" | sed 's/.*\/pull\///')
    echo "✅ Created test PR #$PR_NUMBER: $PR_URL"
    
    return "$PR_NUMBER"
}

# Function to add test labels
add_test_labels() {
    local pr_number=$1
    echo "🏷️  Adding test labels to PR #$pr_number..."
    
    # Add the status label that should trigger cursor dispatch
    gh pr edit "$pr_number" --add-label "status:needs-cursor-fix"
    
    echo "✅ Added status:needs-cursor-fix label"
}

# Function to monitor PR status
monitor_pr() {
    local pr_number=$1
    echo "👀 Monitoring PR #$pr_number for cursor agent activity..."
    
    for i in {1..10}; do
        echo "🔄 Check $i/10..."
        
        # Get current labels
        LABELS=$(gh pr view "$pr_number" --json labels --jq '.labels[].name' | tr '\n' ', ')
        echo "   Current labels: $LABELS"
        
        # Check for agent labels
        if echo "$LABELS" | grep -q "agent:"; then
            echo "✅ Cursor agents have been dispatched!"
            echo "$LABELS" | grep -o "agent:[^,]*" | sed 's/^/   - /'
        fi
        
        # Check recent comments
        echo "   Recent activity:"
        gh pr view "$pr_number" --json comments --jq '.comments[-2:][].body' | head -3 | sed 's/^/     /'
        
        if [ $i -lt 10 ]; then
            echo "   Waiting 30 seconds..."
            sleep 30
        fi
    done
}

# Function to cleanup test
cleanup_test() {
    local pr_number=$1
    echo "🧹 Cleaning up test PR #$pr_number..."
    
    # Close the PR
    gh pr close "$pr_number" --comment "Test completed - closing PR"
    
    # Switch back to main branch
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || echo "Could not switch to main branch"
    
    # Delete test branch
    TEST_BRANCH=$(git branch --show-current)
    if [[ "$TEST_BRANCH" == test/cursor-dispatch-* ]]; then
        git checkout main 2>/dev/null || git checkout master 2>/dev/null
        git branch -D "$TEST_BRANCH" 2>/dev/null || echo "Could not delete test branch"
        git push origin --delete "$TEST_BRANCH" 2>/dev/null || echo "Could not delete remote test branch"
    fi
    
    # Remove test files if they exist
    rm -f test_cursor_agent.py TEST_README.md
    
    echo "✅ Cleanup complete"
}

# Main execution
case "${1:-}" in
    "create")
        PR_NUMBER=$(create_test_pr)
        add_test_labels "$PR_NUMBER"
        echo ""
        echo "🎯 Test PR created and labeled. You can now:"
        echo "   1. Check the Actions tab for workflow runs"
        echo "   2. Monitor the PR for agent activity with: $0 monitor $PR_NUMBER"
        echo "   3. Clean up when done with: $0 cleanup $PR_NUMBER"
        ;;
    "monitor")
        if [ -z "${2:-}" ]; then
            echo "❌ Usage: $0 monitor <PR_NUMBER>"
            exit 1
        fi
        monitor_pr "$2"
        ;;
    "cleanup")
        if [ -z "${2:-}" ]; then
            echo "❌ Usage: $0 cleanup <PR_NUMBER>"
            exit 1
        fi
        cleanup_test "$2"
        ;;
    "test-workflow")
        echo "🧪 Testing workflow dispatch..."
        # Find a recent PR to test with
        RECENT_PR=$(gh pr list --limit 1 --json number --jq '.[0].number')
        if [ "$RECENT_PR" != "null" ] && [ -n "$RECENT_PR" ]; then
            echo "🔧 Triggering cursor dispatch for PR #$RECENT_PR..."
            gh workflow run cursor-agent-dispatch.yml --field pr_number="$RECENT_PR" --field force_dispatch=true
            echo "✅ Workflow triggered. Check the Actions tab."
        else
            echo "❌ No recent PRs found to test with"
        fi
        ;;
    *)
        echo "🤖 Cursor Agent Dispatch Test Tool"
        echo ""
        echo "Usage:"
        echo "  $0 create          - Create a test PR with files that should trigger cursor agents"
        echo "  $0 monitor <PR>    - Monitor a PR for cursor agent activity"
        echo "  $0 cleanup <PR>    - Clean up a test PR and associated resources"
        echo "  $0 test-workflow   - Test workflow dispatch on a recent PR"
        echo ""
        echo "Example workflow:"
        echo "  $0 create          # Creates test PR"
        echo "  $0 monitor 123     # Monitor PR #123"
        echo "  $0 cleanup 123     # Clean up when done"
        ;;
esac