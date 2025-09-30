### Terraform Playbook

Purpose: Standardize how we manage IaC using Terraform across environments.

Conventions:
- Remote state: configure per environment with locking (# TODO: choose backend)
- Providers: avoid credentials in code; prefer OIDC and env vars
- Modules: keep provider-agnostic scaffolds; wrap upstream modules when possible

Commands:
- Init: `terraform init -input=false`
- Validate: `terraform validate`
- Plan: `terraform plan -input=false -out=tfplan`
- Apply: `terraform apply -input=false tfplan`

References:
- `infra/terraform/README.md`
- HashiCorp Terraform docs (`https://developer.hashicorp.com/terraform`)

Checklist:
- [ ] Backend configured with locking
- [ ] Providers pinned; credentials via OIDC/env
- [ ] Plans reviewed and approved
- [ ] Post-apply verification documented

