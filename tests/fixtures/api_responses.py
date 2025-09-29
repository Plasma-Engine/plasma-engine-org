"""Common API response fixtures for testing HTTP endpoints."""

from typing import Any, Dict


class APIResponseFixtures:
    """Collection of standard API response fixtures."""

    @staticmethod
    def health_response(service_name: str) -> Dict[str, str]:
        """Standard health endpoint response."""
        return {"status": "ok", "service": service_name}

    @staticmethod
    def error_response(message: str, code: str = "GENERIC_ERROR") -> Dict[str, Any]:
        """Standard error response format."""
        return {
            "error": {
                "code": code,
                "message": message,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }

    @staticmethod
    def paginated_response(items: list, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Standard paginated response format."""
        total_items = len(items)
        total_pages = (total_items + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_items = items[start_idx:end_idx]

        return {
            "data": page_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }

    @staticmethod
    def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Standard success response format."""
        return {
            "success": True,
            "message": message,
            "data": data
        }


class ResearchAPIFixtures:
    """Research service specific API response fixtures."""

    @staticmethod
    def search_response() -> Dict[str, Any]:
        """Mock research search response."""
        return {
            "query": "quantum computing advances 2024",
            "results": [
                {
                    "title": "Breakthrough in Quantum Error Correction",
                    "summary": "Researchers achieve 99.9% fidelity in quantum operations",
                    "url": "https://example.com/quantum-breakthrough",
                    "relevance_score": 0.95,
                    "published_date": "2024-01-15T10:30:00Z",
                    "source": "Nature Quantum Information"
                },
                {
                    "title": "New Quantum Computing Architecture",
                    "summary": "Novel approach reduces decoherence time significantly",
                    "url": "https://example.com/quantum-architecture",
                    "relevance_score": 0.89,
                    "published_date": "2024-01-10T14:20:00Z",
                    "source": "Physical Review Letters"
                }
            ],
            "total_results": 2,
            "search_time": 1.23,
            "confidence": 0.87
        }


class ContentAPIFixtures:
    """Content service specific API response fixtures."""

    @staticmethod
    def article_response() -> Dict[str, Any]:
        """Mock article response."""
        return {
            "id": "article-123",
            "title": "The Future of Artificial Intelligence",
            "content": "AI continues to evolve at an unprecedented pace...",
            "summary": "An exploration of upcoming AI developments and their implications",
            "author": "Dr. Jane Smith",
            "published_date": "2024-01-20T09:00:00Z",
            "updated_date": "2024-01-20T09:00:00Z",
            "tags": ["ai", "technology", "future", "machine-learning"],
            "status": "published",
            "metadata": {
                "word_count": 1500,
                "reading_time_minutes": 6,
                "language": "en",
                "seo_score": 85
            },
            "related_articles": ["article-124", "article-125"]
        }

    @staticmethod
    def content_list_response() -> list[Dict[str, Any]]:
        """Mock content list response."""
        return [
            {
                "id": "article-123",
                "title": "The Future of AI",
                "summary": "Exploring AI developments",
                "author": "Dr. Jane Smith",
                "published_date": "2024-01-20T09:00:00Z",
                "tags": ["ai", "technology"],
                "status": "published"
            },
            {
                "id": "article-124",
                "title": "Quantum Computing Explained",
                "summary": "Understanding quantum principles",
                "author": "Prof. John Doe",
                "published_date": "2024-01-19T15:30:00Z",
                "tags": ["quantum", "computing"],
                "status": "published"
            }
        ]


class AgentAPIFixtures:
    """Agent service specific API response fixtures."""

    @staticmethod
    def agent_status_response() -> Dict[str, Any]:
        """Mock agent status response."""
        return {
            "agent_id": "agent-001",
            "name": "Research Assistant",
            "status": "active",
            "capabilities": ["research", "analysis", "summarization"],
            "current_task": {
                "id": "task-456",
                "description": "Analyzing market trends",
                "progress": 0.75,
                "estimated_completion": "2024-01-20T16:00:00Z"
            },
            "metrics": {
                "tasks_completed": 142,
                "success_rate": 0.94,
                "average_response_time": 2.3,
                "uptime": "99.8%"
            }
        }

    @staticmethod
    def task_result_response() -> Dict[str, Any]:
        """Mock task result response."""
        return {
            "task_id": "task-456",
            "agent_id": "agent-001",
            "status": "completed",
            "result": {
                "analysis": "Market trends show strong growth in AI sector...",
                "confidence": 0.89,
                "key_findings": [
                    "AI adoption increased 45% year-over-year",
                    "Investment in AI startups reached $50B",
                    "Enterprise AI deployment up 32%"
                ],
                "recommendations": [
                    "Focus on enterprise AI solutions",
                    "Invest in AI safety research",
                    "Develop AI governance frameworks"
                ]
            },
            "execution_time": 15.7,
            "completed_at": "2024-01-20T16:00:00Z",
            "created_at": "2024-01-20T15:45:00Z"
        }