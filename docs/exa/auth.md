# Exa Authentication

Use API key via `Authorization: Bearer <EXA_API_KEY>` header.

Example curl:
```bash
curl -sS \
  -H "Authorization: Bearer $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.exa.ai/v1/health
```

TODO: Verify base URL and endpoints via MCP.