# Runbook: Rollback Procedure

Triggers:
- KPIs breach SLO
- Elevated error rates sustained > 10 minutes

Decision Matrix:
- App-level rollback to previous image
- Infra-level rollback via Terraform state pinning

Procedure:
1. Identify last known good version/tag.
2. For app: redeploy previous image.
3. For infra: plan against pinned state and apply after approval.
4. Validate smoke tests and KPIs.

TODO: Fill environment-specific commands and approvals.