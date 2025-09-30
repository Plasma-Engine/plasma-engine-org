"""
JWT Authentication Middleware for FastAPI
PE-101: FastAPI middleware for JWT authentication with RBAC
"""

import logging
from typing import Optional, List, Callable, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..services.jwt_service import jwt_service
from ..services.redis_service import redis_service
from ..models.token import TokenType, UserRole, TokenClaims
from ..config import settings


logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    """JWT Bearer token authentication"""

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[TokenClaims]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )

            claims = await self.verify_jwt(credentials.credentials)
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token."
                )

            return claims
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

    async def verify_jwt(self, token: str) -> Optional[TokenClaims]:
        """Verify JWT token and check blacklist"""
        result = jwt_service.verify_token(token, TokenType.ACCESS)

        if not result.valid or not result.claims:
            return None

        # Check if token is blacklisted
        if await redis_service.is_token_blacklisted(result.claims.jti):
            logger.warning(f"Blacklisted token used: {result.claims.jti}")
            return None

        # Update session activity
        if result.claims.session_id:
            await redis_service.update_session_activity(result.claims.session_id)

        return result.claims


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI applications
    Validates JWT tokens and adds user context to requests
    """

    def __init__(
        self,
        app,
        exclude_paths: Optional[List[str]] = None,
        require_email_verified: bool = False
    ):
        """
        Initialize authentication middleware

        Args:
            app: FastAPI application
            exclude_paths: Paths to exclude from authentication
            require_email_verified: Require email verification
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/auth/login",
            "/auth/register",
            "/auth/refresh"
        ]
        self.require_email_verified = require_email_verified

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with authentication"""

        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return Response(
                content="Missing or invalid authorization header",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = authorization.replace("Bearer ", "")

        # Verify token
        result = jwt_service.verify_token(token, TokenType.ACCESS)
        if not result.valid or not result.claims:
            logger.warning(f"Invalid token: {result.error}")
            return Response(
                content=result.error or "Invalid token",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Check if token is blacklisted
        if await redis_service.is_token_blacklisted(result.claims.jti):
            logger.warning(f"Blacklisted token used: {result.claims.jti}")
            return Response(
                content="Token has been revoked",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Check email verification if required
        if self.require_email_verified and not result.claims.email_verified:
            return Response(
                content="Email verification required",
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Update session activity
        if result.claims.session_id:
            await redis_service.update_session_activity(result.claims.session_id)

        # Add user context to request
        request.state.user = result.claims
        request.state.user_id = result.claims.sub
        request.state.user_roles = result.claims.roles
        request.state.user_permissions = result.claims.permissions

        # Process request
        response = await call_next(request)
        return response


class RoleBasedAuthMiddleware:
    """
    Role-based access control middleware
    Checks if user has required roles for specific endpoints
    """

    def __init__(
        self,
        required_roles: Optional[List[UserRole]] = None,
        required_permissions: Optional[List[str]] = None,
        require_all: bool = False
    ):
        """
        Initialize RBAC middleware

        Args:
            required_roles: Required user roles
            required_permissions: Required permissions
            require_all: Require all roles/permissions (AND) vs any (OR)
        """
        self.required_roles = required_roles or []
        self.required_permissions = required_permissions or []
        self.require_all = require_all

    def __call__(self, request: Request) -> TokenClaims:
        """Check if user has required roles/permissions"""

        # Get user from request state (set by AuthMiddleware)
        if not hasattr(request.state, "user"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        user: TokenClaims = request.state.user

        # Check roles
        if self.required_roles:
            user_roles = set(user.roles)
            required = set(self.required_roles)

            if self.require_all:
                has_roles = required.issubset(user_roles)
            else:
                has_roles = bool(required.intersection(user_roles))

            if not has_roles:
                logger.warning(
                    f"Access denied for user {user.sub}. "
                    f"Required roles: {self.required_roles}, User roles: {user.roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

        # Check permissions
        if self.required_permissions:
            user_perms = set(user.permissions)
            required = set(self.required_permissions)

            if self.require_all:
                has_perms = required.issubset(user_perms)
            else:
                has_perms = bool(required.intersection(user_perms))

            if not has_perms:
                logger.warning(
                    f"Access denied for user {user.sub}. "
                    f"Required permissions: {self.required_permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

        return user


def require_roles(
    *roles: UserRole,
    require_all: bool = False
) -> RoleBasedAuthMiddleware:
    """
    Dependency to require specific roles

    Args:
        roles: Required roles
        require_all: Require all roles (AND) vs any (OR)

    Returns:
        RBAC middleware instance
    """
    return RoleBasedAuthMiddleware(
        required_roles=list(roles),
        require_all=require_all
    )


def require_permissions(
    *permissions: str,
    require_all: bool = False
) -> RoleBasedAuthMiddleware:
    """
    Dependency to require specific permissions

    Args:
        permissions: Required permissions
        require_all: Require all permissions (AND) vs any (OR)

    Returns:
        RBAC middleware instance
    """
    return RoleBasedAuthMiddleware(
        required_permissions=list(permissions),
        require_all=require_all
    )


class ServiceAuthMiddleware:
    """
    Service-to-service authentication middleware
    Validates service tokens and API keys
    """

    def __init__(
        self,
        allowed_services: Optional[List[str]] = None,
        require_service_token: bool = True
    ):
        """
        Initialize service auth middleware

        Args:
            allowed_services: List of allowed service names
            require_service_token: Require valid service token
        """
        self.allowed_services = allowed_services
        self.require_service_token = require_service_token

    async def __call__(self, request: Request) -> Optional[TokenClaims]:
        """Validate service authentication"""

        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key and settings.service_api_keys_enabled:
            # TODO: Validate API key against database
            # For now, we'll skip API key validation
            logger.info(f"API key authentication attempted: {api_key[:8]}...")

        # Check for service token
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            if self.require_service_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Service authentication required"
                )
            return None

        token = authorization.replace("Bearer ", "")

        # Verify service token
        result = jwt_service.verify_token(token, TokenType.SERVICE)
        if not result.valid or not result.claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token"
            )

        # Check if service is allowed
        if self.allowed_services:
            service_name = result.claims.service_name
            if service_name not in self.allowed_services:
                logger.warning(
                    f"Service {service_name} not allowed. "
                    f"Allowed: {self.allowed_services}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Service {service_name} not allowed"
                )

        return result.claims


def require_service_auth(
    allowed_services: Optional[List[str]] = None
) -> ServiceAuthMiddleware:
    """
    Dependency to require service authentication

    Args:
        allowed_services: List of allowed service names

    Returns:
        Service auth middleware instance
    """
    return ServiceAuthMiddleware(allowed_services=allowed_services)