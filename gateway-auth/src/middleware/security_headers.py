"""
Security Headers Middleware for FastAPI
PE-101: Enterprise security headers for defense-in-depth
"""

import logging
from typing import Optional, Dict, List, Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware

from ..config import settings


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware for FastAPI
    Implements OWASP recommended security headers
    """

    def __init__(
        self,
        app,
        csp_policy: Optional[str] = None,
        enable_hsts: bool = True,
        enable_cors: bool = True,
        cors_origins: Optional[List[str]] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize security headers middleware

        Args:
            app: FastAPI application
            csp_policy: Content Security Policy
            enable_hsts: Enable HSTS header
            enable_cors: Enable CORS handling
            cors_origins: Allowed CORS origins
            custom_headers: Additional custom headers
        """
        super().__init__(app)

        # Default CSP policy (restrictive)
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"
        )

        self.enable_hsts = enable_hsts
        self.enable_cors = enable_cors
        self.cors_origins = cors_origins or settings.cors_origins
        self.custom_headers = custom_headers or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""

        # Process request
        response = await call_next(request)

        # Skip headers for excluded paths (health checks, etc.)
        if request.url.path in ["/health", "/metrics"]:
            return response

        # Add security headers if enabled
        if settings.security_headers_enabled:
            # Content Security Policy
            response.headers["Content-Security-Policy"] = self.csp_policy

            # X-Content-Type-Options
            response.headers["X-Content-Type-Options"] = "nosniff"

            # X-Frame-Options
            response.headers["X-Frame-Options"] = "DENY"

            # X-XSS-Protection (legacy but still useful)
            response.headers["X-XSS-Protection"] = "1; mode=block"

            # Referrer-Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Permissions-Policy (replaces Feature-Policy)
            response.headers["Permissions-Policy"] = (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            )

            # HSTS (HTTP Strict Transport Security)
            if self.enable_hsts:
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains; preload"
                )

            # Remove server header if present
            response.headers.pop("Server", None)

            # Add custom headers
            for header, value in self.custom_headers.items():
                response.headers[header] = value

        return response


def create_cors_middleware(
    app,
    origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None
) -> CORSMiddleware:
    """
    Create CORS middleware with secure defaults

    Args:
        app: FastAPI application
        origins: Allowed origins
        allow_credentials: Allow credentials
        allow_methods: Allowed methods
        allow_headers: Allowed headers

    Returns:
        Configured CORS middleware
    """
    origins = origins or settings.cors_origins

    return CORSMiddleware(
        app,
        allow_origins=origins,
        allow_credentials=allow_credentials and settings.cors_allow_credentials,
        allow_methods=allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=allow_headers or [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
            "X-Session-ID"
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Request-ID"
        ],
        max_age=3600  # Cache preflight requests for 1 hour
    )


class CSPReportMiddleware:
    """
    Middleware to handle Content Security Policy violation reports
    """

    def __init__(self, report_uri: str = "/api/csp-report"):
        """
        Initialize CSP report middleware

        Args:
            report_uri: Endpoint for CSP reports
        """
        self.report_uri = report_uri

    async def __call__(self, request: Request) -> Dict:
        """Process CSP violation report"""

        if request.url.path == self.report_uri:
            # Log CSP violation
            report = await request.json()
            logger.warning(f"CSP Violation Report: {report}")

            # TODO: Store in database or send to monitoring service

            return {"status": "received"}


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request for tracing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request and response"""

        import uuid

        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add to request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class SecurityScannerProtection(BaseHTTPMiddleware):
    """
    Protection against common security scanners and malicious requests
    """

    def __init__(
        self,
        app,
        block_scanners: bool = True,
        block_suspicious_paths: bool = True
    ):
        """
        Initialize scanner protection

        Args:
            app: FastAPI application
            block_scanners: Block known scanner user agents
            block_suspicious_paths: Block suspicious paths
        """
        super().__init__(app)
        self.block_scanners = block_scanners
        self.block_suspicious_paths = block_suspicious_paths

        # Known scanner user agents (partial list)
        self.scanner_agents = [
            "nikto",
            "nmap",
            "sqlmap",
            "openvas",
            "nessus",
            "metasploit",
            "burp",
            "zap",
            "acunetix",
            "qualys"
        ]

        # Suspicious path patterns
        self.suspicious_paths = [
            "/.env",
            "/.git",
            "/.svn",
            "/wp-admin",
            "/phpmyadmin",
            "/admin",
            "/backup",
            "/.htaccess",
            "/config.php",
            "/.aws",
            "/api/v1/pods"  # Kubernetes probe
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check for malicious requests"""

        # Check user agent for scanners
        if self.block_scanners:
            user_agent = request.headers.get("User-Agent", "").lower()
            for scanner in self.scanner_agents:
                if scanner in user_agent:
                    logger.warning(f"Blocked scanner: {user_agent} from {request.client.host}")
                    return Response(
                        content="Forbidden",
                        status_code=403
                    )

        # Check for suspicious paths
        if self.block_suspicious_paths:
            path = request.url.path.lower()
            for suspicious in self.suspicious_paths:
                if suspicious in path:
                    logger.warning(
                        f"Blocked suspicious path: {path} from {request.client.host}"
                    )
                    return Response(
                        content="Not Found",
                        status_code=404  # Return 404 to not reveal existence
                    )

        return await call_next(request)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    IP whitelist middleware for restricting access to specific IPs
    Useful for admin endpoints or internal services
    """

    def __init__(
        self,
        app,
        whitelist: List[str],
        exclude_paths: Optional[List[str]] = None
    ):
        """
        Initialize IP whitelist middleware

        Args:
            app: FastAPI application
            whitelist: List of allowed IP addresses/ranges
            exclude_paths: Paths to exclude from IP check
        """
        super().__init__(app)
        self.whitelist = whitelist
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check if request IP is whitelisted"""

        # Skip for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host

        # Check whitelist
        if client_ip not in self.whitelist:
            logger.warning(f"Blocked non-whitelisted IP: {client_ip}")
            return Response(
                content="Forbidden",
                status_code=403
            )

        return await call_next(request)