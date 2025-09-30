"""
Scoring and Classification System
Calculates sentiment scores, emotion metrics, and brand impact
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class ImpactLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class TrendDirection(Enum):
    RISING_FAST = "rising_fast"
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    DECLINING_FAST = "declining_fast"


@dataclass
class BrandImpactScore:
    overall_score: float
    sentiment_score: float
    reach_score: float
    engagement_score: float
    virality_score: float
    impact_level: ImpactLevel
    confidence: float
    factors: Dict[str, Any]


class ScoringSystem:
    """
    Advanced scoring system for sentiment analysis
    Calculates various metrics and impact scores
    """

    def __init__(
        self,
        sentiment_weights: Dict[str, float] = None,
        engagement_weights: Dict[str, float] = None,
        virality_threshold: float = 0.7,
        impact_thresholds: Dict[ImpactLevel, float] = None
    ):
        # Default sentiment weights
        self.sentiment_weights = sentiment_weights or {
            'positive': 1.0,
            'negative': -1.5,  # Negative sentiment weighs more
            'neutral': 0.1
        }

        # Default engagement weights
        self.engagement_weights = engagement_weights or {
            'likes': 1.0,
            'shares': 3.0,  # Shares are more valuable
            'comments': 2.0,
            'views': 0.1
        }

        self.virality_threshold = virality_threshold

        # Default impact thresholds
        self.impact_thresholds = impact_thresholds or {
            ImpactLevel.CRITICAL: 0.9,
            ImpactLevel.HIGH: 0.7,
            ImpactLevel.MEDIUM: 0.5,
            ImpactLevel.LOW: 0.3,
            ImpactLevel.MINIMAL: 0.0
        }

        # Historical data for trend analysis
        self.historical_scores = {}
        self.score_window = timedelta(hours=24)

        logger.info("ScoringSystem initialized")

    def calculate_scores(
        self,
        sentiment: Any,  # SentimentResult from engine.py
        brands: List[Any] = None,  # BrandMentions from brand_processor.py
        engagement: Dict[str, int] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        Calculate comprehensive scores for a post

        Args:
            sentiment: Sentiment analysis result
            brands: Brand mentions found
            engagement: Engagement metrics (likes, shares, etc.)
            metadata: Additional metadata

        Returns:
            Dictionary of calculated scores
        """
        scores = {}

        # Calculate base sentiment score
        scores['sentiment_score'] = self._calculate_sentiment_score(sentiment)

        # Calculate emotion intensity
        if hasattr(sentiment, 'emotions') and sentiment.emotions:
            scores['emotion_intensity'] = self._calculate_emotion_intensity(sentiment.emotions)
            scores.update(self._normalize_emotions(sentiment.emotions))

        # Calculate brand-specific scores
        if brands:
            scores['brand_relevance'] = self._calculate_brand_relevance(brands)
            scores['brand_sentiment'] = self._calculate_brand_sentiment(sentiment, brands)

        # Calculate engagement score
        if engagement:
            scores['engagement_score'] = self._calculate_engagement_score(engagement)
            scores['virality_score'] = self._calculate_virality_score(engagement)

        # Calculate reach score
        scores['reach_score'] = self._calculate_reach_score(engagement, metadata)

        # Calculate overall impact
        scores['overall_impact'] = self._calculate_overall_impact(scores)

        # Normalize scores to 0-1 range
        scores = self._normalize_scores(scores)

        return scores

    def _calculate_sentiment_score(self, sentiment: Any) -> float:
        """Calculate weighted sentiment score"""
        if not sentiment:
            return 0.0

        # Use compound score as base
        base_score = sentiment.compound_score

        # Apply confidence weighting
        weighted_score = base_score * sentiment.confidence

        # Apply sentiment type weights
        if sentiment.label == 'POSITIVE':
            weighted_score *= self.sentiment_weights['positive']
        elif sentiment.label == 'NEGATIVE':
            weighted_score *= self.sentiment_weights['negative']
        else:
            weighted_score *= self.sentiment_weights['neutral']

        return weighted_score

    def _calculate_emotion_intensity(self, emotions: Dict[str, float]) -> float:
        """Calculate overall emotion intensity"""
        if not emotions:
            return 0.0

        # Calculate variance to measure emotional complexity
        values = list(emotions.values())
        if not values:
            return 0.0

        # Higher variance means more complex emotions
        variance = np.var(values)

        # Total emotional activation
        total_activation = sum(values)

        # Combine variance and activation
        intensity = (variance * 0.3 + total_activation * 0.7)

        return min(1.0, intensity)

    def _normalize_emotions(self, emotions: Dict[str, float]) -> Dict[str, float]:
        """Normalize emotion scores"""
        if not emotions:
            return {}

        normalized = {}
        for emotion, score in emotions.items():
            normalized[f'emotion_{emotion}'] = min(1.0, score)

        return normalized

    def _calculate_brand_relevance(self, brands: List[Any]) -> float:
        """Calculate how relevant the brands are to the content"""
        if not brands:
            return 0.0

        # Average confidence of brand mentions
        confidences = [b.confidence for b in brands]
        avg_confidence = sum(confidences) / len(confidences)

        # Number of unique brands mentioned
        unique_brands = len(set(b.brand for b in brands))

        # More brands and higher confidence = higher relevance
        relevance = avg_confidence * (1 + np.log1p(unique_brands) / 10)

        return min(1.0, relevance)

    def _calculate_brand_sentiment(self, sentiment: Any, brands: List[Any]) -> float:
        """Calculate sentiment specifically related to brand mentions"""
        if not brands or not sentiment:
            return 0.0

        # Check if sentiment has aspect-based analysis
        if hasattr(sentiment, 'aspects') and sentiment.aspects:
            brand_aspects = []

            for brand in brands:
                for aspect in sentiment.aspects:
                    # Check if aspect relates to brand
                    if brand.text.lower() in aspect.get('aspect', '').lower():
                        brand_aspects.append(aspect.get('score', 0.0))

            if brand_aspects:
                return np.mean(brand_aspects)

        # Fall back to overall sentiment weighted by brand relevance
        return sentiment.compound_score * self._calculate_brand_relevance(brands)

    def _calculate_engagement_score(self, engagement: Dict[str, int]) -> float:
        """Calculate weighted engagement score"""
        if not engagement:
            return 0.0

        total_weighted = 0.0
        total_weight = 0.0

        for metric, value in engagement.items():
            weight = self.engagement_weights.get(metric, 0.5)
            total_weighted += value * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        # Normalize using logarithmic scale
        raw_score = total_weighted / total_weight
        normalized = np.log1p(raw_score) / 10  # Adjust scale as needed

        return min(1.0, normalized)

    def _calculate_virality_score(self, engagement: Dict[str, int]) -> float:
        """Calculate virality potential"""
        if not engagement:
            return 0.0

        shares = engagement.get('shares', 0) + engagement.get('retweets', 0)
        comments = engagement.get('comments', 0) + engagement.get('replies', 0)
        likes = engagement.get('likes', 0) + engagement.get('favorites', 0)

        # Virality formula: shares matter most
        if shares == 0:
            return 0.0

        # Ratio of shares to other engagement
        share_ratio = shares / max(1, shares + comments + likes)

        # Absolute share count (logarithmic)
        share_score = np.log1p(shares) / 10

        # Comments indicate discussion/controversy
        discussion_score = np.log1p(comments) / 20

        virality = (share_ratio * 0.5 + share_score * 0.3 + discussion_score * 0.2)

        return min(1.0, virality)

    def _calculate_reach_score(
        self,
        engagement: Dict[str, int] = None,
        metadata: Dict[str, Any] = None
    ) -> float:
        """Calculate potential reach/impact"""
        reach = 0.0

        if engagement:
            # Direct reach from engagement
            views = engagement.get('views', 0)
            impressions = engagement.get('impressions', 0)
            reach = max(views, impressions)

        if metadata:
            # Author influence
            followers = metadata.get('author_followers', 0)
            if followers > 0:
                # Potential reach includes followers
                reach = max(reach, followers * 0.1)  # Assume 10% see the post

            # Platform reach multiplier
            platform = metadata.get('platform', '')
            platform_multipliers = {
                'twitter': 1.5,
                'reddit': 1.2,
                'facebook': 1.3,
                'instagram': 1.4,
                'tiktok': 2.0
            }
            multiplier = platform_multipliers.get(platform.lower(), 1.0)
            reach *= multiplier

        # Normalize using logarithmic scale
        normalized = np.log1p(reach) / 15  # Adjust scale as needed

        return min(1.0, normalized)

    def _calculate_overall_impact(self, scores: Dict[str, float]) -> float:
        """Calculate overall brand impact score"""
        # Define component weights
        weights = {
            'sentiment_score': 0.25,
            'engagement_score': 0.20,
            'virality_score': 0.20,
            'reach_score': 0.15,
            'brand_relevance': 0.10,
            'brand_sentiment': 0.10
        }

        total = 0.0
        total_weight = 0.0

        for component, weight in weights.items():
            if component in scores:
                total += abs(scores[component]) * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return total / total_weight

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize all scores to 0-1 range"""
        normalized = {}

        for key, value in scores.items():
            if isinstance(value, (int, float)):
                # Keep sentiment scores in -1 to 1 range
                if 'sentiment' in key.lower():
                    normalized[key] = max(-1.0, min(1.0, value))
                else:
                    normalized[key] = max(0.0, min(1.0, abs(value)))
            else:
                normalized[key] = value

        return normalized

    def calculate_brand_impact(
        self,
        sentiment: Any,
        brands: List[Any],
        engagement: Dict[str, int] = None,
        metadata: Dict[str, Any] = None
    ) -> BrandImpactScore:
        """
        Calculate comprehensive brand impact score

        Args:
            sentiment: Sentiment analysis result
            brands: Brand mentions
            engagement: Engagement metrics
            metadata: Additional metadata

        Returns:
            BrandImpactScore with detailed analysis
        """
        # Calculate all component scores
        scores = self.calculate_scores(sentiment, brands, engagement, metadata)

        # Extract specific scores
        sentiment_score = scores.get('brand_sentiment', scores.get('sentiment_score', 0.0))
        reach_score = scores.get('reach_score', 0.0)
        engagement_score = scores.get('engagement_score', 0.0)
        virality_score = scores.get('virality_score', 0.0)

        # Calculate overall impact
        overall_score = scores.get('overall_impact', 0.0)

        # Determine impact level
        impact_level = self._determine_impact_level(overall_score)

        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(sentiment, brands, engagement)

        # Identify key factors
        factors = self._identify_impact_factors(scores)

        return BrandImpactScore(
            overall_score=overall_score,
            sentiment_score=sentiment_score,
            reach_score=reach_score,
            engagement_score=engagement_score,
            virality_score=virality_score,
            impact_level=impact_level,
            confidence=confidence,
            factors=factors
        )

    def _determine_impact_level(self, score: float) -> ImpactLevel:
        """Determine impact level based on score"""
        for level in ImpactLevel:
            if score >= self.impact_thresholds[level]:
                return level
        return ImpactLevel.MINIMAL

    def _calculate_confidence(
        self,
        sentiment: Any,
        brands: List[Any],
        engagement: Dict[str, int]
    ) -> float:
        """Calculate confidence in the impact score"""
        confidence_factors = []

        # Sentiment confidence
        if sentiment:
            confidence_factors.append(sentiment.confidence)

        # Brand detection confidence
        if brands:
            brand_confidences = [b.confidence for b in brands]
            confidence_factors.append(np.mean(brand_confidences))

        # Data completeness
        data_completeness = 0.0
        if sentiment:
            data_completeness += 0.4
        if brands:
            data_completeness += 0.3
        if engagement:
            data_completeness += 0.3

        confidence_factors.append(data_completeness)

        # Average all confidence factors
        if confidence_factors:
            return np.mean(confidence_factors)

        return 0.0

    def _identify_impact_factors(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Identify key factors driving the impact"""
        factors = {
            'primary_drivers': [],
            'risk_factors': [],
            'opportunity_factors': []
        }

        # Identify primary drivers (highest scores)
        sorted_scores = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)

        for key, value in sorted_scores[:3]:
            if abs(value) > 0.5:
                factors['primary_drivers'].append({
                    'factor': key,
                    'impact': value
                })

        # Identify risk factors (negative impacts)
        for key, value in scores.items():
            if value < -0.3:
                factors['risk_factors'].append({
                    'factor': key,
                    'severity': abs(value)
                })

        # Identify opportunity factors (high positive scores)
        for key, value in scores.items():
            if value > 0.7:
                factors['opportunity_factors'].append({
                    'factor': key,
                    'potential': value
                })

        return factors

    def analyze_trend(
        self,
        brand: str,
        current_score: float,
        window_hours: int = 24
    ) -> TrendDirection:
        """
        Analyze sentiment trend for a brand

        Args:
            brand: Brand name
            current_score: Current sentiment score
            window_hours: Hours to look back

        Returns:
            Trend direction
        """
        # Get historical scores
        if brand not in self.historical_scores:
            self.historical_scores[brand] = []

        # Add current score
        now = datetime.now()
        self.historical_scores[brand].append((now, current_score))

        # Clean old scores
        cutoff = now - timedelta(hours=window_hours)
        self.historical_scores[brand] = [
            (ts, score) for ts, score in self.historical_scores[brand]
            if ts >= cutoff
        ]

        # Need at least 2 points for trend
        if len(self.historical_scores[brand]) < 2:
            return TrendDirection.STABLE

        # Calculate trend
        scores = [score for _, score in self.historical_scores[brand]]
        times = [(ts - cutoff).total_seconds() for ts, _ in self.historical_scores[brand]]

        # Simple linear regression
        if len(scores) >= 3:
            slope = np.polyfit(times, scores, 1)[0]

            # Determine trend based on slope
            if slope > 0.01:
                return TrendDirection.RISING_FAST if slope > 0.05 else TrendDirection.RISING
            elif slope < -0.01:
                return TrendDirection.DECLINING_FAST if slope < -0.05 else TrendDirection.DECLINING
            else:
                return TrendDirection.STABLE

        # Fallback to simple comparison
        if current_score > scores[0]:
            return TrendDirection.RISING
        elif current_score < scores[0]:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE