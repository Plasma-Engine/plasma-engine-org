### Build Playbook

This playbook standardizes build automation, artifact management, and SBOM/security gates.

#### Objectives
- Reproducible, cacheable builds with provenance and SBOMs.
- Fast feedback via incremental and parallelized builds.

#### Practices
- Use build caching and CI matrix to parallelize.
- Publish artifacts to a trusted registry; sign images.
  - Source: AWS Well-Architected Operational Excellence: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html
- Generate SBOMs and run SCA/SAST; block on critical vulns.
  - Source: CNCF TAG Security supply chain guidance: https://github.com/cncf/tag-security/blob/main/supply-chain-security/whitepaper/README.md

#### Checklist
- Versioned build outputs with provenance
- SBOM generated and stored
- Image signed (e.g., Sigstore)
- Vulnerability scans passed

#### Metrics
- Build duration, cache hit rate
- Security scan pass/fail trends

#### TODOs (org-specific)
- TODO: Link to registry naming scheme and retention policy
- TODO: Specify SBOM tool(s) and storage location