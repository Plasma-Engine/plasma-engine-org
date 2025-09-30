"""Pydantic models for blog post generation API"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class BlogStyle(str, Enum):
    """Available blog post styles"""
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    LISTICLE = "listicle"
    HOWTO = "how-to"
    OPINION = "opinion"
    NEWS = "news"
    CASE_STUDY = "case-study"
    COMPARISON = "comparison"

class BlogTone(str, Enum):
    """Available blog post tones"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"

class BlogLength(str, Enum):
    """Blog post length options"""
    SHORT = "short"  # 300-500 words
    MEDIUM = "medium"  # 800-1200 words
    LONG = "long"  # 1500-2000 words
    COMPREHENSIVE = "comprehensive"  # 2500+ words

class BlogPostRequest(BaseModel):
    """Request model for blog post generation"""
    topic: str = Field(..., description="The main topic of the blog post", min_length=3, max_length=200)
    style: BlogStyle = Field(BlogStyle.INFORMATIVE, description="The style of the blog post")
    tone: BlogTone = Field(BlogTone.PROFESSIONAL, description="The tone of the blog post")
    length: BlogLength = Field(BlogLength.MEDIUM, description="Desired length of the blog post")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords to include", max_items=10)
    target_audience: Optional[str] = Field(None, description="Target audience for the blog post")
    include_images: bool = Field(False, description="Whether to include image suggestions")
    include_cta: bool = Field(True, description="Whether to include call-to-action")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions", max_length=500)

    @validator('keywords')
    def validate_keywords(cls, v):
        """Ensure keywords are unique and properly formatted"""
        return list(set([kw.strip().lower() for kw in v if kw.strip()]))

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "The Future of AI in Healthcare",
                "style": "informative",
                "tone": "professional",
                "length": "medium",
                "keywords": ["AI healthcare", "medical AI", "healthcare technology"],
                "target_audience": "Healthcare professionals and tech enthusiasts",
                "include_images": True,
                "include_cta": True
            }
        }

class BlogSection(BaseModel):
    """Model for a blog post section"""
    heading: str
    content: str
    subheadings: Optional[List[str]] = None
    keywords_used: List[str] = Field(default_factory=list)

class SEOMetadata(BaseModel):
    """SEO metadata for the blog post"""
    meta_title: str = Field(..., max_length=60)
    meta_description: str = Field(..., max_length=160)
    slug: str
    keywords: List[str]
    readability_score: Optional[float] = None
    keyword_density: Optional[Dict[str, float]] = None
    structured_data: Optional[Dict[str, Any]] = None

class BlogPost(BaseModel):
    """Complete blog post model"""
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = Field(default="AI Content Generator")
    created_at: datetime = Field(default_factory=datetime.now)
    style: BlogStyle
    tone: BlogTone
    introduction: str
    sections: List[BlogSection]
    conclusion: str
    call_to_action: Optional[str] = None
    seo_metadata: SEOMetadata
    word_count: int
    reading_time: int  # in minutes
    image_suggestions: Optional[List[Dict[str, str]]] = None
    related_topics: Optional[List[str]] = None
    sources: Optional[List[str]] = None

class BlogPostResponse(BaseModel):
    """Response model for blog post generation"""
    success: bool
    content: BlogPost
    generation_time: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content": {
                    "title": "The Future of AI in Healthcare: Transforming Patient Care",
                    "subtitle": "How artificial intelligence is revolutionizing medical diagnosis and treatment",
                    "author": "AI Content Generator",
                    "created_at": "2024-01-15T10:30:00",
                    "style": "informative",
                    "tone": "professional",
                    "introduction": "Artificial intelligence is rapidly transforming...",
                    "sections": [],
                    "conclusion": "The future of AI in healthcare is bright...",
                    "call_to_action": "Stay informed about the latest AI healthcare innovations...",
                    "seo_metadata": {
                        "meta_title": "AI in Healthcare: Future of Medical Technology",
                        "meta_description": "Discover how AI is transforming healthcare...",
                        "slug": "ai-healthcare-future-medical-technology",
                        "keywords": ["AI healthcare", "medical AI"]
                    },
                    "word_count": 1200,
                    "reading_time": 5
                }
            }
        }

class BlogOutline(BaseModel):
    """Model for blog post outline"""
    title: str
    sections: List[Dict[str, Any]]
    estimated_word_count: int
    keywords_coverage: List[str]

class ResearchResult(BaseModel):
    """Model for topic research results"""
    topic: str
    key_points: List[str]
    related_topics: List[str]
    trending_angles: List[str]
    competitors: Optional[List[Dict[str, str]]] = None
    data_points: Optional[List[Dict[str, Any]]] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    services: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.now)