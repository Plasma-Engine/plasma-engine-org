"""Global pytest configuration and shared fixtures for all Plasma Engine services.

This module provides common test utilities, fixtures, and configuration
that can be used across all Python microservices in the Plasma Engine ecosystem.
"""

import asyncio
import os
import tempfile
from typing import Any, AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Provide a temporary directory that's cleaned up after test."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Provide a context for setting temporary environment variables."""
    original_env = os.environ.copy()
    test_env = {
        "OPENAI_API_KEY": "test-key",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000",
        "LOG_LEVEL": "DEBUG"
    }
    os.environ.update(test_env)
    yield test_env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client for testing external API calls."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def mock_openai_client() -> Mock:
    """Provide a mock OpenAI client for testing AI integrations."""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content="Mock AI response",
                    role="assistant"
                ),
                finish_reason="stop"
            )
        ],
        usage=Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
    )
    return mock_client


@pytest.fixture
def sample_research_data() -> dict[str, Any]:
    """Provide sample research data for testing."""
    return {
        "query": "What are the latest developments in quantum computing?",
        "sources": [
            {
                "title": "Quantum Computing Breakthrough 2024",
                "url": "https://example.com/quantum-2024",
                "content": "Recent advances in quantum error correction...",
                "relevance_score": 0.95
            }
        ],
        "summary": "Latest quantum computing developments include improved error correction...",
        "confidence": 0.87
    }


@pytest.fixture
def sample_content_data() -> dict[str, Any]:
    """Provide sample content data for testing."""
    return {
        "title": "The Future of AI",
        "content": "Artificial Intelligence continues to evolve...",
        "tags": ["ai", "technology", "future"],
        "author": "Test Author",
        "status": "published",
        "metadata": {
            "word_count": 500,
            "reading_time": 2
        }
    }


class DatabaseTestMixin:
    """Mixin providing database testing utilities."""

    @staticmethod
    def setup_test_db():
        """Set up a test database connection."""
        # Implementation will be added when database layer is implemented
        pass

    @staticmethod
    def cleanup_test_db():
        """Clean up test database."""
        # Implementation will be added when database layer is implemented
        pass


class ServiceTestMixin:
    """Mixin providing service testing utilities."""

    @staticmethod
    def create_test_client(app: FastAPI) -> TestClient:
        """Create a test client for FastAPI applications."""
        return TestClient(app)

    @staticmethod
    def assert_health_response(response: httpx.Response, service_name: str) -> None:
        """Assert standard health endpoint response format."""
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == service_name


# Common test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow