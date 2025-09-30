import dotenv from 'dotenv';
import { ServiceDefinition } from '../types';

dotenv.config();

export interface Config {
  isDevelopment: boolean;
  server: {
    port: number;
    graphqlPath: string;
    bodyLimit: string;
  };
  cors: {
    origin: string | string[] | boolean;
    credentials: boolean;
  };
  federation: {
    introspection: boolean;
    pollInterval: number;
    maxQueryComplexity: number;
    services: ServiceDefinition[];
  };
  auth: {
    jwksUri: string;
    audience: string;
    issuer: string;
    algorithms: string[];
    enabled: boolean;
  };
  redis: {
    host: string;
    port: number;
    password?: string;
    db: number;
    keyPrefix: string;
  };
  rateLimit: {
    windowMs: number;
    max: number;
    standardHeaders: boolean;
    legacyHeaders: boolean;
    skipSuccessfulRequests: boolean;
    skipFailedRequests: boolean;
  };
  monitoring: {
    enabled: boolean;
    sentry?: {
      dsn: string;
      environment: string;
      tracesSampleRate: number;
    };
  };
}

export const config: Config = {
  isDevelopment: process.env.NODE_ENV !== 'production',

  server: {
    port: parseInt(process.env.PORT || '4000', 10),
    graphqlPath: process.env.GRAPHQL_PATH || '/graphql',
    bodyLimit: process.env.BODY_LIMIT || '10mb',
  },

  cors: {
    origin: process.env.CORS_ORIGIN ?
      process.env.CORS_ORIGIN.split(',').map(o => o.trim()) :
      true,
    credentials: true,
  },

  federation: {
    introspection: process.env.ENABLE_INTROSPECTION === 'true' || process.env.NODE_ENV !== 'production',
    pollInterval: parseInt(process.env.POLL_INTERVAL || '10000', 10),
    maxQueryComplexity: parseInt(process.env.MAX_QUERY_COMPLEXITY || '1000', 10),
    services: [
      {
        name: 'research',
        url: process.env.RESEARCH_SERVICE_URL || 'http://localhost:4001/graphql',
        healthUrl: process.env.RESEARCH_HEALTH_URL || 'http://localhost:4001/health',
      },
      {
        name: 'content',
        url: process.env.CONTENT_SERVICE_URL || 'http://localhost:4002/graphql',
        healthUrl: process.env.CONTENT_HEALTH_URL || 'http://localhost:4002/health',
      },
      {
        name: 'brand',
        url: process.env.BRAND_SERVICE_URL || 'http://localhost:4003/graphql',
        healthUrl: process.env.BRAND_HEALTH_URL || 'http://localhost:4003/health',
      },
      {
        name: 'agent',
        url: process.env.AGENT_SERVICE_URL || 'http://localhost:4004/graphql',
        healthUrl: process.env.AGENT_HEALTH_URL || 'http://localhost:4004/health',
      },
    ].filter(service => {
      // Only include services that are explicitly enabled
      const enableKey = `ENABLE_${service.name.toUpperCase()}_SERVICE`;
      return process.env[enableKey] !== 'false';
    }),
  },

  auth: {
    jwksUri: process.env.JWKS_URI || 'https://your-auth-domain/.well-known/jwks.json',
    audience: process.env.JWT_AUDIENCE || 'https://api.plasma-engine.com',
    issuer: process.env.JWT_ISSUER || 'https://auth.plasma-engine.com/',
    algorithms: ['RS256'],
    enabled: process.env.DISABLE_AUTH !== 'true',
  },

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
    db: parseInt(process.env.REDIS_DB || '0', 10),
    keyPrefix: process.env.REDIS_KEY_PREFIX || 'plasma:gateway:',
  },

  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10), // 1 minute
    max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10), // 100 requests per window
    standardHeaders: true,
    legacyHeaders: false,
    skipSuccessfulRequests: false,
    skipFailedRequests: true,
  },

  monitoring: {
    enabled: process.env.MONITORING_ENABLED === 'true',
    sentry: process.env.SENTRY_DSN ? {
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV || 'development',
      tracesSampleRate: parseFloat(process.env.SENTRY_TRACES_SAMPLE_RATE || '0.1'),
    } : undefined,
  },
};