"""
Brand Mention Extraction and Processing
Identifies and processes brand references in social media data
"""

import re
import logging
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import spacy
from fuzzywuzzy import fuzz
import unicodedata


logger = logging.getLogger(__name__)


@dataclass
class BrandMention:
    brand: str
    text: str
    position: int
    context: str
    confidence: float
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrandProfile:
    name: str
    aliases: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    handles: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    min_confidence: float = 0.7


class BrandProcessor:
    """
    Extract and process brand mentions from text data
    Handles variations, misspellings, and contextual references
    """

    def __init__(
        self,
        brands: List[BrandProfile] = None,
        fuzzy_matching: bool = True,
        min_confidence: float = 0.7
    ):
        self.brands = brands or []
        self.fuzzy_matching = fuzzy_matching
        self.min_confidence = min_confidence

        # Build lookup structures
        self._build_brand_index()

        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Named entity recognition will be limited.")
            self.nlp = None

        logger.info(f"BrandProcessor initialized with {len(self.brands)} brands")

    def _build_brand_index(self):
        """Build efficient lookup structures for brand matching"""
        self.brand_names = {}
        self.brand_patterns = defaultdict(set)
        self.hashtag_map = {}
        self.handle_map = {}

        for brand in self.brands:
            # Add main brand name
            brand_lower = brand.name.lower()
            self.brand_names[brand_lower] = brand

            # Add aliases
            for alias in brand.aliases:
                alias_lower = alias.lower()
                self.brand_names[alias_lower] = brand

            # Add hashtags
            for hashtag in brand.hashtags:
                hashtag_lower = hashtag.lower()
                if not hashtag_lower.startswith('#'):
                    hashtag_lower = '#' + hashtag_lower
                self.hashtag_map[hashtag_lower] = brand

            # Add handles
            for handle in brand.handles:
                handle_lower = handle.lower()
                if not handle_lower.startswith('@'):
                    handle_lower = '@' + handle_lower
                self.handle_map[handle_lower] = brand

            # Build regex patterns for each brand
            patterns = [re.escape(brand.name)]
            patterns.extend(re.escape(alias) for alias in brand.aliases)
            self.brand_patterns[brand.name] = re.compile(
                r'\b(' + '|'.join(patterns) + r')\b',
                re.IGNORECASE
            )

    def add_brand(self, brand_profile: BrandProfile):
        """Add a new brand profile to the processor"""
        self.brands.append(brand_profile)
        self._build_brand_index()
        logger.info(f"Added brand profile: {brand_profile.name}")

    def extract_mentions(
        self,
        text: str,
        source: str = "",
        extract_context: bool = True,
        context_window: int = 50
    ) -> List[BrandMention]:
        """
        Extract all brand mentions from text

        Args:
            text: Text to analyze
            source: Source of the text (e.g., 'twitter', 'reddit')
            extract_context: Whether to extract surrounding context
            context_window: Number of characters for context window

        Returns:
            List of BrandMention objects
        """
        mentions = []

        # Clean and normalize text
        normalized_text = self._normalize_text(text)

        # Direct matching
        mentions.extend(self._extract_direct_mentions(text, normalized_text, source))

        # Hashtag matching
        mentions.extend(self._extract_hashtag_mentions(text, source))

        # Handle matching
        mentions.extend(self._extract_handle_mentions(text, source))

        # Fuzzy matching if enabled
        if self.fuzzy_matching:
            mentions.extend(self._extract_fuzzy_mentions(text, normalized_text, source))

        # Named entity recognition if available
        if self.nlp:
            mentions.extend(self._extract_ner_mentions(text, source))

        # Extract context for each mention
        if extract_context:
            for mention in mentions:
                mention.context = self._extract_context(
                    text,
                    mention.position,
                    context_window
                )

        # Deduplicate mentions
        mentions = self._deduplicate_mentions(mentions)

        return mentions

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Remove accents
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return text

    def _extract_direct_mentions(
        self,
        original_text: str,
        normalized_text: str,
        source: str
    ) -> List[BrandMention]:
        """Extract direct brand name matches"""
        mentions = []

        for brand_name, pattern in self.brand_patterns.items():
            for match in pattern.finditer(normalized_text):
                brand = self.brand_names.get(brand_name.lower())
                if brand:
                    mentions.append(BrandMention(
                        brand=brand.name,
                        text=match.group(),
                        position=match.start(),
                        context="",
                        confidence=1.0,
                        source=source,
                        metadata={'match_type': 'direct'}
                    ))

        return mentions

    def _extract_hashtag_mentions(self, text: str, source: str) -> List[BrandMention]:
        """Extract brand mentions from hashtags"""
        mentions = []
        hashtag_pattern = re.compile(r'#\w+')

        for match in hashtag_pattern.finditer(text):
            hashtag = match.group().lower()
            if hashtag in self.hashtag_map:
                brand = self.hashtag_map[hashtag]
                mentions.append(BrandMention(
                    brand=brand.name,
                    text=match.group(),
                    position=match.start(),
                    context="",
                    confidence=0.95,
                    source=source,
                    metadata={'match_type': 'hashtag', 'hashtag': hashtag}
                ))

        return mentions

    def _extract_handle_mentions(self, text: str, source: str) -> List[BrandMention]:
        """Extract brand mentions from social media handles"""
        mentions = []
        handle_pattern = re.compile(r'@\w+')

        for match in handle_pattern.finditer(text):
            handle = match.group().lower()
            if handle in self.handle_map:
                brand = self.handle_map[handle]
                mentions.append(BrandMention(
                    brand=brand.name,
                    text=match.group(),
                    position=match.start(),
                    context="",
                    confidence=1.0,
                    source=source,
                    metadata={'match_type': 'handle', 'handle': handle}
                ))

        return mentions

    def _extract_fuzzy_mentions(
        self,
        original_text: str,
        normalized_text: str,
        source: str
    ) -> List[BrandMention]:
        """Extract fuzzy matches for brand names (handles misspellings)"""
        mentions = []

        # Split text into words
        words = re.findall(r'\b\w+\b', normalized_text.lower())

        for word in words:
            if len(word) < 3:  # Skip short words
                continue

            for brand_name, brand in self.brand_names.items():
                # Calculate similarity
                similarity = fuzz.ratio(word, brand_name) / 100.0

                if similarity >= self.min_confidence and similarity < 1.0:
                    # Find position in original text
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    match = pattern.search(original_text)

                    if match:
                        mentions.append(BrandMention(
                            brand=brand.name,
                            text=match.group(),
                            position=match.start(),
                            context="",
                            confidence=similarity,
                            source=source,
                            metadata={
                                'match_type': 'fuzzy',
                                'similarity': similarity,
                                'original': brand_name
                            }
                        ))

        return mentions

    def _extract_ner_mentions(self, text: str, source: str) -> List[BrandMention]:
        """Extract brand mentions using Named Entity Recognition"""
        if not self.nlp:
            return []

        mentions = []
        doc = self.nlp(text)

        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                # Check if this entity matches any brand
                ent_lower = ent.text.lower()

                for brand_name, brand in self.brand_names.items():
                    similarity = fuzz.ratio(ent_lower, brand_name) / 100.0

                    if similarity >= self.min_confidence:
                        mentions.append(BrandMention(
                            brand=brand.name,
                            text=ent.text,
                            position=ent.start_char,
                            context="",
                            confidence=similarity * 0.9,  # Slightly lower confidence for NER
                            source=source,
                            metadata={
                                'match_type': 'ner',
                                'entity_type': ent.label_,
                                'similarity': similarity
                            }
                        ))
                        break

        return mentions

    def _extract_context(self, text: str, position: int, window: int) -> str:
        """Extract surrounding context for a mention"""
        start = max(0, position - window)
        end = min(len(text), position + window)
        context = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'

        return context

    def _deduplicate_mentions(self, mentions: List[BrandMention]) -> List[BrandMention]:
        """Remove duplicate mentions, keeping highest confidence"""
        unique = {}

        for mention in mentions:
            key = (mention.brand, mention.position)
            if key not in unique or mention.confidence > unique[key].confidence:
                unique[key] = mention

        return list(unique.values())

    def analyze_brand_presence(
        self,
        texts: List[str],
        source: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze brand presence across multiple texts

        Args:
            texts: List of texts to analyze
            source: Source of the texts

        Returns:
            Dictionary with brand presence statistics
        """
        all_mentions = []
        for text in texts:
            mentions = self.extract_mentions(text, source)
            all_mentions.extend(mentions)

        # Calculate statistics
        brand_counts = defaultdict(int)
        brand_confidences = defaultdict(list)
        brand_sources = defaultdict(set)

        for mention in all_mentions:
            brand_counts[mention.brand] += 1
            brand_confidences[mention.brand].append(mention.confidence)
            if mention.source:
                brand_sources[mention.brand].add(mention.source)

        # Build analysis results
        analysis = {
            'total_mentions': len(all_mentions),
            'unique_brands': len(brand_counts),
            'brands': {}
        }

        for brand, count in brand_counts.items():
            confidences = brand_confidences[brand]
            analysis['brands'][brand] = {
                'count': count,
                'frequency': count / len(texts) if texts else 0,
                'avg_confidence': sum(confidences) / len(confidences),
                'min_confidence': min(confidences),
                'max_confidence': max(confidences),
                'sources': list(brand_sources[brand])
            }

        return analysis

    def get_brand_competitors(self, brand_name: str) -> List[str]:
        """Get competitors for a specific brand"""
        brand_lower = brand_name.lower()
        if brand_lower in self.brand_names:
            brand = self.brand_names[brand_lower]
            return brand.competitors
        return []

    def compare_brand_mentions(
        self,
        texts: List[str],
        brand_name: str,
        include_competitors: bool = True
    ) -> Dict[str, Any]:
        """
        Compare mentions of a brand with its competitors

        Args:
            texts: List of texts to analyze
            brand_name: Target brand name
            include_competitors: Whether to include competitor analysis

        Returns:
            Comparison analysis dictionary
        """
        target_brand = self.brand_names.get(brand_name.lower())
        if not target_brand:
            return {'error': f'Brand {brand_name} not found'}

        # Extract all mentions
        all_mentions = []
        for text in texts:
            mentions = self.extract_mentions(text)
            all_mentions.extend(mentions)

        # Count mentions
        brand_mentions = [m for m in all_mentions if m.brand == target_brand.name]
        competitor_mentions = defaultdict(list)

        if include_competitors:
            for competitor in target_brand.competitors:
                competitor_mentions[competitor] = [
                    m for m in all_mentions if m.brand == competitor
                ]

        # Build comparison
        comparison = {
            'target_brand': target_brand.name,
            'target_mentions': len(brand_mentions),
            'target_share': len(brand_mentions) / len(all_mentions) if all_mentions else 0,
            'competitors': {}
        }

        for competitor, mentions in competitor_mentions.items():
            comparison['competitors'][competitor] = {
                'mentions': len(mentions),
                'share': len(mentions) / len(all_mentions) if all_mentions else 0,
                'relative_to_target': len(mentions) / len(brand_mentions) if brand_mentions else 0
            }

        return comparison