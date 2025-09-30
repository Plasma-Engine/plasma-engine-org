"""Tests for SEO optimization functionality"""

import pytest
from app.seo_optimizer import SEOOptimizer
from app.models import BlogPost, BlogSection, SEOMetadata, BlogStyle, BlogTone
from datetime import datetime

@pytest.fixture
def seo_optimizer():
    """Create SEO optimizer instance"""
    return SEOOptimizer()

@pytest.fixture
def sample_blog_post():
    """Create sample blog post for testing"""
    return BlogPost(
        title="Introduction to Machine Learning",
        subtitle="A Beginner's Guide",
        author="Test Author",
        created_at=datetime.now(),
        style=BlogStyle.INFORMATIVE,
        tone=BlogTone.PROFESSIONAL,
        introduction="Machine learning is transforming how we solve problems.",
        sections=[
            BlogSection(
                heading="What is Machine Learning?",
                content="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                subheadings=[],
                keywords_used=[]
            ),
            BlogSection(
                heading="Types of Machine Learning",
                content="There are three main types: supervised, unsupervised, and reinforcement learning.",
                subheadings=["Supervised Learning", "Unsupervised Learning"],
                keywords_used=[]
            )
        ],
        conclusion="Machine learning continues to evolve and shape our future.",
        call_to_action="Start your machine learning journey today!",
        seo_metadata=SEOMetadata(
            meta_title="Introduction to Machine Learning",
            meta_description="Learn the basics of machine learning",
            slug="introduction-machine-learning",
            keywords=["machine learning", "AI", "artificial intelligence"]
        ),
        word_count=500,
        reading_time=2
    )

@pytest.mark.asyncio
async def test_optimize_blog_post(seo_optimizer, sample_blog_post):
    """Test blog post optimization"""
    keywords = ["machine learning", "AI", "data science"]
    topic = "Machine Learning Basics"

    optimized = await seo_optimizer.optimize(sample_blog_post, keywords, topic)

    assert optimized is not None
    assert isinstance(optimized, BlogPost)
    assert optimized.title is not None
    assert optimized.seo_metadata is not None

def test_optimize_title(seo_optimizer):
    """Test title optimization"""
    title = "Understanding Python"
    keywords = ["Python programming", "coding", "development"]
    topic = "Python Programming"

    optimized_title = seo_optimizer._optimize_title(title, keywords, topic)

    assert optimized_title is not None
    assert len(optimized_title) <= 60
    # Should try to include primary keyword
    assert "python" in optimized_title.lower()

def test_optimize_heading(seo_optimizer):
    """Test heading optimization"""
    heading = "Getting Started Guide"
    keywords = ["Python", "programming", "tutorial"]

    optimized_heading = seo_optimizer._optimize_heading(heading, keywords)

    assert optimized_heading is not None
    assert isinstance(optimized_heading, str)

def test_optimize_paragraph(seo_optimizer):
    """Test paragraph optimization"""
    paragraph = """This is a sample paragraph about programming.
    It contains information about coding and development.
    We will discuss various aspects of software engineering."""

    keywords = ["programming", "coding", "software"]

    optimized = seo_optimizer._optimize_paragraph(paragraph, keywords)

    assert optimized is not None
    assert isinstance(optimized, str)

def test_improve_readability(seo_optimizer):
    """Test readability improvement"""
    long_sentence = " ".join(["word"] * 40)  # 40-word sentence

    improved = seo_optimizer._improve_readability(long_sentence)

    # Should break long sentences
    assert improved is not None
    sentences = improved.split(". ")
    for sentence in sentences:
        assert len(sentence.split()) <= 35  # No sentence should be too long

def test_calculate_readability_score(seo_optimizer, sample_blog_post):
    """Test readability score calculation"""
    score = seo_optimizer._calculate_readability_score(sample_blog_post)

    assert isinstance(score, float)
    assert 0 <= score <= 100

def test_generate_related_topics(seo_optimizer, sample_blog_post):
    """Test related topics generation"""
    topic = "Machine Learning"
    related = seo_optimizer._generate_related_topics(topic, sample_blog_post)

    assert isinstance(related, list)
    assert len(related) <= 5
    for topic in related:
        assert isinstance(topic, str)

def test_generate_structured_data(seo_optimizer, sample_blog_post):
    """Test structured data generation"""
    structured_data = seo_optimizer._generate_structured_data(sample_blog_post)

    assert isinstance(structured_data, dict)
    assert structured_data["@context"] == "https://schema.org"
    assert structured_data["@type"] == "BlogPosting"
    assert "headline" in structured_data
    assert "wordCount" in structured_data

def test_analyze_content(seo_optimizer):
    """Test content analysis"""
    content = """# Main Title

    This is the introduction paragraph. It contains important information.

    ## Section 1
    Here we discuss the first topic in detail. This section has multiple sentences.

    ## Section 2
    The second section covers additional points. We explore various aspects here.

    This is the conclusion paragraph. It summarizes everything."""

    analysis = seo_optimizer.analyze_content(content)

    assert "word_count" in analysis
    assert "sentence_count" in analysis
    assert "paragraph_count" in analysis
    assert "heading_structure" in analysis
    assert "keyword_opportunities" in analysis
    assert "readability_issues" in analysis

def test_find_keyword_opportunities(seo_optimizer):
    """Test keyword opportunity detection"""
    content = """How to improve your coding skills.
    Best practices for software development.
    Tips for optimizing performance.
    Guide to advanced programming techniques."""

    opportunities = seo_optimizer._find_keyword_opportunities(content)

    assert isinstance(opportunities, list)
    assert len(opportunities) > 0
    # Should find patterns like "how to", "best practices", etc.

def test_find_readability_issues(seo_optimizer):
    """Test readability issue detection"""
    # Create content with known issues
    long_sentence = " ".join(["word"] * 35)  # Very long sentence
    content = f"{long_sentence}. Short sentence. Another short one."

    issues = seo_optimizer._find_readability_issues(content)

    assert isinstance(issues, list)
    assert len(issues) > 0
    # Should detect the long sentence
    assert any("Long sentence" in issue for issue in issues)

def test_keyword_density_calculation(seo_optimizer, sample_blog_post):
    """Test keyword density calculation"""
    keywords = ["machine learning", "AI"]

    # Optimize to calculate keyword density
    seo_optimizer._enhance_seo_metadata(
        sample_blog_post.seo_metadata,
        sample_blog_post,
        keywords
    )

    assert sample_blog_post.seo_metadata.keyword_density is not None
    for keyword in keywords:
        if keyword in sample_blog_post.seo_metadata.keyword_density:
            density = sample_blog_post.seo_metadata.keyword_density[keyword]
            assert isinstance(density, float)
            assert density >= 0

def test_meta_description_optimization(seo_optimizer):
    """Test meta description optimization"""
    metadata = SEOMetadata(
        meta_title="Test Title",
        meta_description="This is a test description",
        slug="test-slug",
        keywords=[]
    )

    blog_post = BlogPost(
        title="Test",
        style=BlogStyle.INFORMATIVE,
        tone=BlogTone.PROFESSIONAL,
        introduction="Test intro",
        sections=[],
        conclusion="Test conclusion",
        seo_metadata=metadata,
        word_count=100,
        reading_time=1,
        created_at=datetime.now()
    )

    keywords = ["SEO", "optimization"]

    enhanced = seo_optimizer._enhance_seo_metadata(metadata, blog_post, keywords)

    assert enhanced.meta_description is not None
    assert len(enhanced.meta_description) <= 160
    # Should include keywords if possible
    assert any(kw.lower() in enhanced.meta_description.lower() for kw in keywords)