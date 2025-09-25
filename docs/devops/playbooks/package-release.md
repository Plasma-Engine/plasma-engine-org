# Playbook: Package & Release

Purpose: Package artifacts and create releases with changelogs.

Checklist:
- [ ] CI green on main
- [ ] Semver chosen and changelog updated
- [ ] Images built and signed

Commands (examples):
```bash
# Tag
git tag vX.Y.Z && git push origin vX.Y.Z

# Build/push image (example)
docker build -t ghcr.io/<org>/<name>:vX.Y.Z .
docker push ghcr.io/<org>/<name>:vX.Y.Z
```

TODO: Add provenance/signing (cosign) and SBOM generation.