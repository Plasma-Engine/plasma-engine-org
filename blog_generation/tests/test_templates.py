"""Tests for blog post templates"""

import pytest
from app.templates import BlogTemplateManager, BlogTemplate
from app.models import BlogStyle

@pytest.fixture
def template_manager():
    """Create template manager instance"""
    return BlogTemplateManager()

def test_template_manager_initialization(template_manager):
    """Test template manager is properly initialized"""
    assert template_manager is not None
    assert template_manager.templates is not None
    assert len(template_manager.templates) > 0

def test_get_template(template_manager):
    """Test retrieving a specific template"""
    template = template_manager.get_template(BlogStyle.INFORMATIVE)

    assert template is not None
    assert isinstance(template, BlogTemplate)
    assert template.style == BlogStyle.INFORMATIVE
    assert template.name == "Informative Blog Post"
    assert len(template.structure) > 0
    assert template.instructions is not None

def test_get_all_blog_styles(template_manager):
    """Test that all blog styles have templates"""
    for style in BlogStyle:
        template = template_manager.get_template(style)
        assert template is not None, f"Missing template for {style}"
        assert template.style == style
        assert template.name is not None
        assert template.structure is not None
        assert len(template.structure) > 0

def test_list_templates(template_manager):
    """Test listing all available templates"""
    templates = template_manager.list_templates()

    assert isinstance(templates, list)
    assert len(templates) == len(BlogStyle)

    for template_info in templates:
        assert "style" in template_info
        assert "name" in template_info
        assert "recommended_length" in template_info
        assert "example_topics" in template_info

def test_get_template_structure(template_manager):
    """Test getting template structure"""
    structure = template_manager.get_template_structure(BlogStyle.HOWTO)

    assert isinstance(structure, list)
    assert len(structure) > 0

    for section in structure:
        assert "section" in section
        assert "purpose" in section

def test_get_seo_tips(template_manager):
    """Test getting SEO tips for a style"""
    tips = template_manager.get_seo_tips(BlogStyle.LISTICLE)

    assert isinstance(tips, list)
    assert len(tips) > 0
    for tip in tips:
        assert isinstance(tip, str)

def test_template_completeness(template_manager):
    """Test that all templates have complete information"""
    for style in BlogStyle:
        template = template_manager.get_template(style)

        # Check all required fields
        assert template.name is not None and len(template.name) > 0
        assert template.style == style
        assert len(template.structure) >= 3  # At least intro, body, conclusion
        assert template.instructions is not None and len(template.instructions) > 10
        assert len(template.example_topics) >= 2
        assert template.recommended_length is not None
        assert len(template.seo_tips) >= 2

def test_template_structure_validity(template_manager):
    """Test that template structures are valid"""
    for style in BlogStyle:
        template = template_manager.get_template(style)

        # Check structure has introduction and conclusion
        sections = [s["section"].lower() for s in template.structure]
        assert any("intro" in s or "hook" in s or "lead" in s for s in sections), \
            f"{style} missing introduction section"
        assert any("conclu" in s or "wrap" in s or "takeaway" in s for s in sections), \
            f"{style} missing conclusion section"

def test_howto_template_specifics(template_manager):
    """Test How-To template has specific required sections"""
    template = template_manager.get_template(BlogStyle.HOWTO)

    sections = [s["section"].lower() for s in template.structure]

    # How-To should have step-by-step instructions
    assert any("step" in s or "instruction" in s for s in sections)
    # Should have prerequisites or materials
    assert any("prerequisite" in s or "material" in s for s in sections)

def test_case_study_template_specifics(template_manager):
    """Test Case Study template has specific required sections"""
    template = template_manager.get_template(BlogStyle.CASE_STUDY)

    sections = [s["section"].lower() for s in template.structure]

    # Case study should have these essential sections
    assert any("challenge" in s or "problem" in s for s in sections)
    assert any("solution" in s for s in sections)
    assert any("result" in s or "outcome" in s for s in sections)

def test_comparison_template_specifics(template_manager):
    """Test Comparison template has specific required sections"""
    template = template_manager.get_template(BlogStyle.COMPARISON)

    sections = [s["section"].lower() for s in template.structure]

    # Comparison should have analysis of options
    assert any("option" in s or "analysis" in s for s in sections)
    assert any("comparison" in s or "versus" in s or "side-by-side" in s for s in sections)
    assert any("verdict" in s or "recommendation" in s for s in sections)

def test_technical_template_specifics(template_manager):
    """Test Technical template has specific required sections"""
    template = template_manager.get_template(BlogStyle.TECHNICAL)

    sections = [s["section"].lower() for s in template.structure]

    # Technical posts should have these sections
    assert any("prerequisite" in s or "requirement" in s for s in sections)
    assert any("implementation" in s or "code" in s for s in sections)
    assert any("test" in s or "validation" in s for s in sections)

def test_seo_tips_relevance(template_manager):
    """Test that SEO tips are relevant to the style"""
    # Test listicle SEO tips
    listicle_tips = template_manager.get_seo_tips(BlogStyle.LISTICLE)
    assert any("number" in tip.lower() for tip in listicle_tips), \
        "Listicle should have tips about using numbers"

    # Test how-to SEO tips
    howto_tips = template_manager.get_seo_tips(BlogStyle.HOWTO)
    assert any("how to" in tip.lower() for tip in howto_tips), \
        "How-to should have tips about 'how to' in title"

    # Test case study SEO tips
    case_study_tips = template_manager.get_seo_tips(BlogStyle.CASE_STUDY)
    assert any("case study" in tip.lower() or "result" in tip.lower() or "metric" in tip.lower()
              for tip in case_study_tips), \
        "Case study should have tips about including results/metrics"