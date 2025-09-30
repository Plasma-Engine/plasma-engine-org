import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import jwksRsa from 'jwks-rsa';
import { config } from '../config';
import { logger } from '../utils/logger';
import { User } from '../types';

// JWKS client for RSA key retrieval
const jwksClient = jwksRsa({
  jwksUri: config.auth.jwksUri,
  cache: true,
  cacheMaxEntries: 5,
  cacheMaxAge: 600000, // 10 minutes
  rateLimit: true,
  jwksRequestsPerMinute: 10,
});

// Helper to get signing key
const getKey = (header: jwt.JwtHeader, callback: jwt.SigningKeyCallback) => {
  jwksClient.getSigningKey(header.kid!, (error, key) => {
    if (error) {
      callback(error);
    } else {
      const signingKey = key?.getPublicKey();
      callback(null, signingKey);
    }
  });
};

// Extend Request type to include user
declare global {
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // Skip authentication if disabled
  if (!config.auth.enabled) {
    logger.debug('Authentication is disabled');
    return next();
  }

  // Allow introspection queries without auth in development
  if (config.isDevelopment && req.body?.query?.includes('__schema')) {
    logger.debug('Allowing introspection query in development');
    return next();
  }

  // Extract token from Authorization header
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    // Check for API key authentication
    const apiKey = req.headers['x-api-key'] as string;
    if (apiKey) {
      return handleApiKeyAuth(apiKey, req, res, next);
    }

    // Allow unauthenticated requests for public operations
    if (isPublicOperation(req)) {
      return next();
    }

    return res.status(401).json({
      error: 'Unauthorized',
      message: 'No authorization token provided',
    });
  }

  const token = authHeader.split(' ')[1]; // Bearer <token>
  if (!token) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid authorization header format',
    });
  }

  // Verify JWT token
  jwt.verify(
    token,
    getKey,
    {
      audience: config.auth.audience,
      issuer: config.auth.issuer,
      algorithms: config.auth.algorithms as jwt.Algorithm[],
    },
    (error, decoded) => {
      if (error) {
        logger.error('JWT verification failed:', error);

        if (error.name === 'TokenExpiredError') {
          return res.status(401).json({
            error: 'Unauthorized',
            message: 'Token has expired',
          });
        }

        if (error.name === 'JsonWebTokenError') {
          return res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid token',
          });
        }

        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Token verification failed',
        });
      }

      // Extract user information from token
      const payload = decoded as jwt.JwtPayload;

      req.user = {
        id: payload.sub || payload.userId,
        email: payload.email,
        name: payload.name,
        roles: payload.roles || [],
        permissions: payload.permissions || [],
        organizationId: payload.organizationId || payload.org_id,
        metadata: {
          ...payload,
        },
      };

      logger.debug('Authenticated user:', {
        id: req.user.id,
        email: req.user.email,
        organizationId: req.user.organizationId,
      });

      next();
    }
  );
};

// Handle API key authentication
function handleApiKeyAuth(apiKey: string, req: Request, res: Response, next: NextFunction) {
  // In a real implementation, this would validate against a database
  // For now, we'll check against environment variables
  const validApiKeys = process.env.API_KEYS?.split(',') || [];

  if (!validApiKeys.includes(apiKey)) {
    logger.warn('Invalid API key attempt:', apiKey.substring(0, 8) + '...');
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid API key',
    });
  }

  // Set user context for API key authentication
  req.user = {
    id: `api-key-${apiKey.substring(0, 8)}`,
    roles: ['api_user'],
    permissions: ['read', 'write'],
    metadata: {
      authType: 'api_key',
    },
  };

  logger.debug('Authenticated via API key');
  next();
}

// Check if the operation is public (doesn't require authentication)
function isPublicOperation(req: Request): boolean {
  const publicOperations = [
    'GetPublicContent',
    'SearchPublicBrands',
    'GetSystemStatus',
  ];

  const operationName = req.body?.operationName;
  if (operationName && publicOperations.includes(operationName)) {
    return true;
  }

  // Check for specific public queries in the GraphQL query
  const query = req.body?.query;
  if (query) {
    for (const op of publicOperations) {
      if (query.includes(op)) {
        return true;
      }
    }
  }

  return false;
}

// Role-based access control middleware
export const requireRole = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    const userRoles = req.user.roles || [];
    const hasRole = roles.some(role => userRoles.includes(role));

    if (!hasRole) {
      logger.warn('Access denied - insufficient role:', {
        userId: req.user.id,
        requiredRoles: roles,
        userRoles,
      });

      return res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient permissions',
      });
    }

    next();
  };
};

// Permission-based access control middleware
export const requirePermission = (permissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    const userPermissions = req.user.permissions || [];
    const hasPermission = permissions.some(permission => userPermissions.includes(permission));

    if (!hasPermission) {
      logger.warn('Access denied - insufficient permission:', {
        userId: req.user.id,
        requiredPermissions: permissions,
        userPermissions,
      });

      return res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient permissions',
      });
    }

    next();
  };
};