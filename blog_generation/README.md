# Blog Post Generation Service

AI-powered blog post generation service using FastAPI and LangChain, with multiple style templates and SEO optimization.

## Features

- **Multiple Blog Styles**: Support for 11 different blog post styles (informative, how-to, listicle, technical, opinion, case study, comparison, narrative, persuasive, news)
- **LangChain Integration**: Uses Claude 3.5 Sonnet (primary) and GPT-4 (fallback) for high-quality content generation
- **SEO Optimization**: Built-in SEO optimization including keyword density, meta tags, readability scoring, and structured data
- **Content Templates**: Pre-defined templates for each blog style with recommended structures
- **Topic Research**: AI-powered topic research and outline generation
- **Customizable Output**: Control tone, length, target audience, and include custom instructions
- **FastAPI Backend**: High-performance async API with automatic documentation

## Architecture

```
blog_generation/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── content_generator.py    # LangChain content generation
│   ├── templates.py            # Blog post templates
│   └── seo_optimizer.py        # SEO optimization utilities
├── tests/
│   ├── test_api.py            # API endpoint tests
│   ├── test_seo.py            # SEO optimizer tests
│   └── test_templates.py      # Template system tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Installation

1. **Clone and navigate to the blog generation directory:**
```bash
cd blog_generation
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the service:**
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health Check
- `GET /` - Service health status

### Content Generation
- `POST /api/v1/generate` - Generate a complete blog post
- `POST /api/v1/generate-outline` - Generate blog post outline
- `POST /api/v1/research-topic` - Research a topic for content ideas

### Templates & Styles
- `GET /api/v1/templates` - List available templates
- `GET /api/v1/styles` - List available blog styles

## Usage Examples

### Generate a Blog Post

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "topic": "The Future of AI in Healthcare",
        "style": "informative",
        "tone": "professional",
        "length": "medium",
        "keywords": ["AI healthcare", "medical AI", "healthcare technology"],
        "target_audience": "Healthcare professionals and tech enthusiasts",
        "include_images": True,
        "include_cta": True
    }
)

blog_post = response.json()
```

### Generate an Outline

```python
response = requests.post(
    "http://localhost:8000/api/v1/generate-outline",
    params={
        "topic": "Cloud Computing Best Practices",
        "style": "howto"
    }
)

outline = response.json()
```

## Blog Styles

1. **Informative**: Factual, educational content with data and statistics
2. **How-To**: Step-by-step guides and tutorials
3. **Listicle**: Numbered or bulleted lists with descriptions
4. **Technical**: Code examples, architecture designs, technical deep-dives
5. **Opinion**: Thought leadership and perspective pieces
6. **Case Study**: Real-world examples with metrics and results
7. **Comparison**: Side-by-side analysis of options
8. **Narrative**: Story-driven content with personal experiences
9. **Persuasive**: Convince readers to take action
10. **News**: Timely updates and announcements
11. **Comprehensive**: In-depth, long-form content (2500+ words)

## Blog Tones

- Professional
- Casual
- Conversational
- Academic
- Humorous
- Inspirational
- Authoritative
- Friendly

## SEO Features

- **Keyword Optimization**: Automatic keyword placement with optimal density
- **Meta Tags**: Generated title tags and meta descriptions
- **Readability Scoring**: Flesch Reading Ease score calculation
- **Structured Data**: Schema.org JSON-LD for rich snippets
- **Heading Optimization**: SEO-friendly heading structure
- **Internal Linking**: Suggested related topics for linking
- **Content Analysis**: Keyword opportunities and readability issues detection

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific test categories:

```bash
pytest tests/test_api.py -v      # API tests
pytest tests/test_seo.py -v      # SEO tests
pytest tests/test_templates.py -v # Template tests
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Claude API key (primary LLM)
- `OPENAI_API_KEY`: OpenAI API key (fallback LLM)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)

## Performance Considerations

- Content generation typically takes 5-15 seconds depending on length
- API responses are async for better concurrency
- LLM fallback ensures service availability
- Caching can be implemented for frequently requested topics

## Migration to plasma-engine-content

This implementation is designed as a prototype that should be migrated to the `plasma-engine-content` repository. When migrating:

1. Update imports to match the content service structure
2. Integrate with existing authentication/authorization
3. Connect to production databases (PostgreSQL, Redis)
4. Add Celery tasks for async processing
5. Implement content storage in Cloudflare R2
6. Add monitoring with OpenTelemetry

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

Part of the Plasma Engine platform - see main repository for license details.