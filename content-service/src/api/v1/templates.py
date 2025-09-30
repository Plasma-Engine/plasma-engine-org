"""
Content template API endpoints.
"""

from typing import List, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class TemplateCreate(BaseModel):
    """Create template request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=1000)
    category: str = Field(..., max_length=100)
    system_prompt: str = Field(...)
    user_prompt_template: str = Field(...)


class TemplateResponse(BaseModel):
    """Template response."""
    id: str
    name: str
    description: str
    category: str


# Default templates for demo
DEFAULT_TEMPLATES = [
    {
        "id": str(uuid4()),
        "name": "Blog Post Template",
        "description": "Standard blog post template with SEO optimization",
        "category": "blog",
    },
    {
        "id": str(uuid4()),
        "name": "Product Description",
        "description": "E-commerce product description template",
        "category": "ecommerce",
    },
    {
        "id": str(uuid4()),
        "name": "Email Newsletter",
        "description": "Email newsletter template for marketing campaigns",
        "category": "email",
    },
]


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
):
    """List all available content templates."""
    templates = DEFAULT_TEMPLATES

    # Filter by category if provided
    if category:
        templates = [t for t in templates if t["category"] == category]

    # Apply pagination
    return templates[skip : skip + limit]


@router.post("/templates", response_model=TemplateResponse)
async def create_template(template: TemplateCreate):
    """Create a new content template."""
    try:
        # Create new template (simplified)
        new_template = TemplateResponse(
            id=str(uuid4()),
            name=template.name,
            description=template.description,
            category=template.category,
        )

        logger.info(f"Created template: {new_template.id}")
        return new_template

    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID."""
    # Find template in defaults
    for template in DEFAULT_TEMPLATES:
        if template["id"] == template_id:
            return template

    raise HTTPException(status_code=404, detail="Template not found")