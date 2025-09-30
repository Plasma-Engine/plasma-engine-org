"""
Comprehensive tests for the Sentiment Analysis Pipeline (PE-304)
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import json

# Import modules to test
from sentiment_analysis.engine import (
    SentimentEngine,
    SentimentModel,
    SentimentResult
)
from sentiment_analysis.brand_processor import (
    BrandProcessor,
    BrandProfile,
    BrandMention
)
from sentiment_analysis.scoring import (
    ScoringSystem,
    ImpactLevel,
    TrendDirection,
    BrandImpactScore
)
from sentiment_analysis.alerts import (
    AlertSystem,
    Alert,
    AlertSeverity,
    AlertType,
    AlertThreshold,
    AlertChannel
)
from sentiment_analysis.pipeline import (
    SentimentPipeline,
    SocialMediaPost,
    DataSource,
    ProcessedPost
)
from sentiment_analysis.integrations import (
    TwitterCollector,
    RedditCollector,
    IntegrationManager
)


# Test fixtures
@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "I absolutely love the new Apple iPhone! The camera quality is amazing and the battery life is fantastic."


@pytest.fixture
def negative_text():
    """Negative sentiment text"""
    return "This product is terrible. Worst customer service ever from Samsung. I'm extremely disappointed and angry."


@pytest.fixture
def brand_profiles():
    """Sample brand profiles for testing"""
    return [
        BrandProfile(
            name="Apple",
            aliases=["AAPL", "Apple Inc"],
            hashtags=["#Apple", "#iPhone", "#iPad"],
            handles=["@Apple", "@AppleSupport"],
            competitors=["Samsung", "Google"],
            products=["iPhone", "iPad", "Mac", "AirPods"]
        ),
        BrandProfile(
            name="Samsung",
            aliases=["Samsung Electronics"],
            hashtags=["#Samsung", "#Galaxy"],
            handles=["@Samsung", "@SamsungMobile"],
            competitors=["Apple", "Google"],
            products=["Galaxy", "Note", "Tab"]
        )
    ]


@pytest.fixture
def social_media_post():
    """Sample social media post"""
    return SocialMediaPost(
        id="12345",
        text="Just got my new Apple iPhone 15 Pro! #Apple #iPhone",
        source=DataSource.TWITTER,
        timestamp=datetime.now(),
        author="testuser",
        url="https://twitter.com/testuser/status/12345",
        metadata={
            'author_followers': 1000,
            'author_verified': False
        },
        engagement={
            'likes': 100,
            'shares': 20,
            'comments': 15
        }
    )


class TestSentimentEngine:
    """Test the sentiment analysis engine"""

    def test_engine_initialization(self):
        """Test engine initialization with different models"""
        engine = SentimentEngine(
            models=[SentimentModel.VADER, SentimentModel.TEXTBLOB],
            batch_size=50
        )
        assert engine is not None
        assert len(engine.models) == 2
        assert engine.batch_size == 50

    @patch('sentiment_analysis.engine.SentimentIntensityAnalyzer')
    def test_vader_analysis(self, mock_vader, sample_text):
        """Test VADER sentiment analysis"""
        # Mock VADER response
        mock_analyzer = Mock()
        mock_analyzer.polarity_scores.return_value = {
            'compound': 0.8,
            'pos': 0.7,
            'neg': 0.0,
            'neu': 0.3
        }
        mock_vader.return_value = mock_analyzer

        engine = SentimentEngine(models=[SentimentModel.VADER])
        result = engine.analyze(sample_text)

        assert result is not None
        assert result.label == 'POSITIVE'
        assert result.compound_score == pytest.approx(0.8, 0.1)
        assert result.confidence > 0

    @patch('sentiment_analysis.engine.TextBlob')
    def test_textblob_analysis(self, mock_textblob, sample_text):
        """Test TextBlob sentiment analysis"""
        # Mock TextBlob response
        mock_blob = Mock()
        mock_blob.sentiment.polarity = 0.6
        mock_blob.sentiment.subjectivity = 0.3
        mock_textblob.return_value = mock_blob

        engine = SentimentEngine(models=[SentimentModel.TEXTBLOB])
        result = engine.analyze(sample_text)

        assert result is not None
        assert result.label == 'POSITIVE'
        assert result.compound_score == pytest.approx(0.6, 0.1)

    def test_batch_analysis(self, sample_text, negative_text):
        """Test batch sentiment analysis"""
        engine = SentimentEngine(models=[SentimentModel.VADER])
        texts = [sample_text, negative_text]

        results = engine.analyze_batch(texts, parallel=False)

        assert len(results) == 2
        assert all(isinstance(r, SentimentResult) for r in results)

    def test_emotion_detection(self, sample_text):
        """Test emotion detection"""
        engine = SentimentEngine(models=[SentimentModel.VADER])
        result = engine.analyze(sample_text, detect_emotions=True)

        assert result.emotions is not None
        assert 'joy' in result.emotions
        assert all(0 <= v <= 1 for v in result.emotions.values())

    def test_aspect_extraction(self, sample_text):
        """Test aspect-based sentiment extraction"""
        engine = SentimentEngine(models=[SentimentModel.VADER])
        result = engine.analyze(sample_text, extract_aspects=True)

        # Aspects depend on spaCy being loaded
        if engine.nlp:
            assert result.aspects is not None


class TestBrandProcessor:
    """Test the brand mention extraction system"""

    def test_brand_processor_initialization(self, brand_profiles):
        """Test brand processor initialization"""
        processor = BrandProcessor(brands=brand_profiles)

        assert processor is not None
        assert len(processor.brands) == 2
        assert 'apple' in processor.brand_names
        assert 'samsung' in processor.brand_names

    def test_direct_brand_mention(self, brand_profiles):
        """Test direct brand name extraction"""
        processor = BrandProcessor(brands=brand_profiles)
        text = "I love my new Apple iPhone!"

        mentions = processor.extract_mentions(text)

        assert len(mentions) > 0
        assert any(m.brand == 'Apple' for m in mentions)
        assert all(m.confidence >= 0.7 for m in mentions)

    def test_hashtag_extraction(self, brand_profiles):
        """Test hashtag-based brand mention extraction"""
        processor = BrandProcessor(brands=brand_profiles)
        text = "Check out this amazing photo! #Apple #iPhone15"

        mentions = processor.extract_mentions(text)

        assert len(mentions) > 0
        assert any(m.metadata.get('match_type') == 'hashtag' for m in mentions)

    def test_handle_extraction(self, brand_profiles):
        """Test social media handle extraction"""
        processor = BrandProcessor(brands=brand_profiles)
        text = "Thanks @Apple for the great customer support!"

        mentions = processor.extract_mentions(text)

        assert len(mentions) > 0
        assert any(m.metadata.get('match_type') == 'handle' for m in mentions)

    def test_fuzzy_matching(self, brand_profiles):
        """Test fuzzy matching for misspellings"""
        processor = BrandProcessor(brands=brand_profiles, fuzzy_matching=True)
        text = "I bought a new Aple phone yesterday"  # Intentional misspelling

        mentions = processor.extract_mentions(text)

        # Should find Apple with lower confidence
        if mentions:
            apple_mentions = [m for m in mentions if m.brand == 'Apple']
            if apple_mentions:
                assert apple_mentions[0].confidence < 1.0

    def test_brand_presence_analysis(self, brand_profiles):
        """Test brand presence analysis across multiple texts"""
        processor = BrandProcessor(brands=brand_profiles)
        texts = [
            "Apple released a new iPhone",
            "Samsung Galaxy is better than iPhone",
            "I love my Apple Watch"
        ]

        analysis = processor.analyze_brand_presence(texts)

        assert 'total_mentions' in analysis
        assert 'unique_brands' in analysis
        assert analysis['unique_brands'] >= 1
        assert 'Apple' in analysis['brands']

    def test_competitor_comparison(self, brand_profiles):
        """Test competitor comparison analysis"""
        processor = BrandProcessor(brands=brand_profiles)
        texts = [
            "Apple iPhone is amazing",
            "Samsung Galaxy has better features",
            "Apple wins in design"
        ]

        comparison = processor.compare_brand_mentions(texts, "Apple")

        assert comparison['target_brand'] == 'Apple'
        assert 'competitors' in comparison
        assert 'Samsung' in comparison['competitors']


class TestScoringSystem:
    """Test the scoring and classification system"""

    def test_scoring_initialization(self):
        """Test scoring system initialization"""
        scoring = ScoringSystem()

        assert scoring is not None
        assert scoring.virality_threshold == 0.7
        assert len(scoring.impact_thresholds) > 0

    def test_sentiment_score_calculation(self):
        """Test sentiment score calculation"""
        scoring = ScoringSystem()

        # Mock sentiment result
        sentiment = Mock()
        sentiment.compound_score = 0.8
        sentiment.confidence = 0.9
        sentiment.label = 'POSITIVE'
        sentiment.emotions = None

        scores = scoring.calculate_scores(sentiment=sentiment)

        assert 'sentiment_score' in scores
        assert scores['sentiment_score'] > 0

    def test_engagement_score_calculation(self):
        """Test engagement score calculation"""
        scoring = ScoringSystem()

        engagement = {
            'likes': 1000,
            'shares': 200,
            'comments': 150
        }

        scores = scoring.calculate_scores(
            sentiment=Mock(compound_score=0.5, confidence=0.8, label='POSITIVE', emotions=None),
            engagement=engagement
        )

        assert 'engagement_score' in scores
        assert 'virality_score' in scores
        assert scores['engagement_score'] > 0

    def test_brand_impact_calculation(self, brand_profiles):
        """Test brand impact score calculation"""
        scoring = ScoringSystem()

        sentiment = Mock()
        sentiment.compound_score = -0.8
        sentiment.confidence = 0.9
        sentiment.label = 'NEGATIVE'
        sentiment.emotions = None
        sentiment.aspects = []

        brands = [
            BrandMention(
                brand="Apple",
                text="Apple",
                position=0,
                context="",
                confidence=1.0
            )
        ]

        engagement = {'likes': 10000, 'shares': 5000}

        impact = scoring.calculate_brand_impact(sentiment, brands, engagement)

        assert isinstance(impact, BrandImpactScore)
        assert impact.impact_level in ImpactLevel
        assert 0 <= impact.overall_score <= 1
        assert 0 <= impact.confidence <= 1

    def test_trend_analysis(self):
        """Test trend direction analysis"""
        scoring = ScoringSystem()

        # Add historical scores
        for i in range(5):
            trend = scoring.analyze_trend("Apple", 0.5 + i * 0.1)

        assert trend in TrendDirection
        assert trend == TrendDirection.RISING or trend == TrendDirection.RISING_FAST

    def test_impact_level_determination(self):
        """Test impact level determination"""
        scoring = ScoringSystem()

        assert scoring._determine_impact_level(0.95) == ImpactLevel.CRITICAL
        assert scoring._determine_impact_level(0.75) == ImpactLevel.HIGH
        assert scoring._determine_impact_level(0.55) == ImpactLevel.MEDIUM
        assert scoring._determine_impact_level(0.35) == ImpactLevel.LOW
        assert scoring._determine_impact_level(0.1) == ImpactLevel.MINIMAL


class TestAlertSystem:
    """Test the alert system"""

    def test_alert_system_initialization(self):
        """Test alert system initialization"""
        alert_system = AlertSystem()

        assert alert_system is not None
        assert len(alert_system.thresholds) > 0
        assert alert_system.deduplication_window == 300

    def test_threshold_checking(self, social_media_post):
        """Test threshold checking and alert generation"""
        alert_system = AlertSystem()

        sentiment = Mock()
        sentiment.compound_score = -0.9
        sentiment.confidence = 0.95
        sentiment.label = 'NEGATIVE'

        scores = {
            'sentiment_score': -0.9,
            'virality_score': 0.8,
            'engagement_score': 0.7
        }

        alerts = alert_system.check_thresholds(
            social_media_post,
            sentiment,
            scores
        )

        assert len(alerts) > 0
        assert any(a.type == AlertType.SENTIMENT_CRISIS for a in alerts)

    def test_alert_deduplication(self, social_media_post):
        """Test alert deduplication"""
        alert_system = AlertSystem(deduplication_window=60)

        sentiment = Mock()
        sentiment.compound_score = -0.9
        sentiment.confidence = 0.95
        sentiment.label = 'NEGATIVE'

        scores = {'sentiment_score': -0.9}

        # Generate first alert
        alerts1 = alert_system.check_thresholds(social_media_post, sentiment, scores)

        # Try to generate duplicate
        alerts2 = alert_system.check_thresholds(social_media_post, sentiment, scores)

        assert len(alerts1) > 0
        assert len(alerts2) < len(alerts1)  # Should be deduplicated

    def test_custom_threshold(self, social_media_post):
        """Test custom threshold addition"""
        alert_system = AlertSystem()

        custom_threshold = AlertThreshold(
            metric="custom_metric",
            operator="gt",
            value=0.5,
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.CUSTOM
        )

        alert_system.add_threshold(custom_threshold)

        scores = {'custom_metric': 0.7}
        alerts = alert_system.check_thresholds(
            social_media_post,
            Mock(compound_score=0, confidence=1, label='NEUTRAL'),
            scores
        )

        assert any(a.type == AlertType.CUSTOM for a in alerts)

    @pytest.mark.asyncio
    async def test_alert_channel(self):
        """Test alert channel configuration"""
        alert_system = AlertSystem()

        channel = AlertChannel(
            name="test_slack",
            type="slack",
            config={'webhook_url': 'https://hooks.slack.com/test'},
            severity_filter=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        )

        alert_system.add_channel(channel)

        alert = Alert(
            severity=AlertSeverity.HIGH,
            type=AlertType.SENTIMENT_CRISIS,
            message="Test alert"
        )

        # Mock the slack send method
        with patch.object(alert_system, '_send_slack', new=AsyncMock()):
            await alert_system.send_alert(alert)
            alert_system._send_slack.assert_called_once()

    def test_alert_statistics(self, social_media_post):
        """Test alert statistics tracking"""
        alert_system = AlertSystem()

        # Generate some alerts
        for i in range(5):
            sentiment = Mock(compound_score=-0.9, confidence=0.9, label='NEGATIVE')
            scores = {'sentiment_score': -0.9}
            alert_system.check_thresholds(social_media_post, sentiment, scores)

        stats = alert_system.get_alert_statistics()

        assert 'total_alerts' in stats
        assert stats['total_alerts'] > 0
        assert 'alerts_by_type' in stats


class TestSentimentPipeline:
    """Test the real-time processing pipeline"""

    @pytest.fixture
    def mock_pipeline(self, brand_profiles):
        """Create a mock pipeline for testing"""
        engine = SentimentEngine(models=[SentimentModel.VADER])
        processor = BrandProcessor(brands=brand_profiles)
        scoring = ScoringSystem()
        alerts = AlertSystem()

        return SentimentPipeline(
            sentiment_engine=engine,
            brand_processor=processor,
            scoring_system=scoring,
            alert_system=alerts,
            batch_size=10
        )

    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, mock_pipeline):
        """Test pipeline initialization"""
        await mock_pipeline.initialize()

        assert mock_pipeline is not None
        assert mock_pipeline.batch_size == 10

    @pytest.mark.asyncio
    async def test_historical_processing(self, mock_pipeline, social_media_post):
        """Test historical data processing"""
        posts = [social_media_post] * 5

        with patch.object(mock_pipeline.sentiment_engine, 'analyze') as mock_analyze:
            mock_analyze.return_value = Mock(
                label='POSITIVE',
                compound_score=0.8,
                confidence=0.9,
                emotions=None,
                aspects=None
            )

            processed = await mock_pipeline.process_historical(posts, parallel=False)

            assert len(processed) == 5
            assert all(isinstance(p, ProcessedPost) for p in processed)
            assert all(p.sentiment is not None for p in processed)

    def test_pipeline_stats(self, mock_pipeline):
        """Test pipeline statistics"""
        stats = mock_pipeline.get_stats()

        assert 'posts_received' in stats
        assert 'posts_processed' in stats
        assert 'is_running' in stats
        assert stats['is_running'] == False


class TestIntegrations:
    """Test social media integrations"""

    @pytest.mark.asyncio
    async def test_twitter_collector_initialization(self):
        """Test Twitter collector initialization"""
        collector = TwitterCollector(
            api_endpoint="http://test-api",
            kafka_topic="test-topic"
        )

        assert collector is not None
        assert collector.api_endpoint == "http://test-api"

    @pytest.mark.asyncio
    async def test_reddit_collector_initialization(self):
        """Test Reddit collector initialization"""
        collector = RedditCollector(
            api_endpoint="http://test-api",
            subreddits=["test", "news"]
        )

        assert collector is not None
        assert len(collector.subreddits) == 2

    def test_tweet_parsing(self):
        """Test tweet data parsing"""
        collector = TwitterCollector()

        tweet_data = {
            'id': '12345',
            'text': 'Test tweet',
            'created_at': datetime.now().isoformat(),
            'author': {'username': 'testuser', 'followers_count': 100},
            'public_metrics': {'like_count': 10, 'retweet_count': 5}
        }

        post = collector._parse_tweet(tweet_data)

        assert isinstance(post, SocialMediaPost)
        assert post.source == DataSource.TWITTER
        assert post.text == 'Test tweet'
        assert post.engagement['likes'] == 10

    def test_reddit_post_parsing(self):
        """Test Reddit post parsing"""
        collector = RedditCollector()

        reddit_data = {
            'id': 'abc123',
            'title': 'Test post',
            'body': 'Test content',
            'created_utc': datetime.now().timestamp(),
            'author': 'testuser',
            'subreddit': 'test',
            'score': 100,
            'num_comments': 50
        }

        post = collector._parse_reddit_post(reddit_data)

        assert isinstance(post, SocialMediaPost)
        assert post.source == DataSource.REDDIT
        assert 'Test post' in post.text
        assert post.engagement['likes'] == 100

    @pytest.mark.asyncio
    async def test_integration_manager(self, mock_pipeline):
        """Test integration manager"""
        manager = IntegrationManager(pipeline=mock_pipeline)

        # Add collectors
        twitter = TwitterCollector()
        reddit = RedditCollector()

        manager.add_collector('twitter', twitter)
        manager.add_collector('reddit', reddit)

        assert len(manager.collectors) == 2
        assert 'twitter' in manager.collectors


# Performance and Load Testing
class TestPerformance:
    """Performance and load testing"""

    @pytest.mark.skip(reason="Performance test - run manually")
    def test_large_batch_processing(self):
        """Test processing large batches of texts"""
        engine = SentimentEngine(models=[SentimentModel.VADER])

        # Generate 1000 texts
        texts = ["This is test text number {}".format(i) for i in range(1000)]

        import time
        start = time.time()
        results = engine.analyze_batch(texts, parallel=True)
        end = time.time()

        assert len(results) == 1000
        processing_time = end - start
        assert processing_time < 60  # Should complete within 60 seconds

        print(f"Processed 1000 texts in {processing_time:.2f} seconds")

    @pytest.mark.skip(reason="Load test - run manually")
    @pytest.mark.asyncio
    async def test_concurrent_stream_processing(self, mock_pipeline):
        """Test concurrent stream processing"""
        # Create mock stream of posts
        async def mock_stream():
            for i in range(100):
                yield SocialMediaPost(
                    id=str(i),
                    text=f"Test post {i}",
                    source=DataSource.TWITTER,
                    timestamp=datetime.now(),
                    author=f"user{i}"
                )
                await asyncio.sleep(0.01)  # Simulate real-time stream

        results = []

        async def collect_results(processed):
            results.append(processed)

        # Process stream
        await mock_pipeline.process_stream(mock_stream(), collect_results)

        assert len(results) > 0
        print(f"Processed {len(results)} posts from stream")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])