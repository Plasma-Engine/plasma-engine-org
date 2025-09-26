### Exa Rate Limits (Quick Reference)

Typical default limits apply per account. Handle 429 responses with exponential backoff and jitter.

#### Error Handling Pattern (pseudo)
```json
{
  "status": 429,
  "message": "Rate limit exceeded",
  "retryAfterSeconds": 2
}
```

Guidance:
- Use client-side token bucket or queueing.
- Respect `Retry-After` header when present.

Reference: https://docs.exa.ai/reference/rate-limits

#### TODOs (org-specific)
- TODO: Define max concurrency per service and CI job
- TODO: Centralize backoff policy and telemetry events