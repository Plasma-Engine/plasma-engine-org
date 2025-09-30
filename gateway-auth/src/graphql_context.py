"""
Apollo GraphQL Context Integration
PE-101: Integration with Apollo Federation for GraphQL authentication context
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException, Depends
from strawberry import field, type as strawberry_type
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from .services.jwt_service import jwt_service
from .services.redis_service import redis_service
from .models.token import TokenClaims, UserRole, TokenType
from .middleware.auth_middleware import JWTBearer


logger = logging.getLogger(__name__)


class GraphQLContext:
    """
    GraphQL context for Apollo Federation
    Provides authentication and user context to resolvers
    """

    def __init__(
        self,
        request: Request,
        user: Optional[TokenClaims] = None,
        session_id: Optional[str] = None
    ):
        """
        Initialize GraphQL context

        Args:
            request: FastAPI request object
            user: Authenticated user claims
            session_id: Active session ID
        """
        self.request = request
        self.user = user
        self.session_id = session_id
        self.is_authenticated = user is not None
        self.user_id = user.sub if user else None
        self.user_roles = user.roles if user else []
        self.user_permissions = user.permissions if user else []

    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role"""
        return role in self.user_roles if self.user_roles else False

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.user_permissions if self.user_permissions else False

    def has_any_role(self, roles: List[UserRole]) -> bool:
        """Check if user has any of the specified roles"""
        if not self.user_roles:
            return False
        return any(role in self.user_roles for role in roles)

    def has_all_roles(self, roles: List[UserRole]) -> bool:
        """Check if user has all specified roles"""
        if not self.user_roles:
            return False
        return all(role in self.user_roles for role in roles)

    def require_authentication(self) -> None:
        """Require user to be authenticated"""
        if not self.is_authenticated:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )

    def require_role(self, role: UserRole) -> None:
        """Require user to have a specific role"""
        self.require_authentication()
        if not self.has_role(role):
            raise HTTPException(
                status_code=403,
                detail=f"Role {role.value} required"
            )

    def require_permission(self, permission: str) -> None:
        """Require user to have a specific permission"""
        self.require_authentication()
        if not self.has_permission(permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission {permission} required"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for federation"""
        return {
            "is_authenticated": self.is_authenticated,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "roles": [role.value for role in self.user_roles],
            "permissions": self.user_permissions
        }


async def get_graphql_context(
    request: Request,
    jwt_bearer: Optional[TokenClaims] = Depends(JWTBearer(auto_error=False))
) -> GraphQLContext:
    """
    Dependency to get GraphQL context with authentication

    Args:
        request: FastAPI request
        jwt_bearer: JWT authentication dependency

    Returns:
        GraphQLContext instance
    """
    # Create context with authentication info
    context = GraphQLContext(
        request=request,
        user=jwt_bearer,
        session_id=jwt_bearer.session_id if jwt_bearer else None
    )

    # Update session activity if authenticated
    if context.is_authenticated and context.session_id:
        await redis_service.update_session_activity(context.session_id)

    return context


# Strawberry GraphQL type definitions for authentication

@strawberry_type
class AuthUser:
    """Authenticated user type for GraphQL"""
    id: str
    email: Optional[str]
    email_verified: bool
    roles: List[str]
    permissions: List[str]


@strawberry_type
class AuthContext:
    """Authentication context type for GraphQL"""
    is_authenticated: bool
    user: Optional[AuthUser]
    session_id: Optional[str]


def create_apollo_context_factory():
    """
    Create context factory for Apollo Federation

    Returns:
        Context factory function for Apollo Server
    """
    async def context_factory(request: Request) -> Dict[str, Any]:
        """
        Apollo context factory

        Args:
            request: Incoming HTTP request

        Returns:
            Context dictionary for Apollo Federation
        """
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")

        user = None
        session_id = None

        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")

            # Verify token
            result = jwt_service.verify_token(token, TokenType.ACCESS)

            if result.valid and result.claims:
                # Check if token is blacklisted
                if not await redis_service.is_token_blacklisted(result.claims.jti):
                    user = result.claims
                    session_id = result.claims.session_id

                    # Update session activity
                    if session_id:
                        await redis_service.update_session_activity(session_id)

        # Create GraphQL context
        context = GraphQLContext(
            request=request,
            user=user,
            session_id=session_id
        )

        # Return context as dictionary for Apollo
        return {
            "request": request,
            "auth": context.to_dict(),
            "user": user,
            "context": context
        }

    return context_factory


# Decorator for GraphQL resolvers requiring authentication

def authenticated(func):
    """
    Decorator to require authentication for GraphQL resolvers

    Usage:
        @authenticated
        async def protected_resolver(self, info: Info) -> str:
            context = info.context["context"]
            return f"Hello {context.user_id}"
    """
    async def wrapper(self, info: Info, *args, **kwargs):
        context = info.context.get("context")

        if not context or not context.is_authenticated:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )

        return await func(self, info, *args, **kwargs)

    return wrapper


def requires_role(*roles: UserRole):
    """
    Decorator to require specific roles for GraphQL resolvers

    Args:
        roles: Required roles

    Usage:
        @requires_role(UserRole.ADMIN)
        async def admin_resolver(self, info: Info) -> str:
            return "Admin access granted"
    """
    def decorator(func):
        async def wrapper(self, info: Info, *args, **kwargs):
            context = info.context.get("context")

            if not context or not context.is_authenticated:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            if not context.has_any_role(roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"One of these roles required: {[r.value for r in roles]}"
                )

            return await func(self, info, *args, **kwargs)

        return wrapper
    return decorator


def requires_permission(*permissions: str):
    """
    Decorator to require specific permissions for GraphQL resolvers

    Args:
        permissions: Required permissions

    Usage:
        @requires_permission("users.write", "admin.access")
        async def protected_mutation(self, info: Info) -> bool:
            return True
    """
    def decorator(func):
        async def wrapper(self, info: Info, *args, **kwargs):
            context = info.context.get("context")

            if not context or not context.is_authenticated:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            missing = [p for p in permissions if not context.has_permission(p)]
            if missing:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing permissions: {missing}"
                )

            return await func(self, info, *args, **kwargs)

        return wrapper
    return decorator


# Federation directives for authentication

FEDERATION_DIRECTIVES = """
directive @authenticated on FIELD_DEFINITION
directive @requiresRole(roles: [String!]!) on FIELD_DEFINITION
directive @requiresPermission(permissions: [String!]!) on FIELD_DEFINITION
"""


def add_auth_directives_to_schema(schema_str: str) -> str:
    """
    Add authentication directives to GraphQL schema

    Args:
        schema_str: GraphQL schema string

    Returns:
        Schema with authentication directives
    """
    return FEDERATION_DIRECTIVES + "\n" + schema_str