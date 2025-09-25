#!/bin/bash

# Simple script to create GitHub issues for Phase 1

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GITHUB_ORG="Plasma-Engine"

echo -e "${BLUE}Creating Phase 1 Issues for Plasma Engine${NC}"

# Function to create issue
create_issue() {
    local repo=$1
    local title=$2
    local body=$3
    local labels=$4
    
    echo -e "${YELLOW}Creating: ${title}${NC}"
    
    gh issue create \
        --repo "${GITHUB_ORG}/${repo}" \
        --title "${title}" \
        --body "${body}" \
        --label "${labels}" 2>/dev/null && \
        echo -e "${GREEN}✓ Created${NC}" || \
        echo -e "  Issue might already exist"
}

# Gateway Issues
echo -e "\n${BLUE}Gateway Service Issues:${NC}"
create_issue "plasma-engine-gateway" \
    "[PE-GW-001] Set up FastAPI application structure" \
    "Initialize FastAPI application with proper project structure, dependency injection, and configuration management.
    
Priority: High
Sprint: 1
    
Tasks:
- Set up FastAPI project structure
- Configure dependency injection
- Implement configuration management
- Set up logging
- Create health check endpoints" \
    "type:feature,priority:high,service:gateway"

create_issue "plasma-engine-gateway" \
    "[PE-GW-002] Implement JWT authentication" \
    "Implement JWT-based authentication with refresh tokens and role-based access control.
    
Priority: Critical
Sprint: 1
    
Tasks:
- Implement JWT token generation
- Create refresh token mechanism
- Add role-based access control
- Implement token validation middleware
- Create user authentication endpoints" \
    "type:feature,priority:critical,service:gateway"

create_issue "plasma-engine-gateway" \
    "[PE-GW-003] GraphQL Federation setup" \
    "Set up Apollo Federation for GraphQL schema composition across services.
    
Priority: High
Sprint: 2
    
Tasks:
- Install and configure Apollo Federation
- Create base GraphQL schema
- Implement schema composition
- Set up GraphQL playground
- Add query complexity analysis" \
    "type:feature,priority:high,service:gateway"

# Research Issues
echo -e "\n${BLUE}Research Service Issues:${NC}"
create_issue "plasma-engine-research" \
    "[PE-RS-001] GraphRAG core implementation" \
    "Implement core GraphRAG functionality with Neo4j and vector embeddings.
    
Priority: Critical
Sprint: 1
    
Tasks:
- Set up Neo4j connection
- Implement graph schema
- Create embedding generation
- Build graph construction logic
- Implement retrieval algorithms" \
    "type:feature,priority:critical,service:research,ai:graphrag"

create_issue "plasma-engine-research" \
    "[PE-RS-002] Multi-source search orchestration" \
    "Implement parallel search across multiple data sources with result aggregation.
    
Priority: High
Sprint: 1
    
Tasks:
- Create search interface abstraction
- Implement parallel search execution
- Build result ranking algorithm
- Add caching layer
- Create search API endpoints" \
    "type:feature,priority:high,service:research"

create_issue "plasma-engine-research" \
    "[PE-RS-003] Knowledge ingestion pipeline" \
    "Build pipeline for ingesting and processing documents into knowledge graph.
    
Priority: High
Sprint: 2
    
Tasks:
- Create document parsers
- Implement chunking strategies
- Build entity extraction
- Create relationship mapping
- Add incremental update support" \
    "type:feature,priority:high,service:research,ai:graphrag"

# Brand Issues
echo -e "\n${BLUE}Brand Service Issues:${NC}"
create_issue "plasma-engine-brand" \
    "[PE-BR-001] Social media monitoring setup" \
    "Implement monitoring for Twitter, LinkedIn, Reddit, and other platforms.
    
Priority: High
Sprint: 1
    
Tasks:
- Set up API connections
- Create data collection workers
- Implement rate limiting
- Build data normalization
- Create monitoring dashboard" \
    "type:feature,priority:high,service:brand"

create_issue "plasma-engine-brand" \
    "[PE-BR-002] Sentiment analysis engine" \
    "Implement real-time sentiment analysis for brand mentions.
    
Priority: Medium
Sprint: 2
    
Tasks:
- Integrate sentiment analysis models
- Create analysis pipeline
- Build confidence scoring
- Implement trend detection
- Add alerting system" \
    "type:feature,priority:medium,service:brand,ai:llm"

# Content Issues
echo -e "\n${BLUE}Content Service Issues:${NC}"
create_issue "plasma-engine-content" \
    "[PE-CT-001] AI content generation pipeline" \
    "Build content generation pipeline with multiple LLM providers.
    
Priority: High
Sprint: 1
    
Tasks:
- Integrate AI SDK
- Create content templates
- Implement generation workflow
- Add quality scoring
- Build content versioning" \
    "type:feature,priority:high,service:content,ai:llm"

create_issue "plasma-engine-content" \
    "[PE-CT-002] Multi-platform publishing" \
    "Implement publishing to various platforms (blog, social, email).
    
Priority: Medium
Sprint: 2
    
Tasks:
- Create publishing adapters
- Implement scheduling system
- Build platform-specific formatting
- Add publishing analytics
- Create rollback mechanism" \
    "type:feature,priority:medium,service:content"

# Agent Issues
echo -e "\n${BLUE}Agent Service Issues:${NC}"
create_issue "plasma-engine-agent" \
    "[PE-AG-001] MCP server integration" \
    "Integrate Model Context Protocol for agent communication.
    
Priority: Critical
Sprint: 1
    
Tasks:
- Set up MCP server
- Implement tool registry
- Create agent communication protocol
- Build context management
- Add agent orchestration" \
    "type:feature,priority:critical,service:agent"

create_issue "plasma-engine-agent" \
    "[PE-AG-002] Browser automation framework" \
    "Implement Playwright-based browser automation for web interactions.
    
Priority: High
Sprint: 2
    
Tasks:
- Set up Playwright
- Create action abstractions
- Implement session management
- Build error recovery
- Add screenshot capabilities" \
    "type:feature,priority:high,service:agent"

# Infrastructure Issues
echo -e "\n${BLUE}Infrastructure Issues:${NC}"
create_issue "plasma-engine-infra" \
    "[PE-INF-001] Kubernetes manifests" \
    "Create Kubernetes deployment manifests for all services.
    
Priority: High
Sprint: 1
    
Tasks:
- Create deployment manifests
- Set up ConfigMaps
- Configure Secrets
- Create Services
- Add Ingress rules" \
    "type:infrastructure,priority:high"

create_issue "plasma-engine-infra" \
    "[PE-INF-002] Terraform infrastructure" \
    "Set up Terraform for cloud infrastructure provisioning.
    
Priority: High
Sprint: 1
    
Tasks:
- Create Terraform modules
- Set up state management
- Configure providers
- Create environment configs
- Add resource tagging" \
    "type:infrastructure,priority:high"

create_issue "plasma-engine-infra" \
    "[PE-INF-003] Monitoring stack" \
    "Deploy Prometheus, Grafana, and Loki for observability.
    
Priority: Medium
Sprint: 2
    
Tasks:
- Deploy Prometheus
- Configure Grafana dashboards
- Set up Loki for logs
- Create alerting rules
- Add service monitors" \
    "type:infrastructure,priority:medium"

echo -e "\n${GREEN}✅ Issue creation complete!${NC}"
echo -e "${BLUE}View all issues at: https://github.com/issues?q=org%3APlasma-Engine+is%3Aopen${NC}"
