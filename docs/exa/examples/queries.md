<!--
Explainer: Example Exa API queries. Replace endpoints/fields after syncing
with official docs via Rube MCP.
-->

## Example: Search (curl)
```bash
curl -sS \
  -H "Authorization: Bearer $EXA_API_KEY" \
  "https://api.exa.example.invalid/search?q=hello%20world"
```

## Example: Ingest (curl)
```bash
curl -sS -X POST \
  -H "Authorization: Bearer $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/post"}' \
  "https://api.exa.example.invalid/documents"
```

> # TODO: Add Python and TypeScript SDK examples once endpoints are verified.

