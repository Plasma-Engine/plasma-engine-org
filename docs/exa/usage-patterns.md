### Exa Usage Patterns (Quick Reference)

Concise patterns for common use cases.

#### Pattern: Seed → Expand → Verify
1) Seed: query authoritative domains first
2) Expand: broaden to related domains with filters
3) Verify: cross-check across multiple sources; store attribution

#### Pattern: Caching and Idempotency
- Cache stable results to reduce calls; include query hash keys
- Add idempotency key headers to avoid duplicate work on retries (if supported)

#### Pagination & Concurrency
- Use small pages; pipeline pages with rate-aware concurrency

References
- API Reference: https://docs.exa.ai/reference/overview

#### TODOs (org-specific)
- TODO: Define caching layer and TTLs
- TODO: Add logging fields for attribution and provenance