"""
Unit tests for JWT Service
PE-101: Test JWT token creation, verification, and management
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from jose import jwt, JWTError

from src.services.jwt_service import JWTService
from src.models.token import TokenType, UserRole, TokenValidationResult


@pytest.fixture
def jwt_service():
    """Create JWT service instance with test keys"""
    with patch("src.services.jwt_service.settings") as mock_settings:
        mock_settings.jwt_algorithm = "RS256"
        mock_settings.jwt_issuer = "test-issuer"
        mock_settings.jwt_audience = "test-audience"
        mock_settings.jwt_access_token_expire_minutes = 15
        mock_settings.jwt_refresh_token_expire_days = 7
        mock_settings.service_token_expire_minutes = 60

        # Generate test RSA keys
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        mock_settings.jwt_private_key = private_pem
        mock_settings.jwt_public_key = public_pem

        return JWTService()


class TestJWTService:
    """Test JWT service functionality"""

    def test_create_access_token(self, jwt_service):
        """Test access token creation"""
        user_id = "user123"
        email = "user@example.com"
        roles = [UserRole.USER, UserRole.ADMIN]
        permissions = ["read:all", "write:all"]

        token = jwt_service.create_access_token(
            user_id=user_id,
            email=email,
            roles=roles,
            permissions=permissions,
            email_verified=True,
            session_id="session123"
        )

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        decoded = jwt.decode(
            token,
            jwt_service.public_key,
            algorithms=["RS256"],
            audience="test-audience",
            issuer="test-issuer"
        )

        assert decoded["sub"] == user_id
        assert decoded["email"] == email
        assert decoded["token_type"] == TokenType.ACCESS.value
        assert decoded["session_id"] == "session123"
        assert decoded["email_verified"] is True

    def test_create_refresh_token(self, jwt_service):
        """Test refresh token creation"""
        user_id = "user456"
        session_id = "session456"

        token = jwt_service.create_refresh_token(
            user_id=user_id,
            session_id=session_id
        )

        assert token is not None

        # Decode and verify
        decoded = jwt.decode(
            token,
            jwt_service.public_key,
            algorithms=["RS256"],
            audience="test-audience",
            issuer="test-issuer"
        )

        assert decoded["sub"] == user_id
        assert decoded["token_type"] == TokenType.REFRESH.value
        assert decoded["session_id"] == session_id

    def test_create_service_token(self, jwt_service):
        """Test service token creation"""
        service_name = "gateway-service"
        permissions = ["service:read", "service:write"]

        token = jwt_service.create_service_token(
            service_name=service_name,
            permissions=permissions,
            expire_minutes=30
        )

        assert token is not None

        # Decode and verify
        decoded = jwt.decode(
            token,
            jwt_service.public_key,
            algorithms=["RS256"],
            audience="test-audience",
            issuer="test-issuer"
        )

        assert decoded["sub"] == f"service:{service_name}"
        assert decoded["token_type"] == TokenType.SERVICE.value
        assert decoded["service_name"] == service_name
        assert UserRole.SERVICE.value in decoded["roles"]

    def test_verify_valid_token(self, jwt_service):
        """Test verification of valid token"""
        user_id = "user789"
        token = jwt_service.create_access_token(
            user_id=user_id,
            roles=[UserRole.USER]
        )

        result = jwt_service.verify_token(token, TokenType.ACCESS)

        assert result.valid is True
        assert result.claims is not None
        assert result.claims.sub == user_id
        assert result.claims.token_type == TokenType.ACCESS
        assert result.error is None

    def test_verify_expired_token(self, jwt_service):
        """Test verification of expired token"""
        # Create token with past expiration
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)

        payload = {
            "sub": "user999",
            "iat": int(past.timestamp()),
            "exp": int(past.timestamp()) + 1,  # Expired
            "iss": "test-issuer",
            "aud": "test-audience",
            "jti": "test-jti",
            "token_type": TokenType.ACCESS.value
        }

        expired_token = jwt.encode(
            payload,
            jwt_service.private_key,
            algorithm="RS256"
        )

        result = jwt_service.verify_token(expired_token)

        assert result.valid is False
        assert result.error == "Token has expired"
        assert result.error_code == "TOKEN_EXPIRED"
        assert result.claims is None

    def test_verify_invalid_signature(self, jwt_service):
        """Test verification with invalid signature"""
        # Create token with different key
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        # Generate different key
        wrong_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        wrong_pem = wrong_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        payload = {
            "sub": "user111",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iss": "test-issuer",
            "aud": "test-audience",
            "jti": "test-jti",
            "token_type": TokenType.ACCESS.value
        }

        invalid_token = jwt.encode(payload, wrong_pem, algorithm="RS256")

        result = jwt_service.verify_token(invalid_token)

        assert result.valid is False
        assert "Invalid token" in result.error
        assert result.error_code == "INVALID_TOKEN"

    def test_verify_wrong_token_type(self, jwt_service):
        """Test verification with wrong token type"""
        token = jwt_service.create_refresh_token(
            user_id="user222",
            session_id="session222"
        )

        # Try to verify refresh token as access token
        result = jwt_service.verify_token(token, TokenType.ACCESS)

        assert result.valid is False
        assert "Invalid token type" in result.error
        assert result.error_code == "INVALID_TOKEN_TYPE"

    def test_create_token_response(self, jwt_service):
        """Test complete token response creation"""
        user_id = "user333"
        email = "user333@example.com"
        roles = [UserRole.USER]

        response = jwt_service.create_token_response(
            user_id=user_id,
            email=email,
            roles=roles,
            email_verified=True,
            include_refresh=True
        )

        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "Bearer"
        assert response.expires_in == 15 * 60  # 15 minutes in seconds
        assert response.session_id is not None

    def test_refresh_access_token_valid(self, jwt_service):
        """Test refreshing access token with valid refresh token"""
        user_id = "user444"
        session_id = "session444"

        # Create refresh token
        refresh_token = jwt_service.create_refresh_token(
            user_id=user_id,
            session_id=session_id
        )

        # Refresh access token
        response = jwt_service.refresh_access_token(refresh_token)

        assert response is not None
        assert response.access_token is not None
        assert response.refresh_token == refresh_token
        assert response.session_id == session_id

    def test_refresh_access_token_invalid(self, jwt_service):
        """Test refreshing with invalid refresh token"""
        result = jwt_service.refresh_access_token("invalid_token")
        assert result is None

    def test_token_claims_validation(self):
        """Test token claims model validation"""
        from src.models.token import TokenClaims

        now = datetime.now(timezone.utc)

        # Valid claims
        valid_claims = TokenClaims(
            sub="user555",
            iat=now,
            exp=now + timedelta(hours=1),
            nbf=now,
            iss="test",
            aud="test",
            jti="jti123",
            token_type=TokenType.ACCESS
        )

        assert valid_claims.sub == "user555"

        # Invalid expiration (before issued at)
        with pytest.raises(ValueError) as exc_info:
            TokenClaims(
                sub="user666",
                iat=now,
                exp=now - timedelta(hours=1),  # Before iat
                nbf=now,
                iss="test",
                aud="test",
                jti="jti456",
                token_type=TokenType.ACCESS
            )

        assert "expiration must be after issued" in str(exc_info.value)

    def test_token_with_metadata(self, jwt_service):
        """Test token creation with metadata"""
        metadata = {
            "client_id": "mobile-app",
            "device_id": "device123",
            "ip": "192.168.1.1"
        }

        token = jwt_service.create_access_token(
            user_id="user777",
            metadata=metadata
        )

        result = jwt_service.verify_token(token)

        assert result.valid is True
        assert result.claims.metadata == metadata