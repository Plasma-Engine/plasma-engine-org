"""
Main FastAPI Application with JWT Authentication
PE-101: Example application demonstrating JWT authentication middleware usage
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any

from .config import settings
from .services.jwt_service import jwt_service
from .services.redis_service import redis_service
from .models.token import (
    TokenRequest, TokenResponse, RefreshTokenRequest,
    RevokeTokenRequest, ServiceTokenRequest, UserRole
)
from .middleware.auth_middleware import (
    AuthMiddleware, JWTBearer, require_roles, require_service_auth
)
from .middleware.rate_limit_middleware import (
    RateLimitMiddleware, rate_limit
)
from .middleware.security_headers import (
    SecurityHeadersMiddleware, RequestIDMiddleware,
    SecurityScannerProtection, create_cors_middleware
)
from .graphql_context import get_graphql_context, GraphQLContext


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting JWT Authentication Service")
    await redis_service.connect()
    yield
    # Shutdown
    logger.info("Shutting down JWT Authentication Service")
    await redis_service.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Plasma Engine JWT Authentication",
    description="Enterprise-grade JWT authentication middleware for GraphQL Gateway",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware in correct order (outer to inner)

# 1. Security Scanner Protection (outermost)
app.add_middleware(SecurityScannerProtection)

# 2. Request ID for tracing
app.add_middleware(RequestIDMiddleware)

# 3. Security Headers
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=True,
    enable_cors=True
)

# 4. CORS
if settings.security_headers_enabled:
    app = create_cors_middleware(app)

# 5. Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_requests_per_minute,
    requests_per_hour=settings.rate_limit_requests_per_hour
)

# 6. JWT Authentication (innermost)
app.add_middleware(
    AuthMiddleware,
    require_email_verified=settings.require_email_verification
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "jwt-auth"}


# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(
    request: TokenRequest,
    _: None = Depends(rate_limit("10/minute"))
) -> TokenResponse:
    """
    Login endpoint with password authentication
    Returns access and refresh tokens
    """
    # TODO: Implement actual user authentication
    # This is a placeholder implementation

    # Validate credentials (placeholder)
    if request.password == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create tokens for user
    user_id = request.username or request.email or "user123"
    response = jwt_service.create_token_response(
        user_id=user_id,
        email=request.email,
        roles=[UserRole.USER],
        permissions=["read:profile", "write:profile"],
        email_verified=True
    )

    # Create session in Redis
    if response.session_id:
        await redis_service.create_session(
            session_id=response.session_id,
            user_id=user_id,
            expire_seconds=settings.jwt_refresh_token_expire_days * 86400
        )

    logger.info(f"User {user_id} logged in successfully")
    return response


@app.post("/auth/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(
    request: RefreshTokenRequest,
    _: None = Depends(rate_limit("30/minute"))
) -> TokenResponse:
    """
    Refresh access token using refresh token
    """
    response = jwt_service.refresh_access_token(request.refresh_token)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    return response


@app.post("/auth/logout", tags=["Authentication"])
async def logout(
    request: RevokeTokenRequest,
    current_user = Depends(JWTBearer())
) -> Dict[str, str]:
    """
    Logout endpoint - revokes tokens and invalidates session
    """
    # Blacklist the token
    await redis_service.blacklist_token(
        jti=current_user.jti,
        expire_seconds=settings.jwt_access_token_expire_minutes * 60,
        reason=request.reason or "User logout"
    )

    # Invalidate session
    if current_user.session_id:
        await redis_service.invalidate_session(current_user.session_id)

    logger.info(f"User {current_user.sub} logged out")
    return {"message": "Successfully logged out"}


@app.post("/auth/revoke", tags=["Authentication"])
async def revoke_token(
    request: RevokeTokenRequest,
    current_user = Depends(JWTBearer())
) -> Dict[str, str]:
    """
    Revoke a specific token
    """
    # Verify the token to get JTI
    result = jwt_service.verify_token(request.token)

    if not result.valid or not result.claims:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    # Blacklist the token
    await redis_service.blacklist_token(
        jti=result.claims.jti,
        expire_seconds=86400,  # 24 hours
        reason=request.reason or f"Revoked by {current_user.sub}"
    )

    logger.info(f"Token {result.claims.jti} revoked by {current_user.sub}")
    return {"message": "Token successfully revoked"}


@app.post("/auth/service-token", response_model=TokenResponse, tags=["Service Auth"])
async def create_service_token(
    request: ServiceTokenRequest,
    _: None = Depends(rate_limit("5/minute"))
) -> Dict[str, str]:
    """
    Create service-to-service authentication token
    """
    # TODO: Validate API key against database
    if request.api_key == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Create service token
    token = jwt_service.create_service_token(
        service_name=request.service_name,
        permissions=request.requested_scopes
    )

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": settings.service_token_expire_minutes * 60
    }


# Protected endpoints examples
@app.get("/api/profile", tags=["Protected"])
async def get_profile(current_user = Depends(JWTBearer())) -> Dict[str, Any]:
    """
    Get user profile (requires authentication)
    """
    return {
        "user_id": current_user.sub,
        "email": current_user.email,
        "roles": [role.value for role in current_user.roles],
        "permissions": current_user.permissions,
        "email_verified": current_user.email_verified
    }


@app.get("/api/admin", tags=["Protected"])
async def admin_endpoint(
    current_user = Depends(require_roles(UserRole.ADMIN))
) -> Dict[str, str]:
    """
    Admin-only endpoint (requires ADMIN role)
    """
    return {"message": f"Welcome admin {current_user.sub}"}


@app.get("/api/service", tags=["Protected"])
async def service_endpoint(
    service = Depends(require_service_auth(["gateway", "research"]))
) -> Dict[str, str]:
    """
    Service-to-service endpoint
    """
    return {"message": f"Service {service.service_name} authenticated"}


@app.get("/api/sessions", tags=["Session Management"])
async def get_user_sessions(current_user = Depends(JWTBearer())) -> Dict[str, Any]:
    """
    Get all active sessions for current user
    """
    sessions = await redis_service.get_user_sessions(current_user.sub)
    return {
        "user_id": current_user.sub,
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "ip_address": s.ip_address,
                "user_agent": s.user_agent
            }
            for s in sessions
        ]
    }


@app.post("/api/sessions/invalidate", tags=["Session Management"])
async def invalidate_other_sessions(
    current_user = Depends(JWTBearer())
) -> Dict[str, Any]:
    """
    Invalidate all other sessions except current
    """
    count = await redis_service.invalidate_user_sessions(
        user_id=current_user.sub,
        except_session=current_user.session_id
    )
    return {
        "message": f"Invalidated {count} sessions",
        "kept_session": current_user.session_id
    }


# GraphQL endpoint (example integration)
@app.post("/graphql", tags=["GraphQL"])
async def graphql_endpoint(
    context: GraphQLContext = Depends(get_graphql_context)
) -> Dict[str, Any]:
    """
    GraphQL endpoint with authentication context
    This is a placeholder - actual implementation would use Strawberry or similar
    """
    return {
        "is_authenticated": context.is_authenticated,
        "user_id": context.user_id,
        "roles": [r.value for r in context.user_roles] if context.user_roles else []
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )