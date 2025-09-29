# Plasma Engine Test Suite Documentation

## Overview

This comprehensive test suite provides complete testing coverage for all Plasma Engine components with >90% code coverage, automated CI/CD integration, and performance benchmarking.

## 📁 Test Structure

```
tests/
├── conftest.py                 # Global pytest configuration and fixtures
├── fixtures/                   # Shared test data and fixtures
│   ├── __init__.py
│   └── api_responses.py        # Standard API response fixtures
├── mocks/                      # Mock services and utilities
│   ├── __init__.py
│   └── external_services.py    # Mock external APIs (OpenAI, Anthropic, etc.)
├── helpers/                    # Test utility functions
│   ├── __init__.py
│   └── test_utils.py           # Helper classes and functions
├── integration/                # Inter-service workflow tests
│   └── test_service_communication.py
├── e2e/                        # End-to-end tests with Playwright
│   ├── conftest.py
│   └── test_user_workflows.py
├── performance/                # Performance benchmarking tests
│   └── test_benchmarks.py
└── requirements-*.txt          # Test-specific dependencies
```

### Service-Specific Tests

Each service has its own test directory:
- `plasma-engine-research/tests/`
- `plasma-engine-content/tests/`
- `plasma-engine-brand/tests/`
- `plasma-engine-agent/tests/`
- `plasma-engine-gateway/tests/`

## 🚀 Running Tests

### Quick Start - All Tests

```bash
# Run all Python service tests
pytest

# Run specific service tests
cd plasma-engine-research && pytest tests/

# Run Gateway (Node.js) tests
cd plasma-engine-gateway && npm test

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Test Categories

#### Unit Tests
Test individual functions and classes in isolation:

```bash
# Run only unit tests
pytest -m unit

# Run unit tests for specific service
cd plasma-engine-research && pytest tests/test_config.py tests/test_main.py
```

#### Integration Tests
Test communication between services:

```bash
# Run integration tests
pytest tests/integration/ -v

# Run with service mocking
pytest tests/integration/ --mock-services
```

#### End-to-End Tests
Test complete user workflows using Playwright:

```bash
# Install E2E dependencies
pip install -r tests/requirements-e2e.txt
playwright install chromium

# Run E2E tests
pytest tests/e2e/ --html=e2e-report.html
```

#### Performance Tests
Benchmark service performance:

```bash
# Install performance dependencies
pip install -r tests/requirements-performance.txt

# Run performance benchmarks
pytest tests/performance/ --benchmark-json=benchmark-results.json

# Run quick performance tests (excludes slow tests)
pytest tests/performance/ -m "performance and not slow"
```

### Test Markers

Use pytest markers to run specific test categories:

```bash
pytest -m unit                  # Unit tests only
pytest -m integration          # Integration tests only
pytest -m e2e                  # End-to-end tests only
pytest -m performance          # Performance tests only
pytest -m "not slow"           # Exclude slow-running tests
pytest -m ai                   # AI service integration tests only
```

## 📊 Coverage Requirements

All services must maintain **>90% test coverage**:

- **Unit Test Coverage**: >90% for all modules
- **Integration Coverage**: Critical workflows tested
- **E2E Coverage**: Major user paths verified
- **Performance Coverage**: All endpoints benchmarked

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage in browser
open htmlcov/index.html

# Terminal coverage report
pytest --cov=app --cov-report=term-missing
```

## 🔧 Test Configuration

### Global Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests plasma-engine-*/tests
addopts = --strict-markers --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
    ai: Tests involving AI services
```

### Service-Specific Configuration

Each service has its own `pyproject.toml` with pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=app",
    "--cov-fail-under=90",
    "--strict-markers"
]
```

## 🏗️ Writing Tests

### Test Structure Guidelines

1. **Arrange, Act, Assert (AAA) Pattern**:
```python
def test_health_endpoint_returns_ok():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

2. **Use Descriptive Test Names**:
```python
# ✅ Good
def test_research_endpoint_returns_results_for_valid_query():

# ❌ Bad
def test_research():
```

3. **Test One Thing Per Test**:
```python
# ✅ Good - focused test
def test_health_endpoint_returns_200_status():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_endpoint_returns_correct_service_name():
    response = client.get("/health")
    data = response.json()
    assert data["service"] == "plasma-engine-research"

# ❌ Bad - testing multiple concerns
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "plasma-engine-research"
    assert "status" in response.json()
```

### Using Test Fixtures

```python
@pytest.fixture
def mock_research_data():
    return {
        "query": "AI developments",
        "results": [{"title": "AI News", "summary": "Latest AI news"}]
    }

def test_research_processing(mock_research_data):
    # Test uses the fixture data
    result = process_research_data(mock_research_data)
    assert result["processed"] == True
```

### Mocking External Services

```python
from tests.mocks.external_services import MockOpenAIService

def test_ai_integration():
    mock_ai = MockOpenAIService()
    mock_ai.setup_chat_completion_mock("Test AI response")

    # Test code that uses AI service
    result = generate_ai_response("test prompt")
    assert result == "Test AI response"
```

## 🚀 Continuous Integration

### GitHub Actions Workflow

Our CI pipeline runs comprehensive tests on every push and pull request:

```yaml
# .github/workflows/test-suite.yml
- Python Services: Lint, type-check, unit tests with coverage
- Gateway Service: Lint, type-check, unit tests with coverage
- Integration Tests: Cross-service communication tests
- E2E Tests: User workflow validation with Playwright
- Performance Tests: Benchmarking and regression detection
- Security Scanning: Vulnerability detection
```

### Coverage Reporting

- **Codecov Integration**: Automatic coverage reporting
- **Coverage Badges**: README status indicators
- **PR Comments**: Coverage reports on pull requests
- **Trend Tracking**: Coverage history and regression detection

### Performance Monitoring

- **Benchmark Tracking**: Performance regression detection
- **Load Testing**: Concurrent request handling
- **Resource Monitoring**: Memory and CPU usage validation

## 🛠️ Debugging Tests

### Running Tests in Debug Mode

```bash
# Verbose output with full traceback
pytest -vvs --tb=long

# Stop at first failure
pytest -x

# Run last failed tests only
pytest --lf

# Run specific test with debugging
pytest tests/test_main.py::test_health_endpoint -vvs --pdb
```

### Common Test Issues

1. **Import Errors**:
   - Ensure service dependencies are installed: `pip install -e ".[dev]"`
   - Check Python path in test environment

2. **Async Test Issues**:
   - Use `pytest-asyncio` for async tests
   - Mark async tests with `@pytest.mark.asyncio`

3. **Mock Problems**:
   - Clear mocks between tests: Use `mock.reset_mock()`
   - Verify mock calls: `mock.assert_called_with(...)`

4. **Coverage Issues**:
   - Check excluded files in coverage config
   - Ensure test files don't inflate coverage
   - Use `# pragma: no cover` for uncoverable lines

### Test Environment Setup

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install all test dependencies
pip install -r tests/requirements-integration.txt
pip install -r tests/requirements-e2e.txt
pip install -r tests/requirements-performance.txt

# Install all services in development mode
for service in research content brand agent; do
    cd plasma-engine-$service && pip install -e ".[dev]" && cd ..
done

# Install Gateway dependencies
cd plasma-engine-gateway && npm install
```

## 📈 Performance Benchmarks

### Baseline Performance Targets

| Service | Response Time | Throughput | Memory Usage |
|---------|---------------|------------|--------------|
| Research | <100ms | >100 RPS | <500MB |
| Content | <50ms | >200 RPS | <300MB |
| Brand | <75ms | >150 RPS | <400MB |
| Agent | <200ms | >50 RPS | <1GB |
| Gateway | <25ms | >500 RPS | <200MB |

### Running Performance Tests

```bash
# Quick performance check
pytest tests/performance/ -m "performance and not slow" --benchmark-only

# Comprehensive performance suite
pytest tests/performance/ --benchmark-json=results.json

# Compare with baseline
pytest tests/performance/ --benchmark-compare=baseline.json
```

## 🤝 Contributing to Tests

### Before Submitting PR

1. **Run Full Test Suite**:
```bash
pytest --cov=. --cov-fail-under=90
```

2. **Check Code Quality**:
```bash
ruff check .
mypy app/
```

3. **Verify E2E Tests**:
```bash
pytest tests/e2e/ --html=report.html
```

### Test Review Checklist

- [ ] All tests have descriptive names
- [ ] Tests follow AAA pattern
- [ ] Appropriate use of fixtures and mocks
- [ ] Coverage remains >90%
- [ ] Performance tests pass baseline
- [ ] Integration tests cover new features
- [ ] E2E tests verify user workflows

## 🆘 Support & Troubleshooting

### Common Commands Reference

```bash
# Quick health check for all services
pytest -k "test_health" --tb=short

# Run tests matching pattern
pytest -k "research and not slow"

# Generate detailed test report
pytest --html=report.html --self-contained-html

# Profile test execution time
pytest --durations=10

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

### Getting Help

1. **Review Test Logs**: Check detailed output in CI artifacts
2. **Check Service Health**: Verify all services are running
3. **Validate Environment**: Ensure all dependencies are installed
4. **Contact Team**: Create issue with test failure details

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Codecov Documentation](https://docs.codecov.io/)
- [GitHub Actions Guide](https://docs.github.com/en/actions)

---

**Always Works™ Implementation**: This test suite is designed to work reliably across all environments and provides comprehensive coverage for the entire Plasma Engine ecosystem.