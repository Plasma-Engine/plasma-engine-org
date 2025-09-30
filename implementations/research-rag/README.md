# RAG Query Engine Implementation for Plasma Engine Research Service

This directory contains the implementation of the RAG (Retrieval-Augmented Generation) Query Engine for PE-206.

## Overview

This implementation provides a complete RAG system with:
- LangChain 0.1+ integration with LCEL
- Context window management (8K tokens)
- Chain-of-thought prompting
- Hallucination detection
- Citation formatting (APA/MLA)
- Streaming responses
- FastAPI endpoints

## Files Structure

```
research-rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI main application
│   └── rag/
│       ├── __init__.py
│       ├── query_engine.py   # Core RAG engine
│       ├── context_manager.py # Context window management
│       ├── api.py           # API endpoints
│       └── examples.py      # Usage examples
├── tests/
│   └── test_rag.py         # Unit tests
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README_RAG.md         # Comprehensive documentation
```

## Integration Instructions

To integrate this into the `plasma-engine-research` repository:

1. Copy the entire directory structure to `plasma-engine-research/`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see `.env.example`)
4. Run the service: `uvicorn app.main:app --reload`

## Key Features Implemented

✅ **Context Retrieval** - Multi-query expansion and intelligent retrieval
✅ **Prompt Engineering** - Chain-of-thought and optimized prompts
✅ **LangChain Integration** - Full LCEL support
✅ **Streaming Responses** - Real-time streaming capability
✅ **Source Attribution** - Automatic citation generation

## API Endpoints

- `POST /api/v1/rag/query` - Execute RAG query
- `POST /api/v1/rag/query/stream` - Stream RAG response
- `POST /api/v1/rag/search` - Semantic search
- `POST /api/v1/rag/ingest` - Ingest documents
- `GET /api/v1/rag/health` - Health check
- `GET /api/v1/rag/stats` - System statistics

## Next Steps

1. Deploy to `plasma-engine-research` repository
2. Connect to production databases (PostgreSQL + pgvector, Neo4j)
3. Configure production OpenAI API keys
4. Set up Redis for caching and task queue
5. Enable CodeRabbit for code review

## Testing

Run tests with:
```bash
pytest tests/test_rag.py -v
```

## Documentation

See `README_RAG.md` for comprehensive documentation including:
- Architecture details
- Configuration options
- Performance considerations
- Troubleshooting guide
- Integration with other Plasma Engine services