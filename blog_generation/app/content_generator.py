"""Content generation using LangChain with multiple LLM providers"""

import os
from typing import List, Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import BaseOutputParser
import json
import re
from datetime import datetime
from app.models import BlogPost, BlogSection, SEOMetadata, BlogStyle, BlogLength, BlogTone
from app.templates import BlogTemplateManager

class ContentGenerator:
    """Main content generation class using LangChain"""

    def __init__(self):
        """Initialize the content generator with LLM providers"""
        self.template_manager = BlogTemplateManager()

        # Initialize LLM providers
        self._setup_llms()

        # Setup prompts
        self._setup_prompts()

    def _setup_llms(self):
        """Setup different LLM providers with fallback"""
        # Primary: Claude 3.5 Sonnet for high-quality content
        if os.getenv("ANTHROPIC_API_KEY"):
            self.primary_llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.7,
                max_tokens=4000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            self.primary_llm = None

        # Fallback: GPT-4 for content generation
        if os.getenv("OPENAI_API_KEY"):
            self.fallback_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=4000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            # Use a mock LLM for testing without API keys
            self.fallback_llm = self._create_mock_llm()

        # Use available LLM
        self.llm = self.primary_llm or self.fallback_llm

    def _create_mock_llm(self):
        """Create a mock LLM for testing purposes"""
        from langchain.llms.fake import FakeListLLM
        responses = [
            json.dumps({
                "title": "Sample Blog Post",
                "content": "This is a sample blog post generated for testing.",
                "sections": [
                    {"heading": "Introduction", "content": "Sample introduction content."},
                    {"heading": "Main Points", "content": "Sample main content."},
                    {"heading": "Conclusion", "content": "Sample conclusion content."}
                ]
            })
        ]
        return FakeListLLM(responses=responses)

    def _setup_prompts(self):
        """Setup prompt templates for different generation tasks"""

        # Main blog generation prompt
        self.blog_generation_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert content writer specializing in creating high-quality blog posts.
                You excel at writing in various styles and tones, optimizing for SEO, and engaging target audiences.
                Generate content that is informative, well-structured, and engaging."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Generate a comprehensive blog post with the following specifications:
                Topic: {topic}
                Style: {style}
                Tone: {tone}
                Target Length: {length} ({word_count} words approximately)
                Keywords to include: {keywords}
                Target Audience: {target_audience}

                Additional Instructions: {custom_instructions}

                Structure the blog post with:
                1. An engaging title
                2. A compelling introduction
                3. Well-organized sections with clear headings
                4. A strong conclusion
                5. A call-to-action if appropriate

                Format the response as a JSON object with the following structure:
                {{
                    "title": "Blog Title",
                    "subtitle": "Optional subtitle",
                    "introduction": "Introduction paragraph",
                    "sections": [
                        {{"heading": "Section 1", "content": "Section content", "subheadings": []}},
                        {{"heading": "Section 2", "content": "Section content", "subheadings": []}}
                    ],
                    "conclusion": "Conclusion paragraph",
                    "call_to_action": "Optional CTA"
                }}"""
            )
        ])

        # Outline generation prompt
        self.outline_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert content strategist. Create detailed blog post outlines that ensure comprehensive coverage of topics."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Create a detailed outline for a blog post about: {topic}
                Style: {style}

                Include:
                - Main title
                - 4-6 main sections with descriptive headings
                - 2-3 sub-points for each section
                - Estimated word count for each section
                - Key points to cover

                Format as JSON with clear structure."""
            )
        ])

        # Topic research prompt
        self.research_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are a research analyst specializing in content marketing.
                Provide comprehensive research insights for blog topics."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Research the topic: {topic}
                Depth level: {depth}

                Provide:
                1. Key points and facts
                2. Current trends and developments
                3. Related topics to explore
                4. Unique angles for content
                5. Potential data points and statistics
                6. Competitor content analysis (if applicable)

                Format as structured JSON."""
            )
        ])

    async def generate(
        self,
        topic: str,
        style: BlogStyle,
        length: BlogLength,
        keywords: List[str],
        tone: BlogTone,
        target_audience: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> BlogPost:
        """Generate a complete blog post"""

        # Determine word count based on length
        word_counts = {
            BlogLength.SHORT: 400,
            BlogLength.MEDIUM: 1000,
            BlogLength.LONG: 1750,
            BlogLength.COMPREHENSIVE: 2500
        }
        word_count = word_counts[length]

        # Get template if available
        template = self.template_manager.get_template(style)

        # Prepare custom instructions
        if template:
            custom_instructions = f"{template.instructions}\n{custom_instructions or ''}"

        # Generate content using LangChain
        chain = LLMChain(llm=self.llm, prompt=self.blog_generation_prompt)

        result = await chain.arun(
            topic=topic,
            style=style.value,
            tone=tone.value,
            length=length.value,
            word_count=word_count,
            keywords=", ".join(keywords) if keywords else "none specified",
            target_audience=target_audience or "general audience",
            custom_instructions=custom_instructions or "Follow best practices for the selected style."
        )

        # Parse the result
        try:
            content_data = json.loads(result)
        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            content_data = self._parse_text_response(result)

        # Create BlogPost object
        sections = [
            BlogSection(
                heading=section.get("heading", ""),
                content=section.get("content", ""),
                subheadings=section.get("subheadings", []),
                keywords_used=self._extract_used_keywords(section.get("content", ""), keywords)
            )
            for section in content_data.get("sections", [])
        ]

        # Calculate word count and reading time
        total_content = (
            content_data.get("introduction", "") +
            " ".join([s.content for s in sections]) +
            content_data.get("conclusion", "")
        )
        word_count_actual = len(total_content.split())
        reading_time = max(1, word_count_actual // 250)  # Average reading speed

        # Generate SEO metadata
        seo_metadata = self._generate_seo_metadata(
            title=content_data.get("title", topic),
            content=total_content,
            keywords=keywords
        )

        return BlogPost(
            title=content_data.get("title", topic),
            subtitle=content_data.get("subtitle"),
            style=style,
            tone=tone,
            introduction=content_data.get("introduction", ""),
            sections=sections,
            conclusion=content_data.get("conclusion", ""),
            call_to_action=content_data.get("call_to_action"),
            seo_metadata=seo_metadata,
            word_count=word_count_actual,
            reading_time=reading_time,
            created_at=datetime.now()
        )

    async def generate_outline(self, topic: str, style: BlogStyle) -> Dict[str, Any]:
        """Generate a blog post outline"""
        chain = LLMChain(llm=self.llm, prompt=self.outline_prompt)

        result = await chain.arun(
            topic=topic,
            style=style.value
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Failed to parse outline", "raw": result}

    async def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """Research a topic for blog post generation"""
        chain = LLMChain(llm=self.llm, prompt=self.research_prompt)

        result = await chain.arun(
            topic=topic,
            depth=depth
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Failed to parse research", "raw": result}

    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available blog templates"""
        return self.template_manager.list_templates()

    def _extract_used_keywords(self, content: str, keywords: List[str]) -> List[str]:
        """Extract which keywords were used in the content"""
        content_lower = content.lower()
        used = []
        for keyword in keywords:
            if keyword.lower() in content_lower:
                used.append(keyword)
        return used

    def _generate_seo_metadata(self, title: str, content: str, keywords: List[str]) -> SEOMetadata:
        """Generate SEO metadata for the blog post"""
        # Create meta title (max 60 chars)
        meta_title = title[:57] + "..." if len(title) > 60 else title

        # Create meta description (max 160 chars)
        first_sentence = content.split(".")[0] if content else title
        meta_description = first_sentence[:157] + "..." if len(first_sentence) > 160 else first_sentence

        # Generate slug
        slug = re.sub(r'[^a-z0-9-]', '', title.lower().replace(" ", "-"))

        # Calculate keyword density
        content_lower = content.lower()
        word_count = len(content.split())
        keyword_density = {}
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density = (count / word_count * 100) if word_count > 0 else 0
            keyword_density[keyword] = round(density, 2)

        return SEOMetadata(
            meta_title=meta_title,
            meta_description=meta_description,
            slug=slug,
            keywords=keywords,
            keyword_density=keyword_density
        )

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        # Simple parsing logic for text responses
        lines = text.split("\n")
        result = {
            "title": lines[0] if lines else "Untitled",
            "introduction": "",
            "sections": [],
            "conclusion": "",
            "call_to_action": ""
        }

        current_section = None
        for line in lines[1:]:
            if line.startswith("## "):
                if current_section:
                    result["sections"].append(current_section)
                current_section = {
                    "heading": line.replace("## ", ""),
                    "content": "",
                    "subheadings": []
                }
            elif current_section:
                current_section["content"] += line + "\n"
            elif not result["introduction"]:
                result["introduction"] = line

        if current_section:
            result["sections"].append(current_section)

        return result