# Security & Compliance Standards

This document defines mandatory security controls, scans, and policies across all repositories. It complements `SECURITY.md` and is enforced via CI as required checks.

## Benchmarks & Frameworks
- OWASP ASVS: Application security verification baseline
- NIST SSDF (SP 800-218): Secure Software Development Framework
- CIS Benchmarks: Container/Kubernetes hardening
- SLSA: Supply chain levels for artifacts and provenance

## Mandatory Scans (CI)
- SAST:
  - CodeQL (GitHub): language-specific code scanning
  - Semgrep (rules: owasp-top-ten, security-audit)
- Dependency:
  - pip-audit (Python), npm audit + `osv-scanner` (Node)
  - Block PRs on High/Critical; Medium allowed only with approved risk acceptance
- Container/Images:
  - Trivy scan on Docker images; block on High/Critical
- Secrets:
  - GitHub Secret Scanning + TruffleHog pre-commit optional
- SBOM:
  - Syft generate SBOM (SPDX or CycloneDX) and attach to releases

## Policies & Gates
- No hardcoded secrets; pre-commit secret detection recommended
- Vulnerability thresholds:
  - Critical: block; fix before merge
  - High: block; fix or explicitly accept with issue and SLA
  - Medium: allowed with ticket and plan; fix within 2 sprints
  - Low: track for backlog
- CVE Remediation SLAs:
  - Critical: 24–72 hours
  - High: 7 days
  - Medium: 30 days
  - Low: best effort

## Dependency Management
- Use Renovate or Dependabot for weekly batched updates
- Pin direct dependencies; allow caret ranges only for tools
- Disallow risky licenses in production (GPL-3.0-only without exceptions); approve via security review

## Supply Chain Security
- Verify checksums/signatures for critical tools
- Use provenance (SLSA) for release artifacts when available
- Use minimal base images; run as non-root; enable seccomp/apparmor profiles

## Runtime Security
- Enforce security headers (see `SECURITY.md`)
- TLS everywhere; rotate keys regularly
- Centralized authn/z; short-lived tokens; least privilege RBAC

## Example CI Snippets
```yaml
jobs:
  security:
    steps:
      - uses: actions/checkout@v4

      # CodeQL (GitHub-native setup required in repo settings)
      - uses: github/codeql-action/init@v3
        with: { languages: 'python,javascript' }
      - uses: github/codeql-action/analyze@v3

      # Semgrep
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >
            p/owasp-top-ten
            p/semgrep-rule-stats

      # Dependencies
      - name: pip-audit
        run: pip install pip-audit && pip-audit
      - name: npm audit
        run: npm ci && npm audit --audit-level=high || true
      - name: osv-scanner
        uses: google/osv-scanner-action@v1

      # Container image scan (if image produced)
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/plasma-engine/${{ github.event.repository.name }}:pr-${{ github.run_id }}
          severity: CRITICAL,HIGH

      # SBOM
      - name: Syft SBOM
        uses: anchore/sbom-action@v0
        with:
          format: cyclonedx-json
```

## Documentation & Exceptions
- All exceptions require: risk description, compensating controls, remediation plan, owner, and SLA
- Track exceptions via GitHub Issues labeled `risk-accepted`