"""Configuration for end-to-end tests using Playwright."""

import pytest
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import AsyncGenerator


@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Provide a browser instance for the test session."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Provide a fresh browser context for each test."""
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Provide a fresh page for each test."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def base_url() -> str:
    """Provide the base URL for the application."""
    return "http://localhost:3000"  # Assuming frontend runs on port 3000


@pytest.fixture
def api_base_url() -> str:
    """Provide the base URL for the API gateway."""
    return "http://localhost:4000"  # Gateway port


@pytest.fixture
def test_user_data():
    """Provide test user data for authentication tests."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }


@pytest.fixture
def mock_research_data():
    """Provide mock research data for E2E tests."""
    return {
        "query": "artificial intelligence trends 2024",
        "results": [
            {
                "title": "AI Market Growth Report",
                "summary": "The AI market is projected to grow significantly",
                "url": "https://example.com/ai-report",
                "relevance_score": 0.95
            }
        ]
    }