# Exa Authentication (Stub)

Purpose: Document auth flows to interact with Exa APIs.

## Token Management
- Obtain API keys from Exa console
- Store keys in CI secrets or local env (.env)

## HTTP Usage
- Include Authorization header: `Bearer <token>`
- Content-Type: application/json unless otherwise specified

# TODO: Validate exact header names, scopes, and rate limits via Rube MCP.