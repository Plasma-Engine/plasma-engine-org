import pino from 'pino';
import { config } from '../config';

const logLevel = process.env.LOG_LEVEL || (config.isDevelopment ? 'debug' : 'info');

const pinoOptions: pino.LoggerOptions = {
  level: logLevel,
  timestamp: pino.stdTimeFunctions.isoTime,
  formatters: {
    level: (label) => {
      return { level: label };
    },
  },
  serializers: {
    error: pino.stdSerializers.err,
    req: (req) => ({
      id: req.id,
      method: req.method,
      url: req.url,
      query: req.query,
      params: req.params,
      headers: {
        host: req.headers.host,
        'user-agent': req.headers['user-agent'],
        'x-correlation-id': req.headers['x-correlation-id'],
      },
      remoteAddress: req.ip || req.connection?.remoteAddress,
    }),
    res: (res) => ({
      statusCode: res.statusCode,
      headers: res.getHeaders?.(),
    }),
  },
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      'req.headers["x-api-key"]',
      '*.password',
      '*.token',
      '*.secret',
      '*.apiKey',
      '*.credentials',
    ],
    remove: true,
  },
};

// Use pretty printing in development
const transport = config.isDevelopment
  ? pino.transport({
      target: 'pino-pretty',
      options: {
        colorize: true,
        ignore: 'pid,hostname',
        translateTime: 'HH:MM:ss.l',
        singleLine: false,
      },
    })
  : undefined;

export const logger = pino(pinoOptions, transport);

// Create child loggers for specific modules
export const createLogger = (module: string) => {
  return logger.child({ module });
};

// Request logger middleware
export const requestLogger = (req: any, res: any, next: any) => {
  const start = Date.now();
  const requestId = generateRequestId();

  req.id = requestId;
  req.log = logger.child({ requestId });

  req.log.info({ req }, 'Request received');

  res.on('finish', () => {
    const duration = Date.now() - start;

    const logData = {
      req,
      res,
      duration,
      responseTime: `${duration}ms`,
    };

    if (res.statusCode >= 400) {
      req.log.error(logData, 'Request failed');
    } else {
      req.log.info(logData, 'Request completed');
    }
  });

  next();
};

// GraphQL operation logger
export const graphqlLogger = {
  requestDidStart() {
    const requestStartTime = Date.now();

    return {
      async didResolveOperation(requestContext: any) {
        logger.debug('GraphQL operation resolved', {
          operationName: requestContext.request.operationName,
          query: requestContext.request.query,
          variables: requestContext.request.variables,
        });
      },

      async didEncounterErrors(requestContext: any) {
        logger.error('GraphQL errors encountered', {
          operationName: requestContext.request.operationName,
          errors: requestContext.errors,
        });
      },

      async willSendResponse(requestContext: any) {
        const duration = Date.now() - requestStartTime;

        const logData = {
          operationName: requestContext.request.operationName,
          duration,
          responseTime: `${duration}ms`,
          errors: requestContext.errors,
        };

        if (requestContext.errors && requestContext.errors.length > 0) {
          logger.error(logData, 'GraphQL operation failed');
        } else {
          logger.info(logData, 'GraphQL operation completed');
        }
      },
    };
  },
};

// Error logger
export const logError = (error: Error, context?: any) => {
  logger.error(
    {
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name,
      },
      context,
    },
    'Error occurred'
  );
};

// Audit logger for sensitive operations
export const auditLog = (action: string, userId: string, details: any) => {
  logger.info(
    {
      audit: true,
      action,
      userId,
      details,
      timestamp: new Date().toISOString(),
    },
    `Audit: ${action}`
  );
};

// Performance logger
export const perfLog = (operation: string, duration: number, metadata?: any) => {
  const level = duration > 1000 ? 'warn' : 'debug';

  logger[level](
    {
      performance: true,
      operation,
      duration,
      durationMs: `${duration}ms`,
      metadata,
    },
    `Performance: ${operation}`
  );
};

// Helper function to generate request IDs
function generateRequestId(): string {
  return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Export log levels for configuration
export const LogLevels = {
  TRACE: 'trace',
  DEBUG: 'debug',
  INFO: 'info',
  WARN: 'warn',
  ERROR: 'error',
  FATAL: 'fatal',
} as const;

// Utility to check if logging is enabled for a level
export const isLogLevelEnabled = (level: keyof typeof LogLevels): boolean => {
  const levels = ['trace', 'debug', 'info', 'warn', 'error', 'fatal'];
  const currentLevelIndex = levels.indexOf(logger.level);
  const checkLevelIndex = levels.indexOf(LogLevels[level]);
  return checkLevelIndex >= currentLevelIndex;
};