# Contributing to Plasma Engine

We love your input! We want to make contributing to Plasma Engine as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Branch Strategy
- `main` - Production branch, automatically deployed
- `develop` - Integration branch for new features
- `feature/*` - Feature branches
- `hotfix/*` - Critical fixes for production

## Getting Started

### Prerequisites
- **Python 3.11+** for backend services
- **Node.js 20+** for gateway service
- **Docker & Docker Compose** for local development
- **Git** for version control

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/plasma-engine/plasma-engine-org.git
   cd plasma-engine-org
   ```

2. **Set up development environment**
   ```bash
   # Install all dependencies
   make install-deps

   # Start infrastructure services
   make start-infra

   # Run all services
   make run-all
   ```

3. **Verify setup**
   ```bash
   # Run tests
   make test-all

   # Run linting
   make lint-all

   # Check services are running
   make ps
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run specific service tests
./scripts/test.sh gateway

# Run all tests with coverage
./scripts/test.sh --coverage

# Run linting
./scripts/lint.sh --fix

# Build to ensure everything compiles
./scripts/build.sh
```

### 4. Commit Your Changes
We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat(gateway): add GraphQL subscription support"
git commit -m "fix(research): resolve memory leak in data processing"
git commit -m "docs: update API documentation"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding missing tests
- `chore`: Build process or auxiliary tool changes

### 5. Submit a Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a pull request through GitHub's interface.

## Code Style Guidelines

### Python (Research, Brand, Content, Agent services)
- **Formatter**: Black (line length: 100)
- **Linter**: Ruff with strict settings
- **Type hints**: Required for all functions
- **Imports**: Sorted with isort

```python
# Good
def process_data(data: List[Dict[str, Any]]) -> ProcessedData:
    """Process raw data into structured format.

    Args:
        data: Raw data list to process

    Returns:
        Processed data object
    """
    return ProcessedData(items=data)

# Bad - no type hints, no docstring
def process_data(data):
    return ProcessedData(items=data)
```

### TypeScript/JavaScript (Gateway service)
- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript rules
- **Style**: Functional programming preferred

```typescript
// Good
interface UserData {
  id: string;
  name: string;
  email: string;
}

const processUser = async (userData: UserData): Promise<User> => {
  return await userService.create(userData);
};

// Bad - any types, no interfaces
const processUser = async (userData: any) => {
  return await userService.create(userData);
};
```

### General Guidelines
- Keep functions small and focused (< 50 lines)
- Use meaningful variable and function names
- Write self-documenting code
- Add comments for complex business logic
- Maintain high test coverage (>90%)

## Testing Standards

### Unit Tests
- Test all public functions
- Mock external dependencies
- Use descriptive test names

```python
def test_user_creation_with_valid_email_creates_user():
    # Given
    user_data = {"email": "test@example.com", "name": "Test User"}

    # When
    user = create_user(user_data)

    # Then
    assert user.email == "test@example.com"
    assert user.name == "Test User"
```

### Integration Tests
- Test service interactions
- Use test databases
- Clean up after tests

### End-to-End Tests
- Test complete user workflows
- Use staging environment
- Run before production deployment

## Documentation

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Document all endpoints, parameters, and responses
- Include example requests/responses

### Code Documentation
- Add docstrings to all functions and classes
- Explain complex algorithms
- Document configuration options

### README Updates
- Keep service READMEs up to date
- Include setup and usage instructions
- Document environment variables

## Performance Guidelines

### Python Services
- Use async/await for I/O operations
- Implement proper database indexing
- Use connection pooling
- Profile memory usage

### Gateway Service
- Implement GraphQL query complexity limits
- Use DataLoader for N+1 query prevention
- Add response caching
- Monitor bundle size

## Security Guidelines

### General
- Never commit secrets to version control
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication/authorization

### Dependencies
- Keep dependencies up to date
- Regularly audit for vulnerabilities
- Use Dependabot for automated updates

### Database
- Use parameterized queries
- Implement proper access controls
- Encrypt sensitive data at rest

## Review Process

### Automated Checks
All PRs must pass:
- ✅ Unit and integration tests
- ✅ Linting and formatting
- ✅ Security scans
- ✅ Type checking
- ✅ Build verification

### Human Review
- At least one approval required
- Focus on:
  - Code correctness and clarity
  - Test coverage and quality
  - Security implications
  - Performance impact
  - Documentation completeness

### AI Review
We use CodeRabbit for additional automated review:
- Code quality analysis
- Security vulnerability detection
- Performance optimization suggestions
- Best practice recommendations

## Deployment

### Staging
- Automatic deployment on merge to `develop`
- Manual testing required
- Performance benchmarks run

### Production
- Automatic deployment on merge to `main`
- Blue-green deployment strategy
- Automatic rollback on failure
- Health checks required

## Issue Guidelines

### Bug Reports
Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information
- Screenshots/logs if applicable

### Feature Requests
Use the feature request template and include:
- Problem description
- Proposed solution
- Alternative solutions considered
- Additional context

### Questions
Use GitHub Discussions for:
- General questions about the project
- Implementation discussions
- Architecture decisions

## Community

### Code of Conduct
This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Request Comments**: Code-specific discussion

## Recognition

Contributors are recognized in several ways:
- Listed in the project README
- Mentioned in release notes
- Invited to become maintainers based on contributions

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

Don't hesitate to ask! Create an issue or start a discussion if you need help getting started.

Thank you for contributing to Plasma Engine! 🚀