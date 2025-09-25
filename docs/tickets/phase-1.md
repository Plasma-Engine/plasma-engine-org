# Phase 1 Ticket Backlog — Automation Streams

> Follows the plasma issue template. Tickets are sequenced for Sprint 1 & Sprint 2 delivery with explicit Always Works™ validation. Move top-level epics into the GitHub Project `Plasma Engine – Automation Streams`.

## PE-101 — Seed Plasma Writing Corpus & Embedding Index
- **Repository**: `plasma-engine-content`
- **Type**: Feature
- **Milestone**: Sprint 1
- **Objective**: Aggregate historic Plasma content and produce an embedding-backed tone library for downstream LinkedIn/X automation.
- **Scope**:
  - In Scope: Beehiiv export, Google Doc parsing, R2 storage, embedding generation using `text-embedding-3-large`.
  - Out of Scope: Scheduler automation, post publishing.
- **Implementation Plan**:
  1. ETL Beehiiv archive via authenticated API; normalize sections/metadata.
  2. Parse Plasma tone guide Google Doc → YAML trait sheet.
  3. Generate embeddings with OpenAI `text-embedding-3-large`; store in Qdrant/Weaviate cluster.
  4. Persist corpus manifest in Cloudflare R2 with versioning; expose retrieval helper module.
  5. Document prompt cookbook referencing tone traits.
- **Validation (Always Works™)**:
  - [ ] `poetry run pytest tests/embeddings` covering vector store writes/reads.
  - [ ] Lint: `ruff check .` / `prettier --check prompts/`.
  - [ ] Manual: Query API endpoint for keyword → verify top-5 tone matches; screenshot stored in ticket.
  - [ ] Monitoring: Ensure vector DB health metrics scraped by Prometheus.
  - [ ] Rollback: R2 manifest retains previous version; revert pointer to prior corpus.
- **Definition of Done**:
  - Corpus + embeddings in staging; README updated with retrieval instructions.
  - Prompt cookbook merged under `docs/prompts/content.md`.

## PE-102 — Policy-Aware LinkedIn/X Scheduler with Manual Approval
- **Repository**: `plasma-engine-content`
- **Type**: Feature
- **Milestone**: Sprint 1
- **Objective**: Adapt ReplyGuy automation to Plasma tone with mandatory human approval and platform compliance safeguards.
- **Implementation Plan**:
  1. Fork & vendor `ReplyGuy-clone` workers; integrate with Plasma prompt library.
  2. Build approval queue UI (Next.js) with Slack notifications.
  3. Enforce rate limits, attribution headers, and compliance checks.
  4. Add dry-run simulation flag for QA.
  5. Wire RAG retrieval from PE-101 embeddings.
- **Validation (Always Works™)**:
  - [ ] Unit + integration: `npm run test`, `npm run e2e:approval`.
  - [ ] Lint/security: `eslint .`, `npm audit --production`.
  - [ ] Manual: Submit draft, approve via UI, verify post hits sandbox LinkedIn/X endpoints.
  - [ ] Monitoring: Ship job metrics to Grafana; alerts on approval bypass attempts.
  - [ ] Rollback: Feature flag to disable scheduler and revert to manual posting.

## PE-103 — Beehiiv → R2 Ingestion Workflow
- **Repository**: `plasma-engine-agent`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Deploy n8n flow ingesting Beehiiv newsletters into Cloudflare R2 with manifest tracking.
- **Implementation Plan**:
  1. Configure n8n credentials (Beehiiv API, R2 S3 key).
  2. Build ingestion flow with dedupe + checksum.
  3. Store normalized Markdown/JSON and update manifest file.
  4. Publish runbook in docs.
- **Validation**:
  - [ ] n8n workflow test run recorded with screenshots.
  - [ ] Integration test: `pytest workflows/test_beehiiv_ingest.py` (uses mocked APIs).
  - [ ] Manual: Spot-check manifest entry; confirm rerun skip logic.
  - [ ] Monitoring: n8n execution logs forwarded to Loki.
  - [ ] Rollback: Delete manifest pointer to revert to previous snapshot.

## PE-104 — Claude 3.5 Sonnet Newsletter Composer
- **Repository**: `plasma-engine-agent`
- **Type**: Feature
- **Milestone**: Sprint 1
- **Objective**: Generate Plasma newsletter summarizing latest archive entries with HTML output and preview email.
- **Implementation Plan**:
  1. Extend PE-103 workflow with Claude 3.5 Sonnet summarization nodes.
  2. Format sections (Top Stories, Plasma POV, Partner Spotlight) into Markdown & HTML.
  3. Configure Gmail/SES preview send to reviewers + Slack QA channel.
  4. Store final artifacts back into R2.
- **Validation**:
  - [ ] Automated flow test via `pytest workflows/test_newsletter_render.py`.
  - [ ] Lint: `yamllint` on n8n JSON, `markdownlint` on templates.
  - [ ] Manual: Preview email received; links verified; acceptance recorded.
  - [ ] Monitoring: Email send metrics instrumented; alert on failure.
  - [ ] Rollback: Disable workflow, revert to previous template version.

## PE-105 — X Thread & CTA Generator
- **Repository**: `plasma-engine-content`
- **Type**: Feature
- **Milestone**: Sprint 2
- **Objective**: Produce thread drafts with engagement scoring and CTA recommendations leveraging GPT-5 family.
- **Implementation Plan**:
  1. Implement thread prompt templates pulling embeddings from PE-101.
  2. Run dual-model experiments (`gpt-5`, `gpt-5-mini`) and log metrics.
  3. Compute engagement heuristics (readability, CTA variety).
  4. Surface results in approval UI with diff view.
- **Validation**:
  - [ ] Integration tests: `npm run test:threads`.
  - [ ] Automated evaluation harness generating sample threads vs baseline.
  - [ ] Manual: Reviewer verifies CTA coverage; screenshot uploaded.
  - [ ] Monitoring: Track model latency & cost budgets.
  - [ ] Rollback: Switch to baseline single-model pipeline via feature flag.

## PE-106 — SmartLead MCP Deployment
- **Repository**: `plasma-engine-infra`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Provision SmartLead MCP server with Terraform, secrets, and monitoring.
- **Implementation Plan**:
  1. Create Terraform module deploying container + secret store (Doppler/Vault).
  2. Configure `.coderabbit.yml` and CI pipeline for infra repo updates.
  3. Validate CLI `npx smartlead-mcp-by-leadmagic install` connectivity.
  4. Register service metrics with Grafana.
- **Validation**:
  - [ ] `terraform plan` + `terraform apply` run in staging with approvals.
  - [ ] Integration test script hitting MCP health endpoint.
  - [ ] Manual: Developer logs in from Cursor, confirms tool catalog.
  - [ ] Monitoring: Grafana dashboard shows request counts & error rates.
  - [ ] Rollback: Terraform destroy of MCP module + secret revocation.

## PE-107 — Outreach CSV Personalization Engine
- **Repository**: `plasma-engine-agent`
- **Type**: Feature
- **Milestone**: Sprint 2
- **Objective**: Enhance email automation with CSV ingestion, persona-aware pricing negotiation, and warmup checks.
- **Implementation Plan**:
  1. Extend workflow to parse CSV + map personas.
  2. Prompt GPT-5 for negotiation copy with price bands.
  3. Integrate deliverability/warmup status from SmartLead API.
  4. Stage emails for approval with diff view.
- **Validation**:
  - [ ] Unit tests: `pytest workflows/test_csv_personalization.py`.
  - [ ] Lint/security: `bandit`, `pip-audit`.
  - [ ] Manual: Import sample CSV, review staged messages, send test email.
  - [ ] Monitoring: Warmup threshold alerts wired.
  - [ ] Rollback: Disable auto-send; fallback to manual templates.

## PE-108 — Partner Intelligence Schema & Vector Memory
- **Repository**: `plasma-engine-research`
- **Type**: Feature
- **Milestone**: Sprint 1
- **Objective**: Design Postgres + vector store schema supporting Telegram BI bot retrieval.
- **Implementation Plan**:
  1. Define ERD for partners, deals, interactions.
  2. Provision vector store (Qdrant) with similarity search API.
  3. Build ingestion script for existing Notion export.
  4. Document data dictionary + RAG retrieval API.
- **Validation**:
  - [ ] `pytest tests/test_partner_schema.py` & migration checks.
  - [ ] Lint: `ruff`, `sqlfluff`.
  - [ ] Manual: Query sample partner question via API, verify response.
  - [ ] Monitoring: DB health metrics + vector cache hit rate dashboards.
  - [ ] Rollback: Revert migration & restore DB snapshot.

## PE-109 — Telegram RAG Bot with Access Controls
- **Repository**: `plasma-engine-agent`
- **Type**: Feature
- **Milestone**: Sprint 2
- **Objective**: Ship Telegram bot reading from PE-108 memory with role-based access and daily digests.
- **Implementation Plan**:
  1. Setup aiogram/Nest service with BotFather credentials.
  2. Implement ACL (admins, partners, observers) and logging.
  3. Integrate RAG response pipeline (Claude 3.5 Sonnet fallback).
  4. Schedule daily digest broadcast summarizing partner news.
- **Validation**:
  - [ ] Unit/integration tests: `pytest bots/test_telegram_acl.py`.
  - [ ] Static analysis: `mypy`, `pylint`.
  - [ ] Manual: Join staging chat, run queries, confirm digest delivery.
  - [ ] Monitoring: Alert on unauthorized access attempts.
  - [ ] Rollback: Disable bot token + revert deployment.

## PE-110 — Reddit API Secrets & Scheduler
- **Repository**: `plasma-engine-infra`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Manage Reddit credentials, configure async scheduler with rate limiting.
- **Implementation Plan**:
  1. Store secrets in Doppler/GCP Secret Manager with rotation policy.
  2. Implement async queue (Celery/Arq) with exponential backoff.
  3. Provide Terraform variables and docs.
- **Validation**:
  - [ ] Integration test hitting Reddit sandbox via mocked responses.
  - [ ] Lint: `terraform fmt -check`, `tflint`.
  - [ ] Manual: Trigger job and verify rate limit headers recorded.
  - [ ] Monitoring: Alerts on near-quota usage.
  - [ ] Rollback: Revoke client secret, disable scheduler.

## PE-111 — Reddit Analytics Dashboard & Digest
- **Repository**: `plasma-engine-brand`
- **Type**: Feature
- **Milestone**: Sprint 2
- **Objective**: Deploy PredictiveDev Reddit analytics app and integrate with weekly fintech insight digest.
- **Implementation Plan**:
  1. Containerize `Search-Reddit-Term-Based-Scraper` with Groq fallback config.
  2. Deploy via Helm chart; expose behind auth.
  3. Create weekly n8n workflow summarizing sentiment into newsletter + dashboard snapshots.
- **Validation**:
  - [ ] CI pipeline run: `pytest`, `black`, `safety`.
  - [ ] Manual: Dashboard accessible, time-series renders; digest email received.
  - [ ] Monitoring: Prometheus scraping app metrics.
  - [ ] Rollback: Helm rollback to previous release.

## PE-112 — Observability Backbone & QA Harness
- **Repository**: `plasma-engine-infra`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Deploy observability stack (Grafana/Loki/Promtail) and create shared QA harnesses.
- **Implementation Plan**:
  1. Provision Loki/Promtail/Grafana via Terraform + Helm.
  2. Define QA harness scripts for content, newsletter, outreach, RAG.
  3. Integrate harness runs into CI pipelines across repositories.
- **Validation**:
  - [ ] Helm tests pass; Grafana dashboards accessible.
  - [ ] QA harness `make qa` executed with logs stored.
  - [ ] Manual: Trigger synthetic check verifying alerts.
  - [ ] Monitoring: Alert rules firing on harness failures.
  - [ ] Rollback: Helm uninstall + restore previous monitoring configuration.

## PE-113 — Model Registry & Cost Guardrails
- **Repository**: `plasma-engine-shared`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Document approved LLM models, costs, usage guidelines, and create cost estimator tooling.
- **Implementation Plan**:
  1. Gather official docs for GPT-5 family and Claude 3.5 Sonnet.
  2. Create markdown registry with usage examples, limits, fallback plans.
  3. Build CLI/Notion integration estimating token costs per workflow.
- **Validation**:
  - [ ] Unit tests on estimator script.
  - [ ] Manual: Run estimator for newsletter flow → attach output.
  - [ ] Documentation published and referenced in READMEs.
  - [ ] Monitoring: Add budget alerts via Cloud cost tooling.
  - [ ] Rollback: Revert registry to previous version if needed.

## PE-114 — Sprint 1 Go/No-Go Checklist
- **Repository**: `plasma-engine-infra`
- **Type**: Task
- **Milestone**: Sprint 1
- **Objective**: Validate readiness across dependencies before Sprint 1 execution.
- **Implementation Plan**:
  1. Compile checklist (infra, access, secrets, board automation).
  2. Conduct walkthrough with leads; capture risks/mitigations.
  3. Publish go/no-go report under `docs/program-status/`.
- **Validation**:
  - [ ] Checklist signed by functional leads.
  - [ ] Manual: Meeting notes uploaded; action items logged as issues.
  - [ ] Monitoring: Ensure board metrics (cycle time) dashboards active.
  - [ ] Rollback: If no-go, create blocking issues and reschedule.


