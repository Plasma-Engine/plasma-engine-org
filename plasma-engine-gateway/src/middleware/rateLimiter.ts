import { Request, Response, NextFunction } from 'express';
import Redis from 'ioredis';
import { RateLimitOptions } from '../types';
import { logger } from '../utils/logger';
import { config } from '../config';

class RateLimiter {
  private redis: Redis;
  private options: RateLimitOptions;

  constructor(options: RateLimitOptions) {
    this.options = options;
    this.redis = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      db: config.redis.db,
      keyPrefix: `${config.redis.keyPrefix}ratelimit:`,
      enableOfflineQueue: false,
      maxRetriesPerRequest: 3,
    });

    this.redis.on('error', (error) => {
      logger.error('Redis rate limiter error:', error);
    });
  }

  async middleware(req: Request, res: Response, next: NextFunction) {
    try {
      // Generate unique key for rate limiting
      const key = this.options.keyGenerator?.(req) || this.defaultKeyGenerator(req);

      // Get current count from Redis
      const current = await this.redis.get(key);
      const count = current ? parseInt(current, 10) : 0;

      // Check if limit exceeded
      if (count >= this.options.max) {
        logger.warn('Rate limit exceeded:', {
          key,
          count,
          max: this.options.max,
          ip: req.ip,
        });

        // Set rate limit headers
        if (this.options.standardHeaders) {
          res.setHeader('X-RateLimit-Limit', this.options.max.toString());
          res.setHeader('X-RateLimit-Remaining', '0');
          res.setHeader('X-RateLimit-Reset', new Date(Date.now() + this.options.windowMs).toISOString());
        }

        if (this.options.legacyHeaders) {
          res.setHeader('X-Rate-Limit-Limit', this.options.max.toString());
          res.setHeader('X-Rate-Limit-Remaining', '0');
          res.setHeader('X-Rate-Limit-Reset', new Date(Date.now() + this.options.windowMs).toISOString());
        }

        // Custom handler or default response
        if (this.options.handler) {
          return this.options.handler(req, res, next, this.options);
        }

        return res.status(429).json({
          error: 'Too Many Requests',
          message: this.options.message || 'Too many requests, please try again later',
          retryAfter: Math.ceil(this.options.windowMs / 1000),
        });
      }

      // Increment counter
      const multi = this.redis.multi();
      multi.incr(key);
      if (count === 0) {
        multi.pexpire(key, this.options.windowMs);
      }
      await multi.exec();

      // Set rate limit headers
      const remaining = Math.max(0, this.options.max - count - 1);

      if (this.options.standardHeaders) {
        res.setHeader('X-RateLimit-Limit', this.options.max.toString());
        res.setHeader('X-RateLimit-Remaining', remaining.toString());
        res.setHeader('X-RateLimit-Reset', new Date(Date.now() + this.options.windowMs).toISOString());
      }

      if (this.options.legacyHeaders) {
        res.setHeader('X-Rate-Limit-Limit', this.options.max.toString());
        res.setHeader('X-Rate-Limit-Remaining', remaining.toString());
        res.setHeader('X-Rate-Limit-Reset', new Date(Date.now() + this.options.windowMs).toISOString());
      }

      // Track successful/failed requests if needed
      res.on('finish', () => {
        const success = res.statusCode < 400;

        if (
          (success && this.options.skipSuccessfulRequests) ||
          (!success && this.options.skipFailedRequests)
        ) {
          // Decrement counter for skipped requests
          this.redis.decr(key).catch(error => {
            logger.error('Failed to decrement rate limit counter:', error);
          });
        }
      });

      next();
    } catch (error) {
      logger.error('Rate limiter error:', error);

      // If Redis is down, allow the request but log the error
      next();
    }
  }

  private defaultKeyGenerator(req: Request): string {
    // Use user ID if authenticated, otherwise use IP
    if (req.user?.id) {
      return `user:${req.user.id}`;
    }

    // Use IP address as fallback
    const ip = req.headers['x-forwarded-for'] || req.ip || 'unknown';
    return `ip:${ip}`;
  }

  async reset(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async getStatus(key: string): Promise<{ count: number; ttl: number }> {
    const [count, ttl] = await Promise.all([
      this.redis.get(key),
      this.redis.pttl(key),
    ]);

    return {
      count: count ? parseInt(count, 10) : 0,
      ttl: ttl > 0 ? ttl : 0,
    };
  }
}

// Create tiered rate limiters for different user types
export function createRateLimiter(options: Partial<RateLimitOptions> = {}) {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Determine rate limit tier based on user type
    let tierOptions: RateLimitOptions;

    if (req.user?.roles?.includes('admin')) {
      // Admin tier - highest limits
      tierOptions = {
        windowMs: options.windowMs || 60000,
        max: 1000,
        ...options,
      };
    } else if (req.user?.roles?.includes('premium')) {
      // Premium tier - higher limits
      tierOptions = {
        windowMs: options.windowMs || 60000,
        max: 500,
        ...options,
      };
    } else if (req.user?.id) {
      // Authenticated tier - standard limits
      tierOptions = {
        windowMs: options.windowMs || 60000,
        max: options.max || 100,
        ...options,
      };
    } else {
      // Anonymous tier - lowest limits
      tierOptions = {
        windowMs: options.windowMs || 60000,
        max: Math.min(options.max || 30, 30),
        ...options,
      };
    }

    const limiter = new RateLimiter(tierOptions);
    await limiter.middleware(req, res, next);
  };
}

// Create a sliding window rate limiter
export class SlidingWindowRateLimiter {
  private redis: Redis;
  private window: number;
  private max: number;

  constructor(window: number, max: number) {
    this.window = window;
    this.max = max;
    this.redis = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      db: config.redis.db,
      keyPrefix: `${config.redis.keyPrefix}sliding:`,
    });
  }

  async isAllowed(key: string): Promise<boolean> {
    const now = Date.now();
    const windowStart = now - this.window;

    // Remove old entries
    await this.redis.zremrangebyscore(key, '-inf', windowStart.toString());

    // Count entries in current window
    const count = await this.redis.zcard(key);

    if (count >= this.max) {
      return false;
    }

    // Add current request
    await this.redis.zadd(key, now, `${now}-${Math.random()}`);
    await this.redis.expire(key, Math.ceil(this.window / 1000));

    return true;
  }

  middleware() {
    return async (req: Request, res: Response, next: NextFunction) => {
      const key = req.user?.id ? `user:${req.user.id}` : `ip:${req.ip}`;
      const allowed = await this.isAllowed(key);

      if (!allowed) {
        return res.status(429).json({
          error: 'Too Many Requests',
          message: 'Rate limit exceeded',
        });
      }

      next();
    };
  }
}