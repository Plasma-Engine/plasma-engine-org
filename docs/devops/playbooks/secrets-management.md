<!--
Explainer: Secrets management playbook for local, CI, and runtime. Assumes a
future secrets manager (AWS Secrets Manager, GCP Secret Manager, or Vault).
-->

## Secrets Management Playbook

### Principles
- Do not commit secrets. Use environment injection and sealed stores.
- Rotate regularly; automate via CI workflows and policies.
- Least privilege for apps and humans.

### Local Development
- [ ] Use `.env` (gitignored) or shell exports
- [ ] Document required keys in service READMEs
- [ ] Provide sample `.env.example`

### CI/CD
- [ ] Store secrets in GitHub Environments (staging/prod) or OIDC to cloud
- [ ] Mask logs; prohibit echoing secret values
- [ ] Use short‑lived tokens where possible

### Runtime
- [ ] Retrieve secrets via IAM role/identity
- [ ] Avoid mounting static files; prefer API fetch at startup

### Exa API
- [ ] `EXA_API_KEY` stored in secrets manager and mapped into runtime
- [ ] Local: export var per `docs/exa/auth.md`

### References
- Release checklist: `docs/devops/release/release-checklist.md`
- Security module: `plasma-engine-infra/infra/terraform/modules/security`

