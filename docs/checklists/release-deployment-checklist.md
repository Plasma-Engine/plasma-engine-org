### Release & Deployment Checklist

- [ ] Release notes drafted (scope, risks, rollback plan)
- [ ] All CI stages green for the release commit
- [ ] Version tag created and pushed (if required)
- [ ] Staging deploy successful; smoke tests pass
- [ ] Manual approval captured for production (GitHub Environment)
- [ ] Monitoring/alerts quiet and healthy post-deploy window
- [ ] Rollback plan validated; `rollback.md` ready
- [ ] Post-release metrics captured (lead time, change failure rate)

Commands (examples)
```bash
make build-all
make push-all
make tag-release
```

References
- ADR-0003 CI/CD bootstrap
- Runbooks: `docs/runbooks/rollback.md`

