# Module Catalog: ONEVO

**Last Updated:** 2026-04-05

## Architecture Overview

ONEVO follows a **Monolithic + Service-Oriented Architecture** (.NET 9) organized into **two product pillars** and a **shared foundation**. All modules live in a single deployable unit under `ONEVO.sln` but maintain strict namespace boundaries.

Inter-module communication:
- **Sync (direct):** Module A calls Module B's public interface (via DI)
- **Async (domain events):** Module A publishes, Module B handles via MediatR
- **Future:** RabbitMQ for scale when in-process events are insufficient

See [[module-boundaries]] for boundary rules. Each module has its own detailed doc in `docs/architecture/modules/`.

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

| # | Module | Detailed Doc | Tables | Owner | Build Week |
|:--|:-------|:-------------|:-------|:------|:-----------|
| 1 | Infrastructure | [[infrastructure]] | 4 | Dev 1 | Week 1 |
| 2 | Auth & Security | [[auth]] | 8 | Dev 2 | Week 1 |
| 3 | Org Structure | [[org-structure]] | 8 | Dev 3 | Week 1 |
| 4 | Core HR | [[core-hr]] | 13 | Dev 1+2 | Week 2 |
| 5 | Leave | [[leave]] | 5 | Dev 1 | Week 3 |
| 6 | Payroll | [[payroll]] | 11 | Dev 3 | Week 4 |
| 7 | Performance | [[performance]] | 7 | Dev 2 | Week 3 |
| 8 | Skills & Learning | [[skills]] | 15 | Dev 3+4 | Week 3 |
| 9 | Documents | [[documents]] | 5 | Dev 4 | Week 4 |

### Pillar 2: Workforce Intelligence

| # | Module | Detailed Doc | Tables | Owner | Build Week |
|:--|:-------|:-------------|:-------|:------|:-----------|
| 10 | Workforce Presence | [[workforce-presence]] | 12 | Dev 3+4 | Week 2 |
| 11 | Activity Monitoring | [[activity-monitoring]] | 8 | Dev 3 | Week 3 |
| 12 | Identity Verification | [[identity-verification]] | 6 | Dev 4 | Week 3 |
| 13 | Exception Engine | [[exception-engine]] | 5 | Dev 2 | Week 4 |
| 14 | Productivity Analytics | [[productivity-analytics]] | 4 | Dev 1 | Week 4 |

### Shared Foundation

| # | Module | Detailed Doc | Tables | Owner | Build Week |
|:--|:-------|:-------------|:-------|:------|:-----------|
| 15 | Shared Platform | [[shared-platform]] | 21 | Dev 4 | Week 1+4 |
| 16 | Notifications | [[notifications]] | 2 | Dev 4 | Week 4 |
| 17 | Configuration | [[configuration]] | 5 | Dev 1 | Week 4 |
| 18 | Calendar | [[calendar]] | 1 | Dev 1 | Week 4 |
| 19 | Reporting Engine | [[reporting-engine]] | 3 | Dev 1 | Week 4 |
| 20 | Grievance | [[grievance]] | 2 | Dev 2 | Week 4 |
| 21 | Expense | [[expense]] | 3 | Dev 2 | Week 4 |
| 22 | Agent Gateway | [[agent-gateway]] | 3 | Dev 4 | Week 1 |

**Total: 22 modules, 151 tables**

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
                    ┌─────────┼──────────┐
                    ▼                    ▼
              Exception           Productivity
              Engine              Analytics

Cross-cutting: Notifications, Configuration, Calendar, Reporting Engine
```

## Adding a New Module

1. Create the project: `ONEVO.Modules.{Name}` under `src/`
2. Create the module doc: `docs/architecture/modules/{name}.md`
3. Define the public API in `Public/` folder
4. Register services: `Add{Name}Module()`
5. Update this catalog
6. Document events in [[event-catalog]]
7. Add ArchUnitNET tests
8. Create sprint task in `tasks/active/`
