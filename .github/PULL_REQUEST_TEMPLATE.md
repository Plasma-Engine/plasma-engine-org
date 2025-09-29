## Summary

Brief description of what this PR does and why.

**Type of Change:**
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration/build changes
- [ ] 🧪 Test improvements
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡️ Performance improvement

## What's Changed

### Added
- List new features or functionality

### Changed
- List changes to existing functionality

### Fixed
- List bug fixes

### Removed
- List removed features or functionality

## Related Issues

Closes #(issue number)
Relates to #(issue number)

## Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

### Test Details
Describe the tests that ran to verify your changes. Provide instructions so reviewers can reproduce.

**Test Configuration:**
- OS: [e.g., macOS, Ubuntu]
- Python version: [e.g., 3.11]
- Node.js version: [e.g., 22]

**Services Affected:**
- [ ] Gateway
- [ ] Research
- [ ] Brand
- [ ] Content
- [ ] Agent
- [ ] Infrastructure

## Screenshots (if applicable)

Include screenshots, GIFs, or videos demonstrating the changes.

## Performance Impact

### Benchmarks
- [ ] Performance tests run
- [ ] No significant performance regression
- [ ] Performance improvement measured

**Details:** Include any performance metrics, before/after comparisons.

## Security Considerations

- [ ] Security implications reviewed
- [ ] No sensitive data exposed
- [ ] Authentication/authorization properly implemented
- [ ] Input validation added where needed
- [ ] Dependencies checked for vulnerabilities

## Database Changes

- [ ] No database changes
- [ ] Migration scripts provided
- [ ] Backward compatible
- [ ] Data loss risk assessed

**Migration Details:** Describe any database schema changes.

## Breaking Changes

**⚠️ List any breaking changes and migration guide:**

1. Change description
   - Before: `old behavior`
   - After: `new behavior`
   - Migration: Steps to update existing code

## Configuration Changes

- [ ] No configuration changes
- [ ] Environment variables added/changed
- [ ] Configuration files updated
- [ ] Documentation updated

**New Environment Variables:**
```env
NEW_VAR=default_value  # Description of what this does
```

## Documentation

- [ ] Code is self-documenting
- [ ] Docstrings added/updated
- [ ] API documentation updated
- [ ] README updated
- [ ] CHANGELOG updated

## Dependencies

### Added Dependencies
- `package-name@version` - Brief explanation why this was added

### Updated Dependencies
- `package-name` from `old-version` to `new-version` - Reason for update

### Security Updates
- [ ] All dependencies up to date
- [ ] Security audit passed
- [ ] No known vulnerabilities

## Deployment

### Deployment Requirements
- [ ] No special deployment requirements
- [ ] Requires database migration
- [ ] Requires environment variable updates
- [ ] Requires infrastructure changes

### Rollback Plan
Describe how to rollback this change if issues occur in production.

## Review Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] No commented-out code
- [ ] No debug logging left in
- [ ] Error handling implemented appropriately
- [ ] Edge cases considered

### Architecture
- [ ] Changes align with overall architecture
- [ ] No circular dependencies introduced
- [ ] Proper separation of concerns
- [ ] Consistent with existing patterns

### Monitoring
- [ ] Logging added for troubleshooting
- [ ] Metrics/monitoring considered
- [ ] Error tracking implemented
- [ ] Health checks updated if needed

## Reviewer Guidelines

### Focus Areas
Please pay special attention to:
- [ ] Security implications
- [ ] Performance impact
- [ ] Error handling
- [ ] Test coverage
- [ ] Documentation completeness

### Testing Instructions
1. Step-by-step instructions to test the changes
2. Expected behavior
3. Edge cases to verify

## AI Review Summary

*This section will be automatically populated by CodeRabbit AI*

---

## Pre-merge Checklist

**Author Checklist:**
- [ ] All CI checks passing
- [ ] Code reviewed by at least one team member
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No merge conflicts
- [ ] Feature branch up to date with base branch

**Reviewer Checklist:**
- [ ] Code logic reviewed and approved
- [ ] Security considerations reviewed
- [ ] Performance impact acceptable
- [ ] Test coverage adequate
- [ ] Documentation sufficient

**Maintainer Checklist:**
- [ ] All required approvals received
- [ ] No requested changes pending
- [ ] CI/CD pipeline successful
- [ ] Ready for deployment

---

**Note:** Delete sections that don't apply to your PR. This template is designed to be comprehensive - use what makes sense for your specific changes.

/assign @team-member-for-review