# Self-Healing GitHub Repository Automation

## Overview

This repository features a comprehensive self-healing automation system that integrates **CodeRabbit**, **Claude AI**, and **Cursor agents** to create a truly autonomous development workflow. The system automatically reviews code, fixes issues, and maintains repository health with minimal human intervention.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CodeRabbit    │ ───▶│   Claude AI     │ ───▶│ Cursor Agents   │
│   (Review)      │    │   (Auto-Repair) │    │   (Fallback)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Health Monitor & Escalation System                │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. **Self-Healing Orchestrator** (`self-healing-orchestrator.yml`)
- Master workflow that coordinates all automation
- Intelligent scheduling based on time of day and repository activity
- Rate-limit aware execution with dynamic throttling
- Parallel processing with safety limits

### 2. **CodeRabbit Integration** (Primary Review)
- Automated PR review and feedback
- Intelligent re-review triggering
- Rate-limit management (60 requests/hour by default)
- Priority-based PR processing

### 3. **Claude AI Auto-Repair** (Secondary Intervention)
- Analyzes CodeRabbit feedback
- Generates and applies automated fixes
- High-confidence threshold filtering (60%+)
- Automated commit generation

### 4. **Cursor Agent Dispatch** (Tertiary Fallback)
- Specialized agents for different file types:
  - `agent:python` - Python-specific fixes
  - `agent:javascript` - JS/TS-specific fixes
  - `agent:infra` - Infrastructure/Terraform
  - `agent:docs` - Documentation updates
  - `agent:security` - Security-related fixes
  - `agent:ops` - Operations/deployment issues
  - `agent:general` - General-purpose fixes

### 5. **Health Monitoring System**
- Continuous system health tracking
- Automatic issue escalation
- Slack/Discord notifications
- GitHub issue creation for critical problems

## 📋 Workflow States

### PR Labels (Status Tracking)
- `status:needs-coderabbit-review` - Waiting for CodeRabbit analysis
- `status:needs-claude-repair` - CodeRabbit found issues, Claude should fix
- `status:needs-cursor-fix` - Claude failed, escalate to Cursor agents
- `status:coderabbit-approved` - PR approved by CodeRabbit
- `claude:auto-repaired` - Claude successfully applied fixes
- `claude:repair-failed` - Claude could not fix the issues

### Agent Labels (Cursor Dispatch)
- `agent:python` - Python code issues
- `agent:javascript` - JavaScript/TypeScript issues  
- `agent:infra` - Infrastructure/DevOps issues
- `agent:docs` - Documentation issues
- `agent:security` - Security-related issues
- `agent:ops` - Operational issues
- `agent:general` - General code issues

## ⚙️ Configuration

### Required Secrets
```yaml
GITHUB_TOKEN: # GitHub API access
ANTHROPIC_API_KEY: # Claude AI access
CURSOR_API_KEY: # Cursor agent access (if available)
SLACK_WEBHOOK_URL: # Optional notifications
DISCORD_WEBHOOK_URL: # Optional notifications
```

### Environment Variables
```yaml
# Rate Limiting
CODERABBIT_MAX_REQUESTS_PER_HOUR: 60
CLAUDE_MAX_REQUESTS_PER_HOUR: 100
CURSOR_MAX_REQUESTS_PER_HOUR: 50

# Retry Configuration
MAX_RETRY_ATTEMPTS: 3
BASE_RETRY_DELAY: 2

# Processing Limits
MAX_PRS_PER_RUN: 5
```

### Repository Variables
```yaml
CODERABBIT_LOGINS: "coderabbitai[bot],coderabbitai"
CURSOR_AGENT_CLASSIFIERS: "src/=agent:python,docs/=agent:docs"
```

## 🚀 Setup Instructions

### 1. Deploy Workflows
```bash
# Workflows are already in place in .github/workflows/
# - self-healing-orchestrator.yml (main workflow)
# - coderabbit-follow-up.yml (legacy compatibility)  
# - cursor-agent-dispatch.yml (legacy compatibility)
```

### 2. Configure Secrets
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add required secrets (GITHUB_TOKEN is automatic)
3. Add ANTHROPIC_API_KEY for Claude integration
4. Optionally add webhook URLs for notifications

### 3. Set Repository Variables
1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Configure CodeRabbit and Cursor settings as needed

### 4. Install CodeRabbit
1. Install the CodeRabbit GitHub App from the marketplace
2. Grant it access to your repository
3. The system will automatically detect and integrate

## 📊 Monitoring & Analytics

### Health Dashboard
The system automatically tracks:
- **Success Rates**: Per-workflow success percentages
- **Processing Times**: Average time to resolve issues
- **Stuck PRs**: PRs that haven't been updated in 48+ hours
- **Rate Limit Usage**: API quota consumption across services
- **Error Rates**: System reliability metrics

### Escalation Thresholds
- **Stuck PRs**: >3 PRs stuck for 48+ hours → Warning
- **Workflow Failures**: <70% success rate → Error
- **High Rate Limits**: >10 hits per hour → Warning
- **System Errors**: >5 errors per run → Error

### Notification Channels
1. **Slack**: Real-time alerts with rich formatting
2. **Discord**: Embedded alerts with color coding
3. **GitHub Issues**: Automatic issue creation for critical problems
4. **PR Comments**: Contextual updates on automation progress

## 🔄 Scheduling Strategy

### Intelligent Scheduling
- **Business Hours** (8 AM - 6 PM UTC): Every 15 minutes (high responsiveness)
- **Off Hours** (6 PM - 8 AM UTC): Every 30 minutes (rate-limit friendly)
- **Weekends**: Every hour (reduced activity)

### Dynamic Rate Limiting
- **Peak Hours** (10 AM - 4 PM UTC): 130% of base limits
- **Off Hours**: 70% of base limits  
- **Weekends**: 60% of base limits

## 🛠️ Advanced Features

### Smart PR Prioritization
PRs are processed based on priority scores considering:
- **Age**: Older PRs get higher priority
- **Labels**: `priority:critical`, `security`, `bug` boost priority
- **Recent Activity**: Recently updated PRs get attention faster
- **Complexity**: Simple fixes processed before complex ones

### Complexity Analysis
The system analyzes PR complexity:
- **Low**: <100 changes, <5 files
- **Medium**: 100-500 changes, 5-10 files  
- **High**: >500 changes, >10 files

Agent dispatch is adjusted based on complexity.

### Fallback Mechanisms
1. **CodeRabbit Timeout**: Falls back to Claude after 2 hours
2. **Claude Failure**: Escalates to Cursor agents
3. **Cursor Timeout**: Creates manual review issue
4. **System Failure**: Sends alerts and pauses automation

## 🎯 Best Practices for Rate Limiting

### CodeRabbit Optimization
- **Batch Reviews**: Process multiple PRs in single API calls
- **Smart Triggers**: Only request reviews when needed
- **Exponential Backoff**: Graceful handling of rate limits
- **Priority Queue**: High-priority PRs bypass normal queuing

### Claude Integration  
- **High-Confidence Filtering**: Only apply fixes with >60% confidence
- **Contextual Prompts**: Include full file context and CodeRabbit feedback
- **Incremental Fixes**: Apply fixes in small, focused commits
- **Error Handling**: Graceful degradation when API is unavailable

### Cursor Agent Management
- **Specialized Dispatch**: Route issues to domain-specific agents
- **Complexity Awareness**: Scale agent assignment based on PR complexity
- **Resource Management**: Serialize heavy operations
- **Timeout Handling**: Escalate stuck agents to human review

## 🔍 Debugging & Troubleshooting

### Common Issues

#### 1. Rate Limit Exceeded
```bash
# Check current usage
cat .github/state/rate-limits.json

# Solution: Adjust rate limits in workflow environment
# or wait for automatic reset
```

#### 2. Claude API Failures
```bash
# Check API key validity
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages

# Solution: Verify API key and quota limits
```

#### 3. Stuck PRs
```bash
# Manually trigger processing
gh workflow run "Self-Healing Repository Orchestrator" -f pr_number=123

# Solution: Check PR labels and remove blocking states
```

### Log Analysis
```bash
# View workflow logs
gh run list --workflow="Self-Healing Repository Orchestrator"
gh run view <run_id> --log

# Check health status
cat .github/state/health-history.json | jq '.[-1]'
```

## 📈 Performance Metrics

### Target Performance
- **CodeRabbit Response Time**: <5 minutes
- **Claude Repair Time**: <10 minutes  
- **Cursor Agent Response**: <30 minutes
- **Overall Resolution Time**: <1 hour for 80% of issues
- **System Uptime**: >99.5%

### Success Rate Targets
- **CodeRabbit Review**: >95% success rate
- **Claude Auto-Repair**: >70% success rate
- **Cursor Agent Fixes**: >85% success rate
- **End-to-End Resolution**: >80% fully automated

## 🚨 Emergency Procedures

### System Shutdown
```bash
# Disable all automation
gh workflow disable "Self-Healing Repository Orchestrator"

# Or use emergency labels
git push origin --tags emergency/disable-automation
```

### Manual Override
```bash
# Force manual review
gh pr edit <pr_number> --add-label "automation:skip"

# Emergency escalation
gh pr edit <pr_number> --add-label "priority:critical"
```

### Recovery
```bash
# Clean state and restart
rm -rf .github/state/
gh workflow enable "Self-Healing Repository Orchestrator"
gh workflow run "Self-Healing Repository Orchestrator"
```

## 🤝 Contributing

### Adding New Agent Types
1. Update `AGENT_LABELS` in `cursor_dispatch.py`
2. Add classification logic in `default_classifier()`
3. Update documentation and examples
4. Test with representative PRs

### Customizing Classification Rules
```python
# In enhanced_cursor_dispatch.py
CURSOR_AGENT_CLASSIFIERS = "src/api=agent:python,infra/=agent:infra"
```

### Extending Health Monitoring
1. Add new metrics to `HealthMetrics` class
2. Implement collection logic in `analyze_pr_health()`
3. Add threshold checks in `check_health_thresholds()`
4. Update notification templates

## 📄 License

This self-healing automation system is part of the plasma-engine project and follows the same licensing terms.

---

**🤖 Autonomous Development, Delivered.**

*This system represents the future of software development - where repositories self-heal, self-improve, and self-maintain with minimal human intervention while preserving the highest quality standards.*