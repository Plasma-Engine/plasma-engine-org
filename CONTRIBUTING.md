# Contributing to Plasma Engine

Thank you for your interest in contributing to Plasma Engine! This document provides guidelines and instructions for contributing to any repository within the Plasma Engine organization.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Contribution Types](#contribution-types)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 Getting Started

### Prerequisites

- Git
- Docker Desktop
- Python 3.11+
- Node.js 20+
- GitHub account

### Setting Up Your Development Environment

1. **Fork the repository** you want to contribute to
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/plasma-engine-SERVICE.git
   cd plasma-engine-SERVICE
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/plasma-engine/plasma-engine-SERVICE.git
   ```

4. **Set up the development environment**:
   ```bash
   # For Python services
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt

   # For TypeScript services
   npm install
   ```

5. **Start local dependencies**:
   ```bash
   docker-compose up -d
   ```

## 🔄 Development Process

### Branching Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/[ticket-id]-description**: Feature branches
- **bugfix/[ticket-id]-description**: Bug fix branches
- **hotfix/[ticket-id]-description**: Emergency fixes

### Workflow

1. **Create an issue** or pick an existing one
2. **Create a feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/PE-123-add-new-feature
   ```

3. **Make your changes** following our coding standards
4. **Write/update tests** for your changes
5. **Update documentation** if needed
6. **Commit your changes** using conventional commits:
   ```bash
   git commit -m "feat: add new authentication method"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/PE-123-add-new-feature
   ```

8. **Create a Pull Request** against `develop`

## 🎯 Contribution Types

### 🐛 Bug Reports

- Use the bug report template
- Include reproduction steps
- Provide environment details
- Attach relevant logs

### ✨ Feature Requests

- Use the feature request template
- Explain the use case
- Provide examples
- Consider backward compatibility

### 📝 Documentation

- Fix typos and grammar
- Improve clarity
- Add examples
- Update outdated information

### 💻 Code Contributions

- Bug fixes
- New features
- Performance improvements
- Refactoring

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commits follow conventional format
- [ ] Branch is up-to-date with `develop`

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Fixes #123
```

### Review Process

1. **Automated checks** run (linting, tests, security)
2. **CodeRabbit** provides automated review
3. **Human review** by maintainers
4. **Address feedback** if requested
5. **Approval and merge**

## 📏 Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 88 (Black formatter)
- Docstrings for all public functions

```python
def calculate_score(data: List[float], weights: Dict[str, float]) -> float:
    """
    Calculate weighted score from data points.
    
    Args:
        data: List of data values
        weights: Dictionary of weight factors
        
    Returns:
        Calculated weighted score
    """
    # Implementation
```

### TypeScript

- Use ESLint configuration
- Prefer functional components (React)
- Use TypeScript strict mode
- Document with JSDoc

```typescript
/**
 * Process user authentication request
 * @param credentials - User login credentials
 * @returns Authentication token
 */
export async function authenticate(
  credentials: UserCredentials
): Promise<AuthToken> {
  // Implementation
}
```

### General

- Clear, descriptive variable names
- Comments for complex logic
- No commented-out code
- Consistent formatting

## 🧪 Testing Requirements

### Test Coverage

- Minimum 80% code coverage
- All new features must have tests
- Bug fixes must include regression tests

### Test Types

1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test service interactions
3. **E2E Tests**: Test complete workflows

### Running Tests

```bash
# Python
pytest
pytest --cov=src --cov-report=html

# TypeScript
npm test
npm run test:coverage
```

## 📚 Documentation

### Code Documentation

- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Update README when needed

### API Documentation

- OpenAPI/Swagger for REST APIs
- GraphQL schema documentation
- Include request/response examples

### Architecture Documentation

- Update ADRs for significant decisions
- Maintain architecture diagrams
- Document design patterns used

## 👥 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General discussions and questions
- **Slack**: Real-time chat (invite required)
- **Email**: support@plasma-engine.org

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Contact maintainers

## 🏆 Recognition

We value all contributions! Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for swag (for significant contributions)

## 📋 Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build process or auxiliary tool changes

Examples:
```
feat: add GraphQL subscription support
fix: resolve memory leak in cache manager
docs: update API authentication guide
```

## 🔒 Security

- Never commit secrets or credentials
- Report security issues privately
- Follow OWASP guidelines
- Use dependency scanning

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Plasma Engine! 🚀

**Questions?** Feel free to ask in GitHub Discussions or contact the maintainers.
