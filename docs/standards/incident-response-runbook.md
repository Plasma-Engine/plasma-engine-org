# Incident Response Runbook

This runbook defines the end-to-end process for handling security incidents. It complements `SECURITY.md` and aligns with NIST SP 800-61 rev.2 and OWASP recommendations.

## Roles
- Incident Commander (IC): Overall coordination and decision maker
- Comms Lead: Stakeholder and customer communications
- Technical Lead: Investigation, containment, eradication
- Scribe: Timeline, artifacts, evidence tracking
- Legal/Privacy (as needed): Compliance and disclosure

## Severity Levels & SLAs
- Critical: Immediate response; patch ≤ 24 hours; notify stakeholders within 4 hours
- High: Response ≤ 24 hours; patch ≤ 7 days
- Medium: Response ≤ 3 days; patch ≤ 30 days
- Low: Best effort

## Lifecycle (NIST 800-61)
1. Preparation: tooling, playbooks, access, contacts, runbooks
2. Detection & Analysis: triage alerts, validate indicators of compromise (IOCs)
3. Containment: short-term isolation, feature flags, traffic blocks
4. Eradication: remove artifacts, patch vulnerabilities, rotate secrets
5. Recovery: restore services, increased monitoring, validate normal ops
6. Post-Incident Activity: lessons learned, postmortem, follow-up actions

## Triage Checklist
- What systems are impacted? Scope blast radius
- What data is at risk? PII/PHI/PCI?
- Active exploitation in progress?
- Initial vector known? (vuln, secret leak, phishing)
- Required notifications? (legal, customers, regulators)

## Communication
- Internal: Slack `#incident-[date]-[shortname]`, executive channel updates
- External: Status page, customer email templates, regulatory notices
- Cadence: Critical incidents update at least hourly until contained

## Evidence Handling
- Preserve logs, traces, configs, and artifacts with timestamps
- Copy disk images or containers if necessary; maintain chain of custody
- Avoid altering evidence on live systems unless necessary for containment

## Containment Options
- Block IPs or ranges at WAF/firewall
- Disable affected credentials; rotate all secrets
- Scale down or isolate affected workloads/namespaces
- Enable feature flags to disable vulnerable endpoints or flows

## Remediation
- Patch vulnerable components
- Add/adjust WAF rules and rate limits
- Harden configurations per CIS benchmarks
- Add tests to prevent regression (unit/integration/e2e)

## Recovery
- Gradually restore traffic; use canary and increased logging
- Monitor error rates, latencies, and security events closely for 24–72 hours

## Postmortem Template
```
Title: [YYYY-MM-DD] <short description>
Summary: <what happened>
Timeline: <key events with timestamps>
Root Cause: <technical and organizational>
Impact: <systems, customers, data>
Detection: <how discovered>
Response: <what worked, what didn’t>
Remediation: <fixes applied>
Follow-ups: <tickets with owners and deadlines>
Lessons Learned: <prevention and improvements>
```

## Tooling
- Monitoring/Alerting: Prometheus, Grafana, OpenTelemetry, SIEM (if available)
- Forensics: Cloud provider snapshots, container image digests, access logs
- Communication: Status page, email lists, incident channels, on-call rotation

## Escalation & Notification Matrix
- Security: security@plasma-engine.org (see `SECURITY.md`)
- Engineering On-Call: rotation documented in runbook appendix
- Legal/Privacy: per-company contacts

## Readiness Drills
- Quarterly incident response tabletop exercises
- Annual red team or third-party penetration tests
- Monthly review of contact lists and playbooks