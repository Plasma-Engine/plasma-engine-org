"""SEO optimization utilities for blog posts"""

import re
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from collections import Counter
import json
from app.models import BlogPost, SEOMetadata

class SEOOptimizer:
    """SEO optimization for blog content"""

    def __init__(self):
        """Initialize SEO optimizer with configuration"""
        self.min_keyword_density = 0.5  # Minimum %
        self.max_keyword_density = 2.5  # Maximum %
        self.optimal_title_length = 60
        self.optimal_meta_desc_length = 160
        self.min_content_length = 300
        self.readability_targets = {
            "sentences_per_paragraph": 3,
            "words_per_sentence": 20,
            "syllables_per_word": 2
        }

    async def optimize(
        self,
        content: BlogPost,
        keywords: List[str],
        topic: str
    ) -> BlogPost:
        """Optimize blog post content for SEO"""

        # Optimize title
        content.title = self._optimize_title(content.title, keywords, topic)

        # Optimize introduction
        content.introduction = self._optimize_paragraph(
            content.introduction,
            keywords,
            is_introduction=True
        )

        # Optimize each section
        for section in content.sections:
            section.content = self._optimize_paragraph(section.content, keywords)
            section.heading = self._optimize_heading(section.heading, keywords)

        # Optimize conclusion
        content.conclusion = self._optimize_paragraph(
            content.conclusion,
            keywords,
            is_conclusion=True
        )

        # Update SEO metadata
        content.seo_metadata = self._enhance_seo_metadata(
            content.seo_metadata,
            content,
            keywords
        )

        # Add internal linking suggestions
        content.related_topics = self._generate_related_topics(topic, content)

        # Add structured data
        content.seo_metadata.structured_data = self._generate_structured_data(content)

        return content

    def _optimize_title(self, title: str, keywords: List[str], topic: str) -> str:
        """Optimize title for SEO"""
        # Include primary keyword if not present
        if keywords and not any(kw.lower() in title.lower() for kw in keywords[:1]):
            primary_keyword = keywords[0]
            # Try to naturally include the keyword
            if len(title) + len(primary_keyword) + 3 <= self.optimal_title_length:
                title = f"{title}: {primary_keyword.title()}"

        # Ensure title length is optimal
        if len(title) > self.optimal_title_length:
            title = title[:self.optimal_title_length-3] + "..."

        # Add power words if space allows
        power_words = ["Ultimate", "Complete", "Essential", "Comprehensive", "Expert"]
        if len(title) < 40 and not any(word in title for word in power_words):
            title = f"{power_words[0]} {title}"

        return title

    def _optimize_heading(self, heading: str, keywords: List[str]) -> str:
        """Optimize section headings for SEO"""
        # Try to include keywords naturally in headings
        for keyword in keywords:
            if len(heading) < 50 and keyword.lower() not in heading.lower():
                # Check if we can naturally add the keyword
                if "guide" in heading.lower() and "guide" not in keyword.lower():
                    heading = heading.replace("Guide", f"{keyword.title()} Guide")
                    break
        return heading

    def _optimize_paragraph(
        self,
        paragraph: str,
        keywords: List[str],
        is_introduction: bool = False,
        is_conclusion: bool = False
    ) -> str:
        """Optimize paragraph for keyword usage and readability"""

        if not paragraph:
            return paragraph

        # Calculate current keyword density
        words = paragraph.lower().split()
        word_count = len(words)

        if word_count < 20:  # Don't optimize very short paragraphs
            return paragraph

        # Check keyword density for each keyword
        for keyword in keywords:
            keyword_lower = keyword.lower()
            current_count = paragraph.lower().count(keyword_lower)
            current_density = (current_count / word_count) * 100 if word_count > 0 else 0

            # Add keywords if density is too low
            if current_density < self.min_keyword_density:
                if is_introduction and current_count == 0:
                    # Add keyword to introduction if missing
                    sentences = paragraph.split(". ")
                    if len(sentences) > 1:
                        # Add to second sentence
                        sentences[1] = f"{sentences[1]} This involves {keyword}"
                        paragraph = ". ".join(sentences)

                elif is_conclusion and current_count == 0:
                    # Add keyword to conclusion if missing
                    paragraph = f"{paragraph} Remember these key points about {keyword}."

        # Optimize sentence structure for readability
        paragraph = self._improve_readability(paragraph)

        # Add semantic variations
        paragraph = self._add_semantic_keywords(paragraph, keywords)

        return paragraph

    def _improve_readability(self, text: str) -> str:
        """Improve text readability"""
        sentences = text.split(". ")
        improved_sentences = []

        for sentence in sentences:
            words = sentence.split()
            # Break very long sentences
            if len(words) > 30:
                # Find a good breaking point (comma, and, or)
                mid_point = len(words) // 2
                for i, word in enumerate(words[mid_point-5:mid_point+5], start=mid_point-5):
                    if word in [",", "and", "or", "but", "while"]:
                        # Split here
                        first_part = " ".join(words[:i])
                        second_part = " ".join(words[i:])
                        improved_sentences.append(first_part)
                        improved_sentences.append(second_part.capitalize())
                        break
                else:
                    improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)

        return ". ".join(improved_sentences)

    def _add_semantic_keywords(self, text: str, keywords: List[str]) -> str:
        """Add semantic variations of keywords"""
        semantic_map = {
            "AI": ["artificial intelligence", "machine learning", "ML", "deep learning"],
            "SEO": ["search engine optimization", "search optimization", "Google ranking"],
            "blog": ["article", "post", "content", "piece"],
            "guide": ["tutorial", "how-to", "walkthrough", "instructions"],
            "tool": ["software", "application", "platform", "solution"],
            "strategy": ["approach", "method", "technique", "plan"],
            "best": ["top", "leading", "optimal", "recommended"],
            "improve": ["enhance", "boost", "optimize", "strengthen"],
            "create": ["build", "develop", "design", "generate"],
            "data": ["information", "insights", "metrics", "analytics"]
        }

        # Add semantic variations where appropriate
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for base_word, variations in semantic_map.items():
                if base_word in keyword_lower:
                    # Check if we can add a variation
                    for variation in variations:
                        if variation not in text.lower():
                            # Add variation naturally
                            sentences = text.split(". ")
                            if len(sentences) > 2:
                                # Add to middle sentence
                                mid_idx = len(sentences) // 2
                                sentences[mid_idx] += f" (also known as {variation})"
                                text = ". ".join(sentences)
                                break
                    break

        return text

    def _enhance_seo_metadata(
        self,
        metadata: SEOMetadata,
        content: BlogPost,
        keywords: List[str]
    ) -> SEOMetadata:
        """Enhance SEO metadata"""

        # Optimize meta title
        if not any(kw.lower() in metadata.meta_title.lower() for kw in keywords[:1]):
            if keywords and len(metadata.meta_title) + len(keywords[0]) + 3 <= self.optimal_title_length:
                metadata.meta_title = f"{metadata.meta_title} | {keywords[0].title()}"

        # Optimize meta description
        if not any(kw.lower() in metadata.meta_description.lower() for kw in keywords[:2]):
            if keywords:
                metadata.meta_description = f"Learn about {keywords[0]}. {metadata.meta_description}"
                if len(metadata.meta_description) > self.optimal_meta_desc_length:
                    metadata.meta_description = metadata.meta_description[:self.optimal_meta_desc_length-3] + "..."

        # Calculate readability score
        metadata.readability_score = self._calculate_readability_score(content)

        # Ensure all keywords are included
        metadata.keywords = list(set(metadata.keywords + keywords))

        return metadata

    def _calculate_readability_score(self, content: BlogPost) -> float:
        """Calculate readability score (simplified Flesch Reading Ease)"""
        # Combine all text
        full_text = (
            content.introduction +
            " ".join([s.content for s in content.sections]) +
            content.conclusion
        )

        sentences = full_text.split(".")
        words = full_text.split()

        if not sentences or not words:
            return 0.0

        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = 1.5  # Simplified estimate

        # Flesch Reading Ease formula (simplified)
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

        # Normalize to 0-100 scale
        return max(0, min(100, score))

    def _generate_related_topics(self, topic: str, content: BlogPost) -> List[str]:
        """Generate related topics for internal linking"""
        related = []

        # Extract key concepts from content
        all_text = (
            content.introduction +
            " ".join([s.content for s in content.sections]) +
            content.conclusion
        )

        # Simple keyword extraction (in production, use NLP)
        words = re.findall(r'\b[A-Za-z]{4,}\b', all_text.lower())
        word_freq = Counter(words)

        # Get top concepts (excluding common words)
        common_words = {"that", "this", "with", "from", "your", "have", "will", "more", "when", "which"}
        top_concepts = [
            word for word, count in word_freq.most_common(20)
            if word not in common_words and count > 2
        ]

        # Generate related topic suggestions
        topic_templates = [
            f"Advanced {concept} techniques",
            f"How to master {concept}",
            f"{concept} best practices",
            f"Common {concept} mistakes",
            f"{concept} vs alternatives"
        ]

        for concept in top_concepts[:3]:
            related.append(topic_templates[0].format(concept=concept))

        return related[:5]  # Return top 5 related topics

    def _generate_structured_data(self, content: BlogPost) -> Dict[str, Any]:
        """Generate structured data for rich snippets"""
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": content.title,
            "description": content.seo_metadata.meta_description,
            "author": {
                "@type": "Organization",
                "name": content.author or "AI Content Generator"
            },
            "datePublished": content.created_at.isoformat() if content.created_at else None,
            "keywords": ", ".join(content.seo_metadata.keywords),
            "wordCount": content.word_count,
            "timeRequired": f"PT{content.reading_time}M",
            "articleSection": content.style.value,
            "inLanguage": "en-US"
        }

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for SEO metrics"""
        analysis = {
            "word_count": len(content.split()),
            "sentence_count": len(content.split(".")),
            "paragraph_count": len(content.split("\n\n")),
            "heading_structure": self._analyze_heading_structure(content),
            "keyword_opportunities": self._find_keyword_opportunities(content),
            "readability_issues": self._find_readability_issues(content)
        }

        return analysis

    def _analyze_heading_structure(self, content: str) -> Dict[str, int]:
        """Analyze heading hierarchy in content"""
        # Simple analysis based on markdown-style headings
        structure = {
            "h1": content.count("# "),
            "h2": content.count("## "),
            "h3": content.count("### "),
            "h4": content.count("#### ")
        }
        return structure

    def _find_keyword_opportunities(self, content: str) -> List[str]:
        """Find potential keyword opportunities"""
        # Extract noun phrases that could be keywords
        opportunities = []

        # Simple pattern matching for noun phrases
        patterns = [
            r'\b(?:how to|guide to|tips for|best|top)\s+\w+(?:\s+\w+)?',
            r'\b\w+\s+(?:strategy|technique|method|approach|tool)',
            r'\b(?:improve|boost|enhance|optimize)\s+\w+',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content.lower())
            opportunities.extend(matches)

        return list(set(opportunities))[:10]

    def _find_readability_issues(self, content: str) -> List[str]:
        """Find potential readability issues"""
        issues = []

        sentences = content.split(".")
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 30:
                issues.append(f"Long sentence ({len(words)} words): {sentence[:50]}...")

        # Check for passive voice (simplified)
        passive_indicators = ["was", "were", "been", "being", "be", "is", "are", "am"]
        passive_count = sum(1 for word in content.split() if word.lower() in passive_indicators)
        if passive_count > len(content.split()) * 0.1:  # More than 10%
            issues.append("High passive voice usage detected")

        # Check paragraph length
        paragraphs = content.split("\n\n")
        for i, para in enumerate(paragraphs):
            if len(para.split()) > 150:
                issues.append(f"Long paragraph {i+1} ({len(para.split())} words)")

        return issues