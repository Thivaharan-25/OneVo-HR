# Current Focus: ONEVO

**Last Updated:** 2026-04-05
**Current Phase:** Phase 1 — Backend First, Then Frontend (React)
**Team Size:** 4 developers
**Delivery Deadline:** 2026-05-05 (1 month)
**Development Approach:** Agentic Development Environment (AI-assisted)

---

## Delivery Plan — 4 Weeks, 4 Developers

### Week 1 (Apr 7–11): Foundation & Infrastructure
> Goal: All foundational modules operational. Auth working. Org structure CRUD complete. Agent Gateway ready.

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | **Infrastructure + Shared Kernel** | [[WEEK1-infrastructure-setup]] | Tenant provisioning (with industry profile), user CRUD, file upload, base entity/repository, multi-tenancy middleware, EF Core setup, PostgreSQL RLS |
| Dev 2 | **Auth & Security** | [[WEEK1-auth-security]] | JWT auth (RS256), RBAC with 90+ permissions (incl. monitoring perms), session management, MFA, audit logging, GDPR consent |
| Dev 3 | **Org Structure** | [[WEEK1-org-structure]] | Hierarchical departments, job families/levels/titles, teams, legal entities |
| Dev 4 | **Shared Platform + Agent Gateway** | [[WEEK1-shared-platform]] | SSO config, subscriptions, feature flags, workflow engine, Agent Gateway (registration, heartbeat, policy sync, ingestion endpoint) |

---

### Week 2 (Apr 14–18): Core HR + Workforce Presence
> Goal: Employee lifecycle fully operational. Unified presence tracking working end-to-end.

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | **Core HR (Employee Profile)** | [[WEEK2-core-hr-profile]] | Employee CRUD, full profile (dependents, addresses, qualifications, work history), salary history, bank details (encrypted), manager hierarchy |
| Dev 2 | **Core HR (Lifecycle)** | [[WEEK2-core-hr-lifecycle]] | Onboarding workflow, offboarding (knowledge risk + penalties), lifecycle events (promotions, transfers, salary changes) |
| Dev 3 | **Workforce Presence (Setup)** | [[WEEK2-workforce-presence-setup]] | Shifts, schedules, templates, holidays, presence sessions, device sessions, break records |
| Dev 4 | **Workforce Presence (Biometric + Agent)** | [[WEEK2-workforce-presence-biometric]] | Biometric device registration, enrollment, event capture, overtime, corrections, agent data integration into presence |

---

### Week 3 (Apr 21–25): Leave + Performance + Activity Monitoring + Identity Verification
> Goal: Leave operational. Performance reviews working. Activity monitoring pipeline functional. Identity verification active.

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | **Leave** | [[WEEK3-leave]] | Leave types, country/level-specific policies with versioning, entitlement calculation, request + approval workflow |
| Dev 2 | **Performance** | [[WEEK3-performance]] | Review cycles, multi-rater reviews, peer feedback, goals (OKR), recognition, succession planning, optional productivity score intake |
| Dev 3 | **Activity Monitoring** | [[WEEK3-activity-monitoring]] | Activity snapshots, app usage tracking, meeting detection, screenshots, daily summary aggregation, raw buffer with partitioning, application categories |
| Dev 4 | **Identity Verification** | [[WEEK3-identity-verification]] | Verification policies (configurable intervals), photo capture API, biometric matching, verification records |

---

### Week 4 (Apr 28 – May 2): Exception Engine + Analytics + Payroll + Supporting
> Goal: Exception detection active. Productivity reports generated. Payroll operational. All bridges defined.

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | **Productivity Analytics + Reporting Engine** | [[WEEK4-productivity-analytics]] | Daily/weekly/monthly employee reports, workforce snapshots, trend analysis, reporting engine serving both pillars, CSV/Excel export |
| Dev 2 | **Exception Engine** | [[WEEK4-exception-engine]] | Configurable anomaly detection rules, threshold triggers, alert generation, escalation chains, exception schedules (work hours only), SignalR push |
| Dev 3 | **Payroll** | [[WEEK4-payroll]] | Payroll providers, tax engines, allowances, pensions, batch execution (Hangfire), reads actual hours from [[workforce-presence]] |
| Dev 4 | **Supporting Modules + Bridges** | [[WEEK4-supporting-bridges]] | Documents, Notifications (enhanced with monitoring alerts), Grievance, Expense, 5 WorkManage Pro bridges (incl. Work Activity) |

---

## Definition of Done — Per Week

### Week 1
- [ ] 22-project solution structure created per [[module-catalog]]
- [ ] Tenant provisioning (signup → seed → activate) with industry profile selection
- [ ] JWT authentication + refresh token rotation working
- [ ] RBAC middleware with 90+ permissions (including workforce:*, exceptions:*, monitoring:*, agent:*, analytics:*, verification:*)
- [ ] Agent Gateway: `/agent/register`, `/agent/heartbeat`, `/agent/policy`, `/agent/ingest` endpoints operational
- [ ] PostgreSQL RLS policies active on all tenant-scoped tables
- [ ] Unit tests ≥80% coverage, Swagger docs for all endpoints

### Week 2
- [ ] Full employee profile CRUD with PII encryption
- [ ] Employee lifecycle events logging
- [ ] Onboarding/offboarding workflows
- [ ] Shift/schedule management, presence sessions, device sessions, break detection
- [ ] Biometric integration via HMAC-SHA256 webhooks
- [ ] Agent data flowing into presence sessions

### Week 3
- [ ] Leave request → approval → entitlement deduction working
- [ ] Performance review cycle end-to-end
- [ ] Activity snapshots ingested from agent, buffered, aggregated into daily summaries
- [ ] App usage tracking with tenant-configurable categories
- [ ] Meeting detection (basic: process name matching)
- [ ] Identity verification at login/logout/configurable intervals
- [ ] Verification photo upload and storage

### Week 4
- [ ] Exception rules configurable per tenant, alerts generated automatically
- [ ] Escalation chains working (manager → CEO with delay)
- [ ] Daily/weekly/monthly productivity reports generated (Hangfire)
- [ ] Payroll run with actual hours from Workforce Presence
- [ ] All 5 WorkManage Pro bridge endpoints functional
- [ ] Document management, notification pipeline, grievance, expense workflows

---

## What We Are NOT Working On Right Now

- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **Frontend (React/Next.js)** — in scope, follows backend completion (see `frontend/AI_CONTEXT/current-focus.md`)
- **Desktop Agent code** — in scope, follows Agent Gateway completion (see `agent/AI_CONTEXT/`)
- **WorkManage Pro features** — other team; we only build [[external-integrations|bridge interfaces]]
- **Teams Graph API deep integration** — Phase 2; Phase 1 uses process name detection
- **Meilisearch** — PostgreSQL FTS sufficient for Phase 1
- **RabbitMQ** — using in-process domain events; RabbitMQ for scale later

## Key Dates & Deadlines

| Milestone | Date | Notes |
|:----------|:-----|:------|
| Week 1 complete: Foundation | 2026-04-11 | Auth, RBAC, Org Structure, Shared Platform, Agent Gateway |
| Week 2 complete: Core HR + Presence | 2026-04-18 | Employee lifecycle, workforce presence tracking |
| Week 3 complete: Leave + Performance + Monitoring | 2026-04-25 | Leave, performance, activity monitoring, identity verification |
| Week 4 complete: All modules + Payroll | 2026-05-02 | Exception engine, analytics, payroll, supporting, bridges |
| Final testing & bug fixes | 2026-05-05 | Buffer for integration testing |
