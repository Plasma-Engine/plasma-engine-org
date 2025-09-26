### Backup & Restore Runbook

This runbook documents backup schedules, storage, and verified restore procedures.

#### Scope
- Databases, object storage, and critical configuration/state

#### Backup Policy
- Frequency and retention per data classification
- Encrypted at rest and in transit; tested restores
- Immutable backups and offsite replication for DR

#### Restore Procedure
1) Assess RPO/RTO and select restore point
2) Verify backup integrity (hashes/manifest)
3) Restore to staging and validate application-level consistency
4) Coordinate maintenance window; restore to production
5) Post-restore verification: checksums, app health, data correctness

#### Verification
- Health checks pass; no data anomalies in sampling
- Users confirm recovery of impacted functions

#### References
- AWS Well-Architected Reliability Pillar — Backup and Restore: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html

#### TODOs (org-specific)
- TODO: Link to backup schedules, storage locations, encryption keys custody
- TODO: Define verification queries and app-level data checks