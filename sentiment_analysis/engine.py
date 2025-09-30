"""
Multi-model Sentiment Analysis Engine
Supports VADER, TextBlob, and Transformer models (RoBERTa, XLM-RoBERTa)
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy


logger = logging.getLogger(__name__)


class SentimentModel(Enum):
    VADER = "vader"
    TEXTBLOB = "textblob"
    ROBERTA = "roberta"
    XLM_ROBERTA = "xlm-roberta"
    ENSEMBLE = "ensemble"


@dataclass
class SentimentResult:
    text: str
    model: str
    compound_score: float
    positive: float
    negative: float
    neutral: float
    label: str
    confidence: float
    emotions: Dict[str, float] = None
    aspects: List[Dict[str, Any]] = None
    language: str = "en"


class SentimentEngine:
    """
    Multi-model sentiment analysis engine with support for:
    - VADER: Rule-based sentiment analysis
    - TextBlob: Pattern-based sentiment analysis
    - RoBERTa: Deep learning sentiment analysis
    - XLM-RoBERTa: Multilingual sentiment analysis
    """

    def __init__(
        self,
        models: List[SentimentModel] = None,
        device: str = None,
        batch_size: int = 32,
        max_workers: int = 4
    ):
        self.models = models or [SentimentModel.VADER, SentimentModel.TEXTBLOB, SentimentModel.ROBERTA]
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.max_workers = max_workers

        logger.info(f"Initializing SentimentEngine with models: {self.models}")
        logger.info(f"Using device: {self.device}")

        self._initialize_models()

    def _initialize_models(self):
        """Initialize all requested models"""
        self.analyzers = {}

        # Initialize VADER
        if SentimentModel.VADER in self.models:
            self.analyzers['vader'] = SentimentIntensityAnalyzer()
            logger.info("VADER analyzer initialized")

        # Initialize TextBlob (no specific initialization needed)
        if SentimentModel.TEXTBLOB in self.models:
            self.analyzers['textblob'] = True
            logger.info("TextBlob analyzer initialized")

        # Initialize RoBERTa
        if SentimentModel.ROBERTA in self.models:
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.analyzers['roberta'] = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("RoBERTa model initialized")

        # Initialize XLM-RoBERTa for multilingual support
        if SentimentModel.XLM_ROBERTA in self.models:
            model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
            self.analyzers['xlm-roberta'] = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("XLM-RoBERTa multilingual model initialized")

        # Initialize spaCy for aspect extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Aspect extraction will be limited.")
            self.nlp = None

    def analyze(
        self,
        text: str,
        models: List[SentimentModel] = None,
        extract_aspects: bool = False,
        detect_emotions: bool = False
    ) -> SentimentResult:
        """
        Analyze sentiment of a single text using specified models

        Args:
            text: Text to analyze
            models: Specific models to use (defaults to all initialized)
            extract_aspects: Whether to extract aspect-based sentiment
            detect_emotions: Whether to detect emotions beyond sentiment

        Returns:
            SentimentResult with comprehensive sentiment analysis
        """
        models = models or self.models
        results = []

        # Run each model
        if SentimentModel.VADER in models and 'vader' in self.analyzers:
            results.append(self._analyze_vader(text))

        if SentimentModel.TEXTBLOB in models and 'textblob' in self.analyzers:
            results.append(self._analyze_textblob(text))

        if SentimentModel.ROBERTA in models and 'roberta' in self.analyzers:
            results.append(self._analyze_roberta(text))

        if SentimentModel.XLM_ROBERTA in models and 'xlm-roberta' in self.analyzers:
            results.append(self._analyze_xlm_roberta(text))

        # Combine results if multiple models
        if len(results) > 1:
            final_result = self._ensemble_results(results)
        else:
            final_result = results[0] if results else None

        # Add aspect-based sentiment if requested
        if extract_aspects and self.nlp and final_result:
            final_result.aspects = self._extract_aspects(text)

        # Add emotion detection if requested
        if detect_emotions and final_result:
            final_result.emotions = self._detect_emotions(text)

        return final_result

    def analyze_batch(
        self,
        texts: List[str],
        models: List[SentimentModel] = None,
        parallel: bool = True
    ) -> List[SentimentResult]:
        """
        Analyze sentiment for a batch of texts

        Args:
            texts: List of texts to analyze
            models: Models to use
            parallel: Whether to process in parallel

        Returns:
            List of SentimentResults
        """
        if not parallel:
            return [self.analyze(text, models) for text in texts]

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.analyze, text, models): i
                for i, text in enumerate(texts)
            }

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append((idx, result))
                except Exception as e:
                    logger.error(f"Error analyzing text at index {idx}: {e}")
                    results.append((idx, None))

        # Sort results by original order
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    def _analyze_vader(self, text: str) -> SentimentResult:
        """Analyze using VADER sentiment analyzer"""
        scores = self.analyzers['vader'].polarity_scores(text)

        # Determine label based on compound score
        if scores['compound'] >= 0.05:
            label = 'POSITIVE'
        elif scores['compound'] <= -0.05:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'

        return SentimentResult(
            text=text,
            model='vader',
            compound_score=scores['compound'],
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu'],
            label=label,
            confidence=abs(scores['compound'])
        )

    def _analyze_textblob(self, text: str) -> SentimentResult:
        """Analyze using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Convert to similar format as VADER
        if polarity > 0.1:
            label = 'POSITIVE'
            positive = polarity
            negative = 0.0
        elif polarity < -0.1:
            label = 'NEGATIVE'
            positive = 0.0
            negative = abs(polarity)
        else:
            label = 'NEUTRAL'
            positive = 0.0
            negative = 0.0

        neutral = 1.0 - abs(polarity)

        return SentimentResult(
            text=text,
            model='textblob',
            compound_score=polarity,
            positive=positive,
            negative=negative,
            neutral=neutral,
            label=label,
            confidence=1.0 - subjectivity  # Higher subjectivity = lower confidence
        )

    def _analyze_roberta(self, text: str) -> SentimentResult:
        """Analyze using RoBERTa transformer model"""
        results = self.analyzers['roberta'](text)

        # Parse transformer output
        scores = {r['label']: r['score'] for r in results}

        # Map to standard format
        label_map = {
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL',
            'LABEL_2': 'POSITIVE',
            'negative': 'NEGATIVE',
            'neutral': 'NEUTRAL',
            'positive': 'POSITIVE'
        }

        # Find the highest scoring label
        max_label = max(scores, key=scores.get)
        mapped_label = label_map.get(max_label, max_label.upper())

        # Calculate compound score
        positive = scores.get('LABEL_2', scores.get('positive', 0.0))
        negative = scores.get('LABEL_0', scores.get('negative', 0.0))
        neutral = scores.get('LABEL_1', scores.get('neutral', 0.0))

        compound_score = positive - negative

        return SentimentResult(
            text=text,
            model='roberta',
            compound_score=compound_score,
            positive=positive,
            negative=negative,
            neutral=neutral,
            label=mapped_label,
            confidence=scores[max_label]
        )

    def _analyze_xlm_roberta(self, text: str) -> SentimentResult:
        """Analyze using XLM-RoBERTa multilingual model"""
        results = self.analyzers['xlm-roberta'](text)

        # Parse transformer output
        scores = {r['label']: r['score'] for r in results}

        # Map to standard format
        label_map = {
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL',
            'LABEL_2': 'POSITIVE',
            'negative': 'NEGATIVE',
            'neutral': 'NEUTRAL',
            'positive': 'POSITIVE'
        }

        # Find the highest scoring label
        max_label = max(scores, key=scores.get)
        mapped_label = label_map.get(max_label, max_label.upper())

        # Calculate compound score
        positive = scores.get('LABEL_2', scores.get('positive', 0.0))
        negative = scores.get('LABEL_0', scores.get('negative', 0.0))
        neutral = scores.get('LABEL_1', scores.get('neutral', 0.0))

        compound_score = positive - negative

        return SentimentResult(
            text=text,
            model='xlm-roberta',
            compound_score=compound_score,
            positive=positive,
            negative=negative,
            neutral=neutral,
            label=mapped_label,
            confidence=scores[max_label],
            language='multilingual'
        )

    def _ensemble_results(self, results: List[SentimentResult]) -> SentimentResult:
        """Combine multiple model results using ensemble method"""
        if not results:
            return None

        # Weighted average based on model confidence
        total_weight = sum(r.confidence for r in results)

        compound_score = sum(r.compound_score * r.confidence for r in results) / total_weight
        positive = sum(r.positive * r.confidence for r in results) / total_weight
        negative = sum(r.negative * r.confidence for r in results) / total_weight
        neutral = sum(r.neutral * r.confidence for r in results) / total_weight

        # Determine overall label
        if compound_score >= 0.05:
            label = 'POSITIVE'
        elif compound_score <= -0.05:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'

        # Average confidence
        confidence = sum(r.confidence for r in results) / len(results)

        return SentimentResult(
            text=results[0].text,
            model='ensemble',
            compound_score=compound_score,
            positive=positive,
            negative=negative,
            neutral=neutral,
            label=label,
            confidence=confidence
        )

    def _extract_aspects(self, text: str) -> List[Dict[str, Any]]:
        """Extract aspect-based sentiment using spaCy"""
        if not self.nlp:
            return []

        doc = self.nlp(text)
        aspects = []

        # Extract noun phrases as potential aspects
        for chunk in doc.noun_chunks:
            # Find associated adjectives/adverbs for sentiment
            sentiment_words = []
            for token in chunk.root.children:
                if token.pos_ in ['ADJ', 'ADV']:
                    sentiment_words.append(token.text)

            if sentiment_words:
                # Analyze sentiment of the aspect context
                context = chunk.text + " " + " ".join(sentiment_words)
                aspect_sentiment = self._analyze_vader(context) if 'vader' in self.analyzers else None

                aspects.append({
                    'aspect': chunk.text,
                    'sentiment_words': sentiment_words,
                    'sentiment': aspect_sentiment.label if aspect_sentiment else 'NEUTRAL',
                    'score': aspect_sentiment.compound_score if aspect_sentiment else 0.0
                })

        return aspects

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions beyond basic sentiment"""
        emotions = {
            'joy': 0.0,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'surprise': 0.0,
            'disgust': 0.0,
            'trust': 0.0,
            'anticipation': 0.0
        }

        # Emotion keywords (simplified approach)
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'delighted', 'pleased', 'cheerful'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'sorrowful'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'rage'],
            'fear': ['afraid', 'scared', 'fearful', 'terrified', 'anxious', 'worried'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusted', 'repulsed', 'revolted', 'sickened', 'appalled'],
            'trust': ['trust', 'confident', 'reliable', 'faithful', 'dependable'],
            'anticipation': ['anticipate', 'expect', 'await', 'look forward', 'eager']
        }

        text_lower = text.lower()

        # Count emotion keywords
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions[emotion] += 1.0

        # Normalize scores
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}

        return emotions