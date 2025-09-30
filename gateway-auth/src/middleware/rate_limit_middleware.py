"""
Rate Limiting Middleware for FastAPI
PE-101: Per-user rate limiting with Redis backend
"""

import logging
import hashlib
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..services.redis_service import redis_service
from ..config import settings


logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting

    Args:
        request: FastAPI request

    Returns:
        User ID if authenticated, IP address otherwise
    """
    # Try to get authenticated user ID
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    # Fall back to IP address
    ip = get_remote_address(request)
    return f"ip:{ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis backend
    Implements per-user and per-IP rate limiting
    """

    def __init__(
        self,
        app,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize rate limiting middleware

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = (
            requests_per_minute or settings.rate_limit_requests_per_minute
        )
        self.requests_per_hour = (
            requests_per_hour or settings.rate_limit_requests_per_hour
        )
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""

        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get user identifier
        identifier = get_user_identifier(request)

        # Check per-minute rate limit
        minute_key = f"{identifier}:minute"
        minute_count, minute_allowed = await redis_service.store_rate_limit(
            minute_key,
            window_seconds=60,
            max_requests=self.requests_per_minute
        )

        if not minute_allowed:
            logger.warning(f"Rate limit exceeded for {identifier}: {minute_count}/min")
            return Response(
                content=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "60",
                    "Retry-After": "60"
                }
            )

        # Check per-hour rate limit
        hour_key = f"{identifier}:hour"
        hour_count, hour_allowed = await redis_service.store_rate_limit(
            hour_key,
            window_seconds=3600,
            max_requests=self.requests_per_hour
        )

        if not hour_allowed:
            logger.warning(f"Rate limit exceeded for {identifier}: {hour_count}/hour")
            return Response(
                content=f"Rate limit exceeded. Max {self.requests_per_hour} requests per hour.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "3600",
                    "Retry-After": "3600"
                }
            )

        # Add rate limit headers to response
        response = await call_next(request)

        # Add rate limit information headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - minute_count)
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - hour_count)
        )

        return response


class EndpointRateLimiter:
    """
    Per-endpoint rate limiter for specific routes
    Can be used as a dependency for fine-grained control
    """

    def __init__(
        self,
        rate: str = "10/minute",
        key_func: Optional[Callable] = None,
        error_message: str = "Rate limit exceeded"
    ):
        """
        Initialize endpoint rate limiter

        Args:
            rate: Rate limit string (e.g., "10/minute", "100/hour")
            key_func: Function to extract rate limit key from request
            error_message: Custom error message
        """
        self.rate = rate
        self.key_func = key_func or get_user_identifier
        self.error_message = error_message

        # Parse rate limit
        count, period = rate.split("/")
        self.max_requests = int(count)

        if period == "second":
            self.window_seconds = 1
        elif period == "minute":
            self.window_seconds = 60
        elif period == "hour":
            self.window_seconds = 3600
        elif period == "day":
            self.window_seconds = 86400
        else:
            raise ValueError(f"Invalid rate limit period: {period}")

    async def __call__(self, request: Request):
        """Check rate limit for endpoint"""

        if not settings.rate_limit_enabled:
            return

        # Get rate limit key
        key = self.key_func(request)
        endpoint = request.url.path.replace("/", "_")
        rate_key = f"{key}:endpoint:{endpoint}"

        # Check rate limit
        count, allowed = await redis_service.store_rate_limit(
            rate_key,
            window_seconds=self.window_seconds,
            max_requests=self.max_requests
        )

        if not allowed:
            logger.warning(
                f"Endpoint rate limit exceeded for {key} on {endpoint}: "
                f"{count}/{self.max_requests}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=self.error_message,
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.window_seconds),
                    "Retry-After": str(self.window_seconds)
                }
            )


def rate_limit(rate: str = "10/minute") -> EndpointRateLimiter:
    """
    Dependency to add rate limiting to specific endpoints

    Args:
        rate: Rate limit string (e.g., "10/minute", "100/hour")

    Returns:
        EndpointRateLimiter instance

    Example:
        @app.get("/api/expensive-operation")
        async def expensive_operation(
            _: None = Depends(rate_limit("5/minute"))
        ):
            return {"result": "success"}
    """
    return EndpointRateLimiter(rate=rate)


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts limits based on user behavior
    and system load
    """

    def __init__(
        self,
        base_rate: int = 60,
        burst_multiplier: float = 1.5,
        penalty_multiplier: float = 0.5,
        reward_multiplier: float = 1.2
    ):
        """
        Initialize adaptive rate limiter

        Args:
            base_rate: Base requests per minute
            burst_multiplier: Multiplier for burst allowance
            penalty_multiplier: Multiplier for penalty (violations)
            reward_multiplier: Multiplier for good behavior
        """
        self.base_rate = base_rate
        self.burst_multiplier = burst_multiplier
        self.penalty_multiplier = penalty_multiplier
        self.reward_multiplier = reward_multiplier

    async def get_user_limit(self, user_id: str) -> int:
        """
        Get adaptive rate limit for user

        Args:
            user_id: User identifier

        Returns:
            Adjusted rate limit
        """
        # TODO: Implement adaptive logic based on:
        # - User history (violations, good behavior)
        # - System load
        # - User tier/subscription
        # - Time of day

        # For now, return base rate
        return self.base_rate

    async def record_violation(self, user_id: str):
        """Record rate limit violation for user"""
        # TODO: Store violation in Redis with timestamp
        logger.info(f"Rate limit violation recorded for user {user_id}")

    async def record_good_behavior(self, user_id: str):
        """Record good behavior (staying under limit)"""
        # TODO: Store good behavior metrics
        logger.debug(f"Good behavior recorded for user {user_id}")


# Create singleton instances
adaptive_limiter = AdaptiveRateLimiter()


# SlowAPI limiter for compatibility
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[
        f"{settings.rate_limit_requests_per_minute}/minute",
        f"{settings.rate_limit_requests_per_hour}/hour"
    ]
)