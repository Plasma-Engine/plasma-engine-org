### Code Playbook

This playbook covers coding standards, branching, reviews, and developer workflows.

#### Objectives
- Maintain code quality and security with fast feedback.
- Standardize branching, PR review, and CI hooks.

#### Practices
- Use trunk-based development with short-lived branches and required reviews.
  - Source: DORA capabilities on CI/CD: https://cloud.google.com/architecture/devops
- Enforce secure coding, secrets management, and dependency hygiene.
  - Source: AWS Well-Architected Security pillar: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html
- Define CODEOWNERS and automated reviewers. Require tests and security scans.

#### Checklist
- Branch named per convention; linked issue
- PR includes tests, docs, ADR impact
- Lint, unit tests, SCA/SAST pass
- Sensitive data policies followed

#### Metrics
- PR lead time, review latency
- Lint/test failure rates

#### TODOs (org-specific)
- TODO: Link to repo-specific coding standards
- TODO: Link to secrets policy and tooling
- TODO: Add CI status checks list