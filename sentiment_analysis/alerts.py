"""
Alert System for Brand Reputation Management
Threshold-based notifications for critical brand issues
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from collections import defaultdict, deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp


logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    SENTIMENT_CRISIS = "sentiment_crisis"
    VIRAL_NEGATIVE = "viral_negative"
    BRAND_ATTACK = "brand_attack"
    COMPETITOR_MENTION = "competitor_mention"
    OPPORTUNITY = "opportunity"
    VOLUME_SPIKE = "volume_spike"
    ENGAGEMENT_ANOMALY = "engagement_anomaly"
    CUSTOM = "custom"


@dataclass
class AlertThreshold:
    metric: str
    operator: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    value: float
    severity: AlertSeverity
    alert_type: AlertType
    cooldown_minutes: int = 60
    aggregation_window: int = 5  # minutes


@dataclass
class Alert:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity = AlertSeverity.INFO
    type: AlertType = AlertType.CUSTOM
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class AlertChannel:
    name: str
    type: str  # 'email', 'slack', 'webhook', 'sms'
    config: Dict[str, Any]
    severity_filter: List[AlertSeverity] = field(default_factory=list)
    type_filter: List[AlertType] = field(default_factory=list)
    enabled: bool = True


class AlertSystem:
    """
    Advanced alert system for brand reputation management
    Monitors metrics and triggers notifications based on thresholds
    """

    def __init__(
        self,
        thresholds: List[AlertThreshold] = None,
        channels: List[AlertChannel] = None,
        alert_history_size: int = 10000,
        deduplication_window: int = 300  # seconds
    ):
        self.thresholds = thresholds or self._default_thresholds()
        self.channels = channels or []
        self.alert_history_size = alert_history_size
        self.deduplication_window = deduplication_window

        # Alert management
        self.alert_history = deque(maxlen=alert_history_size)
        self.alert_cooldowns = {}
        self.metric_buffers = defaultdict(lambda: deque(maxlen=100))

        # Alert handlers
        self.custom_handlers = {}

        # Statistics
        self.alert_stats = defaultdict(int)

        logger.info(f"AlertSystem initialized with {len(self.thresholds)} thresholds")

    def _default_thresholds(self) -> List[AlertThreshold]:
        """Default alert thresholds for brand monitoring"""
        return [
            # Sentiment Crisis
            AlertThreshold(
                metric="sentiment_score",
                operator="lt",
                value=-0.5,
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.SENTIMENT_CRISIS
            ),
            AlertThreshold(
                metric="sentiment_score",
                operator="lt",
                value=-0.8,
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.SENTIMENT_CRISIS
            ),

            # Viral Negative Content
            AlertThreshold(
                metric="virality_score",
                operator="gt",
                value=0.7,
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.VIRAL_NEGATIVE,
                aggregation_window=10
            ),

            # High Engagement Anomaly
            AlertThreshold(
                metric="engagement_score",
                operator="gt",
                value=0.9,
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.ENGAGEMENT_ANOMALY
            ),

            # Volume Spike
            AlertThreshold(
                metric="volume_change",
                operator="gt",
                value=3.0,  # 3x normal volume
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.VOLUME_SPIKE
            ),

            # Opportunity Detection
            AlertThreshold(
                metric="positive_sentiment_spike",
                operator="gt",
                value=0.8,
                severity=AlertSeverity.INFO,
                alert_type=AlertType.OPPORTUNITY
            )
        ]

    def add_threshold(self, threshold: AlertThreshold):
        """Add a new alert threshold"""
        self.thresholds.append(threshold)
        logger.info(f"Added threshold: {threshold.metric} {threshold.operator} {threshold.value}")

    def add_channel(self, channel: AlertChannel):
        """Add a new alert channel"""
        self.channels.append(channel)
        logger.info(f"Added channel: {channel.name} ({channel.type})")

    def register_handler(self, alert_type: AlertType, handler: Callable):
        """Register a custom handler for an alert type"""
        self.custom_handlers[alert_type] = handler
        logger.info(f"Registered handler for {alert_type.value}")

    def check_thresholds(
        self,
        post: Any,  # SocialMediaPost from pipeline
        sentiment: Any,  # SentimentResult from engine
        scores: Dict[str, float],
        brands: List[Any] = None  # BrandMentions from brand_processor
    ) -> List[Alert]:
        """
        Check all thresholds and generate alerts

        Args:
            post: Social media post being analyzed
            sentiment: Sentiment analysis result
            scores: Calculated scores
            brands: Brand mentions found

        Returns:
            List of generated alerts
        """
        alerts = []
        current_time = datetime.now()

        # Add current metrics to buffers
        self._update_metric_buffers(scores)

        for threshold in self.thresholds:
            # Check cooldown
            if self._is_in_cooldown(threshold, current_time):
                continue

            # Get metric value
            metric_value = self._get_metric_value(
                threshold.metric,
                scores,
                sentiment,
                brands
            )

            if metric_value is None:
                continue

            # Check threshold
            if self._check_operator(metric_value, threshold.operator, threshold.value):
                # Additional checks for specific alert types
                if threshold.alert_type == AlertType.VIRAL_NEGATIVE:
                    # Only alert if sentiment is also negative
                    if scores.get('sentiment_score', 0) >= 0:
                        continue

                # Create alert
                alert = self._create_alert(
                    threshold,
                    metric_value,
                    post,
                    sentiment,
                    brands
                )

                # Check for duplicates
                if not self._is_duplicate(alert):
                    alerts.append(alert)
                    self._set_cooldown(threshold, current_time)
                    self.alert_history.append(alert)
                    self.alert_stats[alert.type.value] += 1

        return alerts

    def _update_metric_buffers(self, scores: Dict[str, float]):
        """Update metric buffers for trend analysis"""
        timestamp = datetime.now()
        for metric, value in scores.items():
            self.metric_buffers[metric].append((timestamp, value))

    def _get_metric_value(
        self,
        metric: str,
        scores: Dict[str, float],
        sentiment: Any,
        brands: List[Any]
    ) -> Optional[float]:
        """Get value for a specific metric"""
        # Direct score metrics
        if metric in scores:
            return scores[metric]

        # Sentiment metrics
        if metric == "sentiment_score" and sentiment:
            return sentiment.compound_score

        # Brand metrics
        if metric == "brand_count" and brands:
            return len(brands)

        # Calculated metrics
        if metric == "volume_change":
            return self._calculate_volume_change()

        if metric == "positive_sentiment_spike":
            return self._calculate_sentiment_spike(positive=True)

        return None

    def _check_operator(self, value: float, operator: str, threshold: float) -> bool:
        """Check if value meets threshold based on operator"""
        operators = {
            'gt': lambda v, t: v > t,
            'lt': lambda v, t: v < t,
            'gte': lambda v, t: v >= t,
            'lte': lambda v, t: v <= t,
            'eq': lambda v, t: abs(v - t) < 0.01
        }
        return operators.get(operator, lambda v, t: False)(value, threshold)

    def _is_in_cooldown(self, threshold: AlertThreshold, current_time: datetime) -> bool:
        """Check if threshold is in cooldown period"""
        key = f"{threshold.metric}_{threshold.operator}_{threshold.value}"
        if key in self.alert_cooldowns:
            cooldown_end = self.alert_cooldowns[key]
            return current_time < cooldown_end
        return False

    def _set_cooldown(self, threshold: AlertThreshold, current_time: datetime):
        """Set cooldown for threshold"""
        key = f"{threshold.metric}_{threshold.operator}_{threshold.value}"
        cooldown_end = current_time + timedelta(minutes=threshold.cooldown_minutes)
        self.alert_cooldowns[key] = cooldown_end

    def _is_duplicate(self, alert: Alert) -> bool:
        """Check if alert is duplicate within deduplication window"""
        cutoff = datetime.now() - timedelta(seconds=self.deduplication_window)

        for historical_alert in reversed(self.alert_history):
            if historical_alert.timestamp < cutoff:
                break

            if (historical_alert.type == alert.type and
                historical_alert.severity == alert.severity and
                abs((historical_alert.timestamp - alert.timestamp).total_seconds()) < self.deduplication_window):
                return True

        return False

    def _create_alert(
        self,
        threshold: AlertThreshold,
        metric_value: float,
        post: Any,
        sentiment: Any,
        brands: List[Any]
    ) -> Alert:
        """Create alert from threshold violation"""
        # Build alert message
        message = self._build_alert_message(
            threshold,
            metric_value,
            post,
            sentiment,
            brands
        )

        # Build metadata
        metadata = {
            'threshold': {
                'metric': threshold.metric,
                'operator': threshold.operator,
                'threshold_value': threshold.value,
                'actual_value': metric_value
            },
            'post_id': post.id if post else None,
            'source': post.source.value if post else None,
            'brands': [b.brand for b in brands] if brands else [],
            'sentiment': sentiment.label if sentiment else None
        }

        return Alert(
            severity=threshold.severity,
            type=threshold.alert_type,
            message=message,
            source=post.source.value if post else "",
            metadata=metadata
        )

    def _build_alert_message(
        self,
        threshold: AlertThreshold,
        metric_value: float,
        post: Any,
        sentiment: Any,
        brands: List[Any]
    ) -> str:
        """Build human-readable alert message"""
        messages = {
            AlertType.SENTIMENT_CRISIS: f"Critical negative sentiment detected ({metric_value:.2f})",
            AlertType.VIRAL_NEGATIVE: f"Negative content going viral (virality: {metric_value:.2f})",
            AlertType.BRAND_ATTACK: f"Potential brand attack detected",
            AlertType.VOLUME_SPIKE: f"Unusual volume spike detected ({metric_value:.1f}x normal)",
            AlertType.ENGAGEMENT_ANOMALY: f"Abnormal engagement levels ({metric_value:.2f})",
            AlertType.OPPORTUNITY: f"Positive sentiment opportunity ({metric_value:.2f})"
        }

        base_message = messages.get(
            threshold.alert_type,
            f"{threshold.metric} {threshold.operator} {threshold.value} (actual: {metric_value:.2f})"
        )

        # Add brand context
        if brands:
            brand_names = list(set(b.brand for b in brands))
            base_message += f" | Brands: {', '.join(brand_names[:3])}"

        # Add source
        if post:
            base_message += f" | Source: {post.source.value}"

        return base_message

    def _calculate_volume_change(self) -> float:
        """Calculate volume change compared to baseline"""
        # This would need historical data to calculate properly
        # For now, return a placeholder
        return 1.0

    def _calculate_sentiment_spike(self, positive: bool = True) -> float:
        """Calculate sentiment spike (positive or negative)"""
        sentiment_buffer = self.metric_buffers.get('sentiment_score', deque())

        if len(sentiment_buffer) < 2:
            return 0.0

        recent = [v for _, v in list(sentiment_buffer)[-5:]]
        historical = [v for _, v in list(sentiment_buffer)[:-5]]

        if not historical:
            return 0.0

        recent_avg = sum(recent) / len(recent)
        historical_avg = sum(historical) / len(historical)

        if positive:
            spike = max(0, recent_avg - historical_avg)
        else:
            spike = max(0, historical_avg - recent_avg)

        return spike

    async def send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        # Run custom handler if registered
        if alert.type in self.custom_handlers:
            try:
                handler = self.custom_handlers[alert.type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error running custom handler for {alert.type}: {e}")

        # Send through channels
        for channel in self.channels:
            if not channel.enabled:
                continue

            # Check severity filter
            if channel.severity_filter and alert.severity not in channel.severity_filter:
                continue

            # Check type filter
            if channel.type_filter and alert.type not in channel.type_filter:
                continue

            # Send based on channel type
            try:
                if channel.type == 'email':
                    await self._send_email(alert, channel)
                elif channel.type == 'slack':
                    await self._send_slack(alert, channel)
                elif channel.type == 'webhook':
                    await self._send_webhook(alert, channel)
                elif channel.type == 'sms':
                    await self._send_sms(alert, channel)
                else:
                    logger.warning(f"Unknown channel type: {channel.type}")
            except Exception as e:
                logger.error(f"Error sending alert via {channel.name}: {e}")

    async def _send_email(self, alert: Alert, channel: AlertChannel):
        """Send email alert"""
        config = channel.config

        msg = MIMEMultipart()
        msg['From'] = config.get('from_email', 'alerts@brand-monitor.com')
        msg['To'] = config.get('to_email', '')
        msg['Subject'] = f"[{alert.severity.value.upper()}] Brand Alert: {alert.type.value}"

        body = f"""
        Alert Details:
        --------------
        Severity: {alert.severity.value}
        Type: {alert.type.value}
        Time: {alert.timestamp.isoformat()}

        Message: {alert.message}

        Metadata:
        {json.dumps(alert.metadata, indent=2)}
        """

        msg.attach(MIMEText(body, 'plain'))

        # Send email (simplified, would need proper SMTP config)
        logger.info(f"Email alert sent to {config.get('to_email')}")

    async def _send_slack(self, alert: Alert, channel: AlertChannel):
        """Send Slack alert"""
        config = channel.config
        webhook_url = config.get('webhook_url')

        if not webhook_url:
            logger.error("Slack webhook URL not configured")
            return

        # Build Slack message
        color_map = {
            AlertSeverity.CRITICAL: '#FF0000',
            AlertSeverity.HIGH: '#FFA500',
            AlertSeverity.MEDIUM: '#FFFF00',
            AlertSeverity.LOW: '#00FF00',
            AlertSeverity.INFO: '#0000FF'
        }

        slack_message = {
            'attachments': [{
                'color': color_map.get(alert.severity, '#808080'),
                'title': f"{alert.severity.value.upper()} Alert",
                'text': alert.message,
                'fields': [
                    {'title': 'Type', 'value': alert.type.value, 'short': True},
                    {'title': 'Time', 'value': alert.timestamp.isoformat(), 'short': True}
                ],
                'footer': 'Brand Monitor Alert System',
                'ts': int(alert.timestamp.timestamp())
            }]
        }

        # Send to Slack
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=slack_message) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to send Slack alert: {resp.status}")
                else:
                    logger.info("Slack alert sent successfully")

    async def _send_webhook(self, alert: Alert, channel: AlertChannel):
        """Send webhook alert"""
        config = channel.config
        url = config.get('url')

        if not url:
            logger.error("Webhook URL not configured")
            return

        # Build payload
        payload = {
            'id': alert.id,
            'severity': alert.severity.value,
            'type': alert.type.value,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'source': alert.source,
            'metadata': alert.metadata
        }

        # Send webhook
        async with aiohttp.ClientSession() as session:
            headers = config.get('headers', {})
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status not in [200, 201, 202]:
                    logger.error(f"Failed to send webhook: {resp.status}")
                else:
                    logger.info("Webhook alert sent successfully")

    async def _send_sms(self, alert: Alert, channel: AlertChannel):
        """Send SMS alert (placeholder)"""
        config = channel.config
        phone = config.get('phone_number')

        # This would integrate with SMS service like Twilio
        logger.info(f"SMS alert would be sent to {phone}: {alert.message[:160]}")

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return {
            'total_alerts': len(self.alert_history),
            'alerts_by_type': dict(self.alert_stats),
            'recent_alerts': [
                {
                    'id': alert.id,
                    'type': alert.type.value,
                    'severity': alert.severity.value,
                    'time': alert.timestamp.isoformat()
                }
                for alert in list(self.alert_history)[-10:]
            ]
        }