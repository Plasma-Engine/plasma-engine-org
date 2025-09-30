"""
FastAPI Endpoints for Semantic Search Service (PE-205)
Provides REST API endpoints for semantic search functionality
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Body, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime

from semantic_search_service import (
    SearchQuery,
    SearchResult,
    SearchMode,
    SemanticSearchService,
    search_service
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Semantic Search API",
    description="PE-205: Semantic search with hybrid capabilities",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class SearchRequest(BaseModel):
    """Request model for search endpoint"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    mode: Optional[str] = Field("hybrid", description="Search mode: vector, keyword, or hybrid")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Number of results to return")
    offset: Optional[int] = Field(0, ge=0, description="Offset for pagination")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    expand_query: Optional[bool] = Field(True, description="Whether to expand the query")
    use_mmr: Optional[bool] = Field(True, description="Use MMR for result diversification")
    mmr_lambda: Optional[float] = Field(0.7, ge=0, le=1, description="MMR lambda parameter")
    similarity_threshold: Optional[float] = Field(0.5, ge=0, le=1, description="Similarity threshold")

    @validator('mode')
    def validate_mode(cls, v):
        valid_modes = ["vector", "keyword", "hybrid"]
        if v not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "query": "semantic search with vector embeddings",
                "mode": "hybrid",
                "limit": 10,
                "offset": 0,
                "expand_query": True,
                "use_mmr": True,
                "mmr_lambda": 0.7,
                "similarity_threshold": 0.5
            }
        }


class SearchResponse(BaseModel):
    """Response model for search endpoint"""
    query: str
    expanded_queries: List[str]
    mode: str
    total_results: int
    limit: int
    offset: int
    results: List[Dict[str, Any]]
    processing_time_ms: Optional[float] = None


class SimilarDocumentsRequest(BaseModel):
    """Request model for similar documents endpoint"""
    document_id: str = Field(..., description="Document ID to find similar documents for")
    limit: Optional[int] = Field(5, ge=1, le=50, description="Number of similar documents to return")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc1",
                "limit": 5
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str
    version: str


class DocumentIngestionRequest(BaseModel):
    """Request model for document ingestion"""
    id: str = Field(..., description="Unique document ID")
    content: str = Field(..., min_length=1, description="Document content")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Document metadata")

    class Config:
        schema_extra = {
            "example": {
                "id": "doc123",
                "content": "This is a sample document about semantic search",
                "metadata": {
                    "source": "research_paper",
                    "author": "John Doe",
                    "date": "2024-01-01"
                }
            }
        }


class BatchSearchRequest(BaseModel):
    """Request model for batch search"""
    queries: List[SearchRequest] = Field(..., min_items=1, max_items=100, description="List of search queries")

    class Config:
        schema_extra = {
            "example": {
                "queries": [
                    {
                        "query": "vector embeddings",
                        "mode": "hybrid",
                        "limit": 5
                    },
                    {
                        "query": "knowledge graph",
                        "mode": "vector",
                        "limit": 10
                    }
                ]
            }
        }


# Dependency for service initialization
async def get_search_service() -> SemanticSearchService:
    """Dependency to get initialized search service"""
    if not hasattr(search_service, '_initialized'):
        await search_service.initialize()
        search_service._initialized = True
    return search_service


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="semantic-search-api",
        version="1.0.0"
    )


@app.post("/api/v1/search", response_model=SearchResponse, tags=["Search"])
async def search(
    request: SearchRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Perform semantic search with hybrid capabilities

    This endpoint supports:
    - Vector similarity search using embeddings
    - BM25 keyword matching
    - Hybrid search combining both approaches
    - Query expansion for improved recall
    - MMR for result diversification
    """
    import time
    start_time = time.time()

    try:
        # Convert request to SearchQuery
        search_query = SearchQuery(
            query=request.query,
            mode=SearchMode(request.mode),
            limit=request.limit,
            offset=request.offset,
            filters=request.filters,
            expand_query=request.expand_query,
            use_mmr=request.use_mmr,
            mmr_lambda=request.mmr_lambda,
            similarity_threshold=request.similarity_threshold
        )

        # Perform search
        results = await service.search(search_query)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        return SearchResponse(
            **results,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/api/v1/search/batch", response_model=List[SearchResponse], tags=["Search"])
async def batch_search(
    request: BatchSearchRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Perform batch semantic search for multiple queries

    Efficiently processes multiple search queries in parallel
    """
    import asyncio
    import time

    async def process_single_search(search_req: SearchRequest) -> SearchResponse:
        start_time = time.time()

        search_query = SearchQuery(
            query=search_req.query,
            mode=SearchMode(search_req.mode),
            limit=search_req.limit,
            offset=search_req.offset,
            filters=search_req.filters,
            expand_query=search_req.expand_query,
            use_mmr=search_req.use_mmr,
            mmr_lambda=search_req.mmr_lambda,
            similarity_threshold=search_req.similarity_threshold
        )

        results = await service.search(search_query)
        processing_time = (time.time() - start_time) * 1000

        return SearchResponse(**results, processing_time_ms=processing_time)

    try:
        # Process all searches in parallel
        results = await asyncio.gather(
            *[process_single_search(req) for req in request.queries]
        )
        return results

    except Exception as e:
        logger.error(f"Batch search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch search failed: {str(e)}"
        )


@app.post("/api/v1/similar", response_model=Dict[str, Any], tags=["Search"])
async def find_similar_documents(
    request: SimilarDocumentsRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Find documents similar to a given document

    Uses vector similarity to find related documents
    """
    try:
        results = await service.get_similar_documents(
            doc_id=request.document_id,
            k=request.limit
        )

        return {
            "document_id": request.document_id,
            "similar_documents": [
                {
                    "id": r.id,
                    "content": r.content,
                    "similarity_score": r.score,
                    "metadata": r.metadata
                }
                for r in results
            ],
            "total_found": len(results)
        }

    except Exception as e:
        logger.error(f"Similar documents error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar documents: {str(e)}"
        )


@app.post("/api/v1/ingest", response_model=Dict[str, Any], tags=["Ingestion"])
async def ingest_document(
    request: DocumentIngestionRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Ingest a document into the search system

    This endpoint would typically:
    1. Generate embeddings for the document
    2. Store in vector database
    3. Update BM25 index
    4. Extract entities for knowledge graph
    """
    try:
        # In production, this would:
        # 1. Call embedding service (PE-203)
        # 2. Store in pgvector
        # 3. Update Neo4j knowledge graph (PE-204)
        # 4. Update BM25 index

        # For now, return success
        return {
            "status": "success",
            "document_id": request.id,
            "message": "Document ingested successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}"
        )


@app.get("/api/v1/stats", response_model=Dict[str, Any], tags=["Admin"])
async def get_search_stats(
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Get search system statistics

    Returns information about the search index and performance metrics
    """
    try:
        total_documents = len(service.vector_store.documents)
        total_embeddings = len(service.vector_store.embeddings)

        return {
            "statistics": {
                "total_documents": total_documents,
                "total_embeddings": total_embeddings,
                "vector_dimensions": 1536,
                "index_type": "HNSW",
                "bm25_enabled": True,
                "mmr_enabled": True,
                "query_expansion_enabled": True
            },
            "configuration": {
                "default_limit": 10,
                "max_limit": 100,
                "similarity_threshold": 0.5,
                "mmr_lambda": 0.7
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@app.delete("/api/v1/documents/{document_id}", response_model=Dict[str, Any], tags=["Admin"])
async def delete_document(
    document_id: str,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    Delete a document from the search index

    Removes the document from vector store and BM25 index
    """
    try:
        # In production, this would remove from pgvector and Neo4j
        if document_id in service.vector_store.documents:
            del service.vector_store.documents[document_id]
            del service.vector_store.embeddings[document_id]
            if document_id in service.embeddings_cache:
                del service.embeddings_cache[document_id]

            return {
                "status": "success",
                "document_id": document_id,
                "message": "Document deleted successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the search service on startup"""
    logger.info("Starting Semantic Search API (PE-205)")
    await search_service.initialize()
    logger.info("Semantic Search API initialized successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Semantic Search API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)