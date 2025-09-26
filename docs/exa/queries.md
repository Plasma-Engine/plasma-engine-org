### Exa Query Syntax (Quick Reference)

Common request structure for search queries.

#### JSON Request (example)
```json
{
  "query": "site:sre.google SLO burn rate",
  "numResults": 10,
  "includeDomains": ["sre.google", "cloud.google.com"],
  "excludeDomains": ["example.com"],
  "dateRange": { "from": "2024-01-01", "to": "2025-09-25" },
  "useAutoprompt": true
}
```

#### HTTP Example
```http
POST /search HTTP/1.1
Host: api.exa.ai
Authorization: Bearer EXA_API_KEY
Content-Type: application/json

{"query":"kubernetes pod disruption budget","numResults":5}
```

Reference: https://docs.exa.ai/reference

#### TODOs (org-specific)
- TODO: Add standard filters (allowed domains) for our org
- TODO: Document pagination/concurrency strategy