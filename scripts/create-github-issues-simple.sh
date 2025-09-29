#!/bin/bash

# Simple GitHub Issues Creation Script for Plasma Engine
# Creates all 44 issues across 6 phases

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

GITHUB_ORG="Plasma-Engine"
MAIN_REPO="plasma-engine-org"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Creating All 44 Production Issues for Plasma Engine${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Simple issue creation function
create_issue() {
    local title=$1
    local body=$2
    local labels=$3

    echo -e "${YELLOW}Creating: ${title}${NC}"

    gh issue create \
        --repo "${GITHUB_ORG}/${MAIN_REPO}" \
        --title "${title}" \
        --body "${body}" \
        --label "${labels}" 2>/dev/null && \
        echo -e "${GREEN}✓ Created${NC}" || \
        echo -e "${RED}  Skipped (might exist)${NC}"
}

# PHASE 1: INFRASTRUCTURE
echo -e "\n${BLUE}PHASE 1: Infrastructure (8 issues)${NC}"

create_issue "[INFRA-001] Setup Docker Development Environment" \
"Set up Docker Compose environment for all services including PostgreSQL, Redis, and Neo4j." \
"phase:1-infrastructure,priority:critical"

create_issue "[INFRA-002] Configure GitHub Actions CI/CD" \
"Implement CI/CD pipeline with testing, linting, and deployment automation." \
"phase:1-infrastructure,priority:critical"

create_issue "[INFRA-003] Setup Kubernetes Manifests" \
"Create K8s deployment manifests and Helm charts for production deployment." \
"phase:1-infrastructure,priority:high"

create_issue "[INFRA-004] Implement Monitoring Stack" \
"Deploy Prometheus, Grafana, and logging infrastructure." \
"phase:1-infrastructure,priority:high"

create_issue "[INFRA-005] Setup PostgreSQL with Extensions" \
"Configure PostgreSQL with pgvector and other required extensions." \
"phase:1-infrastructure,priority:critical"

create_issue "[INFRA-006] Configure Redis Cluster" \
"Set up Redis for caching and session management." \
"phase:1-infrastructure,priority:high"

create_issue "[INFRA-007] Setup Neo4j Graph Database" \
"Configure Neo4j for Research service knowledge graph." \
"phase:1-infrastructure,priority:high"

create_issue "[INFRA-008] Implement Secrets Management" \
"Set up secure secrets management with Vault or K8s secrets." \
"phase:1-infrastructure,priority:critical"

# PHASE 2: CORE SERVICES
echo -e "\n${BLUE}PHASE 2: Core Services (8 issues)${NC}"

create_issue "[CORE-001] Implement Gateway Service" \
"Build Apollo GraphQL Gateway with federation support." \
"phase:2-core-services,component:gateway,priority:critical"

create_issue "[CORE-002] Build Authentication Service" \
"Implement Google OAuth with JWT tokens and domain restriction to plasma.to." \
"phase:2-core-services,component:gateway,priority:critical"

create_issue "[CORE-003] Create Research Service Base" \
"Implement Research service with GraphRAG capabilities." \
"phase:2-core-services,component:research,priority:high"

create_issue "[CORE-004] Implement Brand Service" \
"Build brand monitoring and analytics service." \
"phase:2-core-services,component:brand,priority:high"

create_issue "[CORE-005] Build Content Service" \
"Create AI-powered content generation service." \
"phase:2-core-services,component:content,priority:high"

create_issue "[CORE-006] Create Agent Service" \
"Implement multi-agent orchestration service." \
"phase:2-core-services,component:agent,priority:medium"

create_issue "[CORE-007] Implement Service Communication" \
"Set up inter-service communication patterns." \
"phase:2-core-services,priority:high"

create_issue "[CORE-008] Add Service Health Monitoring" \
"Implement health checks and monitoring for all services." \
"phase:2-core-services,priority:high"

# PHASE 3: FRONTEND
echo -e "\n${BLUE}PHASE 3: Frontend & UX (7 issues)${NC}"

create_issue "[UI-001] Create Next.js Application" \
"Set up Next.js 14+ with TypeScript and Material UI." \
"phase:3-frontend,component:frontend,priority:critical"

create_issue "[UI-002] Implement Google OAuth Login" \
"Create login flow with Google OAuth integration." \
"phase:3-frontend,component:frontend,priority:critical"

create_issue "[UI-003] Build Main Dashboard" \
"Create main dashboard with metrics and navigation." \
"phase:3-frontend,component:frontend,priority:high"

create_issue "[UI-004] Create Research Interface" \
"Build interface for research queries and knowledge graph." \
"phase:3-frontend,component:frontend,priority:high"

create_issue "[UI-005] Implement Brand Dashboard" \
"Create brand monitoring interface with analytics." \
"phase:3-frontend,component:frontend,priority:medium"

create_issue "[UI-006] Build Content Creation Tools" \
"Develop content creation and management interface." \
"phase:3-frontend,component:frontend,priority:medium"

create_issue "[UI-007] Add Settings Panel" \
"Create settings and administration interface." \
"phase:3-frontend,component:frontend,priority:low"

# PHASE 4: AI/ML
echo -e "\n${BLUE}PHASE 4: AI/ML Integration (7 issues)${NC}"

create_issue "[AI-001] Integrate OpenAI GPT-4" \
"Set up OpenAI GPT-4 integration for content generation." \
"phase:4-ai-ml,priority:high"

create_issue "[AI-002] Implement Claude Integration" \
"Add Anthropic Claude integration for advanced reasoning." \
"phase:4-ai-ml,priority:high"

create_issue "[AI-003] Build GraphRAG System" \
"Implement Graph-based RAG for knowledge management." \
"phase:4-ai-ml,component:research,priority:critical"

create_issue "[AI-004] Create Embedding Pipeline" \
"Build embedding generation and storage pipeline." \
"phase:4-ai-ml,priority:high"

create_issue "[AI-005] Implement NLP Pipeline" \
"Create NLP pipeline for sentiment and entity analysis." \
"phase:4-ai-ml,component:brand,priority:high"

create_issue "[AI-006] Build Multi-Agent Framework" \
"Implement multi-agent system for complex tasks." \
"phase:4-ai-ml,component:agent,priority:medium"

create_issue "[AI-007] Add Model Monitoring" \
"Implement monitoring for AI model performance." \
"phase:4-ai-ml,priority:low"

# PHASE 5: TESTING
echo -e "\n${BLUE}PHASE 5: Testing & QA (7 issues)${NC}"

create_issue "[QA-001] Implement Unit Tests" \
"Achieve 90%+ unit test coverage across all services." \
"phase:5-testing,type:testing,priority:critical"

create_issue "[QA-002] Create Integration Tests" \
"Build comprehensive integration tests between services." \
"phase:5-testing,type:testing,priority:high"

create_issue "[QA-003] Implement E2E Testing" \
"Create end-to-end tests for critical user journeys." \
"phase:5-testing,type:testing,priority:high"

create_issue "[QA-004] Setup Load Testing" \
"Implement load testing for performance validation." \
"phase:5-testing,type:testing,priority:medium"

create_issue "[QA-005] Security Testing" \
"Conduct comprehensive security testing and scanning." \
"phase:5-testing,type:security,priority:high"

create_issue "[QA-006] Test Data Management" \
"Build test data generation and management system." \
"phase:5-testing,type:testing,priority:medium"

create_issue "[QA-007] QA Documentation" \
"Document all testing procedures and quality standards." \
"phase:5-testing,type:documentation,priority:low"

# PHASE 6: PRODUCTION
echo -e "\n${BLUE}PHASE 6: Production Deployment (7 issues)${NC}"

create_issue "[PROD-001] Setup Production Infrastructure" \
"Deploy production Kubernetes cluster and infrastructure." \
"phase:6-production,priority:critical"

create_issue "[PROD-002] Configure Production Databases" \
"Set up production database instances with HA." \
"phase:6-production,priority:critical"

create_issue "[PROD-003] Deploy Services" \
"Deploy all microservices to production cluster." \
"phase:6-production,priority:critical"

create_issue "[PROD-004] Setup CDN and Load Balancing" \
"Configure CDN and load balancers for production." \
"phase:6-production,priority:high"

create_issue "[PROD-005] Production Monitoring" \
"Deploy comprehensive production monitoring stack." \
"phase:6-production,priority:critical"

create_issue "[PROD-006] Production Validation" \
"Validate production deployment with comprehensive testing." \
"phase:6-production,priority:critical"

create_issue "[PROD-007] Production Launch" \
"Complete production launch and operational handoff." \
"phase:6-production,priority:critical"

echo -e "\n${GREEN}✨ Issue Creation Complete!${NC}"
echo -e "Check issues at: ${BLUE}https://github.com/${GITHUB_ORG}/${MAIN_REPO}/issues${NC}"