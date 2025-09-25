### Exa Authentication

Overview:
- API Key-based authentication with bearer tokens.
- Token scopes determine access to search, retrieval, and analytics endpoints.

Flow:
1. Obtain API key from Exa console.
2. Send requests with `Authorization: Bearer <token>` header.
3. Rotate keys regularly; store secrets in the configured secrets manager.

Example header:
```
Authorization: Bearer EXA_TOKEN_PLACEHOLDER
```

# TODO: Replace with exact Exa auth specification via Rube MCP.

