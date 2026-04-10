# ONEVO Secondary Brain — Full Structure Guide

> This document explains every folder in the vault, what it contains, and how everything connects together.

---

## The Big Picture

This Obsidian vault is the **"secondary brain"** for the ONEVO HR platform. It holds every design decision, database schema, userflow, coding standard, and module spec needed to build the product — without writing a single line of code here. Think of it as the **blueprint warehouse** that any developer (or AI agent) reads before touching the actual codebase.

```
onevo-hr-brain/
├── AI_CONTEXT/          ← "Read me first" for AI agents
├── Userflow/            ← How users interact with the product (screen-by-screen)
├── modules/             ← Backend module specs (the engine blueprints)
├── database/            ← All table schemas + relationships
├── frontend/            ← Frontend architecture, design system, patterns
├── backend/             ← Backend architecture, conventions, messaging
├── current-focus/       ← Dev assignments & sprint tasks
├── code-standards/      ← Coding rules for the whole team
├── infrastructure/      ← Hosting, deployment, multi-tenancy
├── security/            ← Security policies & threat models
├── decisions/           ← Architecture Decision Records (ADRs)
├── meetings/            ← Meeting notes
├── ade/                 ← Agent Development Environment setup
├── scripts/             ← Utility scripts
└── docs/                ← Plans, specs, and reference docs
```

---

## Folder-by-Folder Breakdown

### 1. `AI_CONTEXT/` — The Starting Point

**What it holds:** Project overview, tech stack, coding rules, known issues, and a changelog of major brain updates.

**Key files:**
- `project-context.md` — Full platform overview (two-pillar model, architecture, business rules)
- `tech-stack.md` — Every technology choice with versions (.NET 9, Next.js 14, PostgreSQL 16, etc.)
- `rules.md` — AI coding standards (naming, patterns, what to avoid)
- `known-issues.md` — Gotchas and deprecated patterns
- `changelog/` — History of major changes to the brain itself

**Connects to:** Everything. This is the root context that every other folder assumes you've read.

---

### 2. `modules/` — The Backend Engine Blueprints

**What it holds:** Detailed specs for all 22 backend modules, organized into sub-folders per feature.

**Structure:**
```
modules/
├── auth/                    ← Login, MFA, permissions, sessions
├── core-hr/                 ← Employee profiles, lifecycle, onboarding/offboarding
├── org-structure/           ← Departments, teams, job titles, hierarchy
├── leave/                   ← Leave types, policies, requests, approvals
├── payroll/                 ← Salary, tax, allowances, payslips
├── performance/             ← Reviews, goals, feedback (Phase 2)
├── skills/                  ← Skill tracking, certifications (Phase 2)
├── documents/               ← File management, templates (Phase 2)
├── grievance/               ← Case tracking, disciplinary (Phase 2)
├── expense/                 ← Claims, approvals (Phase 2)
├── calendar/                ← Company events (Phase 2)
├── notifications/           ← In-app, email, real-time push
├── configuration/           ← Monitoring toggles, app allowlist, retention
├── agent-gateway/           ← Desktop agent communication (SignalR)
├── workforce-presence/      ← Clock in/out, biometric, breaks, shifts
├── activity-monitoring/     ← App tracking, screenshots, daily summaries
├── identity-verification/   ← Photo/fingerprint verification
├── exception-engine/        ← Anomaly detection, alerts, escalation
├── productivity-analytics/  ← Daily/weekly/monthly reports, dashboards
├── reporting-engine/        ← Report builder (Phase 2)
├── shared-platform/         ← SSO, workflows, feature flags, billing
└── infrastructure/          ← Multi-tenancy, file storage, reference data
```

Each module folder contains sub-folders for its features (e.g., `auth/authentication/`, `auth/mfa/`, `auth/authorization/`). Every module has an `overview.md` with: purpose, dependencies, database tables, API endpoints, domain events, and business rules.

**Connects to:**
- `database/schemas/` — Each module has a matching schema file
- `Userflow/` — Each userflow references which module handles it
- `backend/` — Module boundaries and messaging rules
- `current-focus/` — Dev tasks reference specific modules

---

### 3. `Userflow/` — The User's Journey (Screen-by-Screen)

**What it holds:** Step-by-step flows showing how a user completes each task in the product.

**Structure:**
```
Userflow/
├── Auth-Access/             ← Login, MFA, password reset, roles, permissions
├── Employee-Management/     ← Onboarding, offboarding, promotions, transfers
├── Org-Structure/           ← Department/team setup, hierarchy management
├── Leave/                   ← Leave requests, approvals, balance checks
├── Workforce-Presence/      ← Clock in/out, shift management, attendance
├── Analytics-Reporting/     ← Dashboards, reports, data export
├── Configuration/           ← Tenant settings, monitoring toggles
├── Documents/               ← Upload, access, versioning, templates
├── Calendar/                ← Event creation, conflict detection
├── Exception-Engine/        ← Alert review, escalation setup, rule config
├── Expense/                 ← Claim submission, approval, categories
├── Grievance/               ← Filing, disciplinary actions
├── Notifications/           ← Notification preferences, inbox
├── Payroll/                 ← Payroll runs, payslips, adjustments
├── Performance/             ← Reviews, goals, feedback
├── Skills-Learning/         ← Skill assessment, courses, certifications
├── Platform-Setup/          ← Initial tenant setup, onboarding wizard
├── Workforce-Intelligence/  ← Activity monitoring, productivity views
├── Cross-Module/            ← Flows that span multiple modules
└── README.md                ← Navigation index
```

Each file describes: **who** does the action, **what screens** they see, **what happens** step by step, and **what the system does** behind the scenes.

**Connects to:**
- `modules/` — Each userflow maps to one or more backend modules
- `frontend/` — Userflows define what the frontend must render
- `database/` — Userflows show what data gets created/updated

---

### 4. `database/` — All the Tables

**What it holds:** Every database table schema, cross-module relationships, migration patterns, and performance guidelines.

**Structure:**
```
database/
├── schemas/
│   ├── auth.md                    ← users, roles, permissions, sessions
│   ├── core-hr.md                 ← employees, lifecycle_events, dependents
│   ├── org-structure.md           ← departments, teams, job_titles
│   ├── leave.md                   ← leave_types, policies, requests
│   ├── workforce-presence.md      ← presence_sessions, shifts, breaks
│   ├── activity-monitoring.md     ← activity_snapshots, app_usage
│   ├── ... (one per module)
│   └── infrastructure.md          ← tenants, files, reference_data
├── schema-catalog.md              ← Quick index of all ~138 tables
├── cross-module-relationships.md  ← How tables reference each other
├── migration-patterns.md          ← How to write EF Core migrations
└── performance.md                 ← Indexing strategies, query patterns
```

**Connects to:**
- `modules/` — 1:1 mapping (each module's tables are in its schema file)
- `backend/` — Query patterns and data access conventions
- `Userflow/` — Userflows create/read the data defined here

---

### 5. `frontend/` — How the UI is Built

**What it holds:** Frontend architecture, design system, component patterns, data layer, and testing strategy.

**Structure:**
```
frontend/
├── architecture/
│   ├── overview.md            ← Next.js 14 App Router structure
│   ├── app-structure.md       ← Folder layout and routing
│   ├── module-boundaries.md   ← Frontend module isolation
│   ├── routing.md             ← Route groups and navigation
│   ├── rendering-strategy.md  ← SSR vs CSR decisions
│   └── error-handling.md      ← Error boundaries, toast patterns
├── design-system/
│   ├── foundations/           ← Colors, typography, spacing, icons
│   ├── components/            ← Button, Modal, Table, Form specs
│   ├── patterns/              ← Layout patterns, dashboard patterns
│   └── theming/               ← Dark mode, tenant branding
├── cross-cutting/
│   ├── authentication.md      ← JWT handling in the browser
│   ├── authorization.md       ← Permission-based rendering
│   ├── i18n.md                ← Internationalization setup
│   ├── feature-flags.md       ← Feature toggle integration
│   └── security.md            ← XSS, CSRF, CSP headers
├── data-layer/
│   ├── api-integration.md     ← TanStack Query + API client
│   ├── caching-strategy.md    ← What to cache and for how long
│   ├── real-time.md           ← SignalR integration
│   └── file-handling.md       ← Upload/download patterns
├── performance/               ← Bundle size, lazy loading, images
└── testing/                   ← Unit, integration, E2E strategy
```

**Connects to:**
- `Userflow/` — Frontend implements the screens described in userflows
- `modules/` — Frontend consumes API endpoints defined in modules
- `backend/api-conventions.md` — REST patterns the frontend follows
- `code-standards/` — Shared coding rules

---

### 6. `backend/` — Backend Architecture & Conventions

**What it holds:** How the backend is structured, API patterns, module communication rules, and the messaging system.

**Key files:**
```
backend/
├── README.md                  ← Backend overview
├── api-conventions.md         ← REST patterns, pagination, errors
├── module-boundaries.md       ← Rules for module isolation
├── module-catalog.md          ← Quick index of all modules
├── monitoring-data-flow.md    ← How monitoring data moves through the system
├── notification-system.md     ← How notifications work end-to-end
├── real-time.md               ← SignalR hub architecture
├── search-architecture.md     ← PostgreSQL FTS setup
├── external-integrations.md   ← WorkManage Pro bridges
└── messaging/
    ├── README.md              ← MediatR domain event patterns
    ├── event-catalog.md       ← All domain events + publishers + consumers
    ├── exchange-topology.md   ← Event routing patterns
    └── error-handling.md      ← Failed event handling
```

**Connects to:**
- `modules/` — Backend conventions apply to every module
- `database/` — Data access patterns
- `frontend/` — API contracts the frontend consumes
- `code-standards/` — Coding rules for backend code

---

### 7. `current-focus/` — What's Being Built Right Now

**What it holds:** Developer task assignments organized by sprint week and developer number.

**Files:** `DEV1-*.md`, `DEV2-*.md`, `DEV3-*.md`, `DEV4-*.md` — each is a self-contained task file with:
- What to build
- Which module spec to read
- Acceptance criteria
- Dependencies on other devs

**Connects to:**
- `modules/` — Tasks reference specific module specs
- `database/schemas/` — Tasks reference which tables to create
- `ADE-START-HERE.md` — Build order and critical path

---

### 8. `code-standards/` — Team Coding Rules

**What it holds:** Shared standards for the entire team.

**Files:**
- `backend-standards.md` — C# / .NET conventions
- `git-workflow.md` — Branching, commits, PRs
- `logging-standards.md` — What/how to log
- `testing-strategy.md` — Test types and coverage expectations

**Connects to:** Everything that involves writing code.

---

### 9. `infrastructure/` — Deployment & Multi-Tenancy

**What it holds:** How the platform is hosted, deployed, and how tenant isolation works.

**Connects to:**
- `modules/infrastructure/` — The infrastructure module spec
- `database/` — Tenant-scoped query patterns
- `backend/` — Multi-tenancy middleware

---

### 10. `security/` — Security Policies

**What it holds:** Security guidelines, threat models, and compliance requirements (GDPR, data retention).

**Connects to:**
- `modules/auth/` — Authentication & authorization
- `modules/configuration/retention-policies/` — Data retention rules
- `frontend/cross-cutting/security.md` — Browser-side security

---

### 11. `decisions/` — Architecture Decision Records

**What it holds:** Major architecture decisions with context, options considered, and the chosen approach.

**Connects to:** Any module or system affected by the decision.

---

### 12. `docs/` — Plans & Specs

**What it holds:** Implementation plans, design specs, and the original HR scope document.

**Structure:**
```
docs/
├── HR-Scope-Document-Phase1-Phase2.md  ← Original product requirements
└── superpowers/
    ├── plans/    ← Implementation plans (restructures, redesigns)
    └── specs/    ← Design specs for major changes
```

**Connects to:** Everything — these are the "why" behind major changes.

---

### 13. `ade/` — Agent Development Environment

**What it holds:** Setup instructions for AI agents working on this codebase.

**Connects to:** `ADE-START-HERE.md` (the root entry point for any AI agent).

---

### 14. `meetings/` — Meeting Notes

**What it holds:** Notes from team meetings and decisions made.

---

### 15. `scripts/` — Utility Scripts

**What it holds:** Helper scripts for common tasks (scaffolding, validation, etc.).

---

## How Everything Connects

```
                        ┌─────────────────┐
                        │  AI_CONTEXT/     │
                        │  (Start Here)    │
                        └────────┬────────┘
                                 │
                    reads context from
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
     ┌────────────┐     ┌──────────────┐    ┌──────────────┐
     │ Userflow/  │     │  modules/    │    │ current-     │
     │ (What the  │     │ (What the    │    │ focus/       │
     │  user sees)│     │  system does)│    │ (What to     │
     └─────┬──────┘     └──────┬───────┘    │  build now)  │
           │                   │            └──────┬───────┘
           │         ┌────────┼────────┐          │
           │         ▼        ▼        ▼          │
           │   ┌─────────┐ ┌──────┐ ┌────────┐   │
           │   │database/ │ │back- │ │front-  │   │
           │   │(Tables)  │ │end/  │ │end/    │   │
           │   └─────────┘ │(How  │ │(How UI │   │
           │               │built)│ │built)  │   │
           │               └──────┘ └────────┘   │
           │                   │                  │
           └───────────────────┼──────────────────┘
                               │
                    governed by │
                               ▼
              ┌────────────────────────────────┐
              │  code-standards/ + security/   │
              │  + infrastructure/ + decisions/ │
              └────────────────────────────────┘
```

### The Connection Logic (Simplified)

1. **AI_CONTEXT/** tells you WHAT the product is
2. **Userflow/** tells you WHAT the user does (screen by screen)
3. **modules/** tells you HOW the backend handles each userflow
4. **database/** tells you WHAT DATA each module stores
5. **frontend/** tells you HOW the UI renders each userflow
6. **backend/** tells you the RULES for how modules talk to each other
7. **current-focus/** tells you WHAT to build this week
8. **code-standards/** tells you HOW to write the code
9. **security/** + **infrastructure/** tell you the CONSTRAINTS
10. **decisions/** tells you WHY things are the way they are

### The Golden Chain

```
User action (Userflow) 
  → triggers Frontend screen (frontend/) 
    → calls Backend API (modules/ + backend/) 
      → reads/writes Database (database/) 
        → fires Domain Events (backend/messaging/) 
          → triggers Notifications/Alerts (modules/notifications/ + modules/exception-engine/)
```

Every feature in ONEVO follows this chain. The vault documents every link.

---

## Quick Reference: "Where Do I Find...?"

| I need to know... | Look in... |
|:-------------------|:-----------|
| What ONEVO does | `AI_CONTEXT/project-context.md` |
| The tech stack | `AI_CONTEXT/tech-stack.md` |
| How a user does X | `Userflow/{module-name}/` |
| How module X works | `modules/{module-name}/overview.md` |
| What tables module X has | `database/schemas/{module-name}.md` |
| How modules talk to each other | `backend/messaging/event-catalog.md` |
| Frontend architecture | `frontend/architecture/overview.md` |
| UI component specs | `frontend/design-system/` |
| What to build this sprint | `current-focus/DEV{N}-*.md` |
| Coding rules | `code-standards/` |
| API patterns | `backend/api-conventions.md` |
| Security & compliance | `security/` |
| Why a decision was made | `decisions/` |
| Phase 1 vs Phase 2 | `ADE-START-HERE.md` |
