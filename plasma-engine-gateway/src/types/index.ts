export interface ServiceDefinition {
  name: string;
  url: string;
  healthUrl?: string;
  version?: string;
  metadata?: Record<string, any>;
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  lastCheck: Date;
  responseTime?: number;
  error?: string;
}

export interface ReadinessCheck {
  ready: boolean;
  services: ServiceHealth[];
  timestamp: Date;
}

export interface Metrics {
  uptime: number;
  requests: {
    total: number;
    successful: number;
    failed: number;
    averageResponseTime: number;
  };
  services: {
    [key: string]: {
      requests: number;
      errors: number;
      averageResponseTime: number;
    };
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  timestamp: Date;
}

export interface User {
  id: string;
  email?: string;
  name?: string;
  roles?: string[];
  permissions?: string[];
  organizationId?: string;
  metadata?: Record<string, any>;
}

export interface GraphQLContext {
  token?: string;
  user?: User;
  correlationId: string;
  dataSources?: any;
}

export interface RateLimitOptions {
  windowMs: number;
  max: number;
  message?: string;
  standardHeaders?: boolean;
  legacyHeaders?: boolean;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
  keyGenerator?: (req: any) => string;
  handler?: (req: any, res: any, next: any, options: RateLimitOptions) => void;
}

export interface QueryComplexity {
  score: number;
  fields: string[];
  depth: number;
}

export interface ServiceRegistration {
  name: string;
  url: string;
  healthUrl?: string;
  schema?: string;
  version?: string;
  capabilities?: string[];
  metadata?: Record<string, any>;
  registeredAt: Date;
  lastSeen: Date;
}

export interface AuthConfig {
  jwksUri: string;
  audience: string;
  issuer: string;
  algorithms: string[];
  credentialsRequired?: boolean;
  getToken?: (req: any) => string | null;
}

export interface CacheConfig {
  ttl?: number;
  checkPeriod?: number;
  maxKeys?: number;
  useClones?: boolean;
}

export interface LogLevel {
  level: 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'fatal';
}

export interface ErrorResponse {
  message: string;
  code?: string;
  path?: string[];
  extensions?: Record<string, any>;
}