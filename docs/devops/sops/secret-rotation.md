### SOP: Secret Rotation

Scope: Rotate API keys and credentials (e.g., Exa token).

Steps:
1. Generate new secret in provider console (or via CLI).
2. Store in secrets manager (# TODO: select provider; e.g., AWS Secrets Manager/Vault).
3. Update GitHub environment/Org secret names (do not commit secrets).
4. Redeploy dependent services; verify access.

References:
- `config/rube/mcp-config.template.json`
- docs/exa/auth.md

Checklist:
- [ ] New secret created and documented
- [ ] Secret stored in manager and permissions validated
- [ ] CI/CD and runtime access verified

