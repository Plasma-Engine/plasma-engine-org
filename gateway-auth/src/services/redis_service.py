"""
Redis Service for Session Management
PE-101: Redis integration for token blacklisting and session management
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError

from ..config import settings
from ..models.token import SessionInfo


logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for token and session management"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client: Optional[redis.Redis] = None
        self.token_prefix = settings.redis_token_prefix
        self.session_prefix = settings.redis_session_prefix
        self.blacklist_prefix = settings.redis_blacklist_prefix

    async def connect(self):
        """Establish Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                }
            )
            await self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")

    async def blacklist_token(
        self,
        jti: str,
        expire_seconds: int,
        reason: Optional[str] = None
    ) -> bool:
        """
        Add token to blacklist

        Args:
            jti: JWT ID to blacklist
            expire_seconds: TTL for blacklist entry
            reason: Reason for blacklisting

        Returns:
            Success status
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False

        try:
            key = f"{self.blacklist_prefix}{jti}"
            value = {
                "blacklisted_at": datetime.utcnow().isoformat(),
                "reason": reason or "Token revoked"
            }

            await self.redis_client.setex(
                key,
                expire_seconds,
                json.dumps(value)
            )
            logger.info(f"Token {jti} blacklisted for {expire_seconds} seconds")
            return True

        except RedisError as e:
            logger.error(f"Failed to blacklist token {jti}: {e}")
            return False

    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if token is blacklisted

        Args:
            jti: JWT ID to check

        Returns:
            True if blacklisted
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False

        try:
            key = f"{self.blacklist_prefix}{jti}"
            result = await self.redis_client.exists(key)
            return bool(result)

        except RedisError as e:
            logger.error(f"Failed to check blacklist status for {jti}: {e}")
            # Fail-safe: assume token is valid if Redis is down
            return False

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        expire_seconds: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new session in Redis

        Args:
            session_id: Session identifier
            user_id: User identifier
            expire_seconds: Session TTL
            ip_address: Client IP
            user_agent: Client user agent
            metadata: Additional metadata

        Returns:
            Success status
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False

        try:
            now = datetime.utcnow()
            session_data = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_activity=now,
                ip_address=ip_address,
                user_agent=user_agent,
                active=True
            )

            # Store session data
            session_key = f"{self.session_prefix}{session_id}"
            await self.redis_client.setex(
                session_key,
                expire_seconds,
                session_data.json()
            )

            # Add to user's session list
            user_sessions_key = f"{self.session_prefix}user:{user_id}"
            await self.redis_client.sadd(user_sessions_key, session_id)

            # Set expiry on user sessions set
            await self.redis_client.expire(user_sessions_key, expire_seconds)

            logger.info(f"Created session {session_id} for user {user_id}")
            return True

        except RedisError as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Retrieve session information

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo or None
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return None

        try:
            session_key = f"{self.session_prefix}{session_id}"
            data = await self.redis_client.get(session_key)

            if data:
                return SessionInfo.parse_raw(data)
            return None

        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False

        try:
            session = await self.get_session(session_id)
            if not session:
                return False

            session.last_activity = datetime.utcnow()

            session_key = f"{self.session_prefix}{session_id}"
            ttl = await self.redis_client.ttl(session_key)

            if ttl > 0:
                await self.redis_client.setex(
                    session_key,
                    ttl,
                    session.json()
                )
                return True
            return False

        except RedisError as e:
            logger.error(f"Failed to update session activity for {session_id}: {e}")
            return False

    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return False

        try:
            # Get session to find user
            session = await self.get_session(session_id)
            if session:
                # Remove from user's session list
                user_sessions_key = f"{self.session_prefix}user:{session.user_id}"
                await self.redis_client.srem(user_sessions_key, session_id)

            # Delete session
            session_key = f"{self.session_prefix}{session_id}"
            result = await self.redis_client.delete(session_key)

            logger.info(f"Invalidated session {session_id}")
            return bool(result)

        except RedisError as e:
            logger.error(f"Failed to invalidate session {session_id}: {e}")
            return False

    async def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user

        Args:
            user_id: User identifier

        Returns:
            List of active sessions
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return []

        try:
            user_sessions_key = f"{self.session_prefix}user:{user_id}"
            session_ids = await self.redis_client.smembers(user_sessions_key)

            sessions = []
            for session_id in session_ids:
                session = await self.get_session(session_id)
                if session:
                    sessions.append(session)

            return sessions

        except RedisError as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    async def count_user_sessions(self, user_id: str) -> int:
        """
        Count active sessions for a user

        Args:
            user_id: User identifier

        Returns:
            Number of active sessions
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return 0

        try:
            user_sessions_key = f"{self.session_prefix}user:{user_id}"
            count = await self.redis_client.scard(user_sessions_key)
            return count or 0

        except RedisError as e:
            logger.error(f"Failed to count sessions for user {user_id}: {e}")
            return 0

    async def invalidate_user_sessions(
        self,
        user_id: str,
        except_session: Optional[str] = None
    ) -> int:
        """
        Invalidate all sessions for a user

        Args:
            user_id: User identifier
            except_session: Session to keep active

        Returns:
            Number of invalidated sessions
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return 0

        try:
            sessions = await self.get_user_sessions(user_id)
            invalidated = 0

            for session in sessions:
                if session.session_id != except_session:
                    if await self.invalidate_session(session.session_id):
                        invalidated += 1

            logger.info(f"Invalidated {invalidated} sessions for user {user_id}")
            return invalidated

        except RedisError as e:
            logger.error(f"Failed to invalidate sessions for user {user_id}: {e}")
            return 0

    async def store_rate_limit(
        self,
        key: str,
        window_seconds: int,
        max_requests: int
    ) -> tuple[int, bool]:
        """
        Implement rate limiting using Redis

        Args:
            key: Rate limit key (e.g., user_id)
            window_seconds: Time window in seconds
            max_requests: Maximum requests in window

        Returns:
            Tuple of (current_count, is_allowed)
        """
        if not self.redis_client:
            logger.error("Redis client not initialized")
            return 0, True  # Allow if Redis is down

        try:
            rate_key = f"rate:{key}"

            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, window_seconds)
            results = await pipe.execute()

            current_count = results[0]
            is_allowed = current_count <= max_requests

            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {key}: {current_count}/{max_requests}")

            return current_count, is_allowed

        except RedisError as e:
            logger.error(f"Rate limiting failed for {key}: {e}")
            return 0, True  # Allow if Redis fails


# Singleton instance
redis_service = RedisService()