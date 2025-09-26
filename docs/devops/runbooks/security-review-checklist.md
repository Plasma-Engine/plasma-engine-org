### Security Review Checklist

This checklist is used for feature/release reviews to manage security risk and compliance.

#### Design & Data
- [ ] Threat model updated; trust boundaries identified
- [ ] Data classification and privacy impact assessed

#### Code & Dependencies
- [ ] SAST and SCA passed with no criticals
- [ ] Secrets scanning clean; SBOM attached

#### Infrastructure & Access
- [ ] IaC plan reviewed; least privilege enforced
- [ ] Network ingress/egress and encryption verified

#### Operations
- [ ] Logging/metrics/traces adequate for audit and forensics
- [ ] Runbooks updated; on-call aware

#### References
- AICPA SOC 2 TSC — https://www.aicpa-cima.com/resources/article/trust-services-criteria-for-security-availability-processing-integrity-confidentiality-privacy
- CIS Benchmarks (Kubernetes) — https://www.cisecurity.org/benchmark/kubernetes

#### TODOs (org-specific)
- TODO: Add approvers and required artifacts per change type
- TODO: Link to exception process and risk acceptance policy