### Exa Authentication (Quick Reference)

Use an API key provisioned in Exa. Store secrets in your vault/secrets manager and inject at runtime.

#### HTTP Header
```http
Authorization: Bearer EXA_API_KEY
```

#### Environment Variable
```bash
export EXA_API_KEY="<redacted>"
```

#### Notes
- Rotate keys regularly; scope per environment/service.
- Never commit keys to VCS; use CI secrets.

Reference: https://docs.exa.ai/docs/authentication

#### TODOs (org-specific)
- TODO: Link to secrets manager path and rotation policy
- TODO: Add CI/CD secret names and access policy