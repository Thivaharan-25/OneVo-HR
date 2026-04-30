# ONEVO — Secondary Brain

The AI-optimized knowledge base for the ONEVO development team. Single source of truth for architecture, conventions, and project context across all three development streams: backend, frontend, and desktop agent.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read [[AI_CONTEXT/project-context|Project Context]] for system overview
3. Read [[current-focus/README|Current Focus]] for delivery plan and sprint priorities
4. Check [[AI_CONTEXT/known-issues|Known Issues]] before writing any code

## System Overview

**ONEVO** is a **multi-tenant white-label SaaS** platform with three product pillars and an IDE extension surface — all sharing one backend and one database:

- **Pillar 1: HR Management** — Employee lifecycle, leave, performance, payroll, skills
- **Pillar 2: Workforce Intelligence** — Activity monitoring, presence tracking, identity verification, exception detection, productivity analytics
- **Pillar 3: WorkSync** — Projects, tasks, sprints, OKR, chat, documents, roadmaps, GitHub integration — built as internal modules in the same backend and database as HR
- **IDE Extension** — Full WorkSync chat sidebar + tag-based automation for every OneVo feature the user has permission to use, embedded in VS Code / JetBrains
- **~288 database tables** across **38 modules**
- **.NET 9** backend (Clean Architecture + CQRS, single deployable monolith)
- **.NET MAUI + Windows Service** desktop monitoring agent (separate solution `ONEVO.Agent.sln`, independent release cycle)
- **Next.js 15** frontend — single frontend for all three pillars
- **PostgreSQL 16** — single unified database, no bridge APIs, no external WMS backend
- **8-week delivery plan** with 8 developers

**Platform shape:** OneVo frontend → OneVo unified backend → single PostgreSQL database. No bridge APIs.

> **Architecture decision (ADR-002 + ADR-003):** WorkSync is NOT an external system. All WorkSync tables live in the same `ApplicationDbContext` as HR and monitoring tables. `backend/bridge-api-contracts.md` is DEPRECATED — do not implement bridge contracts.

## Product Configurations

| Tier | Core | HR Pillar | Workforce Intel | WorkSync | IDE Extension |
|:-----|:----:|:---------:|:---------------:|:--------:|:-------------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | ✗ |
| WorkSync Only | ✓ | ✗ | ✗ | ✓ | Optional add-on |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | ✗ |
| HR + WorkSync | ✓ | ✓ | ✗ | ✓ | Optional add-on |
| Full Suite | ✓ | ✓ | ✓ | ✓ | Optional add-on |

**Core (always active):** Infrastructure + Auth + CoreHR identity + Notifications + SharedPlatform
**IDE Extension:** Per-user/per-tenant entitlement. Chat + tag engine always available when WorkSync is active. Desktop monitoring agent provisioning requires a separate monitoring entitlement checked server-side.

## Repository Structure

```
onevo-hr-brain/
├── AI_CONTEXT/                  # AI context — read FIRST
│   ├── project-context.md       # Three-pillar architecture, business logic
│   ├── tech-stack.md            # .NET 9, PostgreSQL, Next.js 15
│   ├── rules.md                 # AI agent rules (backend + frontend + agent)
│   ├── known-issues.md          # Gotchas, monitoring data, agent auth
│   └── changelog/               # Knowledge base update log (one file per change)
├── Userflow/                    # End-to-end user flows by feature area (permission-based)
│   └── {feature-area}/          # HR + WorkSync + IDE flows
├── modules/                     # Feature specs — 38 modules
│   ├── {hr-module}/             # HR + monitoring module specs
│   ├── work-management/         # WorkSync internal modules (W1–W13)
│   └── ide-extension/           # IDE extension full build spec
├── backend/                     # .NET 9 backend architecture
│   ├── module-catalog.md        # Module index — all 38 modules + solution structure
│   ├── module-boundaries.md     # Boundary rules and enforcement
│   ├── shared-kernel.md         # Cross-cutting code (Result<T>, ITenantContext)
│   └── messaging/               # Event catalog, exchange topology
├── frontend/                    # Next.js 15 frontend architecture
│   ├── architecture/            # App router layout
│   ├── data-layer/              # TanStack Query + Zustand
│   └── design-system/           # UI tokens, components, typography
├── database/                    # PostgreSQL 16 — single unified schema
│   ├── schema-catalog.md        # Authoritative table list (~288 tables, 38 modules)
│   ├── schemas/                 # Per-module schema files (HR + WorkSync + IDE)
│   └── cross-module-relationships.md  # FK map across pillars
├── code-standards/              # Backend + frontend coding standards, git workflow
├── security/                    # Auth architecture, RBAC, compliance, data classification
├── infrastructure/              # CI/CD, observability, multi-tenancy
├── current-focus/               # Sprint tasks — one file per developer
│   ├── README.md                # 8-developer delivery plan + deadlines
│   └── DEV{1-8}-*.md            # Individual task files with acceptance criteria
├── decisions/                   # Architecture decision records (ADR-001 through ADR-003)
├── .cursor/rules/               # Cursor AI auto-injected context
└── scripts/                     # Automation scripts
```

## Information Layers

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | `Userflow/` | End-to-end flows by permission |
| **What to build** | `modules/` | Feature specs, DB schema, APIs |
| **How to build (backend)** | `backend/` | .NET architecture, patterns |
| **How to build (frontend)** | `frontend/` | Next.js 15 structure, components |
| **Data layer** | `database/` | Schema catalog, migrations, performance |
| **Code rules** | `code-standards/` | Naming, git, logging |
| **Security** | `security/` | Auth, RBAC, compliance |
| **Infrastructure** | `infrastructure/` | CI/CD, monitoring, multi-tenancy |

## Delivery Timeline

| Week | Focus | Key Modules |
|:-----|:------|:------------|
| Week 1 | Foundation (all 8 devs) | Infrastructure, Auth, Org Structure, Shared Platform, Agent Gateway, WorkSync Foundation, Chat foundation, Documents foundation |
| Week 2 | Core HR + WorkSync Core | Employee lifecycle, Projects, Tasks, Boards, Chat AI, Wiki |
| Week 3 | Monitoring + Planning | Activity monitoring, Leave, Sprints, Backlog, OKR, Reminders, GitHub integration |
| Week 4 | Intelligence + Analytics | Exception engine, Burndown, Roadmaps, Dashboard shares, CI/CD rules |
| Week 5 | IDE Extension core | IDE auth, WebSocket, sidebar panels (Chat, Tasks, Notifications) |
| Week 6 | IDE Extension — tag engine | Tag parser, all entity/action types, entitlement gate, agent provisioning |
| Week 7 | Integration testing | Cross-module flows, WorkSync ↔ HR flows, IDE ↔ backend flows |
| Week 8 | Buffer + deployment prep | Load testing, security review, deployment checklist |

## Key Principles

1. **Single database, single backend** — All 38 modules share one `ApplicationDbContext`, one migration set, one deployment unit. No bridge APIs.
2. **Multi-tenant by default** — 4-layer isolation on every query (tenant → legal_entity → workspace → user)
3. **Module boundaries enforced** — ArchUnitNET tests prevent violations
4. **Result\<T\> over exceptions** — explicit error handling
5. **Async all the way** — CancellationToken on every async method
6. **PII protection** — encrypted fields, Serilog scrubbing, never log PII
7. **Monitoring is configurable** — per-tenant industry profiles, per-employee overrides
8. **IDE extension is permission-gated** — tag engine respects the same RBAC as the web frontend; the backend validates every action; desktop agent install requires explicit monitoring entitlement checked server-side
