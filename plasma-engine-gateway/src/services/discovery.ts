import { Config } from '../config';
import { ServiceDefinition, ServiceRegistration } from '../types';
import { logger } from '../utils/logger';
import Redis from 'ioredis';
import pRetry from 'p-retry';
import fetch from 'node-fetch';

export class ServiceDiscovery {
  private redis: Redis;
  private config: Config;
  private services: Map<string, ServiceRegistration> = new Map();
  private discoveryInterval: NodeJS.Timeout | null = null;

  constructor(config: Config) {
    this.config = config;
    this.redis = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      db: config.redis.db,
      keyPrefix: `${config.redis.keyPrefix}services:`,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        logger.warn(`Redis connection retry attempt ${times}, waiting ${delay}ms`);
        return delay;
      },
    });

    this.redis.on('error', (error) => {
      logger.error('Redis error:', error);
    });

    this.redis.on('connect', () => {
      logger.info('Connected to Redis for service discovery');
    });
  }

  async start(): Promise<void> {
    // Initialize with configured services
    await this.registerConfiguredServices();

    // Start auto-discovery if enabled
    if (process.env.ENABLE_AUTO_DISCOVERY === 'true') {
      await this.startAutoDiscovery();
    }

    // Start periodic health checks
    this.startHealthChecks();
  }

  async stop(): Promise<void> {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
    }
    await this.redis.quit();
  }

  async getServices(): Promise<ServiceDefinition[]> {
    // First, try to get services from Redis
    const cachedServices = await this.getServicesFromCache();
    if (cachedServices.length > 0) {
      return cachedServices;
    }

    // Fallback to configured services
    return this.config.federation.services;
  }

  async registerService(service: ServiceRegistration): Promise<void> {
    const key = `service:${service.name}`;

    try {
      await this.redis.setex(
        key,
        300, // 5 minutes TTL
        JSON.stringify({
          ...service,
          registeredAt: service.registeredAt.toISOString(),
          lastSeen: new Date().toISOString(),
        })
      );

      this.services.set(service.name, service);
      logger.info(`Registered service: ${service.name} at ${service.url}`);
    } catch (error) {
      logger.error(`Failed to register service ${service.name}:`, error);
      throw error;
    }
  }

  async unregisterService(name: string): Promise<void> {
    const key = `service:${name}`;

    try {
      await this.redis.del(key);
      this.services.delete(name);
      logger.info(`Unregistered service: ${name}`);
    } catch (error) {
      logger.error(`Failed to unregister service ${name}:`, error);
      throw error;
    }
  }

  private async registerConfiguredServices(): Promise<void> {
    for (const service of this.config.federation.services) {
      const registration: ServiceRegistration = {
        name: service.name,
        url: service.url,
        healthUrl: service.healthUrl,
        version: await this.getServiceVersion(service),
        registeredAt: new Date(),
        lastSeen: new Date(),
      };

      await this.registerService(registration);
    }
  }

  private async getServicesFromCache(): Promise<ServiceDefinition[]> {
    try {
      const keys = await this.redis.keys('service:*');
      if (keys.length === 0) {
        return [];
      }

      const services: ServiceDefinition[] = [];
      const values = await this.redis.mget(...keys);

      for (const value of values) {
        if (value) {
          const service = JSON.parse(value);
          services.push({
            name: service.name,
            url: service.url,
            healthUrl: service.healthUrl,
            version: service.version,
            metadata: service.metadata,
          });
        }
      }

      return services;
    } catch (error) {
      logger.error('Failed to get services from cache:', error);
      return [];
    }
  }

  private async startAutoDiscovery(): Promise<void> {
    const discoveryUrl = process.env.SERVICE_DISCOVERY_URL;
    if (!discoveryUrl) {
      logger.warn('SERVICE_DISCOVERY_URL not configured, skipping auto-discovery');
      return;
    }

    const discover = async () => {
      try {
        const response = await pRetry(
          async () => {
            const res = await fetch(discoveryUrl, {
              timeout: 5000,
              headers: {
                'Content-Type': 'application/json',
                'X-Service-Name': 'gateway',
              },
            });
            if (!res.ok) {
              throw new Error(`Discovery failed: ${res.status} ${res.statusText}`);
            }
            return res.json();
          },
          {
            retries: 3,
            minTimeout: 1000,
            maxTimeout: 5000,
          }
        );

        const services = response as ServiceRegistration[];

        for (const service of services) {
          await this.registerService({
            ...service,
            registeredAt: new Date(service.registeredAt),
            lastSeen: new Date(),
          });
        }

        logger.info(`Discovered ${services.length} services`);
      } catch (error) {
        logger.error('Auto-discovery failed:', error);
      }
    };

    // Initial discovery
    await discover();

    // Set up periodic discovery
    this.discoveryInterval = setInterval(discover, 30000); // Every 30 seconds
  }

  private startHealthChecks(): void {
    const checkHealth = async () => {
      const services = await this.getServices();

      for (const service of services) {
        if (service.healthUrl) {
          try {
            const start = Date.now();
            const response = await pRetry(
              async () => {
                const res = await fetch(service.healthUrl!, {
                  timeout: 3000,
                });
                if (!res.ok && res.status !== 503) {
                  throw new Error(`Health check failed: ${res.status}`);
                }
                return res;
              },
              {
                retries: 2,
                minTimeout: 500,
                maxTimeout: 2000,
              }
            );

            const responseTime = Date.now() - start;

            logger.debug(`Health check for ${service.name}: ${response.status} (${responseTime}ms)`);

            // Update service status in cache
            await this.updateServiceHealth(service.name, response.ok, responseTime);
          } catch (error) {
            logger.error(`Health check failed for ${service.name}:`, error);
            await this.updateServiceHealth(service.name, false);
          }
        }
      }
    };

    // Initial health check
    checkHealth().catch(error => {
      logger.error('Initial health check failed:', error);
    });

    // Periodic health checks
    setInterval(checkHealth, 15000); // Every 15 seconds
  }

  private async updateServiceHealth(
    name: string,
    healthy: boolean,
    responseTime?: number
  ): Promise<void> {
    const key = `health:${name}`;

    try {
      await this.redis.setex(
        key,
        60, // 1 minute TTL
        JSON.stringify({
          healthy,
          responseTime,
          lastCheck: new Date().toISOString(),
        })
      );
    } catch (error) {
      logger.error(`Failed to update health for ${name}:`, error);
    }
  }

  private async getServiceVersion(service: ServiceDefinition): Promise<string | undefined> {
    try {
      const response = await fetch(`${service.url.replace('/graphql', '/version')}`, {
        timeout: 3000,
      });

      if (response.ok) {
        const data = await response.json();
        return data.version;
      }
    } catch (error) {
      logger.debug(`Could not get version for ${service.name}:`, error);
    }

    return undefined;
  }
}