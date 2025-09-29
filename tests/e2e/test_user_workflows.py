"""End-to-end tests for critical user workflows in Plasma Engine."""

import pytest
from playwright.async_api import Page, expect
from typing import Dict, Any


class TestResearchWorkflow:
    """Test end-to-end research workflow."""

    @pytest.mark.e2e
    async def test_research_query_workflow(self, page: Page, base_url: str):
        """Test complete research query workflow from UI to results."""
        # Navigate to research page
        await page.goto(f"{base_url}/research")

        # Wait for page to load
        await page.wait_for_load_state("networkidle")

        # Fill in research query
        await page.fill('[data-testid="research-query-input"]', "quantum computing developments")

        # Set research parameters
        await page.select_option('[data-testid="max-results-select"]', "10")
        await page.check('[data-testid="include-summary-checkbox"]')

        # Submit research request
        await page.click('[data-testid="submit-research-button"]')

        # Wait for results to load
        await page.wait_for_selector('[data-testid="research-results"]', timeout=30000)

        # Verify results are displayed
        results = await page.locator('[data-testid="research-result-item"]').count()
        assert results > 0, "No research results displayed"

        # Verify result structure
        first_result = page.locator('[data-testid="research-result-item"]').first
        await expect(first_result.locator('[data-testid="result-title"]')).to_be_visible()
        await expect(first_result.locator('[data-testid="result-summary"]')).to_be_visible()
        await expect(first_result.locator('[data-testid="result-url"]')).to_be_visible()

    @pytest.mark.e2e
    async def test_research_result_interaction(self, page: Page, base_url: str):
        """Test interaction with research results."""
        await page.goto(f"{base_url}/research")
        await page.wait_for_load_state("networkidle")

        # Mock research results by intercepting API call
        await page.route("**/api/research", lambda route: route.fulfill(
            json={
                "query": "test query",
                "results": [
                    {
                        "title": "Test Research Result",
                        "summary": "This is a test research summary",
                        "url": "https://example.com/test",
                        "relevance_score": 0.95
                    }
                ],
                "total_results": 1
            }
        ))

        await page.fill('[data-testid="research-query-input"]', "test query")
        await page.click('[data-testid="submit-research-button"]')

        await page.wait_for_selector('[data-testid="research-result-item"]')

        # Test result expansion
        await page.click('[data-testid="expand-result-button"]')
        await expect(page.locator('[data-testid="result-details"]')).to_be_visible()

        # Test save to content functionality
        await page.click('[data-testid="save-to-content-button"]')
        await expect(page.locator('[data-testid="save-success-message"]')).to_be_visible()


class TestContentManagementWorkflow:
    """Test end-to-end content management workflow."""

    @pytest.mark.e2e
    async def test_create_content_workflow(self, page: Page, base_url: str):
        """Test complete content creation workflow."""
        await page.goto(f"{base_url}/content/create")
        await page.wait_for_load_state("networkidle")

        # Fill in content details
        await page.fill('[data-testid="content-title-input"]', "Test Article Title")
        await page.fill('[data-testid="content-summary-input"]', "This is a test article summary")

        # Fill in main content using rich text editor
        content_editor = page.locator('[data-testid="content-editor"]')
        await content_editor.fill("This is the main content of the test article.")

        # Add tags
        await page.fill('[data-testid="tags-input"]', "test, article, automation")

        # Set author
        await page.fill('[data-testid="author-input"]', "Test Author")

        # Save as draft
        await page.click('[data-testid="save-draft-button"]')

        # Verify success message
        await expect(page.locator('[data-testid="save-success-message"]')).to_be_visible()

        # Verify redirect to content list
        await page.wait_for_url("**/content")

        # Verify content appears in list
        await expect(page.locator('[data-testid="content-list-item"]')).to_be_visible()

    @pytest.mark.e2e
    async def test_publish_content_workflow(self, page: Page, base_url: str):
        """Test content publishing workflow."""
        # Mock existing draft content
        await page.route("**/api/content", lambda route: route.fulfill(
            json={
                "content": [
                    {
                        "id": "content-123",
                        "title": "Draft Article",
                        "status": "draft",
                        "author": "Test Author",
                        "created_at": "2024-01-20T10:00:00Z"
                    }
                ]
            }
        ))

        await page.goto(f"{base_url}/content")
        await page.wait_for_load_state("networkidle")

        # Click on draft content
        await page.click('[data-testid="content-list-item"]')

        # Verify edit page loads
        await page.wait_for_url("**/content/edit/**")

        # Make content ready for publishing
        await page.check('[data-testid="reviewed-checkbox"]')
        await page.check('[data-testid="seo-optimized-checkbox"]')

        # Publish content
        await page.click('[data-testid="publish-button"]')

        # Confirm publication
        await page.click('[data-testid="confirm-publish-button"]')

        # Verify success message
        await expect(page.locator('[data-testid="publish-success-message"]')).to_be_visible()


class TestBrandMonitoringWorkflow:
    """Test end-to-end brand monitoring workflow."""

    @pytest.mark.e2e
    async def test_brand_dashboard_workflow(self, page: Page, base_url: str):
        """Test brand monitoring dashboard workflow."""
        # Mock brand monitoring data
        await page.route("**/api/brand/dashboard", lambda route: route.fulfill(
            json={
                "brand_name": "TechCorp",
                "mentions_today": 45,
                "sentiment_score": 0.7,
                "sentiment_trend": "positive",
                "recent_mentions": [
                    {
                        "content": "TechCorp's new AI product is impressive!",
                        "sentiment": "positive",
                        "source": "twitter.com",
                        "timestamp": "2024-01-20T10:30:00Z"
                    }
                ]
            }
        ))

        await page.goto(f"{base_url}/brand")
        await page.wait_for_load_state("networkidle")

        # Verify dashboard elements are visible
        await expect(page.locator('[data-testid="mentions-count"]')).to_contain_text("45")
        await expect(page.locator('[data-testid="sentiment-score"]')).to_be_visible()
        await expect(page.locator('[data-testid="sentiment-trend"]')).to_contain_text("positive")

        # Test recent mentions section
        await expect(page.locator('[data-testid="recent-mentions"]')).to_be_visible()
        await expect(page.locator('[data-testid="mention-item"]')).to_be_visible()

        # Test sentiment filter
        await page.select_option('[data-testid="sentiment-filter"]', "positive")
        await page.wait_for_selector('[data-testid="mention-item"][data-sentiment="positive"]')

    @pytest.mark.e2e
    async def test_brand_alert_workflow(self, page: Page, base_url: str):
        """Test brand alert management workflow."""
        # Mock brand alerts
        await page.route("**/api/brand/alerts", lambda route: route.fulfill(
            json={
                "alerts": [
                    {
                        "id": "alert-123",
                        "type": "negative_sentiment",
                        "severity": "medium",
                        "message": "Negative sentiment spike detected",
                        "created_at": "2024-01-20T09:00:00Z",
                        "resolved": False
                    }
                ]
            }
        ))

        await page.goto(f"{base_url}/brand/alerts")
        await page.wait_for_load_state("networkidle")

        # Verify alert is displayed
        await expect(page.locator('[data-testid="alert-item"]')).to_be_visible()
        await expect(page.locator('[data-testid="alert-message"]')).to_contain_text("Negative sentiment spike")

        # Test alert actions
        await page.click('[data-testid="view-alert-details-button"]')
        await expect(page.locator('[data-testid="alert-details-modal"]')).to_be_visible()

        # Mark alert as resolved
        await page.click('[data-testid="resolve-alert-button"]')
        await expect(page.locator('[data-testid="alert-resolved-message"]')).to_be_visible()


class TestIntegratedWorkflow:
    """Test integrated workflows spanning multiple services."""

    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_research_to_content_full_workflow(self, page: Page, base_url: str):
        """Test complete research-to-content workflow."""
        # Start with research
        await page.goto(f"{base_url}/research")
        await page.wait_for_load_state("networkidle")

        # Mock research API
        await page.route("**/api/research", lambda route: route.fulfill(
            json={
                "query": "AI market trends",
                "results": [
                    {
                        "title": "AI Market Report 2024",
                        "summary": "Comprehensive analysis of AI market trends",
                        "url": "https://example.com/ai-report",
                        "content": "Detailed market analysis content...",
                        "relevance_score": 0.95
                    }
                ]
            }
        ))

        # Perform research
        await page.fill('[data-testid="research-query-input"]', "AI market trends")
        await page.click('[data-testid="submit-research-button"]')
        await page.wait_for_selector('[data-testid="research-results"]')

        # Save research to content
        await page.click('[data-testid="save-to-content-button"]')

        # Verify redirect to content creation
        await page.wait_for_url("**/content/create**")

        # Verify research data is pre-populated
        title_input = page.locator('[data-testid="content-title-input"]')
        await expect(title_input).to_have_value("AI Market Report 2024")

        # Complete content creation
        await page.fill('[data-testid="author-input"]', "Research Bot")
        await page.click('[data-testid="save-draft-button"]')

        # Verify success
        await expect(page.locator('[data-testid="save-success-message"]')).to_be_visible()

    @pytest.mark.e2e
    async def test_performance_under_user_load(self, page: Page, base_url: str):
        """Test UI performance under simulated user interactions."""
        await page.goto(f"{base_url}/dashboard")
        await page.wait_for_load_state("networkidle")

        # Measure page load performance
        performance = await page.evaluate("""() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            return {
                loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
            };
        }""")

        # Verify performance metrics
        assert performance["loadTime"] < 3000, f"Page load time too slow: {performance['loadTime']}ms"
        assert performance["domContentLoaded"] < 2000, f"DOM load time too slow: {performance['domContentLoaded']}ms"

        # Test rapid navigation
        pages_to_test = ["/research", "/content", "/brand", "/dashboard"]

        for test_page in pages_to_test:
            start_time = await page.evaluate("() => performance.now()")
            await page.goto(f"{base_url}{test_page}")
            await page.wait_for_load_state("networkidle")
            end_time = await page.evaluate("() => performance.now()")

            navigation_time = end_time - start_time
            assert navigation_time < 2000, f"Navigation to {test_page} too slow: {navigation_time}ms"