<!--
Explainer: CI directory documents reusable workflows and expected environment usage
across build/test/security/package/deploy/rollback stages.
-->

## Workflows (reusable)

- `.github/workflows/python-ci.yml`
- `.github/workflows/node-ci.yml`
- `.github/workflows/terraform-ci.yml`
- `.github/workflows/security-scan.yml`
- `.github/workflows/build-and-push.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/rollback.yml`

## Usage (service repo example)

```yaml
jobs:
  python:
    uses: Plasma-Engine/plasma-engine-org/.github/workflows/python-ci.yml@main
    with:
      working-directory: plasma-engine-brand
```

# TODO: Add end-to-end pipeline example chaining build → deploy with environments.

