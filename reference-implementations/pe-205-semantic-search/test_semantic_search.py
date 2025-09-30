"""
Test Suite for Semantic Search API (PE-205)
"""

import pytest
import asyncio
import numpy as np
from typing import List, Dict, Any
import json

from semantic_search_service import (
    SemanticSearchService,
    SearchQuery,
    SearchMode,
    VectorStore,
    BM25Scorer,
    QueryExpander,
    MaximalMarginalRelevance
)


# Test fixtures
@pytest.fixture
async def search_service():
    """Create and initialize a search service for testing"""
    service = SemanticSearchService()
    await service.initialize()
    return service


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "test1",
            "content": "Machine learning algorithms for natural language processing",
            "embedding": np.random.randn(1536)
        },
        {
            "id": "test2",
            "content": "Deep learning neural networks and transformers",
            "embedding": np.random.randn(1536)
        },
        {
            "id": "test3",
            "content": "Vector embeddings and semantic search techniques",
            "embedding": np.random.randn(1536)
        }
    ]


class TestVectorStore:
    """Test VectorStore functionality"""

    @pytest.mark.asyncio
    async def test_add_and_retrieve_embedding(self):
        """Test adding and retrieving embeddings"""
        store = VectorStore()

        doc_id = "test_doc"
        embedding = np.random.randn(1536)
        document = {"content": "Test content", "metadata": {}}

        await store.add_embedding(doc_id, embedding, document)

        retrieved_doc = await store.get_document(doc_id)
        assert retrieved_doc is not None
        assert retrieved_doc["content"] == "Test content"

    @pytest.mark.asyncio
    async def test_similarity_search(self):
        """Test similarity search functionality"""
        store = VectorStore()

        # Add test embeddings
        for i in range(5):
            doc_id = f"doc_{i}"
            embedding = np.random.randn(1536)
            document = {"content": f"Document {i}", "metadata": {}}
            await store.add_embedding(doc_id, embedding, document)

        # Perform similarity search
        query_embedding = np.random.randn(1536)
        results = await store.similarity_search(query_embedding, k=3)

        assert len(results) <= 3
        for doc_id, score in results:
            assert 0 <= score <= 1  # Cosine similarity range


class TestBM25Scorer:
    """Test BM25 scoring functionality"""

    def test_bm25_scoring(self):
        """Test BM25 score calculation"""
        scorer = BM25Scorer()

        documents = [
            ("doc1", "information retrieval systems"),
            ("doc2", "machine learning for information extraction"),
            ("doc3", "natural language processing")
        ]

        scorer.fit(documents)

        query = "information retrieval"
        score = scorer.score(query, "doc1", "information retrieval systems")

        assert score > 0

        # Doc1 should have higher score for this query
        score2 = scorer.score(query, "doc3", "natural language processing")
        assert score > score2


class TestQueryExpander:
    """Test query expansion functionality"""

    @pytest.mark.asyncio
    async def test_query_expansion(self):
        """Test query expansion with synonyms"""
        expander = QueryExpander()

        expanded = await expander.expand("search")

        assert "search" in expanded
        assert len(expanded) > 1  # Should include synonyms

        # Check for expected expansions
        expected_terms = ["find", "lookup", "query", "retrieve"]
        assert any(term in expanded for term in expected_terms)


class TestMaximalMarginalRelevance:
    """Test MMR functionality"""

    def test_mmr_reranking(self):
        """Test MMR reranking for diversity"""
        from semantic_search_service import SearchResult

        # Create sample results
        results = [
            SearchResult(
                id="doc1",
                content="Content 1",
                score=0.9,
                metadata={},
                source="test"
            ),
            SearchResult(
                id="doc2",
                content="Content 2",
                score=0.85,
                metadata={},
                source="test"
            ),
            SearchResult(
                id="doc3",
                content="Content 3",
                score=0.8,
                metadata={},
                source="test"
            )
        ]

        # Create embeddings
        embeddings = {
            "doc1": np.random.randn(1536),
            "doc2": np.random.randn(1536),
            "doc3": np.random.randn(1536)
        }

        query_embedding = np.random.randn(1536)

        # Rerank with MMR
        reranked = MaximalMarginalRelevance.rerank(
            results, embeddings, query_embedding, lambda_param=0.7, k=2
        )

        assert len(reranked) == 2
        assert reranked[0].id == "doc1"  # Highest relevance should be first


class TestSemanticSearchService:
    """Test main semantic search service"""

    @pytest.mark.asyncio
    async def test_vector_search(self, search_service):
        """Test vector similarity search"""
        query = SearchQuery(
            query="machine learning",
            mode=SearchMode.VECTOR,
            limit=5
        )

        results = await search_service.vector_search(query)

        assert isinstance(results, list)
        assert len(results) <= 5

        for result in results:
            assert result.source == "vector"
            assert 0 <= result.score <= 1

    @pytest.mark.asyncio
    async def test_keyword_search(self, search_service):
        """Test BM25 keyword search"""
        query = SearchQuery(
            query="semantic search",
            mode=SearchMode.KEYWORD,
            limit=5
        )

        results = await search_service.keyword_search(query)

        assert isinstance(results, list)
        assert len(results) <= 5

        for result in results:
            assert result.source == "keyword"
            assert result.score >= 0

    @pytest.mark.asyncio
    async def test_hybrid_search(self, search_service):
        """Test hybrid search combining vector and keyword"""
        query = SearchQuery(
            query="vector embeddings",
            mode=SearchMode.HYBRID,
            limit=5,
            use_mmr=True
        )

        response = await search_service.search(query)

        assert "results" in response
        assert response["mode"] == "hybrid"
        assert len(response["results"]) <= 5

    @pytest.mark.asyncio
    async def test_query_expansion_in_search(self, search_service):
        """Test query expansion during search"""
        query = SearchQuery(
            query="search",
            mode=SearchMode.HYBRID,
            expand_query=True
        )

        response = await search_service.search(query)

        assert "expanded_queries" in response
        assert len(response["expanded_queries"]) > 1

    @pytest.mark.asyncio
    async def test_pagination(self, search_service):
        """Test pagination support"""
        # First page
        query1 = SearchQuery(
            query="test query",
            mode=SearchMode.HYBRID,
            limit=2,
            offset=0
        )

        response1 = await search_service.search(query1)

        # Second page
        query2 = SearchQuery(
            query="test query",
            mode=SearchMode.HYBRID,
            limit=2,
            offset=2
        )

        response2 = await search_service.search(query2)

        # Check pagination metadata
        assert response1["limit"] == 2
        assert response1["offset"] == 0
        assert response2["offset"] == 2

    @pytest.mark.asyncio
    async def test_filters(self, search_service):
        """Test metadata filtering"""
        query = SearchQuery(
            query="test",
            mode=SearchMode.HYBRID,
            filters={"category": "research"}
        )

        response = await search_service.search(query)

        # All results should match the filter
        for result in response["results"]:
            if "category" in result["metadata"]:
                assert result["metadata"]["category"] == "research"

    @pytest.mark.asyncio
    async def test_similar_documents(self, search_service):
        """Test finding similar documents"""
        # Add a document first
        await search_service.vector_store.add_embedding(
            "test_doc",
            np.random.randn(1536),
            {"content": "Test document", "metadata": {}}
        )
        search_service.embeddings_cache["test_doc"] = np.random.randn(1536)

        # Find similar documents
        similar = await search_service.get_similar_documents("test_doc", k=3)

        assert isinstance(similar, list)
        # Should not include the query document itself
        assert all(result.id != "test_doc" for result in similar)


class TestPerformanceOptimizations:
    """Test performance optimization features"""

    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch processing of requests"""
        from performance_optimizations import BatchProcessor

        processor = BatchProcessor(batch_size=3)

        # Add multiple requests
        futures = []
        for i in range(5):
            future = await processor.add_embedding_request(f"text_{i}")
            futures.append(future)

        # Process batch
        await processor.process_embedding_batch()

        # Check that futures are resolved
        for future in futures[:3]:  # First batch
            assert future.done()

    @pytest.mark.asyncio
    async def test_caching(self):
        """Test caching functionality"""
        from performance_optimizations import cached_result

        call_count = 0

        @cached_result(ttl=60)
        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call (should use cache)
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_query_optimization(self):
        """Test query optimization"""
        from performance_optimizations import QueryOptimizer

        optimizer = QueryOptimizer()

        # Test stop word removal
        optimized = optimizer.optimize_query("the search for the best results")
        assert "the" not in optimized.lower()

        # Test pattern analysis
        analysis = optimizer.analyze_query_pattern('"exact phrase" AND keyword')
        assert analysis["is_phrase"] is True
        assert analysis["has_operators"] is True


# Integration tests
class TestAPIIntegration:
    """Test API endpoint integration"""

    @pytest.mark.asyncio
    async def test_search_endpoint(self):
        """Test FastAPI search endpoint"""
        from fastapi.testclient import TestClient
        from api_endpoints import app

        client = TestClient(app)

        response = client.post(
            "/api/v1/search",
            json={
                "query": "semantic search",
                "mode": "hybrid",
                "limit": 5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["mode"] == "hybrid"

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        from fastapi.testclient import TestClient
        from api_endpoints import app

        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# Benchmark tests
@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.asyncio
    async def test_search_latency(self, search_service, benchmark):
        """Benchmark search latency"""
        query = SearchQuery(
            query="test query",
            mode=SearchMode.HYBRID,
            limit=10
        )

        result = await benchmark(search_service.search, query)
        assert "results" in result

    @pytest.mark.asyncio
    async def test_concurrent_searches(self, search_service):
        """Test concurrent search handling"""
        queries = [
            SearchQuery(query=f"query_{i}", mode=SearchMode.HYBRID)
            for i in range(10)
        ]

        # Execute searches concurrently
        tasks = [search_service.search(q) for q in queries]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        for result in results:
            assert "results" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])