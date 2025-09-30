"""
Unit tests for Redis Service
PE-101: Test Redis-based session management and token blacklisting
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fakeredis.aioredis import FakeRedis

from src.services.redis_service import RedisService
from src.models.token import SessionInfo


@pytest.fixture
async def redis_service():
    """Create Redis service with fake Redis"""
    service = RedisService()

    # Use FakeRedis for testing
    service.redis_client = FakeRedis(decode_responses=True)

    return service


@pytest.mark.asyncio
class TestRedisService:
    """Test Redis service functionality"""

    async def test_connect_disconnect(self):
        """Test Redis connection and disconnection"""
        service = RedisService()

        with patch("src.services.redis_service.redis.from_url") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock()
            mock_redis.return_value = mock_client

            await service.connect()

            mock_redis.assert_called_once()
            mock_client.ping.assert_called_once()

            await service.disconnect()
            mock_client.close.assert_called_once()

    async def test_blacklist_token(self, redis_service):
        """Test token blacklisting"""
        jti = "test-jti-123"
        expire_seconds = 3600
        reason = "Token revoked by user"

        result = await redis_service.blacklist_token(
            jti=jti,
            expire_seconds=expire_seconds,
            reason=reason
        )

        assert result is True

        # Check if token is in blacklist
        key = f"{redis_service.blacklist_prefix}{jti}"
        value = await redis_service.redis_client.get(key)
        assert value is not None

        data = json.loads(value)
        assert data["reason"] == reason
        assert "blacklisted_at" in data

    async def test_is_token_blacklisted(self, redis_service):
        """Test checking if token is blacklisted"""
        jti = "test-jti-456"

        # Token not blacklisted initially
        is_blacklisted = await redis_service.is_token_blacklisted(jti)
        assert is_blacklisted is False

        # Blacklist the token
        await redis_service.blacklist_token(jti, 3600, "Test")

        # Token should now be blacklisted
        is_blacklisted = await redis_service.is_token_blacklisted(jti)
        assert is_blacklisted is True

    async def test_create_session(self, redis_service):
        """Test session creation"""
        session_id = "session-789"
        user_id = "user-789"
        expire_seconds = 7200
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"

        result = await redis_service.create_session(
            session_id=session_id,
            user_id=user_id,
            expire_seconds=expire_seconds,
            ip_address=ip_address,
            user_agent=user_agent
        )

        assert result is True

        # Check session data
        session_key = f"{redis_service.session_prefix}{session_id}"
        data = await redis_service.redis_client.get(session_key)
        assert data is not None

        session = SessionInfo.parse_raw(data)
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.active is True

    async def test_get_session(self, redis_service):
        """Test retrieving session"""
        session_id = "session-101"
        user_id = "user-101"

        # Create session
        await redis_service.create_session(
            session_id=session_id,
            user_id=user_id,
            expire_seconds=3600
        )

        # Get session
        session = await redis_service.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == user_id

        # Get non-existent session
        non_existent = await redis_service.get_session("non-existent")
        assert non_existent is None

    async def test_update_session_activity(self, redis_service):
        """Test updating session last activity"""
        session_id = "session-202"
        user_id = "user-202"

        # Create session
        await redis_service.create_session(
            session_id=session_id,
            user_id=user_id,
            expire_seconds=3600
        )

        # Get initial session
        session1 = await redis_service.get_session(session_id)
        initial_activity = session1.last_activity

        # Wait a moment
        import asyncio
        await asyncio.sleep(0.1)

        # Update activity
        result = await redis_service.update_session_activity(session_id)
        assert result is True

        # Check updated activity
        session2 = await redis_service.get_session(session_id)
        assert session2.last_activity > initial_activity

    async def test_invalidate_session(self, redis_service):
        """Test session invalidation"""
        session_id = "session-303"
        user_id = "user-303"

        # Create session
        await redis_service.create_session(
            session_id=session_id,
            user_id=user_id,
            expire_seconds=3600
        )

        # Verify session exists
        session = await redis_service.get_session(session_id)
        assert session is not None

        # Invalidate session
        result = await redis_service.invalidate_session(session_id)
        assert result is True

        # Session should no longer exist
        session = await redis_service.get_session(session_id)
        assert session is None

    async def test_get_user_sessions(self, redis_service):
        """Test getting all user sessions"""
        user_id = "user-404"

        # Create multiple sessions
        session_ids = ["session-404-1", "session-404-2", "session-404-3"]

        for session_id in session_ids:
            await redis_service.create_session(
                session_id=session_id,
                user_id=user_id,
                expire_seconds=3600
            )

        # Get all user sessions
        sessions = await redis_service.get_user_sessions(user_id)

        assert len(sessions) == 3
        assert all(s.user_id == user_id for s in sessions)
        assert set(s.session_id for s in sessions) == set(session_ids)

    async def test_count_user_sessions(self, redis_service):
        """Test counting user sessions"""
        user_id = "user-505"

        # Initially no sessions
        count = await redis_service.count_user_sessions(user_id)
        assert count == 0

        # Create sessions
        for i in range(5):
            await redis_service.create_session(
                session_id=f"session-505-{i}",
                user_id=user_id,
                expire_seconds=3600
            )

        # Count should be 5
        count = await redis_service.count_user_sessions(user_id)
        assert count == 5

    async def test_invalidate_user_sessions(self, redis_service):
        """Test invalidating all user sessions except one"""
        user_id = "user-606"
        keep_session = "session-606-keep"

        # Create multiple sessions
        session_ids = [keep_session, "session-606-1", "session-606-2", "session-606-3"]

        for session_id in session_ids:
            await redis_service.create_session(
                session_id=session_id,
                user_id=user_id,
                expire_seconds=3600
            )

        # Invalidate all except keep_session
        count = await redis_service.invalidate_user_sessions(
            user_id=user_id,
            except_session=keep_session
        )

        assert count == 3  # Invalidated 3 sessions

        # Check remaining sessions
        remaining = await redis_service.get_user_sessions(user_id)
        assert len(remaining) == 1
        assert remaining[0].session_id == keep_session

    async def test_rate_limiting(self, redis_service):
        """Test rate limiting functionality"""
        key = "user-707"
        window_seconds = 60
        max_requests = 5

        # Make requests within limit
        for i in range(max_requests):
            count, allowed = await redis_service.store_rate_limit(
                key=key,
                window_seconds=window_seconds,
                max_requests=max_requests
            )
            assert allowed is True
            assert count == i + 1

        # Next request should be denied
        count, allowed = await redis_service.store_rate_limit(
            key=key,
            window_seconds=window_seconds,
            max_requests=max_requests
        )
        assert allowed is False
        assert count == max_requests + 1

    async def test_rate_limiting_window_expiry(self, redis_service):
        """Test rate limit window expiry"""
        key = "user-808"
        window_seconds = 1  # 1 second window
        max_requests = 2

        # Make max requests
        for _ in range(max_requests):
            _, allowed = await redis_service.store_rate_limit(
                key=key,
                window_seconds=window_seconds,
                max_requests=max_requests
            )
            assert allowed is True

        # Next should be denied
        _, allowed = await redis_service.store_rate_limit(
            key=key,
            window_seconds=window_seconds,
            max_requests=max_requests
        )
        assert allowed is False

        # Wait for window to expire
        import asyncio
        await asyncio.sleep(1.1)

        # Should be allowed again
        count, allowed = await redis_service.store_rate_limit(
            key=key,
            window_seconds=window_seconds,
            max_requests=max_requests
        )
        assert allowed is True
        assert count == 1  # Reset count

    async def test_error_handling_no_client(self):
        """Test error handling when Redis client is not initialized"""
        service = RedisService()
        service.redis_client = None

        # All operations should handle gracefully
        result = await service.blacklist_token("jti", 3600, "test")
        assert result is False

        is_blacklisted = await service.is_token_blacklisted("jti")
        assert is_blacklisted is False

        session = await service.get_session("session")
        assert session is None

        count = await service.count_user_sessions("user")
        assert count == 0

        # Rate limiting should allow when Redis is down (fail-open)
        count, allowed = await service.store_rate_limit("key", 60, 10)
        assert allowed is True
        assert count == 0