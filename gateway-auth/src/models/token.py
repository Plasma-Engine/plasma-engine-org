"""
Token Models and Schemas
PE-101: JWT token data models with enterprise security features
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class TokenType(str, Enum):
    """Token types supported by the system"""
    ACCESS = "access"
    REFRESH = "refresh"
    SERVICE = "service"
    API_KEY = "api_key"


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"
    READONLY = "readonly"


class TokenClaims(BaseModel):
    """JWT token claims following RFC 7519"""

    # Standard claims
    sub: str = Field(..., description="Subject (user ID)")
    iat: datetime = Field(..., description="Issued at")
    exp: datetime = Field(..., description="Expiration time")
    nbf: Optional[datetime] = Field(None, description="Not before")
    iss: str = Field(..., description="Issuer")
    aud: str = Field(..., description="Audience")
    jti: str = Field(..., description="JWT ID (unique identifier)")

    # Custom claims
    email: Optional[EmailStr] = Field(None, description="User email")
    roles: List[UserRole] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    email_verified: bool = Field(False, description="Email verification status")
    token_type: TokenType = Field(..., description="Type of token")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    service_name: Optional[str] = Field(None, description="Service name for S2S auth")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("exp")
    def validate_expiration(cls, v, values):
        """Ensure expiration is after issued at"""
        if "iat" in values and v <= values["iat"]:
            raise ValueError("Token expiration must be after issued at time")
        return v


class TokenRequest(BaseModel):
    """Token request for login/authentication"""

    username: Optional[str] = Field(None, description="Username for password flow")
    email: Optional[EmailStr] = Field(None, description="Email for password flow")
    password: str = Field(..., description="User password", min_length=8)
    grant_type: str = Field("password", description="OAuth2 grant type")
    scope: Optional[str] = Field(None, description="Requested scopes")

    @validator("username", "email")
    def validate_identifier(cls, v, values):
        """Ensure at least one identifier is provided"""
        if not values.get("username") and not values.get("email"):
            raise ValueError("Either username or email must be provided")
        return v


class TokenResponse(BaseModel):
    """Token response with access and refresh tokens"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for renewal")
    scope: Optional[str] = Field(None, description="Granted scopes")
    session_id: Optional[str] = Field(None, description="Session identifier")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., description="Valid refresh token")
    grant_type: str = Field("refresh_token", description="Grant type")


class ServiceTokenRequest(BaseModel):
    """Service-to-service authentication request"""

    service_name: str = Field(..., description="Service identifier")
    api_key: str = Field(..., description="Service API key")
    requested_scopes: List[str] = Field(default_factory=list, description="Requested permissions")


class TokenValidationResult(BaseModel):
    """Result of token validation"""

    valid: bool = Field(..., description="Token validity status")
    claims: Optional[TokenClaims] = Field(None, description="Token claims if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    error_code: Optional[str] = Field(None, description="Error code for client handling")


class RevokeTokenRequest(BaseModel):
    """Request to revoke/blacklist a token"""

    token: str = Field(..., description="Token to revoke")
    token_type_hint: Optional[TokenType] = Field(None, description="Hint about token type")
    reason: Optional[str] = Field(None, description="Reason for revocation")


class SessionInfo(BaseModel):
    """Active session information"""

    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    active: bool = Field(True, description="Session active status")