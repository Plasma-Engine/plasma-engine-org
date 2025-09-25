### Exa integration gaps and follow-ups

- OpenAPI schema: Could not retrieve a canonical `openapi.{yaml|json}` from `exa-labs/openapi-spec` in this environment. Action: fetch and pin commit SHA; store under `third_party/exa/`.
- REST endpoints: Upstream pages `docs.exa.ai/api` returned 404 via mirror. Action: enumerate official endpoints and parameters from the reference site; update quick-reference.
- SDK package names: Confirm Python (`exa-py`?) and JS package (`exa` vs `exa-js`) names and import paths.
- Rate limits: Document per-plan quotas and burst behavior; add guidance on backoff and idempotency.
- Authentication: Confirm if header is standard Bearer token or `x-api-key`; document both if supported.
- Error model: Capture error payload schema and common HTTP status codes.
- Pagination and filtering: Document pagination tokens/limits; include examples.
- Webhook/callbacks: Verify if Exa supports async jobs or webhooks.

When resolved, update `docs/exa/quick-reference.md` and attach sources to `docs/exa/raw/`.

