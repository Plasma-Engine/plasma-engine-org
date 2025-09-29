"""Mock external services for testing without dependencies."""

from typing import Any, Dict, List
from unittest.mock import Mock, AsyncMock
import json


class MockOpenAIService:
    """Mock OpenAI API service for testing AI integrations."""

    def __init__(self):
        self.chat = Mock()
        self.embeddings = Mock()
        self.completions = Mock()

    def setup_chat_completion_mock(self, response_content: str = "Mock AI response"):
        """Set up mock chat completion response."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(content=response_content, role="assistant"),
                finish_reason="stop"
            )
        ]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        self.chat.completions.create = AsyncMock(return_value=mock_response)
        return mock_response

    def setup_embedding_mock(self, embeddings: List[List[float]] = None):
        """Set up mock embedding response."""
        if embeddings is None:
            embeddings = [[0.1, 0.2, 0.3] * 256]  # Mock 768-dim embedding

        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=embed, index=i) for i, embed in enumerate(embeddings)
        ]
        mock_response.usage = Mock(prompt_tokens=5, total_tokens=5)

        self.embeddings.create = AsyncMock(return_value=mock_response)
        return mock_response


class MockAnthropicService:
    """Mock Anthropic Claude API service for testing."""

    def __init__(self):
        self.messages = Mock()

    def setup_message_mock(self, content: str = "Mock Claude response"):
        """Set up mock message response."""
        mock_response = Mock()
        mock_response.content = [Mock(text=content, type="text")]
        mock_response.usage = Mock(
            input_tokens=15,
            output_tokens=25
        )
        mock_response.role = "assistant"

        self.messages.create = AsyncMock(return_value=mock_response)
        return mock_response


class MockWebSearchService:
    """Mock web search service for research functionality."""

    def __init__(self):
        self.default_results = [
            {
                "title": "Mock Search Result 1",
                "url": "https://example.com/result-1",
                "snippet": "This is a mock search result for testing purposes.",
                "relevance_score": 0.95
            },
            {
                "title": "Mock Search Result 2",
                "url": "https://example.com/result-2",
                "snippet": "Another mock search result with different content.",
                "relevance_score": 0.87
            }
        ]

    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Mock search method."""
        return self.default_results[:max_results]

    def set_results(self, results: List[Dict[str, Any]]):
        """Set custom search results for testing."""
        self.default_results = results


class MockDatabaseService:
    """Mock database service for testing data persistence."""

    def __init__(self):
        self._data = {}
        self.connected = False

    async def connect(self):
        """Mock database connection."""
        self.connected = True

    async def disconnect(self):
        """Mock database disconnection."""
        self.connected = False

    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Mock data insertion."""
        if table not in self._data:
            self._data[table] = []

        record_id = f"{table}-{len(self._data[table])}"
        record = {"id": record_id, **data}
        self._data[table].append(record)
        return record_id

    async def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock data selection."""
        if table not in self._data:
            return []

        results = self._data[table]

        if filters:
            filtered_results = []
            for record in results:
                match = True
                for key, value in filters.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(record)
            results = filtered_results

        return results

    async def update(self, table: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Mock data update."""
        if table not in self._data:
            return False

        for record in self._data[table]:
            if record["id"] == record_id:
                record.update(data)
                return True
        return False

    async def delete(self, table: str, record_id: str) -> bool:
        """Mock data deletion."""
        if table not in self._data:
            return False

        for i, record in enumerate(self._data[table]):
            if record["id"] == record_id:
                self._data[table].pop(i)
                return True
        return False

    def clear_all(self):
        """Clear all mock data."""
        self._data.clear()


class MockCacheService:
    """Mock cache service for testing caching functionality."""

    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Any:
        """Get value from mock cache."""
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in mock cache."""
        self._cache[key] = value

    async def delete(self, key: str) -> bool:
        """Delete key from mock cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in mock cache."""
        return key in self._cache

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()


class MockMessageQueueService:
    """Mock message queue service for testing async communication."""

    def __init__(self):
        self._queues = {}

    async def publish(self, queue_name: str, message: Dict[str, Any]):
        """Publish message to mock queue."""
        if queue_name not in self._queues:
            self._queues[queue_name] = []
        self._queues[queue_name].append(message)

    async def consume(self, queue_name: str) -> List[Dict[str, Any]]:
        """Consume all messages from mock queue."""
        messages = self._queues.get(queue_name, [])
        if queue_name in self._queues:
            self._queues[queue_name] = []
        return messages

    def get_queue_size(self, queue_name: str) -> int:
        """Get number of messages in queue."""
        return len(self._queues.get(queue_name, []))

    def clear_all(self):
        """Clear all queues."""
        self._queues.clear()


class MockEmailService:
    """Mock email service for testing notifications."""

    def __init__(self):
        self.sent_emails = []

    async def send_email(self, to: str, subject: str, body: str, html_body: str = None):
        """Mock email sending."""
        email = {
            "to": to,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "sent_at": "2024-01-20T10:00:00Z"
        }
        self.sent_emails.append(email)

    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails."""
        return self.sent_emails

    def clear_sent_emails(self):
        """Clear sent email history."""
        self.sent_emails.clear()