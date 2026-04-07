# ONEVO — Secondary Brain

The AI-optimized knowledge base for the ONEVO development team. Single source of truth for architecture, conventions, and project context across all three development streams: backend, frontend, and desktop agent.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read [[project-context]] for system overview
3. Read [[current-focus/README|Current Focus]] for delivery plan and sprint priorities
4. Check [[known-issues]] before writing any code

## System Overview

**ONEVO** is a multi-tenant SaaS platform with two product pillars:

- **Pillar 1: HR Management** — Employee lifecycle, leave, performance, payroll, skills
- **Pillar 2: Workforce Intelligence** — Activity monitoring, presence tracking, identity verification, exception detection, productivity analytics
- **~163 database tables** across **22 modules**
- **.NET 9** backend (Modular Monolith)
- **.NET MAUI + Windows Service** desktop agent
- **Next.js 14** frontend (React)
- **PostgreSQL 16** with Row-Level Security
- **4-week delivery plan** with 4 developers

## Product Configurations

| Configuration | Modules Included |
|:-------------|:----------------|
| **HR Management** (standalone) | Pillar 1 + Shared Foundation |
| **HR + Workforce Intelligence** | Pillar 1 + Pillar 2 + Desktop Agent |
| **HR + Work Management** | Pillar 1 + WorkManage Pro bridges |
| **Full Suite** | All pillars + Desktop Agent + WorkManage Pro |

## Repository Structure

```
onevo-hr-brain/
├── AI_CONTEXT/                  # AI context — read FIRST
│   ├── [[project-context]]       # Two-pillar architecture, business logic
│   ├── [[tech-stack]]            # .NET 9, PostgreSQL, MAUI, Next.js
│   ├── [[rules]]                 # AI agent rules (backend + frontend + agent)
│   ├── [[known-issues]]          # Gotchas, monitoring data, agent auth
│   └── changelog/               # Knowledge base update log (one file per change)
├── modules/                     # Unified module docs — 22 modules, feature-wise
│   └── {module}/{feature}/      # overview.md, end-to-end-logic.md, testing.md, frontend.md
├── cross-cutting/               # Shared concerns across all modules
│   ├── security/                # Auth architecture, data classification, compliance
│   ├── database/                # Schema conventions, migrations, performance
│   ├── messaging/               # Event catalog, exchange topology, error handling
│   ├── deployment/              # CI/CD, environment parity
│   ├── observability/           # Monitoring, logging, observability
│   ├── testing/                 # Test strategy, frontend testing
│   └── guides/                  # Coding standards, git workflow, logging
├── architecture/                # High-level architecture docs
│   ├── [[module-catalog]]        # Module index and dependency map
│   ├── [[module-boundaries]]     # Boundary rules and enforcement
│   ├── [[shared-kernel]]         # Cross-cutting code (Result<T>, ITenantContext)
│   └── ...                      # Integrations, search, notifications, frontend structure
├── design-system/               # Frontend design system (components, tokens, typography)
├── current-focus/               # Sprint tasks — one file per developer per week
│   ├── README.md                # Delivery plan overview + deadlines
│   └── WEEK*.md                 # Individual task files with checkboxes
├── .cursor/rules/               # Cursor AI auto-injected context
├── decisions/                   # Architecture decision records
├── meetings/                    # Meeting notes
└── scripts/                     # Automation scripts (brain-sync, jira-sync)
```

## Delivery Timeline

| Week | Focus | Key Modules |
|:-----|:------|:-----------|
| Week 1 (Apr 7-11) | Foundation | Infrastructure, Auth, Org Structure, Shared Platform, Agent Gateway |
| Week 2 (Apr 14-18) | Core HR + Workforce Presence | Employee lifecycle, shifts, biometric, presence tracking |
| Week 3 (Apr 21-25) | Leave + Performance + Monitoring | Leave policies, reviews, activity monitoring, identity verification |
| Week 4 (Apr 28-May 2) | Supporting + Analytics + Payroll | Exception engine, productivity analytics, payroll, documents, bridges |

## Key Principles

1. **[[multi-tenancy|Multi-tenant]] by default** — 4-layer isolation on every query
2. **[[module-boundaries|Module boundaries]] enforced** — ArchUnitNET tests prevent violations
3. **[[shared-kernel|Result<T>]] over exceptions** — explicit error handling
4. **Async all the way** — CancellationToken on every async method
5. **PII protection** — encrypted fields, [[logging-standards|Serilog scrubbing]], never log PII
6. **Monitoring is configurable** — per-tenant industry profiles, per-employee overrides
