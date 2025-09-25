<!--
Explainer: Security incident runbook for suspected compromise, data leakage,
or unauthorized access attempts.
-->

## Security Incident Runbook

### Triage
- [ ] Classify severity and scope
- [ ] Preserve logs and evidence (forensics)
- [ ] Rotate exposed credentials

### Containment
- [ ] Isolate affected workloads/accounts
- [ ] Block malicious IPs/users
- [ ] Disable compromised access paths

### Eradication & Recovery
- [ ] Patch vulnerabilities
- [ ] Restore from trusted backups
- [ ] Re-enable services with increased monitoring

### Communication
- [ ] Notify stakeholders per policy
- [ ] File incident issue with restricted visibility

### Post-Incident
- [ ] Postmortem with action items
- [ ] Update runbooks and controls

### References
- Security module: `plasma-engine-infra/infra/terraform/modules/security`

