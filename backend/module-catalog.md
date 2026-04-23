# Module Catalog: ONEVO

**Last Updated:** 2026-04-05

## Architecture Overview

ONEVO follows a **Monolithic + Service-Oriented Architecture** (.NET 9) organized into **two product pillars** and a **shared foundation**. All modules live in a single deployable unit under `ONEVO.sln` but maintain strict namespace boundaries.

Inter-module communication:
- **Sync (direct):** Module A calls Module B's public interface (via DI)
- **Async (domain events):** Module A publishes, Module B handles via MediatR
- **Future:** RabbitMQ for scale when in-process events are insufficient

See [[backend/module-boundaries|Module Boundaries]] for boundary rules. Each module has its own detailed doc at `modules/{module-name}/overview.md`.

## Unified Platform Model

ONEVO and WMS coexist as **one platform** with two backends. The ONEVO frontend (Next.js) renders both an HR sidebar and a Workforce/WMS sidebar, consuming both backends.

```
ONEVO PLATFORM
  ONEVO Frontend (Next.js)
    ├── HR Sidebar          → ONEVO Backend (.NET 9)
    └── Workforce Sidebar   → ONEVO Backend + WMS Backend
                                      ↕ bridge contracts
  ONEVO Backend                    WMS Backend
  HR, Workforce, Auth,             Projects, Tasks,
  Payroll, Notifications,          Sprints, Chat,
  File Storage                     OKR, Analytics
```

**Key rule:** Entity ownership is exclusive. Every entity lives in exactly one backend. See [[backend/bridge-api-contracts|Bridge API Contracts]] for the full entity ownership map and conflict resolutions.

## Product Configuration Matrix

| Tier | Core | HR Pillar | Workforce Intel | WMS | Bridges |
|------|:----:|:---------:|:---------------:|:---:|:-------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | — |
| Work Management | ✓ | ✗ | ✗ | ✓ | People Sync only |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | — |
| HR + Work Management | ✓ | ✓ | ✗ | ✓ | All 5 bridges |
| Full Suite | ✓ | ✓ | ✓ | ✓ | All 5 bridges |

**Core (always active):** Infrastructure + Auth + CoreHR identity shell + Notifications + SharedPlatform

**Add-ons within HR Pillar:** Payroll, Performance, Advanced Skills, Documents

**Add-ons within WMS:** Resource Management, OKR, Chat, Advanced Analytics

> WMS-only tenants still get a minimal `employees` row per user — ONEVO `employee_id` is the universal person identifier used by WMS as a FK for task assignees, time logs, etc.

## Solution Structure

```
ONEVO.sln
├── src/
│   ├── ONEVO.Api/                              # ASP.NET Core host, startup, middleware
│   ├── ONEVO.SharedKernel/                     # Base classes, utilities, common types
│   │
│   │  ── PILLAR 1: HR MANAGEMENT ──
│   ├── ONEVO.Modules.Infrastructure/           # Tenants, Users, Files, Countries
│   ├── ONEVO.Modules.Auth/                     # RBAC, Sessions, MFA, Audit
│   ├── ONEVO.Modules.OrgStructure/             # Legal Entities, Departments, Job Families, Teams
│   ├── ONEVO.Modules.CoreHR/                   # Employees, Lifecycle, Onboarding, Offboarding
│   ├── ONEVO.Modules.Leave/                    # Leave Types, Policies, Entitlements, Requests
│   ├── ONEVO.Modules.Payroll/                  # Providers, Tax, Allowances, Pension, Runs
│   ├── ONEVO.Modules.Performance/              # Reviews, Goals, Feedback, Succession
│   ├── ONEVO.Modules.Skills/                   # Skills, Assessments, Courses, Dev Plans
│   ├── ONEVO.Modules.Documents/                # Document Management, Versioning
│   │
│   │  ── PILLAR 2: WORKFORCE INTELLIGENCE ──
│   ├── ONEVO.Modules.WorkforcePresence/        # Shifts, Schedules, Presence, Biometric → replaces Attendance
│   ├── ONEVO.Modules.ActivityMonitoring/       # Snapshots, App Usage, Meetings, Screenshots
│   ├── ONEVO.Modules.IdentityVerification/     # Photo Verification, Biometric Matching
│   ├── ONEVO.Modules.ExceptionEngine/          # Anomaly Rules, Alerts, Escalation
│   ├── ONEVO.Modules.ProductivityAnalytics/    # Reports, Trends, Workforce Snapshots
│   │
│   │  ── SHARED FOUNDATION ──
│   ├── ONEVO.Modules.Grievance/                # Grievance Cases, Disciplinary Actions
│   ├── ONEVO.Modules.Expense/                  # Expense Categories, Claims, Items
│   ├── ONEVO.Modules.Notifications/            # Notifications, Preferences
│   ├── ONEVO.Modules.Configuration/            # Tenant Settings, Integrations, Monitoring Toggles
│   ├── ONEVO.Modules.Calendar/                 # Calendar Events
│   ├── ONEVO.Modules.ReportingEngine/          # Scheduled Reports, Executions
│   ├── ONEVO.Modules.SharedPlatform/           # SSO, Subscriptions, Feature Flags, Workflows
│   └── ONEVO.Modules.AgentGateway/             # Agent Registration, Policy, Ingestion
├── tests/
│   ├── ONEVO.Tests.Unit/
│   ├── ONEVO.Tests.Integration/
│   └── ONEVO.Tests.Architecture/
└── tools/
    └── ONEVO.DbMigrator/
```

## Module Registry

### Pillar 1: HR Management

| #   | Module            | Detailed Doc       | Tables | Phase   | Owner   | Build Week |
| :-- | :---------------- | :----------------- | :----- | :------ | :------ | :--------- |
| 1   | Infrastructure    | [[modules/infrastructure/overview\|Infrastructure]] | 4      | Phase 1 | Dev 1   | Week 1     |
| 2   | Auth & Security   | [[modules/auth/overview\|Auth]]           | 9      | Phase 1 | Dev 2   | Week 1     |
| 3   | Org Structure     | [[modules/org-structure/overview\|Org Structure]]  | 9      | Phase 1 | Dev 3   | Week 1     |
| 4   | Core HR           | [[modules/core-hr/overview\|Core Hr]]        | 13     | Phase 1 | Dev 1+2 | Week 2     |
| 5   | Leave             | [[modules/leave/overview\|Leave]]          | 5      | Phase 1 | Dev 1   | Week 3     |
| 6   | Payroll           | [[modules/payroll/overview\|Payroll]]        | 11     | Phase 2 | Dev 3   | —          |
| 7   | Performance       | [[modules/performance/overview\|Performance]]    | 7      | Phase 2 | Dev 2   | —          |
| 8   | Skills & Learning | [[modules/skills/overview\|Skills]]         | 15 (5 Phase 1, 10 Phase 2) | Mixed | Dev 3+4 | P1: Week 2 |
| 9   | Documents         | [[modules/documents/overview\|Documents]]      | 6      | Phase 2 | Dev 4   | —          |

### Pillar 2: Workforce Intelligence

| # | Module | Detailed Doc | Tables | Phase | Owner | Build Week |
|:--|:-------|:-------------|:-------|:------|:------|:-----------|
| 10 | Workforce Presence | [[modules/workforce-presence/overview\|Workforce Presence]] | 12 | Phase 1 | Dev 3+4 | Week 2 |
| 11 | Activity Monitoring | [[modules/activity-monitoring/overview\|Activity Monitoring]] | 9 | Phase 1 | Dev 3 | Week 3 |
| 11a | Discrepancy Engine | [[modules/discrepancy-engine/overview\|Discrepancy Engine]] | 2 | Phase 1 | Dev 3 | Week 3 |
| 12 | Identity Verification | [[modules/identity-verification/overview\|Identity Verification]] | 6 | Phase 1 | Dev 4 | Week 3 |
| 13 | Exception Engine | [[modules/exception-engine/overview\|Exception Engine]] | 5 | Phase 1 | Dev 2 | Week 4 |
| 14 | Productivity Analytics | [[modules/productivity-analytics/overview\|Productivity Analytics]] | 5 | Phase 1 | Dev 1 | Week 4 |

### Shared Foundation

| # | Module | Detailed Doc | Tables | Phase | Owner | Build Week |
|:--|:-------|:-------------|:-------|:------|:------|:-----------|
| 15 | Shared Platform | [[modules/shared-platform/overview\|Shared Platform]] | 33 | Phase 1 | Dev 4 | Week 1+4 |
| 16 | Notifications | [[modules/notifications/overview\|Notifications]] | — | Phase 1 | Dev 4 | Week 4 |
| 17 | Configuration | [[modules/configuration/overview\|Configuration]] | 6 | Phase 1 | Dev 1 | Week 4 |
| 18 | Calendar | [[modules/calendar/overview\|Calendar]] | 1 | Phase 1 | Dev 1 | Week 4 |
| 19 | Reporting Engine | [[modules/reporting-engine/overview\|Reporting Engine]] | 3 | Phase 2 | Dev 1 | — |
| 20 | Grievance | [[modules/grievance/overview\|Grievance]] | 2 | Phase 2 | Dev 2 | — |
| 21 | Expense | [[modules/expense/overview\|Expense]] | 3 | Phase 2 | Dev 2 | — |
| 22 | Agent Gateway | [[modules/agent-gateway/overview\|Agent Gateway]] | 4 | Phase 1 | Dev 4 | Week 1 |

> Notifications tables (`notification_templates`, `notification_channels`) are physically housed in Shared Platform's `AppDbContext` and counted in row 15. No additional tables.
> ² Skills & Learning: 5 of its 15 tables (`skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests`) are built in Phase 1. The remaining 10 (courses, LMS, assessments, development plans) are Phase 2.

**Total: 23 modules, 170 tables (128 Phase 1 · 42 Phase 2)**

> Discrepancy Engine is its own module (`ONEVO.Modules.DiscrepancyEngine`, 2 tables: `discrepancy_events` + `wms_daily_time_logs`). Both tables were previously grouped under Activity Monitoring schema — split into `database/schemas/discrepancy-engine.md`. Activity Monitoring is now 9 tables. Skills Phase 2 had 2 duplicate entries removed. 5 new WMS integration tables added to Phase 1. Schema catalog is the canonical source of truth.

## Module Dependency Map

```
                        ┌──────────────────┐
                        │  SharedKernel     │
                        └────────┬─────────┘
              ┌──────────────────┼──────────────────────┐
              │                  │                      │
        ┌─────▼─────┐    ┌──────▼──────┐    ┌─────────▼──────────┐
        │ Infra.     │    │   Auth      │    │  SharedPlatform    │
        └─────┬──────┘    └──────┬──────┘    └─────────┬──────────┘
              │                  │                      │
        ┌─────▼──────────────────▼──┐                   │
        │      OrgStructure         │◄──────────────────┘
        └──────────┬────────────────┘
                   │
        ┌──────────▼────────────────┐
        │        CoreHR             │ ◄── Central hub
        └──┬──┬──┬──┬──┬──┬──┬─────┘
           │  │  │  │  │  │  │
  ┌────────┘  │  │  │  │  │  └──────────────┐
  │    ┌──────┘  │  │  │  └──────┐          │
  ▼    ▼         ▼  ▼  ▼         ▼          ▼
Leave Perf.   Skills Docs Griev. Expense  Workforce
                                          Presence
                                            │
  Payroll ◄── Leave + WP                    │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                        Activity      Identity       Agent
                        Monitoring    Verification   Gateway
                              │
                    ┌─────────┼──────────────────┐
                    ▼         ▼                   ▼
              Exception  Discrepancy        Productivity
              Engine     Engine             Analytics

Cross-cutting: Notifications, Configuration, Calendar, Reporting Engine
```

## Adding a New Module

1. Create the project: `ONEVO.Modules.{Name}` under `src/`
2. Create the module doc: `modules/{name}/overview.md`
3. Define the public API in `Public/` folder
4. Register services: `Add{Name}Module()`
5. Update this catalog
6. Document events in [[backend/messaging/event-catalog|Event Catalog]]
7. Add ArchUnitNET tests
8. Create sprint task in `current-focus/`

## Developer Platform — Admin API Layer

`ONEVO.Admin.Api/` is a **separate ASP.NET Core host** (not a module inside `ONEVO.sln`) that serves as the admin API layer for the developer console at `console.onevo.io`. It uses its own JWT issuer (`onevo-platform-admin`) — tokens issued here are never valid against the main ONEVO API.

| Aspect | Detail |
|:-------|:-------|
| Namespace | `ONEVO.Admin.Api` |
| JWT Issuer | `onevo-platform-admin` |
| Detailed Doc | `developer-platform/backend/admin-api-layer.md` |
| Controllers | Map to developer platform modules (tenant management, agent deployment rings, platform accounts) |
| Auth | Separate JWT issuer; platform accounts only — never customer accounts |

---

## WMS — Consumed System (Not an ONEVO Module)

WMS is built and owned by the WMS team. ONEVO consumes it via bridge contracts — it is **not** an ONEVO module and does **not** appear in the module registry above.

| What ONEVO does | How |
|-----------------|-----|
| Read WMS data (projects, tasks) | WMS API called by ONEVO frontend |
| Push employee data to WMS | People Sync bridge (Bridge 1) |
| Receive time logs from WMS | Work Activity bridge (Bridge 3) |
| Receive productivity scores | Productivity Metrics bridge (Bridge 4) |
| Deliver WMS notifications | Notification push endpoint |

Full bridge contracts: [[backend/bridge-api-contracts|Bridge API Contracts]]
