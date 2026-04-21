# ONEVO — Secondary Brain

The AI-optimized knowledge base for the ONEVO development team. Single source of truth for architecture, conventions, and project context across all three development streams: backend, frontend, and desktop agent.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read [[AI_CONTEXT/project-context|Project Context]] for system overview
3. Read [[current-focus/README|Current Focus]] for delivery plan and sprint priorities
4. Check [[AI_CONTEXT/known-issues|Known Issues]] before writing any code

## System Overview

**ONEVO** is a **multi-tenant white-label SaaS** platform with two product pillars and an optional third-party WMS integration:

- **Pillar 1: HR Management** — Employee lifecycle, leave, performance, payroll, skills
- **Pillar 2: Workforce Intelligence** — Activity monitoring, presence tracking, identity verification, exception detection, productivity analytics
- **WMS Integration** — Projects, tasks, sprints, OKR, chat (built by WMS team, consumed via bridge contracts)
- **170 database tables** across **23 modules**
- **.NET 9** backend (Modular Monolith)
- **.NET MAUI + Windows Service** desktop agent
- **Next.js 14** frontend (React) — single frontend consuming both ONEVO and WMS backends
- **PostgreSQL 16** with Row-Level Security
- **4-week delivery plan** with 4 developers

**Platform shape:** ONEVO frontend → ONEVO backend + WMS backend (via 5 bridge contracts). Full architecture: [[docs/superpowers/plans/2026-04-21-unified-platform-architecture|Unified Platform Architecture]].

## Product Configurations

| Tier | Core | HR Pillar | Workforce Intel | WMS | Bridges |
|:-----|:----:|:---------:|:---------------:|:---:|:-------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | — |
| Work Management | ✓ | ✗ | ✗ | ✓ | People Sync only |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | — |
| HR + Work Management | ✓ | ✓ | ✗ | ✓ | All 5 bridges |
| Full Suite | ✓ | ✓ | ✓ | ✓ | All 5 bridges |

**Core (always active):** Infrastructure + Auth + CoreHR identity + Notifications + SharedPlatform

## Repository Structure

```
onevo-hr-brain/
├── AI_CONTEXT/                  # AI context — read FIRST
│   ├── [[AI_CONTEXT/project-context|Project Context]]       # Two-pillar architecture, business logic
│   ├── [[AI_CONTEXT/tech-stack|Tech Stack]]            # .NET 9, PostgreSQL, MAUI, Next.js
│   ├── [[AI_CONTEXT/rules|Rules]]                 # AI agent rules (backend + frontend + agent)
│   ├── [[AI_CONTEXT/known-issues|Known Issues]]          # Gotchas, monitoring data, agent auth
│   └── changelog/               # Knowledge base update log (one file per change)
├── Userflow/                    # End-to-end user flows by feature area (permission-based)
│   └── {feature-area}/          # ~93 flow files across 18 areas
├── modules/                     # Feature specs — 22 modules, feature-wise
│   └── {module}/{feature}/      # overview.md, end-to-end-logic.md, testing.md, frontend.md
├── backend/                     # .NET 9 backend architecture
│   ├── [[backend/module-catalog|Module Catalog]]        # Module index and dependency map
│   ├── [[backend/module-boundaries|Module Boundaries]]     # Boundary rules and enforcement
│   ├── [[backend/shared-kernel|Shared Kernel]]         # Cross-cutting code (Result<T>, ITenantContext)
│   └── messaging/               # Event catalog, exchange topology
├── frontend/                    # Next.js 14 frontend architecture
│   ├── [[frontend/architecture/app-structure|App Structure]]             # App Router layout
│   ├── [[frontend/data-layer/state-management|State Management]]      # TanStack Query + Zustand
│   └── design-system/           # UI tokens, components, typography
├── database/                    # PostgreSQL 16 — migrations, performance
├── code-standards/              # Backend + frontend coding standards, git workflow
├── security/                    # Auth architecture, RBAC, compliance, data classification
├── infrastructure/              # CI/CD, observability, multi-tenancy
├── current-focus/               # Sprint tasks — one file per developer per week
│   ├── README.md                # Delivery plan overview + deadlines
│   └── WEEK*.md                 # Individual task files with checkboxes
├── .cursor/rules/               # Cursor AI auto-injected context
├── decisions/                   # Architecture decision records
└── scripts/                     # Automation scripts (brain-sync, jira-sync)
```

## Information Layers

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | [[Userflow/README\|Userflow/]] | End-to-end flows by permission |
| **What to build** | `modules/` | Feature specs, DB schema, APIs |
| **How to build (backend)** | [[backend/README\|backend/]] | .NET architecture, patterns |
| **How to build (frontend)** | [[frontend/README\|frontend/]] | Next.js structure, components |
| **Data layer** | `database/` | Migrations, performance |
| **Code rules** | [[code-standards/README\|code-standards/]] | Naming, git, logging |
| **Security** | `security/` | Auth, RBAC, compliance |
| **Infrastructure** | `infrastructure/` | CI/CD, monitoring, multi-tenancy |

## Delivery Timeline

| Week | Focus | Key Modules |
|:-----|:------|:-----------|
| Week 1 (Apr 7-11) | Foundation | Infrastructure, Auth, Org Structure, Shared Platform, Agent Gateway |
| Week 2 (Apr 14-18) | Core HR + Workforce Presence | Employee lifecycle, shifts, biometric, presence tracking |
| Week 3 (Apr 21-25) | Leave + Monitoring | Leave policies, activity monitoring, identity verification, exception engine |
| Week 4 (Apr 28-May 2) | Supporting + Analytics + Payroll | Exception engine, productivity analytics, payroll, documents, bridges |

## Key Principles

1. **[[infrastructure/multi-tenancy|Multi-tenant]] by default** — 4-layer isolation on every query
2. **[[backend/module-boundaries|Module boundaries]] enforced** — ArchUnitNET tests prevent violations
3. **[[backend/shared-kernel|Result<T>]] over exceptions** — explicit error handling
4. **Async all the way** — CancellationToken on every async method
5. **PII protection** — encrypted fields, [[code-standards/logging-standards|Serilog scrubbing]], never log PII
6. **Monitoring is configurable** — per-tenant industry profiles, per-employee overrides
