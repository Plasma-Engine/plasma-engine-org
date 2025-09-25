### Runbook: Terraform Plan & Apply

Intent: Safely plan and apply infrastructure changes with approvals.

Pre-reqs
- Backend state configured; environment variables/secrets set in CI or local shell.

Steps
1) Format and validate
```bash
terraform fmt -recursive
terraform validate
```
2) Plan for the target workspace/environment
```bash
terraform workspace select dev || terraform workspace new dev
terraform plan -input=false -no-color -out=plan.out | cat
```
3) Review plan with approvers and capture approval in Issue/PR.
4) Apply in controlled window
```bash
terraform apply -input=false -auto-approve plan.out
```
5) Post-apply verification and drift checks.

Notes
- Use GitHub Environments for manual approvals when running in Actions.
- Record change summary and link to runbook in PR description.

References
- Infra repo `plasma-engine-infra/infra/terraform/`
- ADR-0003 CI/CD bootstrap (terraform.yml reusable workflow)
- Exa: exa://plasma-engine/terraform-operations

