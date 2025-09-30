# Plasma Engine GraphQL Federation Gateway

Apollo Federation Gateway for the Plasma Engine platform, providing unified GraphQL API access to all microservices.

## Features

- **Apollo Federation v2**: Modern GraphQL federation with subgraph composition
- **Service Discovery**: Automatic discovery and registration of federated services
- **JWT Authentication**: Secure authentication with Auth0/Clerk integration
- **Rate Limiting**: Tiered rate limiting based on user roles
- **Query Complexity Analysis**: Prevent expensive queries from overwhelming the system
- **Health Monitoring**: Built-in health checks for gateway and subgraphs
- **Distributed Tracing**: Correlation IDs for request tracking across services
- **Redis Caching**: Performance optimization with Redis cache layer
- **TypeScript**: Fully typed for better developer experience

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Clients   │────▶│   Gateway   │────▶│    Redis    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌────────────┐    ┌────────────┐    ┌────────────┐
│  Research  │    │  Content   │    │   Brand    │
│  Service   │    │  Service   │    │  Service   │
└────────────┘    └────────────┘    └────────────┘
```

## Prerequisites

- Node.js 18+
- Redis 6+
- Docker and Docker Compose (optional)

## Quick Start

### Local Development

1. **Clone and install dependencies:**
```bash
cd plasma-engine-gateway
npm install
```

2. **Configure environment:**
```bash
cp .env.template .env
# Edit .env with your configuration
```

3. **Start Redis:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

4. **Run the gateway:**
```bash
npm run dev
```

5. **Access GraphQL Playground:**
```
http://localhost:4000/graphql
```

### Docker Compose

```bash
docker-compose up
```

This starts the gateway with Redis and mock services for testing.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `4000` |
| `NODE_ENV` | Environment (development/production) | `development` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `JWKS_URI` | JWT public key endpoint | Required |
| `JWT_AUDIENCE` | Expected JWT audience | Required |
| `JWT_ISSUER` | Expected JWT issuer | Required |
| `RESEARCH_SERVICE_URL` | Research service GraphQL endpoint | `http://localhost:4001/graphql` |
| `CONTENT_SERVICE_URL` | Content service GraphQL endpoint | `http://localhost:4002/graphql` |
| `BRAND_SERVICE_URL` | Brand service GraphQL endpoint | `http://localhost:4003/graphql` |

See `.env.template` for complete configuration options.

### Service Registration

Services can be registered in two ways:

1. **Static Configuration**: Define services in environment variables
2. **Dynamic Discovery**: Enable auto-discovery with `ENABLE_AUTO_DISCOVERY=true`

## API Endpoints

### GraphQL
- `POST /graphql` - Main GraphQL endpoint

### Health & Monitoring
- `GET /health` - Basic health check
- `GET /ready` - Readiness check with subgraph status
- `GET /metrics` - Prometheus-compatible metrics

## Authentication

The gateway supports two authentication methods:

### 1. JWT Token
Include the JWT token in the Authorization header:
```http
Authorization: Bearer <jwt-token>
```

### 2. API Key
Include the API key in the X-Api-Key header:
```http
X-Api-Key: <api-key>
```

## Rate Limiting

Rate limits are tiered based on user roles:

| Role | Requests per Minute |
|------|-------------------|
| Admin | 1000 |
| Premium | 500 |
| Authenticated | 100 |
| Anonymous | 30 |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Query Complexity

Queries are analyzed for complexity to prevent abuse. Default maximum complexity is 1000 points.

Complexity factors:
- Each field: 1 point
- Arguments: 0.5 points each
- List fields: 10x multiplier
- Depth penalty: 2 points per level
- Expensive fields: 5x multiplier

## Development

### Scripts

```bash
# Development with hot reload
npm run dev

# Build TypeScript
npm run build

# Production start
npm start

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### Adding a New Subgraph

1. Define the service URL in `.env`:
```env
NEW_SERVICE_URL=http://localhost:4005/graphql
NEW_SERVICE_HEALTH_URL=http://localhost:4005/health
ENABLE_NEW_SERVICE=true
```

2. Update the configuration in `src/config/index.ts`:
```typescript
{
  name: 'new-service',
  url: process.env.NEW_SERVICE_URL || 'http://localhost:4005/graphql',
  healthUrl: process.env.NEW_SERVICE_HEALTH_URL || 'http://localhost:4005/health',
}
```

3. Restart the gateway

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### Load Testing
```bash
npm run test:load
```

## Deployment

### Docker

Build and run with Docker:
```bash
docker build -t plasma-gateway .
docker run -p 4000:4000 --env-file .env plasma-gateway
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests.

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Configure proper JWT keys and audience
- [ ] Set up Redis with persistence
- [ ] Configure rate limiting appropriate for load
- [ ] Enable monitoring (Sentry, OpenTelemetry)
- [ ] Set up health check monitoring
- [ ] Configure CORS for production domains
- [ ] Disable GraphQL introspection (`ENABLE_INTROSPECTION=false`)
- [ ] Set appropriate query complexity limits

## Monitoring

### Metrics Exposed

- Request count and latency
- Subgraph health status
- Query complexity distribution
- Rate limit violations
- Authentication failures
- Memory usage

### Logging

Structured JSON logging with Pino. Log levels:
- `trace`: Very detailed debugging
- `debug`: Debugging information
- `info`: General information
- `warn`: Warning messages
- `error`: Error messages
- `fatal`: Fatal errors

## Troubleshooting

### Gateway won't start
- Check Redis connection
- Verify all required environment variables
- Check subgraph health endpoints

### Authentication errors
- Verify JWKS_URI is accessible
- Check JWT audience and issuer match
- Ensure token hasn't expired

### Subgraph connection issues
- Verify service URLs are correct
- Check network connectivity
- Review subgraph health status at `/ready`

## Security

### Best Practices

1. Always use HTTPS in production
2. Rotate API keys regularly
3. Monitor rate limit violations
4. Implement query whitelisting for production
5. Use Redis ACLs for additional security
6. Regular security audits of dependencies

### Reporting Issues

Report security issues to: security@plasma-engine.com

## License

Copyright © 2025 Plasma Engine. All rights reserved.