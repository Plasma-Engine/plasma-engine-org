"""Tests for FastAPI blog generation endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import BlogStyle, BlogTone, BlogLength

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data

def test_generate_blog_post():
    """Test blog post generation endpoint"""
    request_data = {
        "topic": "The Future of AI in Healthcare",
        "style": "informative",
        "tone": "professional",
        "length": "medium",
        "keywords": ["AI healthcare", "medical AI", "healthcare technology"],
        "target_audience": "Healthcare professionals",
        "include_images": False,
        "include_cta": True
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] == True
    assert "content" in data

    content = data["content"]
    assert "title" in content
    assert "introduction" in content
    assert "sections" in content
    assert "conclusion" in content
    assert "seo_metadata" in content
    assert "word_count" in content
    assert "reading_time" in content

def test_generate_outline():
    """Test blog post outline generation"""
    response = client.post(
        "/api/v1/generate-outline",
        params={"topic": "Cloud Computing Best Practices", "style": "howto"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] == True
    assert "outline" in data

def test_research_topic():
    """Test topic research endpoint"""
    response = client.post(
        "/api/v1/research-topic",
        params={"topic": "Quantum Computing", "depth": "medium"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] == True
    assert "research" in data

def test_get_templates():
    """Test template listing endpoint"""
    response = client.get("/api/v1/templates")
    assert response.status_code == 200

    data = response.json()
    assert "templates" in data
    assert isinstance(data["templates"], list)
    assert len(data["templates"]) > 0

def test_get_styles():
    """Test style listing endpoint"""
    response = client.get("/api/v1/styles")
    assert response.status_code == 200

    data = response.json()
    assert "styles" in data
    assert isinstance(data["styles"], list)
    assert "informative" in data["styles"]
    assert "howto" in data["styles"]

def test_invalid_style():
    """Test with invalid blog style"""
    request_data = {
        "topic": "Test Topic",
        "style": "invalid_style",
        "tone": "professional",
        "length": "medium"
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 422  # Validation error

def test_missing_topic():
    """Test with missing required topic field"""
    request_data = {
        "style": "informative",
        "tone": "professional",
        "length": "medium"
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 422  # Validation error

def test_long_topic():
    """Test with topic exceeding maximum length"""
    request_data = {
        "topic": "x" * 201,  # Exceeds 200 character limit
        "style": "informative",
        "tone": "professional",
        "length": "medium"
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 422  # Validation error

def test_keyword_validation():
    """Test keyword deduplication and formatting"""
    request_data = {
        "topic": "SEO Best Practices",
        "style": "informative",
        "tone": "professional",
        "length": "medium",
        "keywords": ["SEO", "seo", " SEO ", "optimization", "OPTIMIZATION"]
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    # Keywords should be deduplicated and lowercase
    # This would be checked in the actual implementation

def test_all_blog_styles():
    """Test generation with all available blog styles"""
    styles = [style.value for style in BlogStyle]

    for style in styles:
        request_data = {
            "topic": f"Test Topic for {style}",
            "style": style,
            "tone": "professional",
            "length": "short"
        }

        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 200, f"Failed for style: {style}"
        data = response.json()
        assert data["success"] == True

def test_all_blog_tones():
    """Test generation with all available blog tones"""
    tones = [tone.value for tone in BlogTone]

    for tone in tones:
        request_data = {
            "topic": f"Test Topic for {tone} tone",
            "style": "informative",
            "tone": tone,
            "length": "short"
        }

        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 200, f"Failed for tone: {tone}"
        data = response.json()
        assert data["success"] == True

def test_all_blog_lengths():
    """Test generation with all available blog lengths"""
    lengths = [length.value for length in BlogLength]

    for length in lengths:
        request_data = {
            "topic": f"Test Topic for {length} length",
            "style": "informative",
            "tone": "professional",
            "length": length
        }

        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 200, f"Failed for length: {length}"
        data = response.json()
        assert data["success"] == True