"""
JWT Service Implementation
PE-101: Enterprise-grade JWT service with RS256 signing and Redis integration
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import jwt, JWTError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from ..models.token import (
    TokenClaims, TokenType, UserRole, TokenValidationResult,
    TokenResponse
)
from ..config import settings


logger = logging.getLogger(__name__)


class JWTService:
    """JWT token management service with RS256 signing"""

    def __init__(self):
        """Initialize JWT service with RSA keys"""
        self.algorithm = settings.jwt_algorithm
        self.issuer = settings.jwt_issuer
        self.audience = settings.jwt_audience
        self.access_token_expire = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire = settings.jwt_refresh_token_expire_days

        # Load RSA keys
        try:
            self.private_key = settings.jwt_private_key
            self.public_key = settings.jwt_public_key
        except Exception as e:
            logger.warning(f"Failed to load RSA keys from config: {e}")
            # Generate keys if not provided (development only)
            self.private_key, self.public_key = self._generate_rsa_keys()

    def _generate_rsa_keys(self) -> tuple[str, str]:
        """Generate RSA key pair for development (NOT FOR PRODUCTION)"""
        logger.warning("Generating RSA keys dynamically - NOT FOR PRODUCTION USE")

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Extract private key in PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # Extract public key in PEM format
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return private_pem, public_pem

    def create_access_token(
        self,
        user_id: str,
        email: Optional[str] = None,
        roles: Optional[List[UserRole]] = None,
        permissions: Optional[List[str]] = None,
        email_verified: bool = False,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT access token with RS256 signing

        Args:
            user_id: User identifier (subject)
            email: User email address
            roles: User roles for RBAC
            permissions: Specific permissions
            email_verified: Email verification status
            session_id: Session identifier for tracking
            metadata: Additional metadata

        Returns:
            Signed JWT access token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire)
        jti = str(uuid.uuid4())

        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=expire,
            nbf=now,
            iss=self.issuer,
            aud=self.audience,
            jti=jti,
            email=email,
            roles=roles or [],
            permissions=permissions or [],
            email_verified=email_verified,
            token_type=TokenType.ACCESS,
            session_id=session_id,
            metadata=metadata or {}
        )

        # Convert to dict and handle datetime serialization
        payload = claims.dict()
        payload['iat'] = int(now.timestamp())
        payload['exp'] = int(expire.timestamp())
        payload['nbf'] = int(now.timestamp())

        # Sign token with private key
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )

        logger.info(f"Created access token for user {user_id} with JTI {jti}")
        return token

    def create_refresh_token(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a JWT refresh token with longer expiry

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Signed JWT refresh token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire)
        jti = str(uuid.uuid4())

        payload = {
            'sub': user_id,
            'iat': int(now.timestamp()),
            'exp': int(expire.timestamp()),
            'iss': self.issuer,
            'aud': self.audience,
            'jti': jti,
            'token_type': TokenType.REFRESH.value,
            'session_id': session_id
        }

        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )

        logger.info(f"Created refresh token for user {user_id} with JTI {jti}")
        return token

    def create_service_token(
        self,
        service_name: str,
        permissions: Optional[List[str]] = None,
        expire_minutes: Optional[int] = None
    ) -> str:
        """
        Create a JWT token for service-to-service authentication

        Args:
            service_name: Service identifier
            permissions: Service permissions
            expire_minutes: Custom expiry time

        Returns:
            Signed JWT service token
        """
        now = datetime.now(timezone.utc)
        expire_minutes = expire_minutes or settings.service_token_expire_minutes
        expire = now + timedelta(minutes=expire_minutes)
        jti = str(uuid.uuid4())

        payload = {
            'sub': f"service:{service_name}",
            'iat': int(now.timestamp()),
            'exp': int(expire.timestamp()),
            'iss': self.issuer,
            'aud': self.audience,
            'jti': jti,
            'token_type': TokenType.SERVICE.value,
            'service_name': service_name,
            'roles': [UserRole.SERVICE.value],
            'permissions': permissions or []
        }

        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )

        logger.info(f"Created service token for {service_name} with JTI {jti}")
        return token

    def verify_token(
        self,
        token: str,
        expected_type: Optional[TokenType] = None
    ) -> TokenValidationResult:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token to verify
            expected_type: Expected token type

        Returns:
            TokenValidationResult with validity status and claims
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )

            # Check token type if specified
            token_type = payload.get('token_type')
            if expected_type and token_type != expected_type.value:
                return TokenValidationResult(
                    valid=False,
                    error=f"Invalid token type. Expected {expected_type.value}, got {token_type}",
                    error_code="INVALID_TOKEN_TYPE"
                )

            # Convert timestamps to datetime
            payload['iat'] = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
            payload['exp'] = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            if payload.get('nbf'):
                payload['nbf'] = datetime.fromtimestamp(payload['nbf'], tz=timezone.utc)

            # Convert string roles to enum
            if 'roles' in payload:
                payload['roles'] = [UserRole(r) for r in payload.get('roles', [])]

            # Convert token_type string to enum
            if 'token_type' in payload:
                payload['token_type'] = TokenType(payload['token_type'])

            claims = TokenClaims(**payload)

            return TokenValidationResult(
                valid=True,
                claims=claims
            )

        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expired: {token[:20]}...")
            return TokenValidationResult(
                valid=False,
                error="Token has expired",
                error_code="TOKEN_EXPIRED"
            )
        except jwt.JWTClaimsError as e:
            logger.warning(f"Invalid claims: {e}")
            return TokenValidationResult(
                valid=False,
                error=f"Invalid token claims: {str(e)}",
                error_code="INVALID_CLAIMS"
            )
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return TokenValidationResult(
                valid=False,
                error=f"Invalid token: {str(e)}",
                error_code="INVALID_TOKEN"
            )
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return TokenValidationResult(
                valid=False,
                error="Token verification failed",
                error_code="VERIFICATION_ERROR"
            )

    def create_token_response(
        self,
        user_id: str,
        email: Optional[str] = None,
        roles: Optional[List[UserRole]] = None,
        permissions: Optional[List[str]] = None,
        email_verified: bool = False,
        include_refresh: bool = True
    ) -> TokenResponse:
        """
        Create a complete token response with access and optional refresh tokens

        Args:
            user_id: User identifier
            email: User email
            roles: User roles
            permissions: User permissions
            email_verified: Email verification status
            include_refresh: Include refresh token in response

        Returns:
            TokenResponse with access and refresh tokens
        """
        session_id = str(uuid.uuid4())

        # Create access token
        access_token = self.create_access_token(
            user_id=user_id,
            email=email,
            roles=roles,
            permissions=permissions,
            email_verified=email_verified,
            session_id=session_id
        )

        # Create refresh token if requested
        refresh_token = None
        if include_refresh:
            refresh_token = self.create_refresh_token(
                user_id=user_id,
                session_id=session_id
            )

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.access_token_expire * 60,  # Convert to seconds
            refresh_token=refresh_token,
            session_id=session_id
        )

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[TokenResponse]:
        """
        Generate new access token using a refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New TokenResponse or None if refresh token is invalid
        """
        # Verify refresh token
        result = self.verify_token(refresh_token, TokenType.REFRESH)

        if not result.valid or not result.claims:
            logger.warning(f"Invalid refresh token: {result.error}")
            return None

        # Extract user information from refresh token
        user_id = result.claims.sub
        session_id = result.claims.session_id

        # Create new access token with same session
        access_token = self.create_access_token(
            user_id=user_id,
            session_id=session_id,
            # Note: In production, fetch user details from database
            # to get current roles/permissions/email
        )

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.access_token_expire * 60,
            refresh_token=refresh_token,  # Return same refresh token
            session_id=session_id
        )


# Singleton instance
jwt_service = JWTService()