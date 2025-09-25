# Plasma Engine Issue Template

## Issue Metadata
```yaml
ticket_id: PE-XXX
service: [gateway|research|brand|content|agent|shared|infra]
type: [feature|bug|task|spike|adr]
priority: [P0-critical|P1-high|P2-medium|P3-low]
sprint: [1|2|3|4]
points: [1|2|3|5|8|13]
```

## Issue Title Format
`[SERVICE-TYPE] Brief description (PE-XXX)`

Example: `[Gateway-Feature] Implement JWT authentication middleware (PE-101)`

## Issue Body Template

### Summary
Brief description of what needs to be done and why.

### Acceptance Criteria
- [ ] Specific, measurable outcome 1
- [ ] Specific, measurable outcome 2
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and approved

### Technical Details
```
Provide implementation details, API contracts, schemas, etc.
```

### Dependencies
- Blocked by: [PE-XXX]
- Blocks: [PE-YYY]
- Related to: [PE-ZZZ]

### Implementation Notes
Any additional context, design decisions, or technical considerations.

### Definition of Done
- [ ] Code complete and follows style guide
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] PR approved by CODEOWNERS
- [ ] CodeRabbit review passed
- [ ] Deployed to staging
- [ ] Smoke tests passing

### Resources
- Design doc: [link]
- API spec: [link]
- Related PRs: [link]

---

## Issue Types

### Feature
New functionality or capability being added to the system.

### Bug
Something that is broken and needs to be fixed.

### Task
Work that needs to be done but doesn't add new functionality (refactoring, documentation, etc.).

### Spike
Research or investigation to answer questions or reduce uncertainty.

### ADR
Architecture Decision Record for significant technical decisions.

## Priority Levels

- **P0 (Critical)**: System down, data loss, security vulnerability
- **P1 (High)**: Core functionality broken, blocking other work
- **P2 (Medium)**: Important but not blocking, workarounds exist
- **P3 (Low)**: Nice to have, minor improvements

## Story Points

- **1 point**: Trivial change, < 2 hours
- **2 points**: Simple task, < 1 day
- **3 points**: Standard task, 1-2 days
- **5 points**: Complex task, 2-3 days
- **8 points**: Very complex, 3-5 days
- **13 points**: Should be broken down into smaller tasks