<!--
Explainer: Standard release checklist. Copy into each service repo as needed.
Include references to reusable workflows and gates.
-->

## Release Checklist

- [ ] Version bump committed and tagged
- [ ] CI: Lint/Test/Build/Security all green on tag
- [ ] SBOM generated and archived
- [ ] Artifacts published to `ghcr.io/plasma-engine/*`
- [ ] Staging deploy verified (smoke tests, SLOs met)
- [ ] Production approval recorded in GitHub Environments
- [ ] Production deploy verified (dashboards/alerts quiet)
- [ ] Rollback plan validated (dry-run)
- [ ] Post-release monitoring window assigned

# TODO: Link service-specific health checks and dashboards.

