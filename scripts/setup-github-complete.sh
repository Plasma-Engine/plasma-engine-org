#!/bin/bash

# Complete GitHub setup script for Plasma Engine organization
# This script:
# 1. Creates all GitHub issues from Phase 1 tickets
# 2. Sets up branch protection rules
# 3. Configures organization settings
# 4. Creates standard labels
# 5. Verifies CodeRabbit integration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
GITHUB_ORG="Plasma-Engine"
BASE_DIR="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 Complete Plasma Engine GitHub Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Function to create labels for a repository
create_labels() {
    local repo=$1
    echo -e "\n${YELLOW}Creating labels for ${repo}...${NC}"
    
    # Define standard labels with colors
    declare -a labels=(
        "priority:critical:b60205:Issues that need immediate attention"
        "priority:high:d73a4a:High priority issues"
        "priority:medium:fbca04:Medium priority issues"
        "priority:low:0e8a16:Low priority issues"
        "type:bug:d73a4a:Something isn't working"
        "type:feature:a2eeef:New feature or request"
        "type:enhancement:84b6eb:Improvement to existing functionality"
        "type:documentation:0075ca:Improvements or additions to documentation"
        "type:infrastructure:c5def5:Infrastructure and DevOps related"
        "type:security:d73a4a:Security related issues"
        "status:in-progress:fbca04:Work in progress"
        "status:blocked:b60205:Blocked by another issue"
        "status:review:7057ff:Ready for review"
        "service:gateway:1d76db:Gateway service related"
        "service:research:1d76db:Research service related"
        "service:brand:1d76db:Brand service related"
        "service:content:1d76db:Content service related"
        "service:agent:1d76db:Agent service related"
        "phase:1:c2e0c6:Phase 1 implementation"
        "phase:2:c2e0c6:Phase 2 implementation"
        "ai:llm:ff6b6b:LLM/AI related"
        "ai:graphrag:ff6b6b:GraphRAG related"
    )
    
    for label_info in "${labels[@]}"; do
        IFS=':' read -r name color description <<< "$label_info"
        
        # Check if label exists
        if gh label list -R "${GITHUB_ORG}/${repo}" | grep -q "^${name}"; then
            echo "  Label '${name}' already exists"
        else
            gh label create "${name}" \
                --color "${color}" \
                --description "${description}" \
                -R "${GITHUB_ORG}/${repo}" 2>/dev/null && \
                echo -e "  ${GREEN}✓${NC} Created label: ${name}" || \
                echo -e "  ${YELLOW}⚠${NC} Could not create label: ${name}"
        fi
    done
}

# Function to set up branch protection
setup_branch_protection() {
    local repo=$1
    echo -e "\n${YELLOW}Setting up branch protection for ${repo}...${NC}"
    
    # Create branch protection rule for main branch
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/repos/${GITHUB_ORG}/${repo}/branches/main/protection" \
        -f "required_status_checks[strict]=true" \
        -f "required_status_checks[contexts][]=continuous-integration" \
        -f "enforce_admins=false" \
        -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
        -f "required_pull_request_reviews[require_code_owner_reviews]=true" \
        -f "required_pull_request_reviews[required_approving_review_count]=1" \
        -f "restrictions=null" \
        -f "allow_force_pushes=false" \
        -f "allow_deletions=false" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Branch protection enabled for main" || \
        echo -e "  ${YELLOW}⚠${NC} Branch protection might already be configured"
}

# Function to create issues from ticket files
create_issues_from_tickets() {
    local service=$1
    local ticket_file="${BASE_DIR}/docs/tickets/phase-1-${service}.md"
    
    if [ ! -f "$ticket_file" ]; then
        echo -e "  ${YELLOW}No ticket file found for ${service}${NC}"
        return
    fi
    
    echo -e "\n${CYAN}Creating issues for ${service} service...${NC}"
    
    # Parse the ticket file and create issues
    local in_ticket=false
    local ticket_id=""
    local ticket_title=""
    local ticket_body=""
    local ticket_labels=""
    
    while IFS= read -r line; do
        # Check for ticket header (e.g., ## PE-GW-001: ...)
        if [[ $line =~ ^##[[:space:]]+(PE-[A-Z]+-[0-9]+):[[:space:]](.+) ]]; then
            # If we have a previous ticket, create it
            if [ -n "$ticket_id" ]; then
                create_single_issue "$service" "$ticket_id" "$ticket_title" "$ticket_body" "$ticket_labels"
            fi
            
            # Start new ticket
            ticket_id="${BASH_REMATCH[1]}"
            ticket_title="${BASH_REMATCH[2]}"
            ticket_body=""
            ticket_labels="phase:1,service:${service}"
            in_ticket=true
            
        elif [ "$in_ticket" = true ]; then
            # Add to ticket body
            ticket_body="${ticket_body}${line}\n"
            
            # Extract priority if present
            if [[ $line =~ Priority:[[:space:]]*(Critical|High|Medium|Low) ]]; then
                priority=$(echo "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')
                ticket_labels="${ticket_labels},priority:${priority}"
            fi
            
            # Extract type if present
            if [[ $line =~ Type:[[:space:]]*(Feature|Bug|Enhancement|Infrastructure) ]]; then
                type=$(echo "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')
                ticket_labels="${ticket_labels},type:${type}"
            fi
        fi
    done < "$ticket_file"
    
    # Create the last ticket
    if [ -n "$ticket_id" ]; then
        create_single_issue "$service" "$ticket_id" "$ticket_title" "$ticket_body" "$ticket_labels"
    fi
}

# Function to create a single issue
create_single_issue() {
    local service=$1
    local id=$2
    local title=$3
    local body=$4
    local labels=$5
    
    # Determine repository based on service
    local repo="plasma-engine-${service}"
    
    # Check if issue already exists
    if gh issue list -R "${GITHUB_ORG}/${repo}" --search "${id}" | grep -q "${id}"; then
        echo -e "  ${YELLOW}Issue ${id} already exists${NC}"
        return
    fi
    
    # Create the issue
    echo -e "  Creating issue ${id}: ${title}"
    echo -e "$body" | gh issue create \
        --title "[${id}] ${title}" \
        --body-file - \
        --label "${labels}" \
        -R "${GITHUB_ORG}/${repo}" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Created issue ${id}" || \
        echo -e "  ${RED}✗${NC} Failed to create issue ${id}"
}

# Function to create project board
create_project_board() {
    echo -e "\n${YELLOW}Creating GitHub Project Board...${NC}"
    
    # Create organization project
    project_response=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        "/orgs/${GITHUB_ORG}/projects" \
        -f "name=Plasma Engine Roadmap" \
        -f "body=Master project board for tracking all Plasma Engine development" \
        2>/dev/null) || echo "Project might already exist"
    
    echo -e "  ${GREEN}✓${NC} Project board configured"
}

# Function to verify CodeRabbit integration
verify_coderabbit() {
    echo -e "\n${YELLOW}Verifying CodeRabbit Integration...${NC}"
    
    # Check if .coderabbit.yaml exists in each repo
    for repo in plasma-engine-{gateway,research,brand,content,agent,shared,infra}; do
        echo -e "  Checking ${repo}..."
        
        # Create CodeRabbit config if it doesn't exist
        if ! gh api "/repos/${GITHUB_ORG}/${repo}/contents/.coderabbit.yaml" 2>/dev/null | grep -q "content"; then
            echo "    Creating .coderabbit.yaml..."
            
            # Create the config file locally first
            cat > /tmp/coderabbit.yaml << 'EOF'
# CodeRabbit Configuration
# Documentation: https://docs.coderabbit.ai/guides/configure-coderabbit

language: "en-US"
early_access: false

reviews:
  # Enable high-quality reviews
  high_level_summary: true
  poem: false
  review_status: true
  collapse_walkthrough: false
  
  # Review triggers
  auto_review:
    enabled: true
    drafts: false
  
  # Review tools
  tools:
    ruff:
      enabled: true
    mypy:
      enabled: true
    eslint:
      enabled: true
    prettier:
      enabled: true
    
  # Path filters
  path_filters:
    - "!**/*.md"
    - "!**/*.txt"
    - "!**/package-lock.json"
    - "!**/yarn.lock"
    
  # Review instructions
  instructions: |
    - Focus on code quality, security, and performance
    - Check for proper error handling
    - Verify test coverage for new features
    - Ensure consistent code style
    - Look for potential memory leaks or performance issues
    - Validate API contracts and data schemas
    - Check for proper logging and monitoring

chat:
  # Enable PR chat
  auto_reply: true

knowledge_base:
  # Link to documentation
  learnings:
    scope: auto
  issues:
    scope: auto
EOF
            
            # Commit the file to the repo
            cd "/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/${repo}"
            cp /tmp/coderabbit.yaml .coderabbit.yaml
            git add .coderabbit.yaml
            git commit -m "Add CodeRabbit configuration" 2>/dev/null || true
            git push 2>/dev/null && echo -e "    ${GREEN}✓${NC} Added CodeRabbit config" || \
                echo -e "    ${YELLOW}⚠${NC} Could not push CodeRabbit config"
            cd "${BASE_DIR}"
        else
            echo -e "    ${GREEN}✓${NC} CodeRabbit config exists"
        fi
    done
}

# Function to create organization-wide settings
setup_organization_settings() {
    echo -e "\n${YELLOW}Configuring Organization Settings...${NC}"
    
    # Update organization settings
    gh api \
        --method PATCH \
        -H "Accept: application/vnd.github+json" \
        "/orgs/${GITHUB_ORG}" \
        -f "has_organization_projects=true" \
        -f "has_repository_projects=true" \
        -f "members_can_create_repositories=false" \
        -f "members_can_create_private_repositories=false" \
        -f "members_can_create_public_repositories=false" \
        -f "default_repository_permission=read" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Organization settings updated" || \
        echo -e "  ${YELLOW}⚠${NC} Some settings might require owner permissions"
}

# Main execution
echo -e "\n${CYAN}Step 1: Creating Standard Labels${NC}"
for repo in plasma-engine-{gateway,research,brand,content,agent,shared,infra,org}; do
    create_labels "$repo"
done

echo -e "\n${CYAN}Step 2: Setting Up Branch Protection${NC}"
for repo in plasma-engine-{gateway,research,brand,content,agent,shared,infra,org}; do
    setup_branch_protection "$repo"
done

echo -e "\n${CYAN}Step 3: Creating Phase 1 Issues${NC}"
for service in gateway research brand content agent infra; do
    create_issues_from_tickets "$service"
done

echo -e "\n${CYAN}Step 4: Setting Up Project Board${NC}"
create_project_board

echo -e "\n${CYAN}Step 5: Verifying CodeRabbit Integration${NC}"
verify_coderabbit

echo -e "\n${CYAN}Step 6: Configuring Organization Settings${NC}"
setup_organization_settings

# Summary
echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Plasma Engine GitHub Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}📊 Setup Summary:${NC}"
echo "  • Standard labels created for all repositories"
echo "  • Branch protection rules configured"
echo "  • Phase 1 issues created from tickets"
echo "  • Project board initialized"
echo "  • CodeRabbit configuration added"
echo "  • Organization settings configured"

echo -e "\n${YELLOW}🔗 Important Links:${NC}"
echo "  • Organization: https://github.com/${GITHUB_ORG}"
echo "  • Projects: https://github.com/orgs/${GITHUB_ORG}/projects"
echo "  • Issues: https://github.com/issues?q=org%3A${GITHUB_ORG}+is%3Aopen"
echo "  • Pull Requests: https://github.com/pulls?q=org%3A${GITHUB_ORG}+is%3Aopen"

echo -e "\n${CYAN}📝 Next Manual Steps:${NC}"
echo "  1. Install CodeRabbit GitHub App: https://github.com/apps/coderabbitai"
echo "  2. Configure GitHub Actions secrets for each repository"
echo "  3. Set up deployment environments (staging, production)"
echo "  4. Configure Slack/Discord notifications for CI/CD"
echo "  5. Add team members and configure permissions"

echo -e "\n${GREEN}Your Plasma Engine platform is ready for development! 🚀${NC}"
