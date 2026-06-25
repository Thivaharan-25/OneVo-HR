# ONEVO - Secondary Brain


## Quick Start

1. Open in Cursor - `.cursor/rules/` auto-inject AI context
2. Read [[AI_CONTEXT/project-context|Project Context]] for system overview
3. Read [[current-focus/README|Current Focus]] for delivery plan and sprint priorities
4. Check [[AI_CONTEXT/known-issues|Known Issues]] before writing any code

## System Overview

**ONEVO** is a **multi-tenant white-label SaaS** platform with three product pillars and an IDE extension surface - all sharing one backend and one database:

- **Pillar 1: HR Management** - People, Time Off, Time & Attendance, payroll-ready employee data, and employee lifecycle
- **Pillar 2: Monitoring** - Activity monitoring, presence tracking, identity verification, exception detection, productivity analytics
- **Pillar 3: Work** - Phase 1 simple project/work-item management: projects, work items, documents, members, settings, and worklogs. Planner, Goals/OKR, advanced roadmap, and advanced work-planning surfaces are Phase 2.
- **IDE Extension (Phase 2)** - Full WorkSync chat sidebar + tag-based automation for every OneVo feature the user has permission to use, embedded in VS Code
- **~288 database tables** across **38 modules**
- **.NET 10 / C# 14** backend (Clean Architecture + CQRS, single deployable monolith)
- **.NET MAUI + Windows Service** desktop monitoring agent (separate solution `ONEVO.Agent.sln`, independent release cycle)
- **Angular 21** frontend - merged customer-facing app shell plus internal `dev-console`, sharing a `shared` Angular library
- **PostgreSQL 16.13 baseline / PostgreSQL 18 target after validation** - single unified database, no bridge APIs, no external WMS backend
- **8-week delivery plan** with 8 developers

**Platform shape:** OneVo frontend -> OneVo unified backend -> single PostgreSQL database. No bridge APIs.

> **Architecture decision (ADR-002 + ADR-003):** WorkSync is NOT an external system. All WorkSync tables live in the same `ApplicationDbContext` as HR and monitoring tables. `backend/bridge-api-contracts.md` is DEPRECATED - do not implement bridge contracts.

## Product Packaging

ONEVO uses Subscription Plans with base modules, optional module add-ons, resource-only add-ons, and always-included Foundation modules. Each tenant has explicit module entitlements, and the UI, API, navigation, scheduled jobs, desktop agent, and IDE extension must check those entitlements before showing or serving features.

| # | Module | Layer | Plan Role | Tenant Access |
|---:|---|---|---|---|
| 1 | Authentication and Authorization | Foundation | Always Included | None |
| 2 | Tenant Configuration and Onboarding | Foundation | Always Included | None |
| 3 | Roles and Permissions | Foundation | Always Included | Use only |
| 4 | Profile Management | HR Core | Plan-selected module | Full |
| 5 | Time Off and Time & Attendance | HR Core | Plan-selected module | Full |
| 6 | E2E Monitoring | Intelligence | Plan-selected module | View only |
| 7 | Productivity and Performance Analytics | Intelligence | Plan-selected module | View only |
| 8 | Monitoring Alerts | Intelligence | Phase 1 lightweight alerts; full Exception Engine is Phase 2 | View only |
| 9 | Overtime Management | Intelligence | Plan-selected module | Full |
| 10 | Work Management | Work Management | Plan-selected module | Full |
| 11 | Agentic Chat | Work Management | Plan-selected module | Full |
| 12 | Third Party Integrations | Work Management | Plan-selected module | Full |
| 13 | IDE Extension | Work Management | Phase 2 plan-selected module | Full |

**Foundation:** Always active for every tenant.  
**Plan-selected modules:** Classified as base package modules or optional add-ons inside Subscription Plans.

## Repository Structure

```
onevo-hr-brain/
+-- AI_CONTEXT/                  # AI context - read FIRST
|   +-- project-context.md       # Three-pillar architecture, business logic
|   +-- tech-stack.md            # .NET 10 / C# 14, PostgreSQL, Angular 21 customer app + dev console
|   +-- rules.md                 # AI agent rules (backend + frontend + agent)
|   +-- known-issues.md          # Gotchas, monitoring data, agent auth
|   +-- changelog/               # Knowledge base update log (one file per change)
+-- Userflow/                    # End-to-end user flows by feature area (permission-based)
|   +-- {feature-area}/          # HR + WorkSync + IDE flows
+-- modules/                     # Feature specs - 38 modules
|   +-- {hr-module}/             # HR + monitoring module specs
|   +-- work-management/         # WorkSync internal modules (W1-W13)
|   +-- ide-extension/           # IDE extension full build spec
+-- backend/                     # .NET 10 backend architecture
|   +-- module-catalog.md        # Module index - all 38 modules + solution structure
|   +-- module-boundaries.md     # Boundary rules and enforcement
|   +-- shared-kernel.md         # Cross-cutting code (Result<T>, ITenantContext)
|   +-- messaging/               # Event catalog, exchange topology
+-- frontend/                    # Angular 21 customer app shell + dev console architecture
|   +-- architecture/            # Angular Router, app structure, lazy loading
|   +-- data-layer/              # Angular Signals, resource(), SignalR
|   +-- design-system/           # Angular Material, UI tokens, components, typography
+-- database/                    # PostgreSQL 16.13 baseline / PostgreSQL 18 target - single unified schema
|   +-- schema-catalog.md        # Authoritative table list (~288 tables, 38 modules)
|   +-- schemas/                 # Per-module schema files (HR + WorkSync + IDE)
|   +-- cross-module-relationships.md  # FK map across pillars
+-- code-standards/              # Backend + frontend coding standards, git workflow
+-- security/                    # Auth architecture, RBAC, compliance, data classification
+-- infrastructure/              # CI/CD, observability, multi-tenancy
+-- current-focus/               # Sprint tasks - one file per developer
|   +-- README.md                # 8-developer delivery plan + deadlines
|   +-- DEV{1-8}-*.md            # Individual task files with acceptance criteria
+-- decisions/                   # Architecture decision records (ADR-001 through ADR-003)
+-- .cursor/rules/               # Cursor AI auto-injected context
+-- scripts/                     # Automation scripts
```

## Information Layers

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | `Userflow/` | End-to-end flows by permission |
| **What to build** | `modules/` | Feature specs, DB schema, APIs |
| **How to build (backend)** | `backend/` | .NET architecture, patterns |
| **How to build (frontend)** | `frontend/` | Angular 21 merged customer app shell, dev console, components, patterns |
| **Data layer** | `database/` | Schema catalog, migrations, performance |
| **Code rules** | `code-standards/` | Naming, git, logging |
| **Security** | `security/` | Auth, RBAC, compliance |
| **Infrastructure** | `infrastructure/` | CI/CD, monitoring, multi-tenancy |

## Customer-Facing Phase 1 IA

The merged customer app uses this top-level navigation:

1. Home
2. People
3. Time Off
4. Time & Attendance
5. Work
6. Calendar
7. Inbox
8. Monitoring
9. Settings

Rules:

- There is one customer-facing app shell, not separate customer apps for setup/configuration and operations.
- `Settings` is the only customer-facing tenant/system administration area. Do not create a separate top-level `Admin` module.
- `Time Off` is canonical across customer-facing and internal documentation. Use `time_off:*` permissions, `time_off_*` database identifiers, `/api/v1/time-off/*` routes, and `@time-off:*` tags. Deprecated legacy aliases are migration-only and must not be used in new documentation.
- `Home` is the employee-style home/dashboard with permission-shaped content; do not create a separate management home screen.
- `Work` is intentionally simple in Phase 1. Do not include Planner, Goals/OKR, advanced roadmap, or advanced work-planning features.
- `Inbox` is the Phase 1 action center for approvals, requests, invitations, notifications, assignments, and operational action items while Workflow/Automation Engine is deferred.

Canonical Work Phase 1 rules:

- A tenant can create multiple workspaces.
- Each project belongs to exactly one workspace.
- Each project has simple Kanban, List, and Calendar work-item views.
- Project/workspace admins invite members directly to a project; the selected member accepts or declines.
- Simple project-link invitations between project admins are allowed and create project-link records when accepted.
- Workspace linking, linked workspace source pools, owner-to-owner participation governance, and advanced project-link/dependency platforms are Phase 2.

Canonical position access rules:

- Position creation uses the topbar-selected Company as the operating boundary; internally this maps to `legal_entity_id`.
- The Create/Edit Position form does not let normal users select legal entity manually.
- Position access uses **Role granted**, **Can manage employees in**, conditional department/position selectors, and optional **Requires approval**.
- Admin-facing employee visibility options are **Selected departments**, **Selected positions**, and **Entire company**.
- If a role has no employee-data permissions, **Can manage employees in** is hidden or disabled; no employee-data access is backend behavior, not a selectable tenant-admin option.
## Delivery Timeline

| Week | Focus | Key Modules |
|:-----|:------|:------------|
| Week 1 | Foundation (all 8 devs) | Infrastructure, Auth, Org Structure, Shared Platform, Agent Gateway, Work foundation, Documents foundation. Chat foundation is Phase 2. |
| Week 2 | Core HR + Work Core | Employee lifecycle, Projects, Work Items, simple Docs/Pages where retained. Boards and Chat AI are Phase 2. |
| Week 3 | Monitoring + Time Off + Work foundation | Activity monitoring, Time Off, simple Work Items, project membership, reminders, repository links where enabled |
| Week 4 | Intelligence + Analytics | Monitoring alerts, Work reporting, dashboard shares, CI/CD rules |
| Week 5 | IDE Extension core | IDE auth, WebSocket, sidebar panels (Chat, Tasks, Notifications) |
| Week 6 | IDE Extension - tag engine | Tag parser, all entity/action types, entitlement gate, agent provisioning |
| Week 7 | Integration testing | Cross-module flows, WorkSync <-> HR flows, IDE <-> backend flows |
| Week 8 | Buffer + deployment prep | Load testing, security review, deployment checklist |

## Key Principles

1. **Single database, single backend** - All 38 modules share one `ApplicationDbContext`, one migration set, one deployment unit. No bridge APIs.
2. **Multi-tenant by default** - 4-layer isolation on every query (tenant -> legal_entity -> workspace -> user)
3. **Module boundaries enforced** - ArchUnitNET tests prevent violations
4. **Result\<T\> over exceptions** - explicit error handling
5. **Async all the way** - CancellationToken on every async method
6. **PII protection** - encrypted fields, Serilog scrubbing, never log PII
7. **Monitoring is configurable** - per-tenant industry profiles, per-employee overrides
8. **IDE extension is permission-gated** - tag engine respects the same RBAC as the web frontend; the backend validates every action; desktop agent install requires explicit monitoring entitlement checked server-side

## Phase 1 App and Engine Decisions

- Customer-facing setup, employee self-service, manager operations, HR operations, and tenant-admin configuration use one merged customer app shell. Permissions, active company context, position-derived authority, and employee access coverage decide sidebar, sub-sidebar, page actions, and data scope. Demo account switching is only a demo shortcut, not product logic.
- Internal Developer Platform / dev console remains separate at `console.onevo.io`.
- Workflow / Automation Engine is Phase 2. Phase 1 transfer, promotion, position access, and sensitive access approvals use Org Structure management coverage, position-based authority, tenant roles/permissions, lightweight approval requests, `access_grant_requests` where relevant, and Notifications.
- Full configurable Exception Engine is Phase 2. Phase 1 supports lightweight monitoring/attendance alerts and notifications routed through management coverage or authorized reviewer permissions.
