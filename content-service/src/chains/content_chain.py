"""
LangChain chains for content generation.
"""

from typing import Dict, Any, Optional, List

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseOutputParser

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class ContentOutputParser(BaseOutputParser[Dict[str, Any]]):
    """Parser for structured content output."""

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse the LLM output into structured format."""
        lines = text.strip().split('\n')

        # Extract title if present
        title = None
        if lines and lines[0].startswith('#'):
            title = lines[0].strip('#').strip()
            lines = lines[1:]

        # Join remaining lines as content
        content = '\n'.join(lines).strip()

        return {
            "title": title,
            "content": content,
            "word_count": len(content.split()),
        }


class ContentGenerationChain:
    """Main chain for content generation using LangChain."""

    def __init__(self):
        """Initialize the content generation chain."""
        self.output_parser = ContentOutputParser()

    async def generate(
        self,
        prompt: str,
        content_type: str,
        tone: Optional[str] = None,
        target_audience: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        max_length: int = 1000,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate content using LangChain.

        This is a simplified implementation. Full version includes:
        - LLM client integration (OpenAI, Anthropic)
        - Proper chain execution
        - Token tracking
        - Error handling
        """
        # Build the system prompt
        system_prompt = self._build_system_prompt(
            content_type=content_type,
            tone=tone,
            target_audience=target_audience,
            keywords=keywords,
            max_length=max_length,
        )

        logger.info(f"Generating content with model: {model or settings.DEFAULT_MODEL}")

        # Simplified response for initial setup
        # Full implementation would call LLM here
        output = {
            "title": f"Generated {content_type}",
            "content": f"This is placeholder content for: {prompt}",
            "word_count": 10,
            "content_type": content_type,
            "tone": tone,
            "target_audience": target_audience,
            "keywords": keywords,
            "model_used": model or settings.DEFAULT_MODEL,
        }

        return output

    def _build_system_prompt(
        self,
        content_type: str,
        tone: Optional[str] = None,
        target_audience: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        max_length: int = 1000,
    ) -> str:
        """Build the system prompt based on parameters."""
        prompt_parts = [
            f"You are an expert content creator specializing in {content_type}.",
            f"Generate high-quality content that is engaging and well-structured.",
        ]

        if tone:
            prompt_parts.append(f"The tone should be {tone}.")

        if target_audience:
            prompt_parts.append(f"The target audience is: {target_audience}.")

        if keywords:
            keywords_str = ", ".join(keywords)
            prompt_parts.append(f"Include these keywords naturally: {keywords_str}.")

        prompt_parts.append(f"The content should be approximately {max_length} words.")
        prompt_parts.append("Format the output with a clear title (starting with #) followed by the content.")

        return " ".join(prompt_parts)