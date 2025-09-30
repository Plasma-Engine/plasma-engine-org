"""Main FastAPI application for blog post generation"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from app.models import BlogPostRequest, BlogPostResponse, BlogStyle, HealthResponse
from app.content_generator import ContentGenerator
from app.seo_optimizer import SEOOptimizer
from typing import List

load_dotenv()

# Initialize generators
content_generator = None
seo_optimizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global content_generator, seo_optimizer

    # Initialize services on startup
    content_generator = ContentGenerator()
    seo_optimizer = SEOOptimizer()

    yield

    # Cleanup on shutdown
    content_generator = None
    seo_optimizer = None

# Create FastAPI app
app = FastAPI(
    title="Blog Post Generation API",
    description="AI-powered blog post generation with LangChain and SEO optimization",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "content_generator": content_generator is not None,
            "seo_optimizer": seo_optimizer is not None
        }
    )

@app.post("/api/v1/generate", response_model=BlogPostResponse)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post based on the provided parameters"""
    try:
        # Generate initial content
        content = await content_generator.generate(
            topic=request.topic,
            style=request.style,
            length=request.length,
            keywords=request.keywords,
            tone=request.tone,
            target_audience=request.target_audience
        )

        # Optimize for SEO
        optimized_content = await seo_optimizer.optimize(
            content=content,
            keywords=request.keywords,
            topic=request.topic
        )

        return BlogPostResponse(
            success=True,
            content=optimized_content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-outline")
async def generate_outline(topic: str, style: BlogStyle = BlogStyle.INFORMATIVE):
    """Generate a blog post outline for the given topic"""
    try:
        outline = await content_generator.generate_outline(topic, style)
        return {"success": True, "outline": outline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/research-topic")
async def research_topic(topic: str, depth: str = "medium"):
    """Research a topic to gather information for blog post generation"""
    try:
        research = await content_generator.research_topic(topic, depth)
        return {"success": True, "research": research}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/templates")
async def get_templates():
    """Get available blog post templates"""
    templates = content_generator.get_available_templates()
    return {"templates": templates}

@app.get("/api/v1/styles")
async def get_styles():
    """Get available blog post styles"""
    return {
        "styles": [style.value for style in BlogStyle]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)