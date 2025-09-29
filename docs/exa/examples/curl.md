# Exa curl Example (Stub)

```bash
# TODO: Validate base URL and parameters via Rube MCP before use
curl -sS -H "Authorization: Bearer $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"plasma engine exa","limit":10}' \
  https://api.exa.example.com/v1/search
```