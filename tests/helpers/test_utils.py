"""Utility functions for testing Plasma Engine services."""

import json
import tempfile
import asyncio
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from contextlib import asynccontextmanager
from unittest.mock import patch

import httpx
import pytest


class TestDataBuilder:
    """Builder pattern for creating test data consistently."""

    def __init__(self):
        self._data = {}

    def with_id(self, id_value: str) -> 'TestDataBuilder':
        """Add ID to test data."""
        self._data['id'] = id_value
        return self

    def with_title(self, title: str) -> 'TestDataBuilder':
        """Add title to test data."""
        self._data['title'] = title
        return self

    def with_content(self, content: str) -> 'TestDataBuilder':
        """Add content to test data."""
        self._data['content'] = content
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> 'TestDataBuilder':
        """Add metadata to test data."""
        self._data['metadata'] = metadata
        return self

    def with_tags(self, tags: List[str]) -> 'TestDataBuilder':
        """Add tags to test data."""
        self._data['tags'] = tags
        return self

    def with_author(self, author: str) -> 'TestDataBuilder':
        """Add author to test data."""
        self._data['author'] = author
        return self

    def with_timestamp(self, timestamp: str) -> 'TestDataBuilder':
        """Add timestamp to test data."""
        self._data['created_at'] = timestamp
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the test data."""
        return self._data.copy()


class AsyncTestHelper:
    """Helper for async testing operations."""

    @staticmethod
    async def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout: float = 10.0,
        check_interval: float = 0.1
    ) -> bool:
        """Wait for a condition to become True with timeout."""
        elapsed = 0.0
        while elapsed < timeout:
            if condition_func():
                return True
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        return False

    @staticmethod
    async def run_with_timeout(coro, timeout: float = 30.0):
        """Run coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout)

    @staticmethod
    @asynccontextmanager
    async def temporary_server(app, port: int = 0):
        """Context manager for temporary test server."""
        import uvicorn
        from threading import Thread
        import time

        if port == 0:
            # Find free port
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                port = s.getsockname()[1]

        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical")
        server = uvicorn.Server(config)

        def run_server():
            asyncio.run(server.serve())

        thread = Thread(target=run_server, daemon=True)
        thread.start()

        # Wait for server to start
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://127.0.0.1:{port}/health")
                    if response.status_code == 200:
                        break
            except:
                pass
            await asyncio.sleep(0.1)

        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            server.should_exit = True


class FileTestHelper:
    """Helper for file-based testing operations."""

    @staticmethod
    def create_temp_file(content: str, suffix: str = ".txt") -> Path:
        """Create a temporary file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    @staticmethod
    def create_temp_json_file(data: Dict[str, Any]) -> Path:
        """Create a temporary JSON file with given data."""
        content = json.dumps(data, indent=2)
        return FileTestHelper.create_temp_file(content, ".json")

    @staticmethod
    def read_file_content(file_path: Path) -> str:
        """Read content from file."""
        return file_path.read_text()

    @staticmethod
    def cleanup_temp_file(file_path: Path):
        """Clean up temporary file."""
        if file_path.exists():
            file_path.unlink()


class HTTPTestHelper:
    """Helper for HTTP testing operations."""

    @staticmethod
    def assert_valid_json_response(response: httpx.Response):
        """Assert response is valid JSON."""
        assert response.headers.get("content-type", "").startswith("application/json")
        response.json()  # Will raise if not valid JSON

    @staticmethod
    def assert_error_response(
        response: httpx.Response,
        expected_status: int,
        expected_error_code: Optional[str] = None
    ):
        """Assert response is a valid error response."""
        assert response.status_code == expected_status
        HTTPTestHelper.assert_valid_json_response(response)

        data = response.json()
        assert "error" in data

        if expected_error_code:
            assert data["error"]["code"] == expected_error_code

    @staticmethod
    def assert_success_response(response: httpx.Response, expected_data_keys: List[str] = None):
        """Assert response is a valid success response."""
        assert response.status_code == 200
        HTTPTestHelper.assert_valid_json_response(response)

        data = response.json()

        if expected_data_keys:
            for key in expected_data_keys:
                assert key in data

    @staticmethod
    async def make_authenticated_request(
        client: httpx.AsyncClient,
        method: str,
        url: str,
        token: str,
        **kwargs
    ) -> httpx.Response:
        """Make authenticated HTTP request."""
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers

        return await client.request(method, url, **kwargs)


class MockTestHelper:
    """Helper for mock-related testing operations."""

    @staticmethod
    def patch_multiple(target_dict: Dict[str, Any]):
        """Context manager to patch multiple targets."""
        return patch.multiple(**target_dict)

    @staticmethod
    def assert_mock_called_with_partial(mock_obj, **partial_kwargs):
        """Assert mock was called with at least the given kwargs."""
        mock_obj.assert_called()
        call_args, call_kwargs = mock_obj.call_args
        for key, expected_value in partial_kwargs.items():
            assert key in call_kwargs, f"Expected key '{key}' not found in call kwargs"
            assert call_kwargs[key] == expected_value, \
                f"Expected {key}={expected_value}, got {call_kwargs[key]}"


class DatabaseTestHelper:
    """Helper for database testing operations."""

    @staticmethod
    async def ensure_clean_state(db_service):
        """Ensure database is in clean state for testing."""
        if hasattr(db_service, 'clear_all'):
            db_service.clear_all()

    @staticmethod
    async def seed_test_data(db_service, table: str, records: List[Dict[str, Any]]):
        """Seed database with test data."""
        for record in records:
            await db_service.insert(table, record)


class PerformanceTestHelper:
    """Helper for performance testing operations."""

    @staticmethod
    async def measure_execution_time(coro) -> tuple[Any, float]:
        """Measure execution time of coroutine."""
        import time
        start_time = time.perf_counter()
        result = await coro
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    @staticmethod
    def assert_execution_time(execution_time: float, max_time: float, operation_name: str):
        """Assert execution time is within expected bounds."""
        assert execution_time <= max_time, \
            f"{operation_name} took {execution_time:.2f}s, expected <= {max_time}s"

    @staticmethod
    async def run_load_test(
        operation: Callable,
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """Run load test on operation."""
        import time

        start_time = time.perf_counter()

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)

        async def run_single_request():
            async with semaphore:
                return await operation()

        # Execute all requests
        tasks = [run_single_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Analyze results
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        failed_requests = total_requests - successful_requests

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time,
            "average_response_time": total_time / total_requests
        }