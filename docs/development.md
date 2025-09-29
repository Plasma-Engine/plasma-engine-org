# Plasma Engine - Development Guide

## Overview

This guide provides comprehensive instructions for setting up, developing, and contributing to the Plasma Engine platform. It covers everything from initial environment setup to advanced development patterns.

## Development Environment Setup

### Prerequisites

#### Required Software

```bash
# Version requirements
node --version    # >= 20.10.0
python --version  # >= 3.11.0
docker --version  # >= 24.0.0
git --version     # >= 2.40.0

# Package managers
npm --version     # >= 10.0.0
pip --version     # >= 23.0.0
```

#### System Requirements

- **OS**: macOS 12+, Ubuntu 20.04+, or Windows 11 with WSL2
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB available space
- **CPU**: 4+ cores recommended

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/plasma-engine/plasma-engine-org.git
cd plasma-engine-org
```

2. **Run Complete Setup**
```bash
# This will clone all repositories, install dependencies, and initialize databases
make setup
```

3. **Start Development Environment**
```bash
# Start infrastructure services (PostgreSQL, Redis, Neo4j)
make start-infra

# Start all services in development mode
make run-all

# Verify everything is running
make health-check
```

4. **Access Services**
- Gateway (GraphQL): http://localhost:3000/graphql
- Research API: http://localhost:8000/docs
- Brand API: http://localhost:8001/docs
- Content API: http://localhost:8002/docs
- Agent API: http://localhost:8003/docs

### Manual Setup (If make setup fails)

#### 1. Clone All Repositories

```bash
# Clone all service repositories
git clone https://github.com/plasma-engine/plasma-engine-gateway.git
git clone https://github.com/plasma-engine/plasma-engine-research.git
git clone https://github.com/plasma-engine/plasma-engine-brand.git
git clone https://github.com/plasma-engine/plasma-engine-content.git
git clone https://github.com/plasma-engine/plasma-engine-agent.git
git clone https://github.com/plasma-engine/plasma-engine-shared.git
git clone https://github.com/plasma-engine/plasma-engine-infra.git
```

#### 2. Environment Configuration

Create `.env` files for each service:

**Gateway Service** (`plasma-engine-gateway/.env`):
```bash
NODE_ENV=development
PORT=3000
JWT_SECRET=your-super-secret-jwt-key-for-development
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/plasma_gateway
```

**Python Services** (research/brand/content/agent `.env`):
```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/plasma_<service_name>
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
STABILITY_API_KEY=your_stability_api_key
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

#### 3. Infrastructure Setup

```bash
# Start databases and infrastructure
docker-compose up -d postgres redis neo4j elasticsearch

# Wait for services to be ready
sleep 30

# Initialize databases
make init-db
```

#### 4. Service Dependencies

**Gateway Service (TypeScript)**:
```bash
cd plasma-engine-gateway
npm install
npm run build
```

**Python Services**:
```bash
# For each Python service
cd plasma-engine-<service>
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development Workflow

### Branch Strategy

We use GitFlow with the following branches:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Individual feature development
- `hotfix/*` - Emergency fixes for production
- `release/*` - Release preparation

### Creating a New Feature

```bash
# Create and switch to feature branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make your changes
# ... develop feature ...

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
# Create PR targeting develop branch
```

### Commit Message Convention

We follow [Conventional Commits](https://conventionalcommits.org/):

```bash
# Format: type(scope): description
# Examples:
git commit -m "feat(api): add user authentication endpoint"
git commit -m "fix(research): resolve vector search timeout"
git commit -m "docs(readme): update setup instructions"
git commit -m "test(brand): add sentiment analysis tests"
git commit -m "refactor(content): improve content generation pipeline"
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `test` - Adding tests
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `chore` - Maintenance tasks

## Service Development

### Gateway Service (TypeScript)

**Structure:**
```
plasma-engine-gateway/
├── src/
│   ├── index.ts          # Application entry point
│   ├── schema.ts         # GraphQL schema definition
│   ├── resolvers/        # GraphQL resolvers
│   ├── middleware/       # Express middleware
│   ├── auth/            # Authentication logic
│   └── utils/           # Utility functions
├── tests/               # Test files
├── package.json
└── tsconfig.json
```

**Development Commands:**
```bash
cd plasma-engine-gateway

# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Type check
npm run type-check

# Build for production
npm run build
```

**Adding New GraphQL Types:**
```typescript
// src/schema.ts
import { gql } from 'apollo-server-express';

export const typeDefs = gql`
  type User {
    id: ID!
    email: String!
    name: String
    organization: Organization
  }

  type Query {
    me: User
    users: [User!]!
  }

  type Mutation {
    createUser(input: CreateUserInput!): User!
  }
`;
```

### Python Services (FastAPI)

**Structure:**
```
plasma-engine-<service>/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic
│   ├── tasks/            # Celery background tasks
│   └── utils/            # Utility functions
├── tests/                # Test files
├── requirements.txt      # Python dependencies
└── Dockerfile
```

**Development Commands:**
```bash
cd plasma-engine-<service>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run linter
flake8 app/
black app/

# Type checking
mypy app/
```

**Adding New API Endpoints:**
```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.create_user(user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Testing

### Testing Strategy

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test service interactions
3. **API Tests** - Test HTTP endpoints
4. **End-to-End Tests** - Test complete workflows

### TypeScript Testing (Gateway)

**Jest/Vitest Configuration:**
```typescript
// tests/user.test.ts
import request from 'supertest';
import { app } from '../src/index';
import { createTestUser } from './helpers/fixtures';

describe('User API', () => {
  beforeEach(async () => {
    // Setup test database
    await setupTestDb();
  });

  it('should create a new user', async () => {
    const userData = createTestUser();

    const response = await request(app)
      .post('/graphql')
      .send({
        query: `
          mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
              id
              email
              name
            }
          }
        `,
        variables: { input: userData }
      })
      .expect(200);

    expect(response.body.data.createUser).toMatchObject({
      email: userData.email,
      name: userData.name
    });
  });
});
```

### Python Testing (Services)

**Pytest Configuration:**
```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
```

### Running Tests

```bash
# Run all tests for all services
make test-all

# Run tests for specific service
make test-gateway
make test-research
make test-brand

# Run tests with coverage
make test-coverage

# Run integration tests
make test-integration
```

## Database Management

### Database Migrations

**Alembic (Python Services):**
```bash
# Create new migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

**Prisma (TypeScript Services):**
```bash
# Generate migration
npx prisma migrate dev --name add-user-table

# Apply migration
npx prisma migrate deploy

# Reset database
npx prisma migrate reset
```

### Seeding Test Data

```bash
# Seed development database
make seed-dev

# Seed test database
make seed-test
```

## Code Quality

### Linting and Formatting

**TypeScript (ESLint + Prettier):**
```bash
# Check linting
npm run lint

# Fix linting issues
npm run lint -- --fix

# Format code
npm run format
```

**Python (Black + Flake8 + isort):**
```bash
# Format code
black app/

# Sort imports
isort app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

**Pre-commit Configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.4.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files

- repo: https://github.com/psf/black
  rev: 23.3.0
  hooks:
  - id: black

- repo: https://github.com/pycqa/isort
  rev: 5.12.0
  hooks:
  - id: isort

- repo: https://github.com/pre-commit/mirrors-eslint
  rev: v8.43.0
  hooks:
  - id: eslint
    files: \.(js|ts|tsx)$
    additional_dependencies:
    - '@typescript-eslint/eslint-plugin'
    - '@typescript-eslint/parser'
```

## Debugging

### Debug Configuration

**VS Code Launch Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Gateway",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/plasma-engine-gateway/src/index.ts",
      "outFiles": ["${workspaceFolder}/plasma-engine-gateway/build/**/*.js"],
      "env": {
        "NODE_ENV": "development"
      },
      "runtimeArgs": ["-r", "ts-node/register"]
    },
    {
      "name": "Debug Research Service",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/plasma-engine-research/app/main.py",
      "env": {
        "ENVIRONMENT": "development"
      },
      "python": "${workspaceFolder}/plasma-engine-research/venv/bin/python"
    }
  ]
}
```

### Logging

**Structured Logging (Pino for TypeScript):**
```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development' ? {
    target: 'pino-pretty',
    options: { colorize: true }
  } : undefined
});

logger.info({ userId: 123 }, 'User logged in');
logger.error({ error: err }, 'Failed to process request');
```

**Structured Logging (Python):**
```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("User logged in", user_id=123, ip_address="192.168.1.1")
logger.error("Failed to process request", error=str(err), user_id=123)
```

## Performance Optimization

### Caching Strategies

**Redis Caching:**
```python
# Python service caching
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            redis_client.setex(
                cache_key,
                expire_time,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator

@cache_result(expire_time=1800)
async def get_user_profile(user_id: int):
    # Expensive database query
    return await db_query("SELECT * FROM users WHERE id = %s", user_id)
```

### Database Optimization

**Query Optimization:**
```python
# Use database indexes
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Index for frequent lookups
    created_at = Column(DateTime, index=True)        # Index for time-based queries

# Use connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

## Security Guidelines

### Authentication Implementation

**JWT Token Validation:**
```typescript
// TypeScript middleware
import jwt from 'jsonwebtoken';

export const authenticateToken = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.sendStatus(401);
  }

  jwt.verify(token, process.env.JWT_SECRET!, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};
```

**Input Validation:**
```python
# Python input validation with Pydantic
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### Environment Variables

Never commit sensitive data. Use environment variables:

```bash
# .env.example (commit this)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-key

# .env (never commit this)
DATABASE_URL=postgresql://prod_user:secure_password@prod-db:5432/plasma_production
REDIS_URL=redis://prod-redis:6379
JWT_SECRET=ultra-secure-production-key
OPENAI_API_KEY=sk-actual-openai-key
```

## Contributing

### Pull Request Process

1. **Fork and Branch**
```bash
git checkout develop
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Follow coding standards
- Add tests for new functionality
- Update documentation if needed

3. **Test Changes**
```bash
make test-all
make lint-all
```

4. **Submit PR**
- Create descriptive PR title and description
- Link relevant issues
- Request review from maintainers

### Code Review Guidelines

**For Authors:**
- Keep PRs focused and small
- Write clear commit messages
- Add tests for new features
- Update documentation

**For Reviewers:**
- Check functionality and logic
- Verify test coverage
- Review security implications
- Ensure code follows standards

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>
```

**Database Connection Issues:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Reset database
make reset-db
```

**Node Modules Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Python Virtual Environment Issues:**
```bash
# Remove and recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

1. Check existing [GitHub Issues](https://github.com/plasma-engine/plasma-engine-org/issues)
2. Review the [troubleshooting guide](troubleshooting.md)
3. Ask in the development Slack channel
4. Contact the platform engineering team

---

This development guide provides comprehensive coverage for contributing to the Plasma Engine platform. Follow these guidelines to ensure consistent, high-quality development practices across the entire codebase.