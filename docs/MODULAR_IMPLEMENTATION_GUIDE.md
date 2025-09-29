# 📦 Modular Implementation Guide - Plasma Engine

## 🎯 Complete Project Implementation Map

This guide provides a complete modular implementation roadmap for the Plasma Engine project. Each module can be worked on independently by different Cursor agents or developers.

---

## 🏗️ Phase 1: Infrastructure Foundation (Weeks 1-4)

### Module 1A: Docker Environment
**Files to Create/Edit**:
```
docker-compose.yml ✅ (created)
docker-compose.override.yml
.env.example
scripts/init.sql ✅ (created)
scripts/docker-entrypoint.sh
```

**Implementation Steps**:
1. Docker Compose configuration for all services
2. Database initialization scripts
3. Health check configurations
4. Volume mappings for persistence
5. Network configuration

**Commands**:
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

### Module 1B: CI/CD Pipeline
**Files to Create/Edit**:
```
.github/workflows/ci.yml ✅ (created)
.github/workflows/cd.yml
.github/workflows/security.yml
.github/workflows/deploy.yml
codecov.yml
```

**Implementation Steps**:
1. GitHub Actions for testing
2. Security scanning with Snyk
3. Coverage reporting
4. Docker image building
5. Deployment automation

### Module 1C: Kubernetes Setup
**Files to Create**:
```
k8s/namespaces.yaml
k8s/services/gateway/deployment.yaml
k8s/services/gateway/service.yaml
k8s/config/configmap.yaml
k8s/config/secrets.yaml
k8s/ingress/ingress.yaml
helm/plasma-engine/Chart.yaml
helm/plasma-engine/values.yaml
```

**Implementation Steps**:
1. Create K8s manifests for each service
2. Configure Ingress controller
3. Set up ConfigMaps and Secrets
4. Create Helm charts
5. Test deployment locally with minikube

---

## 💻 Phase 2: Core Services (Weeks 5-8)

### Module 2A: Gateway Service (TypeScript)
**Directory**: `plasma-engine-gateway/`

**Files to Create**:
```typescript
src/server.ts
src/apollo/server.ts
src/apollo/schema.ts
src/apollo/federation.ts
src/middleware/auth.ts
src/middleware/rate-limit.ts
src/services/discovery.ts
src/config/index.ts
```

**Implementation**:
```typescript
// src/server.ts
import { ApolloServer } from '@apollo/server';
import { buildSubgraphSchema } from '@apollo/subgraph';
import express from 'express';

const app = express();

const server = new ApolloServer({
  schema: buildSubgraphSchema({
    typeDefs,
    resolvers
  })
});

await server.start();
app.use('/graphql', expressMiddleware(server));
```

### Module 2B: Authentication Service
**Directory**: `plasma-engine-gateway/src/auth/`

**Files to Create**:
```typescript
auth/strategies/google.ts
auth/services/jwt.ts
auth/models/user.ts
auth/middleware/verify.ts
auth/controllers/oauth.ts
```

**Google OAuth Implementation**:
```typescript
// auth/strategies/google.ts
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: '/auth/google/callback'
}, async (accessToken, refreshToken, profile, done) => {
  // Verify @plasma.to domain
  if (!profile.emails[0].value.endsWith('@plasma.to')) {
    return done(new Error('Unauthorized domain'));
  }
  // Create/update user
  const user = await User.findOrCreate({
    googleId: profile.id,
    email: profile.emails[0].value,
    name: profile.displayName
  });
  return done(null, user);
}));
```

### Module 2C: Research Service (Python)
**Directory**: `plasma-engine-research/`

**Files to Create**:
```python
app/main.py
app/api/routes.py
app/models/document.py
app/services/graphrag.py
app/services/neo4j_client.py
app/services/embeddings.py
app/config.py
```

**FastAPI Setup**:
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Research Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Module 2D: Brand Service (Python)
**Directory**: `plasma-engine-brand/`

**Files to Create**:
```python
app/main.py
app/api/monitoring.py
app/services/social_media.py
app/services/sentiment.py
app/services/analytics.py
app/models/brand.py
```

### Module 2E: Content Service (Python)
**Directory**: `plasma-engine-content/`

**Files to Create**:
```python
app/main.py
app/api/generation.py
app/services/ai_generator.py
app/services/templates.py
app/models/content.py
```

### Module 2F: Agent Service (Python)
**Directory**: `plasma-engine-agent/`

**Files to Create**:
```python
app/main.py
app/api/orchestration.py
app/services/agents.py
app/services/tools.py
app/models/task.py
```

---

## 🎨 Phase 3: Frontend (Weeks 9-12)

### Module 3A: Next.js Foundation
**Directory**: `plasma-engine-frontend/`

**Files to Create**:
```typescript
app/layout.tsx
app/page.tsx
app/dashboard/page.tsx
app/login/page.tsx
src/theme/index.ts
src/components/Layout.tsx
src/store/index.ts
```

**Next.js 14 App Router Setup**:
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'
import { Providers } from '@/components/Providers'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### Module 3B: Authentication UI
**Files to Create**:
```typescript
app/login/page.tsx
src/components/GoogleSignIn.tsx
src/hooks/useAuth.ts
src/services/auth.ts
```

**Google Sign-In Component**:
```typescript
// src/components/GoogleSignIn.tsx
import { signIn } from 'next-auth/react';
import { Button } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';

export function GoogleSignIn() {
  return (
    <Button
      variant="contained"
      startIcon={<GoogleIcon />}
      onClick={() => signIn('google')}
    >
      Sign in with Google
    </Button>
  );
}
```

### Module 3C: Dashboard Components
**Files to Create**:
```typescript
src/components/Dashboard/MetricsCard.tsx
src/components/Dashboard/ActivityFeed.tsx
src/components/Dashboard/QuickActions.tsx
src/components/Charts/index.tsx
```

### Module 3D: Service-Specific UIs
**Research UI**:
```typescript
app/research/page.tsx
src/components/Research/QueryBuilder.tsx
src/components/Research/GraphViewer.tsx
src/components/Research/ResultsList.tsx
```

**Brand UI**:
```typescript
app/brand/page.tsx
src/components/Brand/SocialFeed.tsx
src/components/Brand/SentimentChart.tsx
src/components/Brand/AlertsPanel.tsx
```

**Content UI**:
```typescript
app/content/page.tsx
src/components/Content/Editor.tsx
src/components/Content/Templates.tsx
src/components/Content/AIAssistant.tsx
```

---

## 🤖 Phase 4: AI/ML Integration (Weeks 13-16)

### Module 4A: OpenAI Integration
**Directory**: `plasma-engine-content/app/services/`

**Files to Create**:
```python
ai/openai_client.py
ai/gpt4_service.py
ai/prompt_templates.py
ai/token_manager.py
```

**Implementation**:
```python
# ai/openai_client.py
from openai import AsyncOpenAI
from typing import Optional, List, Dict

class GPT4Service:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_content(
        self,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
```

### Module 4B: Claude Integration
**Files to Create**:
```python
ai/anthropic_client.py
ai/claude_service.py
```

### Module 4C: GraphRAG System
**Directory**: `plasma-engine-research/app/services/`

**Files to Create**:
```python
graphrag/ingestion.py
graphrag/graph_builder.py
graphrag/query_engine.py
graphrag/embeddings.py
```

**GraphRAG Implementation**:
```python
# graphrag/graph_builder.py
from neo4j import AsyncGraphDatabase
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

class GraphBuilder:
    def __init__(self, neo4j_uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(
            neo4j_uri, auth=(user, password)
        )

    async def build_knowledge_graph(self, documents: List[str]):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        for doc in documents:
            chunks = splitter.split_text(doc)
            await self._create_nodes_and_edges(chunks)

    async def _create_nodes_and_edges(self, chunks: List[str]):
        async with self.driver.session() as session:
            for i, chunk in enumerate(chunks):
                # Create node
                await session.run(
                    "CREATE (n:Document {id: $id, content: $content})",
                    id=i, content=chunk
                )
                # Create edges between consecutive chunks
                if i > 0:
                    await session.run(
                        "MATCH (a:Document {id: $prev_id}), "
                        "(b:Document {id: $curr_id}) "
                        "CREATE (a)-[:FOLLOWS]->(b)",
                        prev_id=i-1, curr_id=i
                    )
```

### Module 4D: Embedding Pipeline
**Files to Create**:
```python
embeddings/generator.py
embeddings/vector_store.py
embeddings/search.py
```

---

## ✅ Phase 5: Testing (Weeks 17-20)

### Module 5A: Unit Tests
**Backend Tests**:
```python
tests/unit/test_auth.py
tests/unit/test_graphrag.py
tests/unit/test_services.py
tests/conftest.py
```

**Frontend Tests**:
```typescript
tests/unit/components.test.tsx
tests/unit/hooks.test.ts
tests/unit/services.test.ts
```

### Module 5B: Integration Tests
```python
tests/integration/test_api.py
tests/integration/test_database.py
tests/integration/test_services_communication.py
```

### Module 5C: E2E Tests
```typescript
e2e/auth.spec.ts
e2e/dashboard.spec.ts
e2e/workflows.spec.ts
```

---

## 🚀 Phase 6: Production (Weeks 21-26)

### Module 6A: Infrastructure as Code
**Terraform Files**:
```hcl
terraform/main.tf
terraform/variables.tf
terraform/gke.tf
terraform/database.tf
terraform/networking.tf
```

### Module 6B: Monitoring Setup
```yaml
monitoring/prometheus/prometheus.yml
monitoring/grafana/dashboards/
monitoring/alerts/rules.yml
```

### Module 6C: Deployment Scripts
```bash
scripts/deploy.sh
scripts/rollback.sh
scripts/health-check.sh
```

---

## 🎯 Quick Start for Cursor Agents

### For Backend Development:
```bash
# Clone repo
git clone https://github.com/Plasma-Engine/plasma-engine-org.git

# Start infrastructure
docker-compose up -d postgres redis neo4j

# Work on a service
cd plasma-engine-[service]
pip install -e .
uvicorn app.main:app --reload
```

### For Frontend Development:
```bash
# Setup frontend
cd plasma-engine-frontend
npm install
npm run dev

# Access at http://localhost:3000
```

### For Testing:
```bash
# Backend tests
pytest tests/ --cov=app

# Frontend tests
npm test

# E2E tests
npm run test:e2e
```

---

## 📊 Progress Tracking

| Phase | Modules | Status | Completion |
|-------|---------|--------|------------|
| Phase 1 | Infrastructure | 🟡 In Progress | 40% |
| Phase 2 | Core Services | ⏳ Pending | 0% |
| Phase 3 | Frontend | ⏳ Pending | 0% |
| Phase 4 | AI/ML | ⏳ Pending | 0% |
| Phase 5 | Testing | ⏳ Pending | 0% |
| Phase 6 | Production | ⏳ Pending | 0% |

---

## 🔗 Resources

- **GitHub Issues**: https://github.com/Plasma-Engine/plasma-engine-org/issues
- **Project Board**: https://github.com/orgs/Plasma-Engine/projects/1
- **Documentation**: /docs
- **CI/CD Status**: Check GitHub Actions

---

*This guide is designed for parallel development by multiple Cursor agents. Each module is independent and can be completed in isolation.*