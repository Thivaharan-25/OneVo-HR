# OneVo-HR — Phase 1 Timeline

**Duration:** 4 weeks · **Apr 20 → May 15**
**Scope:** 2 pillars (HR Management + Workforce Intelligence) MVP
**Scale:** 16 modules · 170 DB tables
**Stack:** .NET 9 · Next.js 14 · PostgreSQL 16 (RLS) · Redis · .NET MAUI Desktop Agent

---

## Phase 1 — Week-wise Deliverables

### Week 1 — Foundation (Apr 20 – 24)

**Backend**
- [ ] 16-module solution structure
- [ ] SharedKernel: BaseEntity, BaseRepository, Result<T>, ITenantContext, IEncryptionService
- [ ] PostgreSQL 16 + EF Core (snake_case, RLS policies)
- [ ] Redis connection
- [ ] Docker Compose (Postgres + Redis) for local dev
- [ ] Swagger / OpenAPI + Health check endpoints
- [ ] Multi-tenant provisioning (signup → seed → activate) with industry profile
- [ ] Auth: Argon2id password hashing, JWT, MFA, password reset, session management
- [ ] RBAC foundation (roles, permissions, permission keys)
- [ ] Org Structure: Departments, Teams, Jobs, Job Families, Locations
- [ ] Shared Platform services (file upload, email, caching)
- [ ] Agent Gateway (desktop agent authentication + ingestion endpoint)
- [ ] Country reference data seeded (LK, GB, etc.)

**Frontend**
- [ ] Root layout with provider stack (QueryClient, Auth, Permission, SignalR, Theme, Toast)
- [ ] Dashboard layout shell: collapsible Sidebar, Topbar, CommandPalette (Cmd+K), NotificationBell, user menu
- [ ] Permission-gated sidebar navigation
- [ ] Breadcrumbs (auto-generated)
- [ ] Global `error.tsx` + `not-found.tsx`
- [ ] Shared components: PermissionGate, DataTable wrapper, StatusBadge
- [ ] Login / MFA / Password reset UI
- [ ] Department / Team / Job management UI

**🟢 Milestone:** *Foundation Complete* — unblocks every downstream task.

---

### Week 2 — Core HR + Configuration (Apr 27 – May 1)

**Backend**
- [ ] Employee Profile (personal, contact, emergency, banking, compensation)
- [ ] Employee Lifecycle (Onboarding workflow, Offboarding, transfers, promotions)
- [ ] Skills Core — 5 tables:
  - `skill_categories`
  - `skills`
  - `job_skill_requirements`
  - `employee_skills`
  - `skill_validation_requests`
- [ ] Configuration module: tenant settings, monitoring feature toggles, integrations, data retention policies
- [ ] Org hierarchy enforcement rules

**Frontend**
- [ ] Employee list / detail / create / edit
- [ ] Onboarding wizard
- [ ] Offboarding flow
- [ ] Skill taxonomy admin
- [ ] Employee skills profile + My Skills self-service
- [ ] Settings pages (tenant, monitoring, integrations, retention)

**🟢 Milestone:** *Core HR live* — employees can be created, onboarded, managed, skill-mapped.

---

### Week 3 — Leave + Calendar + Monitoring Foundation (May 4 – 8)

**Backend**
- [ ] Leave module: policies, accrual, balance, request → approval → ledger
- [ ] Unified Calendar (holidays, shifts, leaves, company events)
- [ ] Shift management, holiday calendars
- [ ] Workforce Presence setup (presence tracking foundation)
- [ ] Identity Verification (biometric capture + verification flow)
- [ ] Exception Engine (rule evaluation, exception detection, alerting)

**Frontend**
- [ ] Leave management UI (request, approve, balance view)
- [ ] Calendar UI (unified view)
- [ ] Shift / Holiday admin
- [ ] Live workforce dashboard (initial)
- [ ] Verification log
- [ ] Exception dashboard

**🟢 Milestone:** *Extended modules live* — HR workflows + Presence basics both ready.

---

### Week 4 — Analytics + Monitoring + WMS Bridges (May 11 – 15)

**Backend**
- [ ] Activity Monitoring: screenshots, process tracking, window titles, idle detection, categorization
- [ ] Discrepancy Engine: daily cross-reference of HR active time vs WMS reported time vs calendar
- [ ] Workforce Presence — Biometric attendance + Overtime tracking
- [ ] Productivity Analytics: scoring, reports, team + individual dashboards
- [ ] Notifications: in-app, email, delivery preferences, digests
- [ ] WMS Phase 1 bridges:
  - People Sync
  - Availability
  - Work Activity
  - WMS Tenant Provisioning + Role Mapping

**Frontend**
- [ ] Activity detail + Screenshots viewer
- [ ] Productivity reports + dashboards
- [ ] Notification center + preferences
- [ ] Attendance / Overtime UI
- [ ] Agent management UI

**Integration Testing Buffer**
- [ ] Cross-module integration tests
- [ ] End-to-end user flow validation
- [ ] Performance + load smoke tests

**🟢 Milestone:** *All Phase 1 modules complete.*

---

## End-of-Phase-1 State (May 15)

| Area | Deliverable |
|:---|:---|
| Multi-tenant SaaS foundation | RLS, 4-layer isolation, industry profiles |
| Auth + RBAC + MFA | Permission-gated across backend + frontend |
| HR Management pillar | Employees · Lifecycle · Org · Skills (core) · Leave · Calendar · Configuration · Notifications |
| Workforce Intelligence pillar | Presence · Biometric · Identity Verification · Activity Monitoring · Discrepancy Engine · Exception Engine · Productivity Analytics |
| Desktop Agent pipeline | Agent Gateway + ingestion live |
| WMS Integration | 3 bridges (People, Availability, Work Activity) + tenant provisioning |
| Frontend | All Phase 1 pages (dashboard, HR, presence, monitoring, settings) |
| Infrastructure | Docker, Postgres, Redis, Swagger, Health checks |

---

## Out of Scope — Deferred to Phase 2

- Payroll
- Performance
- Documents
- Grievance
- Expense
- Reporting Engine
- Skills LMS (courses, assessments, development plans, certifications)
- Nexis AI Chatbot
- Flutter Mobile Application
- Productivity Metrics Bridge
- Skills Bidirectional Bridge
- Teams Graph API deep integration
- Meilisearch (Postgres FTS sufficient for Phase 1)
- RabbitMQ (in-process domain events for Phase 1)

---

## Critical Path & Dependencies

```
Week 1 Foundation ──► unlocks everything
  ├─ Infrastructure + SharedKernel ──► all modules
  ├─ Auth ──────────────────────────► all RBAC
  ├─ Org Structure ─────────────────► Skills Core (W2)
  └─ Shared Platform ───────────────► Notifications (W4)

Week 2 Core ──► unlocks HR workflows
  ├─ Employee Profile ──────────────► Skills (employee_skills)
  └─ Configuration ─────────────────► Monitoring toggles

Week 3 ──► unlocks analytics
  ├─ Calendar ──────────────────────► Leave + Discrepancy Engine
  ├─ Presence Setup ────────────────► Biometric (W4)
  └─ Activity Monitoring ───────────► Discrepancy Engine + Productivity Analytics (W4)
```

**Slip risk:** Week 1 delay cascades to entire phase. Foundation must close on time.

---

## Milestone Summary

| Milestone | By |
|:---|:---|
| Foundation complete | End of Week 1 (Apr 25) |
| Core modules complete | End of Week 2 (May 1) |
| Extended modules complete | End of Week 3 (May 8) |
| All Phase 1 modules complete | End of Week 4 (May 15) |
| Integration testing buffer | Week 4 |
