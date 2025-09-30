"""
Semantic Search Service Implementation (PE-205)
Provides hybrid search capabilities with vector similarity and keyword matching
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import json

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Search modes supported by the semantic search service"""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class SearchQuery:
    """Represents a search query with various parameters"""
    query: str
    mode: SearchMode = SearchMode.HYBRID
    limit: int = 10
    offset: int = 0
    filters: Optional[Dict[str, Any]] = None
    expand_query: bool = True
    use_mmr: bool = True
    mmr_lambda: float = 0.7
    similarity_threshold: float = 0.5


@dataclass
class SearchResult:
    """Represents a single search result"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str
    highlights: Optional[List[str]] = None


class VectorStore:
    """Mock vector store for demonstration - replace with pgvector in production"""

    def __init__(self):
        self.embeddings = {}
        self.documents = {}

    async def add_embedding(self, doc_id: str, embedding: np.ndarray, document: Dict[str, Any]):
        """Add an embedding to the store"""
        self.embeddings[doc_id] = embedding
        self.documents[doc_id] = document

    async def similarity_search(self, query_embedding: np.ndarray, k: int = 10, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """Perform cosine similarity search"""
        if not self.embeddings:
            return []

        # Convert embeddings to matrix
        doc_ids = list(self.embeddings.keys())
        embeddings_matrix = np.array([self.embeddings[doc_id] for doc_id in doc_ids])

        # Calculate cosine similarities
        similarities = cosine_similarity([query_embedding], embeddings_matrix)[0]

        # Filter by threshold and get top k
        results = []
        for idx, score in enumerate(similarities):
            if score >= threshold:
                results.append((doc_ids[idx], float(score)))

        # Sort by score and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID"""
        return self.documents.get(doc_id)


class BM25Scorer:
    """BM25 scoring for keyword search"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = {}
        self.doc_lengths = {}
        self.avg_doc_length = 0
        self.total_docs = 0
        self.inverted_index = {}

    def fit(self, documents: List[Tuple[str, str]]):
        """Build the BM25 index from documents"""
        total_length = 0

        for doc_id, content in documents:
            tokens = content.lower().split()
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)

            # Build inverted index
            for token in set(tokens):
                if token not in self.inverted_index:
                    self.inverted_index[token] = set()
                self.inverted_index[token].add(doc_id)

                if token not in self.doc_freqs:
                    self.doc_freqs[token] = 0
                self.doc_freqs[token] += 1

        self.total_docs = len(documents)
        self.avg_doc_length = total_length / self.total_docs if self.total_docs > 0 else 0

    def score(self, query: str, doc_id: str, content: str) -> float:
        """Calculate BM25 score for a document given a query"""
        query_tokens = query.lower().split()
        doc_tokens = content.lower().split()
        doc_length = self.doc_lengths.get(doc_id, 0)

        score = 0.0
        for token in query_tokens:
            if token in doc_tokens:
                # Term frequency
                tf = doc_tokens.count(token)

                # Inverse document frequency
                df = self.doc_freqs.get(token, 0)
                idf = np.log((self.total_docs - df + 0.5) / (df + 0.5) + 1)

                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))

                score += idf * (numerator / denominator)

        return score


class QueryExpander:
    """Expands queries using various techniques"""

    async def expand(self, query: str) -> List[str]:
        """Expand the query with synonyms and related terms"""
        # In production, this would use LLM or WordNet for real expansion
        expanded_terms = [query]

        # Simple mock expansion rules
        expansions = {
            "search": ["find", "lookup", "query", "retrieve"],
            "vector": ["embedding", "representation", "feature"],
            "semantic": ["meaning", "contextual", "understanding"],
            "api": ["interface", "endpoint", "service"],
            "document": ["file", "text", "content", "data"]
        }

        for word in query.lower().split():
            if word in expansions:
                expanded_terms.extend(expansions[word])

        return expanded_terms


class MaximalMarginalRelevance:
    """Implements MMR for result diversification"""

    @staticmethod
    def rerank(results: List[SearchResult], embeddings: Dict[str, np.ndarray],
               query_embedding: np.ndarray, lambda_param: float = 0.7, k: int = 10) -> List[SearchResult]:
        """Rerank results using MMR algorithm"""
        if len(results) <= 1:
            return results

        selected = []
        unselected = results.copy()

        # Select first item (highest relevance)
        selected.append(unselected.pop(0))

        while len(selected) < k and unselected:
            best_score = -float('inf')
            best_idx = -1

            for idx, candidate in enumerate(unselected):
                # Relevance score (similarity to query)
                relevance = candidate.score

                # Diversity score (dissimilarity to selected items)
                diversity = 1.0
                if selected and candidate.id in embeddings:
                    candidate_emb = embeddings[candidate.id]
                    for sel in selected:
                        if sel.id in embeddings:
                            sel_emb = embeddings[sel.id]
                            similarity = cosine_similarity([candidate_emb], [sel_emb])[0][0]
                            diversity = min(diversity, 1 - similarity)

                # MMR score
                mmr_score = lambda_param * relevance + (1 - lambda_param) * diversity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx >= 0:
                selected.append(unselected.pop(best_idx))

        return selected


class SemanticSearchService:
    """Main semantic search service implementing PE-205 requirements"""

    def __init__(self):
        self.vector_store = VectorStore()
        self.bm25_scorer = BM25Scorer()
        self.query_expander = QueryExpander()
        self.mmr = MaximalMarginalRelevance
        self.embeddings_cache = {}

    async def initialize(self):
        """Initialize the search service with sample data"""
        # In production, this would connect to pgvector and Neo4j
        sample_documents = [
            {
                "id": "doc1",
                "content": "Semantic search using vector embeddings and neural networks",
                "embedding": np.random.randn(1536)  # Mock embedding
            },
            {
                "id": "doc2",
                "content": "GraphRAG knowledge graph for advanced retrieval",
                "embedding": np.random.randn(1536)
            },
            {
                "id": "doc3",
                "content": "Hybrid search combining vector similarity and keyword matching",
                "embedding": np.random.randn(1536)
            },
            {
                "id": "doc4",
                "content": "Query expansion techniques for improved search relevance",
                "embedding": np.random.randn(1536)
            },
            {
                "id": "doc5",
                "content": "FastAPI endpoints for building modern REST APIs",
                "embedding": np.random.randn(1536)
            }
        ]

        # Add to vector store
        for doc in sample_documents:
            await self.vector_store.add_embedding(
                doc["id"],
                doc["embedding"],
                {"content": doc["content"], "metadata": {}}
            )
            self.embeddings_cache[doc["id"]] = doc["embedding"]

        # Build BM25 index
        doc_pairs = [(doc["id"], doc["content"]) for doc in sample_documents]
        self.bm25_scorer.fit(doc_pairs)

        logger.info("Semantic search service initialized with sample data")

    async def get_query_embedding(self, query: str) -> np.ndarray:
        """Get embedding for a query"""
        # In production, this would call OpenAI or local embedding model
        # For now, return a mock embedding
        query_hash = hashlib.md5(query.encode()).hexdigest()
        np.random.seed(int(query_hash[:8], 16))
        return np.random.randn(1536)

    async def vector_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform pure vector similarity search"""
        query_embedding = await self.get_query_embedding(query.query)

        similar_docs = await self.vector_store.similarity_search(
            query_embedding,
            k=query.limit + query.offset,
            threshold=query.similarity_threshold
        )

        results = []
        for doc_id, score in similar_docs[query.offset:]:
            doc = await self.vector_store.get_document(doc_id)
            if doc:
                results.append(SearchResult(
                    id=doc_id,
                    content=doc["content"],
                    score=score,
                    metadata=doc.get("metadata", {}),
                    source="vector"
                ))

        return results

    async def keyword_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform BM25 keyword search"""
        results = []

        # Score all documents
        for doc_id, doc in self.vector_store.documents.items():
            score = self.bm25_scorer.score(query.query, doc_id, doc["content"])
            if score > 0:
                results.append(SearchResult(
                    id=doc_id,
                    content=doc["content"],
                    score=score,
                    metadata=doc.get("metadata", {}),
                    source="keyword"
                ))

        # Sort by score and apply pagination
        results.sort(key=lambda x: x.score, reverse=True)
        return results[query.offset:query.offset + query.limit]

    async def hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform hybrid search combining vector and keyword approaches"""
        # Get results from both methods
        vector_results = await self.vector_search(query)
        keyword_results = await self.keyword_search(query)

        # Combine and normalize scores
        combined_results = {}

        # Add vector results
        for result in vector_results:
            combined_results[result.id] = {
                "result": result,
                "vector_score": result.score,
                "keyword_score": 0
            }

        # Add/update with keyword results
        for result in keyword_results:
            if result.id in combined_results:
                combined_results[result.id]["keyword_score"] = result.score
            else:
                combined_results[result.id] = {
                    "result": result,
                    "vector_score": 0,
                    "keyword_score": result.score
                }

        # Calculate combined scores (weighted average)
        final_results = []
        for doc_id, scores in combined_results.items():
            # Normalize and combine scores
            vector_weight = 0.7
            keyword_weight = 0.3

            combined_score = (
                vector_weight * scores["vector_score"] +
                keyword_weight * min(scores["keyword_score"] / 10, 1.0)  # Normalize BM25 scores
            )

            result = scores["result"]
            result.score = combined_score
            result.source = "hybrid"
            final_results.append(result)

        # Sort by combined score
        final_results.sort(key=lambda x: x.score, reverse=True)

        # Apply MMR if requested
        if query.use_mmr:
            query_embedding = await self.get_query_embedding(query.query)
            final_results = self.mmr.rerank(
                final_results,
                self.embeddings_cache,
                query_embedding,
                lambda_param=query.mmr_lambda,
                k=query.limit
            )

        return final_results[:query.limit]

    async def search(self, query: SearchQuery) -> Dict[str, Any]:
        """Main search method that routes to appropriate search type"""
        # Expand query if requested
        expanded_queries = [query.query]
        if query.expand_query:
            expanded_queries = await self.query_expander.expand(query.query)

        # Perform search based on mode
        if query.mode == SearchMode.VECTOR:
            results = await self.vector_search(query)
        elif query.mode == SearchMode.KEYWORD:
            results = await self.keyword_search(query)
        else:  # HYBRID
            results = await self.hybrid_search(query)

        # Apply filters if provided
        if query.filters:
            results = self._apply_filters(results, query.filters)

        # Return formatted response
        return {
            "query": query.query,
            "expanded_queries": expanded_queries if query.expand_query else [],
            "mode": query.mode.value,
            "total_results": len(results),
            "limit": query.limit,
            "offset": query.offset,
            "results": [asdict(r) for r in results]
        }

    def _apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """Apply metadata filters to search results"""
        filtered = []
        for result in results:
            match = True
            for key, value in filters.items():
                if key not in result.metadata or result.metadata[key] != value:
                    match = False
                    break
            if match:
                filtered.append(result)
        return filtered

    async def get_similar_documents(self, doc_id: str, k: int = 5) -> List[SearchResult]:
        """Find documents similar to a given document"""
        if doc_id not in self.embeddings_cache:
            return []

        doc_embedding = self.embeddings_cache[doc_id]
        similar_docs = await self.vector_store.similarity_search(doc_embedding, k=k+1)

        # Remove the query document itself
        results = []
        for similar_id, score in similar_docs:
            if similar_id != doc_id:
                doc = await self.vector_store.get_document(similar_id)
                if doc:
                    results.append(SearchResult(
                        id=similar_id,
                        content=doc["content"],
                        score=score,
                        metadata=doc.get("metadata", {}),
                        source="similarity"
                    ))

        return results[:k]


# Service instance
search_service = SemanticSearchService()