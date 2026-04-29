# ONEVO Secondary Brain — Full Structure Guide

> This document explains every folder in the vault, what it contains, and how everything connects together.

---

## The Big Picture

This Obsidian vault is the **"secondary brain"** for the ONEVO HR platform. It holds every design decision, database schema, userflow, coding standard, and module spec needed to build the product — without writing a single line of code here. Think of it as the **blueprint warehouse** that any developer (or AI agent) reads before touching the actual codebase.

```
onevo-hr-brain/
├── AI_CONTEXT/          â† "Read me first" for AI agents
├── Userflow/            â† How users interact with the product (screen-by-screen)
├── modules/             â† Backend module specs (the engine blueprints)
├── database/            â† All table schemas + relationships
├── frontend/            â† Frontend architecture, design system, patterns
├── backend/             â† Backend architecture, conventions, messaging
├── current-focus/       â† Dev assignments & sprint tasks
├── code-standards/      â† Coding rules for the whole team
├── infrastructure/      â† Hosting, deployment, multi-tenancy
├── security/            â† Security policies & threat models
├── decisions/           â† Architecture Decision Records (ADRs)
├── meetings/            â† Meeting notes
├── ade/                 â† Agent Development Environment setup
├── scripts/             â† Utility scripts
├── developer-platform/  â† Internal developer console — architecture, modules, API contracts, userflows
└── docs/                â† Plans, specs, and reference docs
```

---

## Folder-by-Folder Breakdown

### 1. `AI_CONTEXT/` — The Starting Point

**What it holds:** Project overview, tech stack, coding rules, known issues, and a changelog of major brain updates.

**Key files:**
- `project-context.md` — Full platform overview (two-pillar model, architecture, business rules)
- `tech-stack.md` — Every technology choice with versions (.NET 9, Vite + React 19, PostgreSQL 16, etc.)
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
├── auth/                    â† Login, MFA, permissions, sessions
├── core-hr/                 â† Employee profiles, lifecycle, onboarding/offboarding
├── org-structure/           â† Departments, teams, job titles, hierarchy
├── leave/                   â† Leave types, policies, requests, approvals
├── payroll/                 â† Salary, tax, allowances, payslips
├── performance/             â† Reviews, goals, feedback (Phase 2)
├── skills/                  â† Skill tracking, certifications (Phase 2)
├── documents/               â† File management, templates (Phase 2)
├── grievance/               â† Case tracking, disciplinary (Phase 2)
├── expense/                 â† Claims, approvals (Phase 2)
├── calendar/                â† Company events (Phase 1)
├── notifications/           â† In-app, email, real-time push
├── configuration/           â† Monitoring toggles, app allowlist, retention
├── agent-gateway/           â† Desktop agent communication (SignalR)
├── workforce-presence/      â† Clock in/out, biometric, breaks, shifts
├── activity-monitoring/     â† App tracking, screenshots, daily summaries
├── identity-verification/   â† Photo/fingerprint verification
├── exception-engine/        â† Anomaly detection, alerts, escalation
├── productivity-analytics/  â† Daily/weekly/monthly reports, dashboards
├── reporting-engine/        â† Report builder (Phase 2)
├── shared-platform/         â† SSO, workflows, feature flags, billing
└── infrastructure/          â† Multi-tenancy, file storage, reference data
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
├── Auth-Access/             â† Login, MFA, password reset, roles, permissions
├── Employee-Management/     â† Onboarding, offboarding, promotions, transfers
├── Org-Structure/           â† Department/team setup, hierarchy management
├── Leave/                   â† Leave requests, approvals, balance checks
├── Workforce-Presence/      â† Clock in/out, shift management, attendance
├── Analytics-Reporting/     â† Dashboards, reports, data export
├── Configuration/           â† Tenant settings, monitoring toggles
├── Documents/               â† Upload, access, versioning, templates
├── Calendar/                â† Event creation, conflict detection
├── Exception-Engine/        â† Alert review, escalation setup, rule config
├── Expense/                 â† Claim submission, approval, categories
├── Grievance/               â† Filing, disciplinary actions
├── Notifications/           â† Notification preferences, inbox
├── Payroll/                 â† Payroll runs, payslips, adjustments
├── Performance/             â† Reviews, goals, feedback
├── Skills-Learning/         â† Skill assessment, courses, certifications
├── Platform-Setup/          â† Initial tenant setup, onboarding wizard
├── Workforce-Intelligence/  â† Activity monitoring, productivity views
├── Cross-Module/            â† Flows that span multiple modules
└── README.md                â† Navigation index
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
│   ├── auth.md                    â† users, roles, permissions, sessions
│   ├── core-hr.md                 â† employees, lifecycle_events, dependents
│   ├── org-structure.md           â† departments, teams, job_titles
│   ├── leave.md                   â† leave_types, policies, requests
│   ├── workforce-presence.md      â† presence_sessions, shifts, breaks
│   ├── activity-monitoring.md     â† activity_snapshots, app_usage
│   ├── ... (one per module)
│   └── infrastructure.md          â† tenants, files, reference_data
├── schema-catalog.md              â† Quick index of all 170 tables
├── cross-module-relationships.md  â† How tables reference each other
├── migration-patterns.md          â† How to write EF Core migrations
└── performance.md                 â† Indexing strategies, query patterns
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
│   ├── overview.md            â† Vite + React Router structure
│   ├── app-structure.md       â† Folder layout and routing
│   ├── module-boundaries.md   â† Frontend module isolation
│   ├── routing.md             â† Route groups and navigation
│   ├── rendering-strategy.md  â† SSR vs CSR decisions
│   └── error-handling.md      â† Error boundaries, toast patterns
├── design-system/
│   ├── foundations/           â† Colors, typography, spacing, icons
│   ├── components/            â† Button, Modal, Table, Form specs
│   ├── patterns/              â† Layout patterns, dashboard patterns
│   └── theming/               â† Dark mode, tenant branding
├── cross-cutting/
│   ├── authentication.md      â† JWT handling in the browser
│   ├── authorization.md       â† Permission-based rendering
│   ├── i18n.md                â† Internationalization setup
│   ├── feature-flags.md       â† Feature toggle integration
│   └── security.md            â† XSS, CSRF, CSP headers
├── data-layer/
│   ├── api-integration.md     â† TanStack Query + API client
│   ├── caching-strategy.md    â† What to cache and for how long
│   ├── real-time.md           â† SignalR integration
│   └── file-handling.md       â† Upload/download patterns
├── performance/               â† Bundle size, lazy loading, images
└── testing/                   â† Unit, integration, E2E strategy
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
├── README.md                  â† Backend overview
├── api-conventions.md         â† REST patterns, pagination, errors
├── module-boundaries.md       â† Rules for module isolation
├── module-catalog.md          â† Quick index of all modules
├── monitoring-data-flow.md    â† How monitoring data moves through the system
├── notification-system.md     â† How notifications work end-to-end
├── real-time.md               â† SignalR hub architecture
├── search-architecture.md     â† PostgreSQL FTS setup
├── external-integrations.md   â† WorkManage Pro bridges
└── messaging/
    ├── README.md              â† MediatR domain event patterns
    ├── event-catalog.md       â† All domain events + publishers + consumers
    ├── exchange-topology.md   â† Event routing patterns
    └── error-handling.md      â† Failed event handling
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
├── HR-Scope-Document-Phase1-Phase2.md  â† Original product requirements
└── superpowers/
    ├── plans/    â† Implementation plans (restructures, redesigns)
    └── specs/    â† Design specs for major changes
```

**Connects to:** Everything — these are the "why" behind major changes.

---

### 13. `developer-platform/` — Internal Developer Console

**What it holds:** Architecture, modules, API contracts, and userflows for the internal developer console (console.onevo.io) — **not customer-facing**.

**Structure:**
```
developer-platform/
├── modules/         â† Developer console backend modules (api-key-manager, etc.)
├── frontend/        â† Developer console UI architecture and components
├── backend/         â† Developer console API conventions and messaging
├── database/        â† Developer console database schemas and migrations
└── userflow/        â† Developer workflows for managing API keys, integrations
```

**Subdirectories:**
- `modules/` — Internal developer console backend specs (api-key-manager is Phase 2)
- `frontend/` — Console UI architecture, layouts, and component patterns
- `backend/` — API layer and module communication rules for console
- `database/` — Database schemas specific to console functionality
- `userflow/` — Step-by-step workflows for console administrators

**Note:** Phase 2 content (e.g., api-key-manager module) is marked separately in planning docs.

**Connects to:**
- `docs/superpowers/plans/` — Developer platform implementation plans
- `modules/` — May reference core platform modules for integration
- `backend/` — Uses same messaging and API patterns as main platform

---

### 14. `ade/` — Agent Development Environment

**What it holds:** Setup instructions for AI agents working on this codebase.

**Connects to:** `ADE-START-HERE.md` (the root entry point for any AI agent).

---

### 15. `meetings/` — Meeting Notes

**What it holds:** Notes from team meetings and decisions made.

---

### 16. `scripts/` — Utility Scripts

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
