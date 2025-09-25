 # DevOps Documentation Index

 > This directory centralizes operational guidance, runbooks, playbooks, SOPs, and release procedures for the Plasma Engine platform. All automation in `ci/` and `.github/workflows/` must link back to docs here.

 ## Structure
 - `docs/devops/playbooks/` — prescriptive, step-by-step procedures for specific operations
 - `docs/devops/runbooks/` — on-call and incident response guides
 - `docs/devops/release/` — release checklists and gates
 - `docs/devops/activity-log.md` — chronological build log of major changes, validations, and decisions

 ## Authoring Guidance
 - Begin each file with a short explainer and intended audience
 - Include authoritative references using markdown links
 - Use actionable checkboxes for verification steps
 - Flag open items with `# TODO:` so parallel agents can pick up immediately

 ## Ownership
 - Primary: Platform/DevOps team
 - Reviewers: Security, SRE, Application teams

 ## Links
 - Platform ADRs: `docs/adrs/`
 - Process: `docs/devops-process.md`


