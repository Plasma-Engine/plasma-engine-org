"""
JWT Authentication Configuration
PE-101: Enterprise-grade JWT authentication with RS256 signing
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class AuthSettings(BaseSettings):
    """Authentication settings with environment variable support"""

    # JWT Configuration
    jwt_algorithm: str = Field(default="RS256", description="JWT signing algorithm")
    jwt_access_token_expire_minutes: int = Field(default=15, description="Access token expiry in minutes")
    jwt_refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry in days")
    jwt_issuer: str = Field(default="plasma-engine", description="JWT issuer claim")
    jwt_audience: str = Field(default="plasma-engine-api", description="JWT audience claim")

    # RSA Keys (should be loaded from environment/files)
    jwt_private_key: str = Field(..., description="RSA private key for signing JWTs")
    jwt_public_key: str = Field(..., description="RSA public key for verifying JWTs")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Use SSL for Redis connection")
    redis_token_prefix: str = Field(default="token:", description="Redis key prefix for tokens")
    redis_session_prefix: str = Field(default="session:", description="Redis key prefix for sessions")
    redis_blacklist_prefix: str = Field(default="blacklist:", description="Redis key prefix for blacklisted tokens")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Max requests per minute per user")
    rate_limit_requests_per_hour: int = Field(default=1000, description="Max requests per hour per user")

    # Security Headers
    security_headers_enabled: bool = Field(default=True, description="Enable security headers")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")

    # Auth Providers
    auth0_domain: Optional[str] = Field(default=None, description="Auth0 domain")
    auth0_api_audience: Optional[str] = Field(default=None, description="Auth0 API audience")
    clerk_secret_key: Optional[str] = Field(default=None, description="Clerk secret key")

    # Service-to-Service Auth
    service_api_keys_enabled: bool = Field(default=True, description="Enable service API keys")
    service_token_expire_minutes: int = Field(default=60, description="Service token expiry")

    # Security Settings
    password_min_length: int = Field(default=12, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase in password")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase in password")
    password_require_numbers: bool = Field(default=True, description="Require numbers in password")
    password_require_special: bool = Field(default=True, description="Require special chars in password")

    # Token Security
    require_email_verification: bool = Field(default=True, description="Require email verification")
    max_active_sessions: int = Field(default=5, description="Max active sessions per user")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
settings = AuthSettings()