# Release Checklist

Purpose: Ensure safe, compliant releases across all services.

## Preflight
- [ ] Changelog updated and reviewed
- [ ] Version bump committed and tagged
- [ ] Tests green; coverage thresholds met
- [ ] Security scans triaged; no criticals

## Approvals
- [ ] Product owner sign-off
- [ ] Infra approval for Terraform plans
- [ ] Security review (as needed)

## Execution
- [ ] Staging deploy validated
- [ ] Production deploy approved and executed
- [ ] Post-deploy monitoring window observed

## Post-Release
- [ ] Close related tickets and update docs
- [ ] Announce release notes
- [ ] Schedule post-release follow-up

References
- docs/devops/runbooks/deployments.md
- ci/deploy.yaml

# TODO: Map to GitHub environment rules and approvers.