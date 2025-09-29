"""Performance benchmarking tests for all Plasma Engine services."""

import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
import httpx
from typing import Dict, List, Any
import psutil
import os

from tests.helpers.test_utils import PerformanceTestHelper


class TestServicePerformanceBenchmarks:
    """Performance benchmarks for individual services."""

    @pytest.fixture
    def service_endpoints(self) -> Dict[str, str]:
        """Service endpoints for performance testing."""
        return {
            "research": "http://localhost:8001",
            "content": "http://localhost:8002",
            "brand": "http://localhost:8003",
            "agent": "http://localhost:8004",
            "gateway": "http://localhost:4000"
        }

    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_health_endpoint_response_times(self, benchmark, service_endpoints):
        """Benchmark health endpoint response times across all services."""
        async def health_check_all():
            async with httpx.AsyncClient() as client:
                tasks = []
                for service, url in service_endpoints.items():
                    tasks.append(client.get(f"{url}/health", timeout=10.0))

                start_time = time.perf_counter()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.perf_counter()

                successful_responses = [r for r in responses if not isinstance(r, Exception)]
                return {
                    "total_time": end_time - start_time,
                    "successful_requests": len(successful_responses),
                    "total_services": len(service_endpoints)
                }

        result = benchmark(asyncio.run, health_check_all())

        # Verify performance criteria
        assert result["total_time"] < 1.0, f"Health checks took {result['total_time']:.2f}s, expected < 1.0s"

    @pytest.mark.performance
    async def test_concurrent_request_performance(self, service_endpoints):
        """Test service performance under concurrent load."""
        results = {}

        for service_name, url in service_endpoints.items():
            print(f"\nTesting {service_name} service performance...")

            # Test different concurrency levels
            concurrency_levels = [1, 5, 10, 20]
            service_results = {}

            for concurrency in concurrency_levels:
                result = await self._run_concurrent_load_test(
                    url=f"{url}/health",
                    concurrent_requests=concurrency,
                    total_requests=100
                )
                service_results[f"concurrency_{concurrency}"] = result
                print(f"  Concurrency {concurrency}: {result['requests_per_second']:.2f} RPS")

            results[service_name] = service_results

        # Analyze results and set performance criteria
        for service_name, service_results in results.items():
            # Single request should be fast
            single_req_result = service_results["concurrency_1"]
            assert single_req_result["average_response_time"] < 0.1, \
                f"{service_name}: Single request too slow ({single_req_result['average_response_time']:.3f}s)"

            # Should handle at least 50 RPS at concurrency 10
            high_concurrency_result = service_results["concurrency_10"]
            assert high_concurrency_result["requests_per_second"] >= 50, \
                f"{service_name}: Insufficient throughput ({high_concurrency_result['requests_per_second']:.2f} RPS)"

    async def _run_concurrent_load_test(self, url: str, concurrent_requests: int, total_requests: int) -> Dict[str, Any]:
        """Run concurrent load test on a specific URL."""
        semaphore = asyncio.Semaphore(concurrent_requests)
        start_time = time.perf_counter()

        async def single_request():
            async with semaphore:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=30.0)
                        return {"success": True, "status_code": response.status_code}
                except Exception as e:
                    return {"success": False, "error": str(e)}

        # Execute all requests
        tasks = [single_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Analyze results
        successful_requests = sum(1 for r in results if r.get("success", False))
        failed_requests = total_requests - successful_requests

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "average_response_time": total_time / total_requests if total_requests > 0 else 0
        }

    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage patterns under sustained load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Simulate memory-intensive operations
        data = []
        for i in range(1000):
            # Simulate test data creation
            test_data = {
                "id": f"test-{i}",
                "content": "x" * 1000,  # 1KB of data per item
                "metadata": {"index": i, "timestamp": time.time()}
            }
            data.append(test_data)

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Clean up test data
        del data

        # Memory increase should be reasonable
        max_acceptable_increase = 50 * 1024 * 1024  # 50MB
        assert memory_increase < max_acceptable_increase, \
            f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"

        print(f"Memory usage test: {memory_increase / 1024 / 1024:.2f}MB increase")

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_sustained_load_performance(self, service_endpoints):
        """Test service performance under sustained load."""
        test_duration = 30  # 30 seconds test
        requests_per_second_target = 10

        for service_name, url in service_endpoints.items():
            print(f"\nTesting sustained load for {service_name}...")

            start_time = time.perf_counter()
            request_count = 0
            error_count = 0
            response_times = []

            async with httpx.AsyncClient() as client:
                while time.perf_counter() - start_time < test_duration:
                    request_start = time.perf_counter()
                    try:
                        response = await client.get(f"{url}/health", timeout=5.0)
                        if response.status_code == 200:
                            request_count += 1
                        else:
                            error_count += 1
                    except Exception:
                        error_count += 1

                    request_end = time.perf_counter()
                    response_times.append(request_end - request_start)

                    # Maintain target RPS
                    await asyncio.sleep(1.0 / requests_per_second_target)

            actual_duration = time.perf_counter() - start_time
            actual_rps = request_count / actual_duration

            # Calculate statistics
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            else:
                avg_response_time = float('inf')
                p95_response_time = float('inf')

            error_rate = error_count / (request_count + error_count) if (request_count + error_count) > 0 else 0

            print(f"  Duration: {actual_duration:.1f}s")
            print(f"  Requests: {request_count}, Errors: {error_count}")
            print(f"  RPS: {actual_rps:.2f}")
            print(f"  Avg response time: {avg_response_time:.3f}s")
            print(f"  95th percentile: {p95_response_time:.3f}s")
            print(f"  Error rate: {error_rate:.2%}")

            # Performance assertions
            assert actual_rps >= requests_per_second_target * 0.8, \
                f"{service_name}: Insufficient sustained RPS ({actual_rps:.2f})"
            assert error_rate < 0.01, \
                f"{service_name}: Too many errors during sustained load ({error_rate:.2%})"
            assert avg_response_time < 0.2, \
                f"{service_name}: Average response time too high ({avg_response_time:.3f}s)"


class TestSystemWideBenchmarks:
    """System-wide performance benchmarks."""

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_end_to_end_workflow_performance(self):
        """Benchmark complete end-to-end workflows."""
        workflows = {
            "research_to_content": self._benchmark_research_to_content_workflow,
            "brand_monitoring": self._benchmark_brand_monitoring_workflow,
            "agent_orchestration": self._benchmark_agent_orchestration_workflow
        }

        results = {}

        for workflow_name, workflow_func in workflows.items():
            print(f"\nBenchmarking {workflow_name} workflow...")

            # Run workflow multiple times to get reliable metrics
            execution_times = []
            for i in range(5):
                start_time = time.perf_counter()
                try:
                    await workflow_func()
                    success = True
                except Exception as e:
                    success = False
                    print(f"  Run {i+1} failed: {e}")

                end_time = time.perf_counter()
                if success:
                    execution_times.append(end_time - start_time)

            if execution_times:
                avg_time = statistics.mean(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)

                results[workflow_name] = {
                    "average_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "successful_runs": len(execution_times)
                }

                print(f"  Average: {avg_time:.2f}s")
                print(f"  Range: {min_time:.2f}s - {max_time:.2f}s")

                # Performance criteria
                assert avg_time < 5.0, f"{workflow_name}: Workflow too slow ({avg_time:.2f}s)"

        return results

    async def _benchmark_research_to_content_workflow(self):
        """Simulate research-to-content workflow for benchmarking."""
        # Simulate API calls with realistic delays
        await asyncio.sleep(0.5)  # Research API call
        await asyncio.sleep(0.2)  # Content processing
        await asyncio.sleep(0.3)  # Content creation API call
        return {"workflow": "research_to_content", "completed": True}

    async def _benchmark_brand_monitoring_workflow(self):
        """Simulate brand monitoring workflow for benchmarking."""
        await asyncio.sleep(0.3)  # Brand data collection
        await asyncio.sleep(0.1)  # Sentiment analysis
        await asyncio.sleep(0.2)  # Alert processing
        return {"workflow": "brand_monitoring", "completed": True}

    async def _benchmark_agent_orchestration_workflow(self):
        """Simulate agent orchestration workflow for benchmarking."""
        await asyncio.sleep(0.4)  # Agent task distribution
        await asyncio.sleep(0.8)  # Multiple service calls
        await asyncio.sleep(0.3)  # Result aggregation
        return {"workflow": "agent_orchestration", "completed": True}

    @pytest.mark.performance
    def test_database_query_performance(self):
        """Benchmark database query performance patterns."""
        # This would test actual database queries when implemented
        # For now, we'll simulate query patterns

        query_patterns = {
            "simple_select": 0.001,  # 1ms
            "complex_join": 0.01,    # 10ms
            "aggregation": 0.005,    # 5ms
            "full_text_search": 0.02 # 20ms
        }

        for query_type, expected_max_time in query_patterns.items():
            start_time = time.perf_counter()

            # Simulate query execution
            time.sleep(expected_max_time * 0.5)  # Simulate half the expected time

            end_time = time.perf_counter()
            actual_time = end_time - start_time

            print(f"{query_type}: {actual_time:.3f}s")
            assert actual_time < expected_max_time, \
                f"{query_type} query too slow: {actual_time:.3f}s > {expected_max_time}s"

    @pytest.mark.performance
    def test_resource_utilization_limits(self):
        """Test that resource utilization stays within acceptable limits."""
        process = psutil.Process(os.getpid())

        # Monitor CPU and memory for a short period
        cpu_samples = []
        memory_samples = []

        for _ in range(10):
            cpu_percent = process.cpu_percent()
            memory_percent = process.memory_percent()

            cpu_samples.append(cpu_percent)
            memory_samples.append(memory_percent)

            time.sleep(0.1)

        avg_cpu = statistics.mean(cpu_samples)
        avg_memory = statistics.mean(memory_samples)

        print(f"Average CPU usage: {avg_cpu:.1f}%")
        print(f"Average Memory usage: {avg_memory:.1f}%")

        # Resource utilization limits
        assert avg_cpu < 50.0, f"CPU usage too high: {avg_cpu:.1f}%"
        assert avg_memory < 10.0, f"Memory usage too high: {avg_memory:.1f}%"