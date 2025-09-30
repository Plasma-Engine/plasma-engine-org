import { ServiceDefinition, ServiceHealth, ReadinessCheck, Metrics } from '../types';
import { logger } from '../utils/logger';
import fetch from 'node-fetch';
import pRetry from 'p-retry';

export class HealthCheckService {
  private services: ServiceDefinition[];
  private healthStatus: Map<string, ServiceHealth> = new Map();
  private startTime: Date;
  private requestMetrics: {
    total: number;
    successful: number;
    failed: number;
    totalTime: number;
  };

  constructor(services: ServiceDefinition[]) {
    this.services = services;
    this.startTime = new Date();
    this.requestMetrics = {
      total: 0,
      successful: 0,
      failed: 0,
      totalTime: 0,
    };

    // Initialize health status
    for (const service of services) {
      this.healthStatus.set(service.name, {
        name: service.name,
        status: 'healthy',
        lastCheck: new Date(),
      });
    }

    // Start periodic health checks
    this.startPeriodicHealthChecks();
  }

  async checkReadiness(): Promise<ReadinessCheck> {
    const checks = await Promise.all(
      this.services.map(async (service) => {
        return await this.checkServiceHealth(service);
      })
    );

    const ready = checks.every(check => check.status !== 'unhealthy');

    return {
      ready,
      services: checks,
      timestamp: new Date(),
    };
  }

  async checkServiceHealth(service: ServiceDefinition): Promise<ServiceHealth> {
    if (!service.healthUrl) {
      // If no health URL is provided, assume healthy
      return {
        name: service.name,
        status: 'healthy',
        lastCheck: new Date(),
      };
    }

    const start = Date.now();

    try {
      const response = await pRetry(
        async () => {
          const res = await fetch(service.healthUrl!, {
            timeout: 3000,
            headers: {
              'User-Agent': 'PlasmaEngine-Gateway-HealthCheck/1.0',
            },
          });

          return res;
        },
        {
          retries: 2,
          minTimeout: 500,
          maxTimeout: 2000,
          onFailedAttempt: (error) => {
            logger.debug(`Health check retry for ${service.name}: ${error.message}`);
          },
        }
      );

      const responseTime = Date.now() - start;

      let status: ServiceHealth['status'];
      if (response.ok) {
        status = 'healthy';
      } else if (response.status === 503) {
        status = 'degraded';
      } else {
        status = 'unhealthy';
      }

      const health: ServiceHealth = {
        name: service.name,
        status,
        lastCheck: new Date(),
        responseTime,
      };

      this.healthStatus.set(service.name, health);

      logger.debug(`Health check for ${service.name}: ${status} (${responseTime}ms)`);

      return health;
    } catch (error) {
      const responseTime = Date.now() - start;

      const health: ServiceHealth = {
        name: service.name,
        status: 'unhealthy',
        lastCheck: new Date(),
        responseTime,
        error: (error as Error).message,
      };

      this.healthStatus.set(service.name, health);

      logger.error(`Health check failed for ${service.name}:`, error);

      return health;
    }
  }

  async getMetrics(): Promise<Metrics> {
    const uptime = Date.now() - this.startTime.getTime();

    const memoryUsage = process.memoryUsage();
    const totalMemory = memoryUsage.heapTotal;
    const usedMemory = memoryUsage.heapUsed;
    const memoryPercentage = (usedMemory / totalMemory) * 100;

    // Calculate service-specific metrics
    const serviceMetrics: Metrics['services'] = {};

    for (const [name, health] of this.healthStatus.entries()) {
      serviceMetrics[name] = {
        requests: 0, // This would be tracked in a real implementation
        errors: health.status === 'unhealthy' ? 1 : 0,
        averageResponseTime: health.responseTime || 0,
      };
    }

    return {
      uptime,
      requests: {
        total: this.requestMetrics.total,
        successful: this.requestMetrics.successful,
        failed: this.requestMetrics.failed,
        averageResponseTime: this.requestMetrics.total > 0
          ? this.requestMetrics.totalTime / this.requestMetrics.total
          : 0,
      },
      services: serviceMetrics,
      memory: {
        used: usedMemory,
        total: totalMemory,
        percentage: memoryPercentage,
      },
      timestamp: new Date(),
    };
  }

  updateRequestMetrics(success: boolean, responseTime: number): void {
    this.requestMetrics.total++;
    if (success) {
      this.requestMetrics.successful++;
    } else {
      this.requestMetrics.failed++;
    }
    this.requestMetrics.totalTime += responseTime;
  }

  getServiceStatus(serviceName: string): ServiceHealth | undefined {
    return this.healthStatus.get(serviceName);
  }

  getAllServicesStatus(): ServiceHealth[] {
    return Array.from(this.healthStatus.values());
  }

  isHealthy(): boolean {
    for (const health of this.healthStatus.values()) {
      if (health.status === 'unhealthy') {
        return false;
      }
    }
    return true;
  }

  isDegraded(): boolean {
    for (const health of this.healthStatus.values()) {
      if (health.status === 'degraded') {
        return true;
      }
    }
    return false;
  }

  private startPeriodicHealthChecks(): void {
    const interval = parseInt(process.env.HEALTH_CHECK_INTERVAL || '30000', 10);

    const performChecks = async () => {
      for (const service of this.services) {
        try {
          await this.checkServiceHealth(service);
        } catch (error) {
          logger.error(`Periodic health check failed for ${service.name}:`, error);
        }
      }
    };

    // Initial check
    performChecks().catch(error => {
      logger.error('Initial health checks failed:', error);
    });

    // Set up periodic checks
    setInterval(() => {
      performChecks().catch(error => {
        logger.error('Periodic health checks failed:', error);
      });
    }, interval);

    logger.info(`Started periodic health checks every ${interval}ms`);
  }
}