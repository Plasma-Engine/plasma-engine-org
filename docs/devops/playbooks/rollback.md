 # Playbook: Rollback

 Audience: Platform/SRE

 Purpose: Rapidly restore service to last known-good.

 Checklist
 - [ ] Identify candidate release
 - [ ] Execute rollback workflow with `environment` and `release_id`
 - [ ] Confirm recovery metrics and alerts clear

 Workflow Links
 - `.github/workflows/reusable-rollback.yml`
 - `ci/actions/rollback/action.yml`


