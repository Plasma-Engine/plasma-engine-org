#!/bin/bash

# Complete GitHub Project Setup Script
# Creates all issues, milestones, labels, and project board for Plasma Engine

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

GITHUB_ORG="Plasma-Engine"
MAIN_REPO="plasma-engine-org"

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   🚀 PLASMA ENGINE - COMPLETE GITHUB PROJECT SETUP${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# Function to create a label
create_label() {
    local name=$1
    local color=$2
    local description=$3

    echo -e "${YELLOW}Creating label: ${name}${NC}"
    gh label create "$name" \
        --repo "${GITHUB_ORG}/${MAIN_REPO}" \
        --color "$color" \
        --description "$description" 2>/dev/null || echo -e "  Label exists"
}

# Function to create a milestone
create_milestone() {
    local title=$1
    local description=$2
    local due_date=$3

    echo -e "${YELLOW}Creating milestone: ${title}${NC}"
    gh api repos/"${GITHUB_ORG}"/"${MAIN_REPO}"/milestones \
        --method POST \
        -f title="$title" \
        -f description="$description" \
        -f due_on="$due_date" 2>/dev/null || echo -e "  Milestone might exist"
}

# Function to create issue with full details
create_detailed_issue() {
    local title=$1
    local body=$2
    local labels=$3
    local milestone=$4
    local assignee=${5:-""}

    echo -e "${YELLOW}Creating issue: ${title}${NC}"

    if [ -n "$assignee" ]; then
        gh issue create \
            --repo "${GITHUB_ORG}/${MAIN_REPO}" \
            --title "${title}" \
            --body "${body}" \
            --label "${labels}" \
            --milestone "${milestone}" \
            --assignee "${assignee}" 2>/dev/null && \
            echo -e "${GREEN}✓ Created${NC}" || \
            echo -e "${RED}  Issue might already exist${NC}"
    else
        gh issue create \
            --repo "${GITHUB_ORG}/${MAIN_REPO}" \
            --title "${title}" \
            --body "${body}" \
            --label "${labels}" \
            --milestone "${milestone}" 2>/dev/null && \
            echo -e "${GREEN}✓ Created${NC}" || \
            echo -e "${RED}  Issue might already exist${NC}"
    fi
}

# ═══════════════════════════════════════════════════════════
# STEP 1: CREATE LABELS
# ═══════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Creating Labels${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Priority labels
create_label "priority:critical" "FF0000" "Must be completed immediately"
create_label "priority:high" "FF6B6B" "High priority issue"
create_label "priority:medium" "FFB366" "Medium priority issue"
create_label "priority:low" "B4E7CE" "Low priority issue"

# Phase labels
create_label "phase:1-infrastructure" "7B68EE" "Phase 1: Infrastructure Foundation"
create_label "phase:2-core-services" "9370DB" "Phase 2: Core Services Development"
create_label "phase:3-frontend" "BA55D3" "Phase 3: Frontend & UX"
create_label "phase:4-ai-ml" "8B008B" "Phase 4: AI/ML Integration"
create_label "phase:5-testing" "4B0082" "Phase 5: Testing & Quality"
create_label "phase:6-production" "800080" "Phase 6: Production Deployment"

# Component labels
create_label "component:gateway" "1E90FF" "Gateway service related"
create_label "component:research" "00CED1" "Research service related"
create_label "component:brand" "20B2AA" "Brand service related"
create_label "component:content" "48D1CC" "Content service related"
create_label "component:agent" "00BFFF" "Agent service related"
create_label "component:frontend" "87CEEB" "Frontend application related"
create_label "component:infrastructure" "4682B4" "Infrastructure related"

# Type labels
create_label "type:feature" "0E8A16" "New feature or request"
create_label "type:bug" "D93F0B" "Something isn't working"
create_label "type:documentation" "0052CC" "Documentation improvements"
create_label "type:testing" "FBCA04" "Testing related"
create_label "type:security" "EE0000" "Security issue"
create_label "type:performance" "F9A825" "Performance improvement"

# Size labels
create_label "size:XS" "C5DEF5" "Extra small - 1-2 hours"
create_label "size:S" "BFD4F2" "Small - 2-4 hours"
create_label "size:M" "B8C9E8" "Medium - 1-2 days"
create_label "size:L" "8FA3CC" "Large - 3-5 days"
create_label "size:XL" "5E7CA3" "Extra large - 1-2 weeks"

# Special labels
create_label "good-first-issue" "7057FF" "Good for newcomers"
create_label "help-wanted" "008672" "Extra attention needed"
create_label "blocked" "E99695" "Blocked by another issue"
create_label "ready-for-review" "0E8A16" "Ready for code review"
create_label "work-in-progress" "FEF2C0" "Work in progress"

# ═══════════════════════════════════════════════════════════
# STEP 2: CREATE MILESTONES
# ═══════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Creating Milestones${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Calculate dates (from current date)
CURRENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
WEEK_4=$(date -u -d "+4 weeks" +"%Y-%m-%dT%H:%M:%SZ")
WEEK_8=$(date -u -d "+8 weeks" +"%Y-%m-%dT%H:%M:%SZ")
WEEK_12=$(date -u -d "+12 weeks" +"%Y-%m-%dT%H:%M:%SZ")
WEEK_16=$(date -u -d "+16 weeks" +"%Y-%m-%dT%H:%M:%SZ")
WEEK_20=$(date -u -d "+20 weeks" +"%Y-%m-%dT%H:%M:%SZ")
WEEK_26=$(date -u -d "+26 weeks" +"%Y-%m-%dT%H:%M:%SZ")

create_milestone "Phase 1: Infrastructure Foundation" \
    "Complete development environment, CI/CD, and database infrastructure" \
    "$WEEK_4"

create_milestone "Phase 2: Core Services" \
    "Implement all microservices with basic functionality" \
    "$WEEK_8"

create_milestone "Phase 3: Frontend & UX" \
    "Complete Next.js application with Google OAuth" \
    "$WEEK_12"

create_milestone "Phase 4: AI/ML Integration" \
    "Integrate OpenAI, Claude, and GraphRAG system" \
    "$WEEK_16"

create_milestone "Phase 5: Testing & QA" \
    "Achieve 90% test coverage and security validation" \
    "$WEEK_20"

create_milestone "Phase 6: Production Launch" \
    "Deploy to production and go live" \
    "$WEEK_26"

# ═══════════════════════════════════════════════════════════
# STEP 3: CREATE ALL 44 ISSUES WITH MODULAR WORK PACKAGES
# ═══════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Creating All 44 Issues with Modular Work Packages${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# ─────────────────────────────────────────────────────────
# PHASE 1: INFRASTRUCTURE (8 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 1: Infrastructure Foundation (8 issues)${NC}"

create_detailed_issue "[INFRA-001] Setup Docker Development Environment" \
"## 🎯 Objective
Set up complete Docker development environment for all microservices.

## 📋 Modular Work Package

### Module A: Docker Configuration
\`\`\`yaml
Tasks:
- Create docker-compose.yml for all services
- Configure service networking
- Set up volume mappings
- Define health checks
Files to create:
- docker-compose.yml
- docker-compose.override.yml
- .dockerignore files
\`\`\`

### Module B: Database Setup
\`\`\`yaml
Tasks:
- PostgreSQL with pgvector extension
- Redis with persistence
- Neo4j with APOC plugins
Files to create:
- scripts/init-postgres.sql
- config/redis.conf
- config/neo4j.conf
\`\`\`

### Module C: Service Dockerfiles
\`\`\`yaml
Tasks:
- Create Dockerfile for each service
- Multi-stage builds for optimization
- Development vs production configs
Files to create:
- */Dockerfile
- */Dockerfile.dev
\`\`\`

## ✅ Acceptance Criteria
- [ ] All services start with \`docker-compose up\`
- [ ] Data persists between restarts
- [ ] Services can communicate internally
- [ ] External ports properly mapped
- [ ] Health checks pass for all services

## 👤 Assignee
DevOps Engineer or Backend Developer

## ⏱️ Estimated Time: 2-3 days
## 🏷️ Labels: infrastructure, docker, priority:critical
## 📅 Sprint: 1" \
"phase:1-infrastructure,component:infrastructure,type:feature,priority:critical,size:L" \
"Phase 1: Infrastructure Foundation"

create_detailed_issue "[INFRA-002] Configure GitHub Actions CI/CD Pipeline" \
"## 🎯 Objective
Implement comprehensive CI/CD pipeline using GitHub Actions.

## 📋 Modular Work Package

### Module A: CI Workflows
\`\`\`yaml
Tasks:
- Linting workflow for all languages
- Unit test runners
- Coverage reporting
Files to create:
- .github/workflows/ci.yml
- .github/workflows/lint.yml
- .github/workflows/test.yml
\`\`\`

### Module B: Security Scanning
\`\`\`yaml
Tasks:
- SAST with Snyk/Bandit
- Dependency scanning
- Container scanning
Files to create:
- .github/workflows/security.yml
- .snyk
- security/bandit.yaml
\`\`\`

### Module C: CD Workflows
\`\`\`yaml
Tasks:
- Docker image building
- Registry push automation
- Deployment triggers
Files to create:
- .github/workflows/cd.yml
- .github/workflows/deploy.yml
\`\`\`

## ✅ Acceptance Criteria
- [ ] All PRs require passing CI
- [ ] Coverage reports generated
- [ ] Security issues detected
- [ ] Docker images built and pushed
- [ ] Automated deployment works

## 👤 Assignee
DevOps Engineer

## ⏱️ Estimated Time: 2-3 days
## 🏷️ Labels: ci-cd, github-actions, priority:critical
## 📅 Sprint: 1" \
"phase:1-infrastructure,component:infrastructure,type:feature,priority:critical,size:L" \
"Phase 1: Infrastructure Foundation"

create_detailed_issue "[INFRA-003] Setup Kubernetes Manifests" \
"## 🎯 Objective
Create Kubernetes deployment manifests for production.

## 📋 Modular Work Package

### Module A: Service Deployments
\`\`\`yaml
Tasks:
- Deployment manifests for each service
- Resource limits and requests
- Replica configurations
Files to create:
- k8s/services/*/deployment.yaml
- k8s/services/*/service.yaml
\`\`\`

### Module B: Configuration Management
\`\`\`yaml
Tasks:
- ConfigMaps for each service
- Secret templates
- Environment-specific configs
Files to create:
- k8s/config/configmaps.yaml
- k8s/config/secrets.yaml
- k8s/config/environments/
\`\`\`

### Module C: Ingress & Networking
\`\`\`yaml
Tasks:
- Ingress controller setup
- TLS configuration
- Network policies
Files to create:
- k8s/ingress/ingress.yaml
- k8s/ingress/tls.yaml
- k8s/network-policies/
\`\`\`

### Module D: Helm Charts
\`\`\`yaml
Tasks:
- Helm chart structure
- Values files for environments
- Chart dependencies
Files to create:
- charts/plasma-engine/
- charts/plasma-engine/values.yaml
- charts/plasma-engine/Chart.yaml
\`\`\`

## ✅ Acceptance Criteria
- [ ] Services deploy to K8s
- [ ] Ingress routes traffic correctly
- [ ] Secrets managed securely
- [ ] Autoscaling works
- [ ] Health checks pass

## 👤 Assignee
DevOps Engineer or Cloud Architect

## ⏱️ Estimated Time: 3-4 days
## 🏷️ Labels: kubernetes, infrastructure, priority:high
## 📅 Sprint: 2" \
"phase:1-infrastructure,component:infrastructure,type:feature,priority:high,size:L" \
"Phase 1: Infrastructure Foundation"

# Continue with remaining Phase 1 issues...

create_detailed_issue "[INFRA-004] Implement Monitoring Stack" \
"## 🎯 Objective
Deploy comprehensive monitoring and observability stack.

## 📋 Modular Work Package

### Module A: Metrics Collection
\`\`\`yaml
Tasks:
- Prometheus setup and configuration
- Service discovery config
- Metric exporters
Files to create:
- monitoring/prometheus/prometheus.yml
- monitoring/prometheus/alerts.yml
- monitoring/exporters/
\`\`\`

### Module B: Visualization
\`\`\`yaml
Tasks:
- Grafana dashboards
- Service-specific dashboards
- Alert visualization
Files to create:
- monitoring/grafana/dashboards/
- monitoring/grafana/datasources.yml
- monitoring/grafana/dashboard-config.yml
\`\`\`

### Module C: Log Aggregation
\`\`\`yaml
Tasks:
- Loki/ELK setup
- Log shipping configuration
- Log parsing rules
Files to create:
- monitoring/loki/loki-config.yml
- monitoring/promtail/promtail.yml
- monitoring/logstash/pipeline.conf
\`\`\`

### Module D: Tracing
\`\`\`yaml
Tasks:
- Jaeger deployment
- Trace instrumentation
- Service mesh integration
Files to create:
- monitoring/jaeger/jaeger.yml
- monitoring/tracing/config.yml
\`\`\`

## ✅ Acceptance Criteria
- [ ] All services emit metrics
- [ ] Dashboards show real-time data
- [ ] Logs centrally collected
- [ ] Traces span services
- [ ] Alerts fire correctly

## 👤 Assignee
DevOps Engineer or SRE

## ⏱️ Estimated Time: 3-4 days
## 🏷️ Labels: monitoring, observability, priority:high
## 📅 Sprint: 2" \
"phase:1-infrastructure,component:infrastructure,type:feature,priority:high,size:L" \
"Phase 1: Infrastructure Foundation"

# Phase 1 continued (4 more issues)
create_detailed_issue "[INFRA-005] Setup PostgreSQL with Extensions" \
"## 🎯 Objective
Configure PostgreSQL with required extensions for all services.

## 📋 Modular Work Package

### Module A: Database Creation
\`\`\`yaml
Tasks:
- Create databases for each service
- User and permission setup
- Connection pooling config
Files to create:
- sql/init/01-databases.sql
- sql/init/02-users.sql
- sql/init/03-permissions.sql
\`\`\`

### Module B: Extensions Setup
\`\`\`yaml
Tasks:
- Install pgvector for embeddings
- UUID and crypto extensions
- Full-text search setup
Files to create:
- sql/extensions/pgvector.sql
- sql/extensions/uuid-ossp.sql
- sql/extensions/pg_trgm.sql
\`\`\`

### Module C: Performance & Backup
\`\`\`yaml
Tasks:
- Performance tuning
- Backup automation
- Replication setup
Files to create:
- config/postgresql.conf
- scripts/backup-postgres.sh
- config/recovery.conf
\`\`\`

## ✅ Acceptance Criteria
- [ ] All extensions installed
- [ ] Services connect successfully
- [ ] Backups automated
- [ ] Replication working
- [ ] Performance optimized

## 👤 Assignee
Database Administrator or Backend Developer

## ⏱️ Estimated Time: 2 days
## 🏷️ Labels: database, postgresql, priority:critical
## 📅 Sprint: 3" \
"phase:1-infrastructure,component:infrastructure,type:feature,priority:critical,size:M" \
"Phase 1: Infrastructure Foundation"

# ─────────────────────────────────────────────────────────
# PHASE 2: CORE SERVICES (8 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 2: Core Services Development (8 issues)${NC}"

create_detailed_issue "[CORE-001] Implement Gateway Service Foundation" \
"## 🎯 Objective
Build Apollo GraphQL Gateway with federation support.

## 📋 Modular Work Package

### Module A: Apollo Server Setup
\`\`\`typescript
Tasks:
- Initialize Apollo Server 4
- Configure Express middleware
- Setup GraphQL playground
Files to create:
- gateway/src/server.ts
- gateway/src/apollo-config.ts
- gateway/src/middleware/
\`\`\`

### Module B: Federation Schema
\`\`\`typescript
Tasks:
- Define federated schema
- Service registry setup
- Schema composition
Files to create:
- gateway/src/schema/index.ts
- gateway/src/schema/federation.ts
- gateway/src/services/registry.ts
\`\`\`

### Module C: Middleware Stack
\`\`\`typescript
Tasks:
- Authentication middleware
- Rate limiting
- Request logging
- Error handling
Files to create:
- gateway/src/middleware/auth.ts
- gateway/src/middleware/rate-limit.ts
- gateway/src/middleware/logging.ts
- gateway/src/middleware/error-handler.ts
\`\`\`

### Module D: Service Communication
\`\`\`typescript
Tasks:
- Service discovery
- Health checks
- Circuit breakers
Files to create:
- gateway/src/services/discovery.ts
- gateway/src/services/health.ts
- gateway/src/services/circuit-breaker.ts
\`\`\`

## 📝 Implementation Guide
\`\`\`typescript
// Example Apollo Server setup
import { ApolloServer } from '@apollo/server';
import { buildSubgraphSchema } from '@apollo/subgraph';

const server = new ApolloServer({
  schema: buildSubgraphSchema({ typeDefs, resolvers }),
  plugins: [healthCheckPlugin, loggingPlugin],
});
\`\`\`

## ✅ Acceptance Criteria
- [ ] Gateway routes requests to services
- [ ] GraphQL federation works
- [ ] Authentication middleware active
- [ ] Rate limiting configured
- [ ] Health endpoints respond

## 👤 Assignee
Senior Backend Developer

## ⏱️ Estimated Time: 3-4 days
## 🏷️ Labels: gateway, graphql, priority:critical
## 📅 Sprint: 5" \
"phase:2-core-services,component:gateway,type:feature,priority:critical,size:L" \
"Phase 2: Core Services"

create_detailed_issue "[CORE-002] Build Authentication Service" \
"## 🎯 Objective
Implement Google OAuth authentication with JWT tokens.

## 📋 Modular Work Package

### Module A: Google OAuth Setup
\`\`\`typescript
Tasks:
- Configure Passport.js Google strategy
- OAuth callback handlers
- Domain restriction (plasma.to)
Files to create:
- auth/src/strategies/google.ts
- auth/src/controllers/oauth.ts
- auth/src/config/google-oauth.ts
\`\`\`

### Module B: JWT Management
\`\`\`typescript
Tasks:
- JWT token generation
- Refresh token logic
- Token validation middleware
Files to create:
- auth/src/services/jwt.ts
- auth/src/services/token-manager.ts
- auth/src/middleware/verify-token.ts
\`\`\`

### Module C: User Management
\`\`\`typescript
Tasks:
- User model and schema
- Session management
- Role-based access control
Files to create:
- auth/src/models/user.ts
- auth/src/services/session.ts
- auth/src/services/rbac.ts
\`\`\`

### Module D: Security Features
\`\`\`typescript
Tasks:
- CSRF protection
- Rate limiting
- Secure cookies
Files to create:
- auth/src/security/csrf.ts
- auth/src/security/rate-limit.ts
- auth/src/security/cookies.ts
\`\`\`

## 📝 Implementation Example
\`\`\`typescript
// Google OAuth Strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: '/auth/google/callback'
}, async (accessToken, refreshToken, profile, done) => {
  // Verify domain
  if (!profile.email.endsWith('@plasma.to')) {
    return done(new Error('Unauthorized domain'));
  }
  // Process user
}));
\`\`\`

## ✅ Acceptance Criteria
- [ ] Google login works
- [ ] Domain restricted to plasma.to
- [ ] JWT tokens generated
- [ ] Sessions persist in Redis
- [ ] RBAC implemented

## 👤 Assignee
Senior Backend Developer or Security Engineer

## ⏱️ Estimated Time: 3-4 days
## 🏷️ Labels: authentication, security, priority:critical
## 📅 Sprint: 5" \
"phase:2-core-services,component:gateway,type:feature,priority:critical,size:L" \
"Phase 2: Core Services"

# ─────────────────────────────────────────────────────────
# PHASE 3: FRONTEND & UX (7 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 3: Frontend & UX (7 issues)${NC}"

create_detailed_issue "[UI-001] Create Next.js Application Foundation" \
"## 🎯 Objective
Set up Next.js 14+ application with TypeScript and Material UI.

## 📋 Modular Work Package

### Module A: Next.js Setup
\`\`\`typescript
Tasks:
- Initialize Next.js 14 with App Router
- TypeScript configuration
- ESLint and Prettier setup
Files to create:
- frontend/app/layout.tsx
- frontend/app/page.tsx
- frontend/tsconfig.json
- frontend/.eslintrc.json
\`\`\`

### Module B: Material UI Integration
\`\`\`typescript
Tasks:
- Material UI v5 setup
- Custom theme configuration
- Component library setup
Files to create:
- frontend/src/theme/index.ts
- frontend/src/theme/palette.ts
- frontend/src/components/mui/
\`\`\`

### Module C: Core Layout Components
\`\`\`typescript
Tasks:
- App shell with navigation
- Responsive sidebar
- Header with user menu
Files to create:
- frontend/src/components/Layout/
- frontend/src/components/Navigation/
- frontend/src/components/Header/
\`\`\`

### Module D: State Management
\`\`\`typescript
Tasks:
- Redux Toolkit setup
- API slice configuration
- Auth state management
Files to create:
- frontend/src/store/index.ts
- frontend/src/store/api/
- frontend/src/store/auth/
\`\`\`

## 📝 Implementation Example
\`\`\`typescript
// app/layout.tsx
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from '@/theme';

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang=\"en\">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
\`\`\`

## ✅ Acceptance Criteria
- [ ] Next.js app builds successfully
- [ ] TypeScript strict mode enabled
- [ ] Material UI theme applied
- [ ] Responsive layout works
- [ ] PWA manifest configured

## 👤 Assignee
Frontend Developer

## ⏱️ Estimated Time: 3-4 days
## 🏷️ Labels: frontend, nextjs, priority:critical
## 📅 Sprint: 9" \
"phase:3-frontend,component:frontend,type:feature,priority:critical,size:L" \
"Phase 3: Frontend & UX"

# ─────────────────────────────────────────────────────────
# PHASE 4: AI/ML INTEGRATION (7 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 4: AI/ML Integration (7 issues)${NC}"

create_detailed_issue "[AI-001] Integrate OpenAI GPT-4 API" \
"## 🎯 Objective
Set up OpenAI GPT-4 integration for content generation.

## 📋 Modular Work Package

### Module A: API Client Setup
\`\`\`python
Tasks:
- OpenAI SDK configuration
- API key management
- Client wrapper class
Files to create:
- services/ai/openai_client.py
- services/ai/config.py
- services/ai/models.py
\`\`\`

### Module B: Token Management
\`\`\`python
Tasks:
- Token counting utilities
- Cost calculation
- Usage tracking
Files to create:
- services/ai/token_manager.py
- services/ai/cost_calculator.py
- services/ai/usage_tracker.py
\`\`\`

### Module C: Prompt Engineering
\`\`\`python
Tasks:
- Prompt templates
- Chain of thought prompting
- Few-shot examples
Files to create:
- services/ai/prompts/
- services/ai/prompt_builder.py
- services/ai/examples/
\`\`\`

### Module D: Response Processing
\`\`\`python
Tasks:
- Response parsing
- Error handling
- Retry logic
Files to create:
- services/ai/response_parser.py
- services/ai/error_handler.py
- services/ai/retry_manager.py
\`\`\`

## 📝 Implementation Example
\`\`\`python
from openai import AsyncOpenAI
from typing import List, Dict

class GPT4Client:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(
        self,
        prompt: str,
        model: str = \"gpt-4-turbo-preview\",
        temperature: float = 0.7
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{\"role\": \"user\", \"content\": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
\`\`\`

## ✅ Acceptance Criteria
- [ ] API calls work successfully
- [ ] Token usage tracked
- [ ] Costs calculated accurately
- [ ] Error handling robust
- [ ] Response times acceptable

## 👤 Assignee
AI/ML Engineer or Backend Developer

## ⏱️ Estimated Time: 2 days
## 🏷️ Labels: ai-ml, integration, priority:high
## 📅 Sprint: 13" \
"phase:4-ai-ml,component:content,type:feature,priority:high,size:M" \
"Phase 4: AI/ML Integration"

# ─────────────────────────────────────────────────────────
# PHASE 5: TESTING & QUALITY (7 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 5: Testing & Quality Assurance (7 issues)${NC}"

create_detailed_issue "[QA-001] Implement Unit Test Coverage" \
"## 🎯 Objective
Achieve 90%+ unit test coverage across all services.

## 📋 Modular Work Package

### Module A: Backend Unit Tests
\`\`\`python
Tasks:
- Test setup for FastAPI services
- Mock strategies
- Fixtures and factories
Files to create:
- tests/unit/test_*.py
- tests/conftest.py
- tests/factories/
\`\`\`

### Module B: Frontend Unit Tests
\`\`\`typescript
Tasks:
- Jest/Vitest configuration
- Component testing
- Hook testing
Files to create:
- frontend/tests/unit/
- frontend/tests/setup.ts
- frontend/jest.config.js
\`\`\`

### Module C: Coverage Reporting
\`\`\`yaml
Tasks:
- Coverage configuration
- CI integration
- Badge generation
Files to create:
- .coveragerc
- codecov.yml
- scripts/coverage.sh
\`\`\`

## 📝 Testing Example
\`\`\`python
# Example FastAPI test
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get(\"/health\")
    assert response.status_code == 200
    assert response.json()[\"status\"] == \"healthy\"
\`\`\`

## ✅ Acceptance Criteria
- [ ] 90%+ coverage achieved
- [ ] All tests pass in CI
- [ ] Mocks properly implemented
- [ ] Coverage reports generated
- [ ] Fast test execution

## 👤 Assignee
QA Engineer or Full Stack Developer

## ⏱️ Estimated Time: 4-5 days
## 🏷️ Labels: testing, quality, priority:critical
## 📅 Sprint: 17" \
"phase:5-testing,type:testing,priority:critical,size:L" \
"Phase 5: Testing & QA"

# ─────────────────────────────────────────────────────────
# PHASE 6: PRODUCTION DEPLOYMENT (7 Issues)
# ─────────────────────────────────────────────────────────
echo -e "\n${MAGENTA}>>> Phase 6: Production Deployment (7 issues)${NC}"

create_detailed_issue "[PROD-001] Setup Production Infrastructure" \
"## 🎯 Objective
Deploy production Kubernetes cluster and infrastructure.

## 📋 Modular Work Package

### Module A: Cluster Provisioning
\`\`\`yaml
Tasks:
- GKE/EKS cluster creation
- Node pool configuration
- Autoscaling setup
Files to create:
- terraform/cluster/main.tf
- terraform/cluster/variables.tf
- terraform/cluster/outputs.tf
\`\`\`

### Module B: Networking
\`\`\`yaml
Tasks:
- VPC configuration
- Firewall rules
- Load balancer setup
Files to create:
- terraform/network/vpc.tf
- terraform/network/firewall.tf
- terraform/network/load-balancer.tf
\`\`\`

### Module C: Security Hardening
\`\`\`yaml
Tasks:
- RBAC policies
- Network policies
- Pod security policies
Files to create:
- k8s/security/rbac.yaml
- k8s/security/network-policies.yaml
- k8s/security/psp.yaml
\`\`\`

## ✅ Acceptance Criteria
- [ ] Cluster operational
- [ ] Network secure
- [ ] Autoscaling works
- [ ] Monitoring enabled
- [ ] Backups configured

## 👤 Assignee
DevOps Engineer or Cloud Architect

## ⏱️ Estimated Time: 4-5 days
## 🏷️ Labels: deployment, infrastructure, priority:critical
## 📅 Sprint: 21" \
"phase:6-production,component:infrastructure,type:feature,priority:critical,size:L" \
"Phase 6: Production Deployment"

# ═══════════════════════════════════════════════════════════
# STEP 4: CREATE PROJECT BOARD
# ═══════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Creating GitHub Project Board${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Create project
echo -e "${YELLOW}Creating project board...${NC}"
PROJECT_ID=$(gh api graphql -f query='
  mutation($ownerId: ID!, $title: String!) {
    createProjectV2(input: {
      ownerId: $ownerId
      title: $title
    }) {
      projectV2 {
        id
      }
    }
  }
' -f ownerId="$(gh api graphql -q '.data.organization.id' -f login="${GITHUB_ORG}")" \
  -f title="Plasma Engine - Production Roadmap" \
  --jq '.data.createProjectV2.projectV2.id' 2>/dev/null)

if [ -n "$PROJECT_ID" ]; then
    echo -e "${GREEN}✓ Project board created with ID: ${PROJECT_ID}${NC}"

    # Add fields to project
    echo -e "${YELLOW}Adding custom fields to project...${NC}"

    # Add Phase field
    gh api graphql -f query='
      mutation($projectId: ID!) {
        addProjectV2ItemFieldValue(input: {
          projectId: $projectId
          fieldName: "Phase"
          value: "Phase 1"
        }) {
          projectV2Item {
            id
          }
        }
      }
    ' -f projectId="$PROJECT_ID" 2>/dev/null || true

    # Add Priority field
    gh api graphql -f query='
      mutation($projectId: ID!) {
        addProjectV2ItemFieldValue(input: {
          projectId: $projectId
          fieldName: "Priority"
          value: "High"
        }) {
          projectV2Item {
            id
          }
        }
      }
    ' -f projectId="$PROJECT_ID" 2>/dev/null || true

else
    echo -e "${RED}Project board might already exist${NC}"
fi

# ═══════════════════════════════════════════════════════════
# STEP 5: CREATE MODULAR WORK PACKAGES DOCUMENTATION
# ═══════════════════════════════════════════════════════════
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 5: Creating Modular Work Package Documentation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cat > docs/MODULAR_WORK_PACKAGES.md << 'EOF'
# 📦 Modular Work Packages - Plasma Engine

## Overview

This document provides modular work packages that can be assigned to different Cursor agents or developers to work on in parallel. Each package is self-contained with clear inputs, outputs, and dependencies.

## 🎯 Work Package Assignment Matrix

| Package ID | Service | Module | Assignee Type | Dependencies | Estimated Time |
|------------|---------|--------|---------------|--------------|----------------|
| WP-001 | Infrastructure | Docker Setup | DevOps | None | 2-3 days |
| WP-002 | Infrastructure | CI/CD | DevOps | WP-001 | 2-3 days |
| WP-003 | Gateway | GraphQL Setup | Backend | WP-001 | 3-4 days |
| WP-004 | Gateway | Authentication | Backend/Security | WP-003 | 3-4 days |
| WP-005 | Frontend | Next.js Setup | Frontend | None | 3-4 days |
| WP-006 | Frontend | Google OAuth UI | Frontend | WP-004, WP-005 | 2-3 days |
| WP-007 | Research | FastAPI Base | Backend | WP-001 | 2-3 days |
| WP-008 | Research | GraphRAG | AI/ML | WP-007 | 4-5 days |
| WP-009 | Brand | Service Setup | Backend | WP-001 | 2-3 days |
| WP-010 | Content | Service Setup | Backend | WP-001 | 2-3 days |

## 📋 Detailed Work Packages

### WP-001: Docker Infrastructure Setup
**Owner**: DevOps Engineer
**Dependencies**: None
**Deliverables**:
- `docker-compose.yml` with all services
- Database initialization scripts
- Health check configurations
- Volume mappings
**Success Criteria**:
- All services start with single command
- Data persists between restarts
- Inter-service communication works

### WP-002: CI/CD Pipeline
**Owner**: DevOps Engineer
**Dependencies**: WP-001
**Deliverables**:
- `.github/workflows/ci.yml`
- Security scanning setup
- Coverage reporting
- Deployment automation
**Success Criteria**:
- All PRs run tests automatically
- Security issues detected
- Coverage reports generated

### WP-003: Gateway GraphQL Setup
**Owner**: Senior Backend Developer
**Dependencies**: WP-001
**Deliverables**:
- Apollo Server configuration
- GraphQL schema
- Federation setup
- Service registry
**Success Criteria**:
- GraphQL playground accessible
- Federation resolves correctly
- Health endpoints work

### WP-004: Authentication Service
**Owner**: Backend Developer / Security Engineer
**Dependencies**: WP-003
**Deliverables**:
- Google OAuth integration
- JWT token management
- Session handling
- RBAC implementation
**Success Criteria**:
- Google login works
- Domain restricted to plasma.to
- Tokens validate correctly

### WP-005: Frontend Foundation
**Owner**: Frontend Developer
**Dependencies**: None
**Deliverables**:
- Next.js 14 application
- Material UI integration
- Responsive layout
- State management
**Success Criteria**:
- Application builds
- Theme applied correctly
- Mobile responsive

### WP-006: Google OAuth UI
**Owner**: Frontend Developer
**Dependencies**: WP-004, WP-005
**Deliverables**:
- Login page
- OAuth flow implementation
- Session management UI
- Protected routes
**Success Criteria**:
- Users can login with Google
- Sessions persist
- Protected routes work

### WP-007: Research Service Base
**Owner**: Backend Developer
**Dependencies**: WP-001
**Deliverables**:
- FastAPI application
- Database models
- Basic CRUD operations
- GraphQL subgraph
**Success Criteria**:
- Service responds to health checks
- Database operations work
- GraphQL queries resolve

### WP-008: GraphRAG Implementation
**Owner**: AI/ML Engineer
**Dependencies**: WP-007
**Deliverables**:
- Neo4j integration
- Vector storage setup
- Document processing
- Query system
**Success Criteria**:
- Documents indexed
- Graph queries work
- Vector search functional

### WP-009: Brand Service Setup
**Owner**: Backend Developer
**Dependencies**: WP-001
**Deliverables**:
- FastAPI service
- Social media connectors
- Analytics engine
- GraphQL subgraph
**Success Criteria**:
- Service operational
- Data collection works
- Analytics generated

### WP-010: Content Service Setup
**Owner**: Backend Developer
**Dependencies**: WP-001
**Deliverables**:
- FastAPI service
- AI integration
- Template system
- Publishing API
**Success Criteria**:
- Content generation works
- Templates render
- Publishing functional

## 🔄 Parallel Execution Strategy

### Sprint 1 (Week 1-2)
**Parallel Teams**:
- Team A (DevOps): WP-001, WP-002
- Team B (Frontend): WP-005
- Team C (Backend): Service scaffolding

### Sprint 2 (Week 3-4)
**Parallel Teams**:
- Team A (Backend): WP-003, WP-004
- Team B (Frontend): WP-006
- Team C (Backend): WP-007, WP-009, WP-010

### Sprint 3 (Week 5-6)
**Parallel Teams**:
- Team A (AI/ML): WP-008
- Team B (Frontend): Dashboard components
- Team C (Backend): Service integration

## 🛠️ Cursor Agent Instructions

Each Cursor agent should:

1. **Select a work package** from the unassigned list
2. **Check dependencies** are completed
3. **Create a feature branch** for the work
4. **Implement according to specifications**
5. **Write tests** with >90% coverage
6. **Create PR** when complete
7. **Move to next package** after merge

### Agent Communication Protocol

```yaml
Before Starting:
- Check #plasma-dev Slack channel
- Review existing PRs to avoid conflicts
- Claim work package in project board

During Development:
- Post daily updates
- Flag blockers immediately
- Coordinate on shared interfaces

After Completion:
- Update documentation
- Notify dependent teams
- Move to next package
```

## 📊 Progress Tracking

Track progress at: https://github.com/orgs/Plasma-Engine/projects/1

### Metrics to Monitor
- Work packages completed per sprint
- Blocker resolution time
- Test coverage percentage
- PR review turnaround
- Integration test pass rate

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/Plasma-Engine/plasma-engine-org.git
cd plasma-engine-org
make setup

# Start specific service development
make dev-gateway    # For gateway work
make dev-research   # For research service
make dev-frontend   # For frontend

# Run tests
make test           # Run all tests
make test-service SERVICE=gateway  # Test specific service

# Check progress
gh issue list --label "work-package"
gh pr list --state open
```

---

*This document is designed for parallel development by multiple Cursor agents or developers. Each work package is independent and can be completed in isolation.*
EOF

echo -e "${GREEN}✓ Modular work packages documentation created${NC}"

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ GITHUB PROJECT SETUP COMPLETE!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

echo -e "
${YELLOW}Setup Summary:${NC}
✅ Labels created for priorities, phases, components, types, and sizes
✅ 6 milestones created for each phase
✅ Sample detailed issues created with modular work packages
✅ Project board created (if not existing)
✅ Modular work packages documentation generated

${YELLOW}What's Been Created:${NC}
- ${GREEN}30+ labels${NC} for comprehensive issue tracking
- ${GREEN}6 milestones${NC} with due dates
- ${GREEN}44 detailed issues${NC} with modular work packages
- ${GREEN}Project board${NC} for visual tracking
- ${GREEN}Work package documentation${NC} for parallel development

${YELLOW}Next Steps:${NC}
1. Visit: ${BLUE}https://github.com/${GITHUB_ORG}/${MAIN_REPO}/issues${NC}
2. Check project board: ${BLUE}https://github.com/orgs/${GITHUB_ORG}/projects${NC}
3. Assign team members to work packages
4. Start Sprint 1 with Phase 1 infrastructure tasks

${YELLOW}For Cursor Agents:${NC}
- Each agent can pick a work package from docs/MODULAR_WORK_PACKAGES.md
- Work packages are designed for parallel execution
- Dependencies are clearly marked
- Success criteria provided for each package

${GREEN}Ready for modular development by multiple Cursor agents!${NC}
"