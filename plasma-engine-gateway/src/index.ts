import { ApolloServer } from '@apollo/server';
import { ApolloGateway, RemoteGraphQLDataSource, IntrospectAndCompose } from '@apollo/gateway';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { ApolloServerPluginLandingPageLocalDefault } from '@apollo/server/plugin/landingPage/default';
import express from 'express';
import cors from 'cors';
import http from 'http';
import { config } from './config';
import { logger } from './utils/logger';
import { authMiddleware } from './middleware/auth';
import { ServiceDiscovery } from './services/discovery';
import { HealthCheckService } from './services/health';
import { createRateLimiter } from './middleware/rateLimiter';
import { QueryComplexityPlugin } from './plugins/queryComplexity';

async function startServer() {
  const app = express();
  const httpServer = http.createServer(app);

  // Initialize service discovery
  const serviceDiscovery = new ServiceDiscovery(config);
  const services = await serviceDiscovery.getServices();

  // Initialize health check service
  const healthCheck = new HealthCheckService(services);

  // Create Apollo Gateway with federation v2
  const gateway = new ApolloGateway({
    supergraphSdl: new IntrospectAndCompose({
      subgraphs: services.map(service => ({
        name: service.name,
        url: service.url,
      })),
      subgraphHealthCheck: true,
      pollIntervalInMs: config.federation.pollInterval,
    }),
    buildService({ name, url }) {
      return new RemoteGraphQLDataSource({
        url,
        willSendRequest({ request, context }) {
          // Forward JWT token to subgraphs
          if (context.token) {
            request.http.headers.set('authorization', context.token);
          }
          // Add correlation ID for distributed tracing
          if (context.correlationId) {
            request.http.headers.set('x-correlation-id', context.correlationId);
          }
        },
        didReceiveResponse({ response }) {
          // Log subgraph response time
          const responseTime = response.http.headers.get('x-response-time');
          if (responseTime) {
            logger.debug(`Subgraph response time: ${responseTime}ms`);
          }
          return response;
        },
        didEncounterError({ error, request, response }) {
          logger.error('Subgraph error:', {
            error: error.message,
            request: request.http.url,
            response: response?.http?.status,
          });
        },
      });
    },
    debug: config.isDevelopment,
  });

  // Create Apollo Server
  const server = new ApolloServer({
    gateway,
    csrfPrevention: true,
    cache: 'bounded',
    introspection: config.federation.introspection,
    plugins: [
      ApolloServerPluginDrainHttpServer({ httpServer }),
      ...(config.isDevelopment
        ? [ApolloServerPluginLandingPageLocalDefault({ footer: false })]
        : []),
      QueryComplexityPlugin(config.federation.maxQueryComplexity),
    ],
    formatError: (formattedError, error) => {
      // Log errors
      logger.error('GraphQL Error:', {
        message: formattedError.message,
        path: formattedError.path,
        extensions: formattedError.extensions,
      });

      // Remove stack traces in production
      if (!config.isDevelopment) {
        delete formattedError.extensions?.exception;
      }

      return formattedError;
    },
  });

  await server.start();

  // Apply middleware
  app.use(cors(config.cors));
  app.use(express.json({ limit: config.server.bodyLimit }));

  // Health check endpoints
  app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
  });

  app.get('/ready', async (req, res) => {
    const readiness = await healthCheck.checkReadiness();
    res.status(readiness.ready ? 200 : 503).json(readiness);
  });

  app.get('/metrics', async (req, res) => {
    const metrics = await healthCheck.getMetrics();
    res.json(metrics);
  });

  // GraphQL endpoint with auth and rate limiting
  app.use(
    config.server.graphqlPath,
    authMiddleware,
    createRateLimiter(config.rateLimit),
    expressMiddleware(server, {
      context: async ({ req }) => ({
        token: req.headers.authorization,
        user: (req as any).user,
        correlationId: req.headers['x-correlation-id'] || generateCorrelationId(),
      }),
    })
  );

  httpServer.listen(config.server.port, () => {
    logger.info(`🚀 Apollo Federation Gateway ready at http://localhost:${config.server.port}${config.server.graphqlPath}`);
    logger.info(`🔍 GraphQL Playground available at http://localhost:${config.server.port}${config.server.graphqlPath}`);
    logger.info(`📊 Health check available at http://localhost:${config.server.port}/health`);
    logger.info(`✅ Ready check available at http://localhost:${config.server.port}/ready`);
    logger.info(`📈 Metrics available at http://localhost:${config.server.port}/metrics`);

    // Log discovered services
    logger.info('Federated services:', services.map(s => s.name).join(', '));
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    logger.info('SIGTERM signal received: closing HTTP server');
    await server.stop();
    httpServer.close(() => {
      logger.info('HTTP server closed');
      process.exit(0);
    });
  });
}

function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Start the server
startServer().catch(error => {
  logger.error('Failed to start server:', error);
  process.exit(1);
});