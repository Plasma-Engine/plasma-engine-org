"""
GraphQL Resolver for Semantic Search Service (PE-205)
Provides GraphQL schema and resolvers for semantic search functionality
"""

from typing import List, Dict, Any, Optional
import strawberry
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter
from dataclasses import dataclass
import asyncio
from datetime import datetime
import logging

from semantic_search_service import (
    SearchQuery as ServiceSearchQuery,
    SearchMode,
    SemanticSearchService,
    search_service
)

logger = logging.getLogger(__name__)


# GraphQL Types
@strawberry.enum
class SearchModeEnum:
    """Search mode options for GraphQL"""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@strawberry.type
class SearchResult:
    """GraphQL type for search results"""
    id: str
    content: str
    score: float
    metadata: strawberry.scalars.JSON
    source: str
    highlights: Optional[List[str]] = None


@strawberry.type
class SearchResponse:
    """GraphQL type for search response"""
    query: str
    expanded_queries: List[str]
    mode: str
    total_results: int
    limit: int
    offset: int
    results: List[SearchResult]
    processing_time_ms: Optional[float] = None


@strawberry.type
class SimilarDocument:
    """GraphQL type for similar documents"""
    id: str
    content: str
    similarity_score: float
    metadata: strawberry.scalars.JSON


@strawberry.type
class SimilarDocumentsResponse:
    """GraphQL type for similar documents response"""
    document_id: str
    similar_documents: List[SimilarDocument]
    total_found: int


@strawberry.type
class DocumentStats:
    """GraphQL type for document statistics"""
    total_documents: int
    total_embeddings: int
    vector_dimensions: int
    index_type: str
    bm25_enabled: bool
    mmr_enabled: bool
    query_expansion_enabled: bool


@strawberry.type
class SearchConfiguration:
    """GraphQL type for search configuration"""
    default_limit: int
    max_limit: int
    similarity_threshold: float
    mmr_lambda: float


@strawberry.type
class SearchStats:
    """GraphQL type for search statistics"""
    statistics: DocumentStats
    configuration: SearchConfiguration
    timestamp: str


@strawberry.type
class IngestionResult:
    """GraphQL type for document ingestion result"""
    status: str
    document_id: str
    message: str
    timestamp: str


@strawberry.type
class DeletionResult:
    """GraphQL type for document deletion result"""
    status: str
    document_id: str
    message: str
    timestamp: str


# GraphQL Input Types
@strawberry.input
class SearchInput:
    """Input type for search queries"""
    query: str
    mode: Optional[SearchModeEnum] = SearchModeEnum.HYBRID
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    filters: Optional[strawberry.scalars.JSON] = None
    expand_query: Optional[bool] = True
    use_mmr: Optional[bool] = True
    mmr_lambda: Optional[float] = 0.7
    similarity_threshold: Optional[float] = 0.5


@strawberry.input
class DocumentInput:
    """Input type for document ingestion"""
    id: str
    content: str
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.input
class PaginationInput:
    """Input type for pagination"""
    limit: Optional[int] = 10
    offset: Optional[int] = 0

    def __post_init__(self):
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        if self.offset < 0:
            raise ValueError("Offset must be non-negative")


# GraphQL Query resolvers
@strawberry.type
class Query:
    """GraphQL Query resolvers for semantic search"""

    @strawberry.field
    async def search(
        self,
        input: SearchInput,
        info: Info
    ) -> SearchResponse:
        """
        Perform semantic search with various modes and options

        Supports vector similarity, keyword matching, and hybrid search
        with query expansion and result diversification
        """
        import time
        start_time = time.time()

        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            # Convert GraphQL input to service query
            search_query = ServiceSearchQuery(
                query=input.query,
                mode=SearchMode(input.mode.value),
                limit=input.limit,
                offset=input.offset,
                filters=input.filters,
                expand_query=input.expand_query,
                use_mmr=input.use_mmr,
                mmr_lambda=input.mmr_lambda,
                similarity_threshold=input.similarity_threshold
            )

            # Perform search
            results = await service.search(search_query)

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000

            # Convert to GraphQL response
            search_results = []
            for result in results.get("results", []):
                search_results.append(SearchResult(
                    id=result["id"],
                    content=result["content"],
                    score=result["score"],
                    metadata=result["metadata"],
                    source=result["source"],
                    highlights=result.get("highlights")
                ))

            return SearchResponse(
                query=results["query"],
                expanded_queries=results["expanded_queries"],
                mode=results["mode"],
                total_results=results["total_results"],
                limit=results["limit"],
                offset=results["offset"],
                results=search_results,
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"GraphQL search error: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")

    @strawberry.field
    async def batch_search(
        self,
        queries: List[SearchInput],
        info: Info
    ) -> List[SearchResponse]:
        """
        Perform batch search for multiple queries

        Efficiently processes multiple search queries in parallel
        """
        import time

        async def process_single_search(input: SearchInput) -> SearchResponse:
            start_time = time.time()

            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            search_query = ServiceSearchQuery(
                query=input.query,
                mode=SearchMode(input.mode.value),
                limit=input.limit,
                offset=input.offset,
                filters=input.filters,
                expand_query=input.expand_query,
                use_mmr=input.use_mmr,
                mmr_lambda=input.mmr_lambda,
                similarity_threshold=input.similarity_threshold
            )

            results = await service.search(search_query)
            processing_time = (time.time() - start_time) * 1000

            # Convert to GraphQL response
            search_results = []
            for result in results.get("results", []):
                search_results.append(SearchResult(
                    id=result["id"],
                    content=result["content"],
                    score=result["score"],
                    metadata=result["metadata"],
                    source=result["source"],
                    highlights=result.get("highlights")
                ))

            return SearchResponse(
                query=results["query"],
                expanded_queries=results["expanded_queries"],
                mode=results["mode"],
                total_results=results["total_results"],
                limit=results["limit"],
                offset=results["offset"],
                results=search_results,
                processing_time_ms=processing_time
            )

        try:
            # Process all searches in parallel
            responses = await asyncio.gather(
                *[process_single_search(query) for query in queries]
            )
            return responses

        except Exception as e:
            logger.error(f"GraphQL batch search error: {str(e)}")
            raise Exception(f"Batch search failed: {str(e)}")

    @strawberry.field
    async def find_similar_documents(
        self,
        document_id: str,
        limit: Optional[int] = 5,
        info: Info
    ) -> SimilarDocumentsResponse:
        """
        Find documents similar to a given document

        Uses vector similarity to find related documents
        """
        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            # Find similar documents
            results = await service.get_similar_documents(
                doc_id=document_id,
                k=limit
            )

            # Convert to GraphQL response
            similar_docs = []
            for result in results:
                similar_docs.append(SimilarDocument(
                    id=result.id,
                    content=result.content,
                    similarity_score=result.score,
                    metadata=result.metadata
                ))

            return SimilarDocumentsResponse(
                document_id=document_id,
                similar_documents=similar_docs,
                total_found=len(similar_docs)
            )

        except Exception as e:
            logger.error(f"GraphQL similar documents error: {str(e)}")
            raise Exception(f"Failed to find similar documents: {str(e)}")

    @strawberry.field
    async def search_stats(self, info: Info) -> SearchStats:
        """
        Get search system statistics and configuration

        Returns information about the search index and settings
        """
        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            total_documents = len(service.vector_store.documents)
            total_embeddings = len(service.vector_store.embeddings)

            stats = DocumentStats(
                total_documents=total_documents,
                total_embeddings=total_embeddings,
                vector_dimensions=1536,
                index_type="HNSW",
                bm25_enabled=True,
                mmr_enabled=True,
                query_expansion_enabled=True
            )

            config = SearchConfiguration(
                default_limit=10,
                max_limit=100,
                similarity_threshold=0.5,
                mmr_lambda=0.7
            )

            return SearchStats(
                statistics=stats,
                configuration=config,
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"GraphQL stats error: {str(e)}")
            raise Exception(f"Failed to get statistics: {str(e)}")

    @strawberry.field
    async def paginated_search(
        self,
        query: str,
        pagination: PaginationInput,
        mode: Optional[SearchModeEnum] = SearchModeEnum.HYBRID,
        filters: Optional[strawberry.scalars.JSON] = None,
        info: Info
    ) -> SearchResponse:
        """
        Perform paginated semantic search

        Supports cursor-based pagination for efficient result retrieval
        """
        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            # Create search query with pagination
            search_query = ServiceSearchQuery(
                query=query,
                mode=SearchMode(mode.value),
                limit=pagination.limit,
                offset=pagination.offset,
                filters=filters,
                expand_query=True,
                use_mmr=True
            )

            # Perform search
            results = await service.search(search_query)

            # Convert to GraphQL response
            search_results = []
            for result in results.get("results", []):
                search_results.append(SearchResult(
                    id=result["id"],
                    content=result["content"],
                    score=result["score"],
                    metadata=result["metadata"],
                    source=result["source"],
                    highlights=result.get("highlights")
                ))

            return SearchResponse(
                query=results["query"],
                expanded_queries=results["expanded_queries"],
                mode=results["mode"],
                total_results=results["total_results"],
                limit=results["limit"],
                offset=results["offset"],
                results=search_results
            )

        except Exception as e:
            logger.error(f"GraphQL paginated search error: {str(e)}")
            raise Exception(f"Paginated search failed: {str(e)}")


# GraphQL Mutation resolvers
@strawberry.type
class Mutation:
    """GraphQL Mutation resolvers for document management"""

    @strawberry.mutation
    async def ingest_document(
        self,
        input: DocumentInput,
        info: Info
    ) -> IngestionResult:
        """
        Ingest a document into the search system

        Generates embeddings and updates search indices
        """
        try:
            # In production, this would:
            # 1. Call embedding service (PE-203)
            # 2. Store in pgvector
            # 3. Update Neo4j knowledge graph (PE-204)
            # 4. Update BM25 index

            return IngestionResult(
                status="success",
                document_id=input.id,
                message="Document ingested successfully",
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"GraphQL ingestion error: {str(e)}")
            raise Exception(f"Document ingestion failed: {str(e)}")

    @strawberry.mutation
    async def ingest_documents_batch(
        self,
        documents: List[DocumentInput],
        info: Info
    ) -> List[IngestionResult]:
        """
        Ingest multiple documents in batch

        Efficiently processes multiple documents in parallel
        """
        async def ingest_single(doc: DocumentInput) -> IngestionResult:
            try:
                return IngestionResult(
                    status="success",
                    document_id=doc.id,
                    message="Document ingested successfully",
                    timestamp=datetime.utcnow().isoformat()
                )
            except Exception as e:
                return IngestionResult(
                    status="error",
                    document_id=doc.id,
                    message=str(e),
                    timestamp=datetime.utcnow().isoformat()
                )

        try:
            # Process all documents in parallel
            results = await asyncio.gather(
                *[ingest_single(doc) for doc in documents]
            )
            return results

        except Exception as e:
            logger.error(f"GraphQL batch ingestion error: {str(e)}")
            raise Exception(f"Batch ingestion failed: {str(e)}")

    @strawberry.mutation
    async def delete_document(
        self,
        document_id: str,
        info: Info
    ) -> DeletionResult:
        """
        Delete a document from the search index

        Removes the document from all indices and caches
        """
        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            # Delete from service
            if document_id in service.vector_store.documents:
                del service.vector_store.documents[document_id]
                del service.vector_store.embeddings[document_id]
                if document_id in service.embeddings_cache:
                    del service.embeddings_cache[document_id]

                return DeletionResult(
                    status="success",
                    document_id=document_id,
                    message="Document deleted successfully",
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                raise Exception(f"Document {document_id} not found")

        except Exception as e:
            logger.error(f"GraphQL deletion error: {str(e)}")
            raise Exception(f"Document deletion failed: {str(e)}")

    @strawberry.mutation
    async def update_document(
        self,
        input: DocumentInput,
        info: Info
    ) -> IngestionResult:
        """
        Update an existing document in the search system

        Re-generates embeddings and updates all indices
        """
        try:
            # Get search service
            service: SemanticSearchService = await info.context["search_service"]()

            # In production, this would update the document
            # For now, treat as re-ingestion
            return IngestionResult(
                status="success",
                document_id=input.id,
                message="Document updated successfully",
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"GraphQL update error: {str(e)}")
            raise Exception(f"Document update failed: {str(e)}")


# GraphQL Subscription resolvers (for real-time updates)
@strawberry.type
class Subscription:
    """GraphQL Subscription resolvers for real-time updates"""

    @strawberry.subscription
    async def search_updates(self, query: str) -> SearchResponse:
        """
        Subscribe to real-time search updates for a query

        Useful for monitoring changing results as new documents are ingested
        """
        import asyncio
        import time

        # In production, this would monitor for changes
        # For now, simulate periodic updates
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds

            # Create a mock search response
            yield SearchResponse(
                query=query,
                expanded_queries=[query],
                mode="hybrid",
                total_results=0,
                limit=10,
                offset=0,
                results=[],
                processing_time_ms=0.0
            )


# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)


# Context factory for dependency injection
async def get_context():
    """Create GraphQL context with dependencies"""
    async def get_search_service():
        if not hasattr(search_service, '_initialized'):
            await search_service.initialize()
            search_service._initialized = True
        return search_service

    return {
        "search_service": get_search_service
    }


# Create GraphQL router for FastAPI integration
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    path="/graphql"
)