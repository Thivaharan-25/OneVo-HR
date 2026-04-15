# ONEVO — ADE Entry Point

> **Read this file first.** It tells you what ONEVO is, what to build (Phase 1), what NOT to build (Phase 2), and where to find everything.

---

## What Is ONEVO?

ONEVO is a **multi-tenant employee monitoring SaaS** product. It tracks workforce presence (clock-in/out, biometric, desktop agent), monitors application usage and activity on company laptops, detects anomalies via an exception engine, and provides productivity analytics dashboards for managers, CEOs, and employees.

**Core value proposition:** "Is this employee present and working? What are they doing? Are there any anomalies?"

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Backend** | .NET 9, C# 13, Minimal APIs |
| **Database** | PostgreSQL 16 + EF Core 9 |
| **Frontend** | Next.js 14, TypeScript, shadcn/ui, TanStack Query |
| **Real-time** | SignalR (bidirectional: server↔agent, server→browser) |
| **Background Jobs** | Hangfire |
| **Messaging** | MediatR (in-process domain events) |
| **Caching** | Redis |
| **File Storage** | Azure Blob Storage |
| **Email** | Resend |
| **Auth** | JWT + refresh tokens, MFA (TOTP) |
| **Search** | PostgreSQL FTS (Phase 1) |

**Architecture:** Monolithic + service-oriented. All modules in one .NET solution with strict namespace boundaries (`ONEVO.Modules.{ModuleName}`). Cross-module communication via domain events only — never direct service calls.

---

## Phase 1 — Build These (15 Modules)

These are the modules to implement. Each links to its full spec.

| # | Module | Purpose | Spec |
|:--|:-------|:--------|:-----|
| 1 | **Infrastructure** | Multi-tenancy, file management, reference data | [[modules/infrastructure/overview\|Infrastructure]] |
| 2 | **Auth** | Login, MFA, JWT, hybrid permission model | [[modules/auth/overview\|Auth]] |
| 3 | **Core HR** | Employee profiles, lifecycle events (onboard/offboard) | [[modules/core-hr/overview\|Core HR]] |
| 4 | **Org Structure** | Departments, teams, job titles, hierarchy | [[modules/org-structure/overview\|Org Structure]] |
| 5 | **Shared Platform** | SSO, workflow engine, approval routing | [[modules/shared-platform/overview\|Shared Platform]] |
| 6 | **Agent Gateway** | Desktop agent communication (bidirectional SignalR), policy distribution, remote commands | [[modules/agent-gateway/overview\|Agent Gateway]] |
| 7 | **Configuration** | Monitoring toggles, app allowlist (tenant→role→employee), retention policies | [[modules/configuration/overview\|Configuration]] |
| 8 | **Workforce Presence** | Clock in/out, biometric events, breaks, unified presence sessions | [[modules/workforce-presence/overview\|Workforce Presence]] |
| 9 | **Identity Verification** | Photo/fingerprint verification, on-demand capture from manager alerts | [[modules/identity-verification/overview\|Identity Verification]] |
| 10 | **Activity Monitoring** | App/device/meeting tracking, screenshots, daily summaries | [[modules/activity-monitoring/overview\|Activity Monitoring]] |
| 11 | **Exception Engine** | Anomaly detection rules, alerts, escalation, remote capture trigger | [[modules/exception-engine/overview\|Exception Engine]] |
| 12 | **Notifications** | In-app, email (Resend), SignalR real-time push | [[modules/notifications/overview\|Notifications]] |
| 13 | **Leave** | Leave types, policies, entitlements, approval workflow | [[modules/leave/overview\|Leave]] |
| 14 | **Calendar** | Company events, leave-conflict checks via `ICalendarConflictService` | [[modules/calendar/overview\|Calendar]] |
| 15 | **Productivity Analytics** | Daily/weekly/monthly reports, manager/CEO/employee dashboards | [[modules/productivity-analytics/overview\|Productivity Analytics]] |

---

## Phase 2 — Do NOT Build These (7 Modules)

Specs exist but are explicitly deferred. Each module overview has a `**Phase:** 2 — Deferred` marker and a warning box.

| Module | Reason Deferred |
|:-------|:----------------|
| **Performance** | Performance reviews not core to monitoring |
| **Skills** | Skill tracking / learning paths — not monitoring |
| **Grievance** | Case tracking — not monitoring |
| **Expense** | Claims / routing — not monitoring |
| **Documents** | File management / versioning — not monitoring |
| **Payroll** | Full payroll engine — Phase 2 only; activity data feed is read-only in Phase 1 |
| **Reporting Engine** | Subsumed by Productivity Analytics for Phase 1 |

**Also deferred (Phase 2 features inside Phase 1 modules):**
- Teams Graph API meeting participation analysis (Activity Monitoring)
- Face recognition ML matching (Identity Verification)
- App blocking / silent capture (Agent Gateway)
- AI-powered anomaly detection (Exception Engine)
- Screen recording (Activity Monitoring)

These are documented inside each module's `## Phase 2 Features (Do NOT Build)` section.

---

## Build Order / Critical Path

```
Week 1 (Foundation):
  DEV1: Infrastructure ──────> (ALL other modules depend on this)
  DEV2: Auth & Security ─────> (ALL modules use permissions from this)
  DEV3: Org Structure
  DEV4: Shared Platform + Agent Gateway

Week 2 (Core):
  DEV1: Core HR — Employee Profile
  DEV2: Core HR — Employee Lifecycle
  DEV3: Workforce Presence (setup, shifts, schedules)
  DEV4: Workforce Presence (biometric integration)

Week 3 (Intelligence):
  DEV1: Leave
  DEV2: Exception Engine ←(not Performance — that's Phase 2)
  DEV3: Activity Monitoring
  DEV4: Identity Verification

Week 4 (Analytics + Calendar):
  DEV1: Productivity Analytics
  DEV2: Exception Engine (continued)
  DEV3: Calendar
  DEV4: Notifications + Configuration
```

**Hard dependencies:**
- Infrastructure MUST be first (multi-tenancy context for everything)
- Auth MUST be second (all endpoints need authorization)
- Core HR before Workforce Presence (employee context)
- Workforce Presence before Activity Monitoring (monitoring lifecycle)
- Agent Gateway before Activity Monitoring (data pipeline)
- Activity Monitoring before Exception Engine (anomaly source data)
- Activity Monitoring + Workforce Presence before Productivity Analytics (aggregation sources)

---

## Key Architecture Concepts

### Hybrid Permission Model
NOT simple RBAC. Roles are **templates** — Super Admin can grant any feature to any role or individual employee. Access is hierarchy-scoped (manager sees their team only). See [[modules/auth/overview|Auth]].

### Monitoring Lifecycle
Desktop agent data collection is controlled by clock-in/break/clock-out events from Workforce Presence. No data captured before clock-in, during breaks, or after clock-out. This is a **GDPR requirement**. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]].

### Three-Tier App Allowlist
Tenant default → Role override → Employee override. Most specific wins. See [[modules/configuration/app-allowlist/overview|App Allowlist]].

### Bidirectional SignalR
- **Agent → Server:** Heartbeats, data push (screenshots, app usage, device sessions)
- **Server → Agent:** Commands (start/stop/pause monitoring, request screenshot/photo, update policy)

See [[modules/agent-gateway/remote-commands/overview|Remote Commands]].

### Domain Events (Not Direct Calls)
Modules communicate via MediatR domain events. Module A publishes `PresenceSessionStarted`, Module B handles it. No module imports another module's internals. See [[backend/messaging/event-catalog|Event Catalog]].

---

## How to Read a Module Spec

Every module overview (`modules/*/overview.md`) follows the same structure:

1. **Header** — Namespace, Phase, Pillar, Owner, Tables
2. **Purpose** — What this module does (1-2 paragraphs)
3. **Dependencies** — What it depends on and what consumes it
4. **Public Interface** — The C# interface other modules call
5. **Database Tables** — Full schema with columns, types, indexes
6. **Domain Events** — Events published and their consumers
7. **Key Business Rules** — Critical logic constraints
8. **API Endpoints** — REST routes with permissions
9. **Hangfire Jobs** — Background jobs with schedules
10. **Features** — Links to sub-feature specs
11. **Related** — Cross-references to other docs

---

## Essential Reference Docs

| Doc | Purpose | Link |
|:----|:--------|:-----|
| **Project Context** | Full project background | [[AI_CONTEXT/project-context\|Project Context]] |
| **Tech Stack** | All technology choices with versions | [[AI_CONTEXT/tech-stack\|Tech Stack]] |
| **Rules** | AI coding standards and conventions | [[AI_CONTEXT/rules\|Rules]] |
| **Current Focus** | Dev assignments, deadlines, task files | [[current-focus/README\|Current Focus]] |
| **Module Catalog** | Quick index of all 22 modules | [[backend/module-catalog\|Module Catalog]] |
| **Shared Kernel** | Cross-cutting code (Result, AuditableEntity, etc.) | [[backend/shared-kernel\|Shared Kernel]] |
| **API Conventions** | REST patterns, pagination, error format | [[backend/api-conventions\|API Conventions]] |
| **Event Catalog** | All domain events across modules | [[backend/messaging/event-catalog\|Event Catalog]] |
| **Multi-Tenancy** | Tenant isolation patterns | [[infrastructure/multi-tenancy\|Multi-Tenancy]] |
| **Known Issues** | Gotchas and deprecated patterns | [[AI_CONTEXT/known-issues\|Known Issues]] |

---

## For Each Developer

Each developer has task files in `current-focus/` with self-contained instructions:

- **Dev 1:** [[current-focus/DEV1-infrastructure-setup|Infrastructure]], [[current-focus/DEV1-core-hr-profile|Core HR Profile]], [[current-focus/DEV1-leave|Leave]], [[current-focus/DEV1-productivity-analytics|Productivity Analytics]]
- **Dev 2:** [[current-focus/DEV2-auth-security|Auth]], [[current-focus/DEV2-core-hr-lifecycle|Core HR Lifecycle]], [[current-focus/DEV2-exception-engine|Exception Engine]]
- **Dev 3:** [[current-focus/DEV3-org-structure|Org Structure]], [[current-focus/DEV3-workforce-presence-setup|Workforce Presence]], [[current-focus/DEV3-activity-monitoring|Activity Monitoring]], [[current-focus/DEV3-calendar|Calendar]]
- **Dev 4:** [[current-focus/DEV4-shared-platform-agent-gateway|Shared Platform + Agent Gateway]], [[current-focus/DEV4-workforce-presence-biometric|Workforce Presence Biometric]], [[current-focus/DEV4-identity-verification|Identity Verification]]

**Deadline:** 2026-05-05 (1 month from start)

---

## What NOT to Do

1. **Do not build Phase 2 modules** — check `**Phase:**` marker in each module overview
2. **Do not build Phase 2 features** — check `## Phase 2 Features (Do NOT Build)` sections
3. **Do not use RabbitMQ** — in-process MediatR domain events for Phase 1
4. **Do not use Meilisearch** — PostgreSQL FTS is sufficient
5. **Do not import one module's internals into another** — use public interfaces and domain events only
6. **Do not capture agent data outside monitoring lifecycle** — no data before clock-in, during breaks, or after clock-out
