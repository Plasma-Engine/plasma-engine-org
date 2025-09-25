 # Playbook: Test

 Audience: Platform/CI Maintainers, Service Owners

 Purpose: Standardize unit test execution for Python/Node services.

 Checklist
 - [ ] Ensure test dependencies are installed
 - [ ] Run unit tests and capture artifacts
 - [ ] Record flaky tests and open issues

 Commands
 - Python: `pytest -q`
 - Node: `vitest run` or `jest --ci`

 Workflow Links
 - `.github/workflows/reusable-test.yml`
 - `ci/actions/test/action.yml`


