# Project Context: ONEVO

## 1. Project Overview

- **Project Name:** ONEVO
- **Short Description:** A production-grade, multi-tenant SaaS platform combining HR Management, Workforce Intelligence, and optional Work/Task Management into a unified ecosystem.
- **Vision:** Become the go-to integrated HR + Workforce Monitoring platform for SMBs and mid-market companies.
- **Mission:** Provide accurate, automated, and unbiased visibility of employee work behaviour alongside seamless employee lifecycle management.
- **Key Stakeholders:** Product Owner, 4-member development team, enterprise clients
- **Current Status:** Active development — Phase 1 (backend first, then frontend)

## 2. Product Strategy

ONEVO is designed around **two core pillars** sold in multiple configurations:

| Configuration | Target Market | Modules Included |
|:-------------|:-------------|:----------------|
| **HR Management** | Companies needing core HR | Pillar 1 + Shared Foundation |
| **HR + Workforce Intelligence** | Companies wanting employee monitoring | Pillar 1 + Pillar 2 + Desktop Agent |
| **HR + Work Management** | Companies wanting HR + project/task management | Pillar 1 + WorkManage Pro via bridges |
| **Full Suite** | Companies wanting everything | All pillars + Desktop Agent + WorkManage Pro |

**WorkManage Pro** is a separate Jira-like project/task management product built by another team. Our platform exposes clean integration points via 5 connectivity bridges.

## 3. System Architecture

### Two-Pillar Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        ONEVO PLATFORM                           │
│                                                                 │
│  ┌──────────────────────┐     ┌──────────────────────────────┐ │
│  │   PILLAR 1: HR        │     │   PILLAR 2: WORKFORCE        │ │
│  │   MANAGEMENT          │     │   INTELLIGENCE               │ │
│  │                       │     │                              │ │
│  │  Core HR              │     │  Activity Monitoring         │ │
│  │  Org Structure        │     │  Workforce Presence          │ │
│  │  Leave                │     │  Identity Verification       │ │
│  │  Performance          │     │  Exception Engine            │ │
│  │  Skills & Learning    │     │  Productivity Analytics      │ │
│  │  Payroll              │     │                              │ │
│  │  Documents            │     │                              │ │
│  │  Grievance            │     │                              │ │
│  │  Expense              │     │                              │ │
│  └──────────┬───────────┘     └──────────────┬───────────────┘ │
│             │                                │                  │
│  ┌──────────▼────────────────────────────────▼───────────────┐ │
│  │              SHARED FOUNDATION                             │ │
│  │  Auth | Notifications | Workflows | Reporting Engine       │ │
│  │  Configuration | Calendar | Compliance | Billing           │ │
│  │  Agent Gateway                                             │ │
│  └────────────────────────┬──────────────────────────────────┘ │
│                           │                                     │
│  ┌────────────────────────▼──────────────────────────────────┐ │
│  │              CONNECTIVITY BRIDGES                          │ │
│  │  People Sync | Availability | Performance | Skills         │ │
│  │  Work Activity (task time correlation)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         ▲                                          ▲
         │                                          │
    WorkManage Pro                          Desktop Agent
    (separate product)                     (.NET Windows Service
                                            + MAUI tray app)
```

### Architecture Style

- **Monolithic with Service-Oriented internal structure** (Modular Monolith)
- Single deployable .NET 9 application
- Strict module boundaries enforced via namespaces and dependency rules
- Inter-module communication: sync (direct service calls) for queries, domain events for side effects
- See [[module-catalog]] for full module registry

## 4. Key Stats

- **~138 database tables** across 22 modules
- **90+ permissions** in RBAC system
- **40+ notification events** across 3 channels
- **18 subscribable webhook events**
- **5 connectivity bridges** to WorkManage Pro
- **22 modules** across two pillars + shared foundation

## 5. Core Business Logic & Domain Concepts

### Key Entities

- **Tenant** — An organization/company account (multi-tenant isolation)
- **User** — Login identity (authentication)
- **Employee** — HR identity linked 1:1 to User (the central hub entity)
- **Department** — Hierarchical org unit (unlimited nesting)
- **Job Family / Level / Title** — Career ladder structure
- **Legal Entity** — Registered business entity within a tenant
- **Activity Snapshot** — Periodic activity data from desktop agent (keyboard/mouse counts, active app, idle time)
- **Presence Session** — Unified daily presence record per employee (combines biometric + agent data)
- **Exception Alert** — Anomaly detection trigger (idle too long, low activity, etc.)
- **Registered Agent** — Desktop agent installation linked to an employee device

### Core Processes

1. **Employee Lifecycle:** Hire → Onboard → Active → [Promotion/Transfer/Salary Change] → Offboard → Exit
2. **Attendance/Presence Flow:** Biometric Event / Agent Heartbeat → Presence Session → Device Session → Break Detection → Payroll
3. **Leave Flow:** Type Config → Policy → Entitlement → Request → Approval → Payroll Deduction
4. **Payroll Flow:** Salary + Allowances + Tax + Pension + Leave + Actual Hours → Run → Line Items → Provider Sync
5. **Performance Flow:** Review Cycle → Self/Manager/Peer Assessment → [Productivity Score] → Calibration → Goals → Dev Plan
6. **Skills Flow:** Skill Creation → Assessment → Gap Analysis → Course Assignment → Validation
7. **Monitoring Flow:** Agent Install → Register → Policy Sync → Activity Capture → Buffer → Aggregate → Exception Check → Alert/Report
8. **Exception Flow:** Rule Trigger → Alert → Notify Manager → Escalate (if unacknowledged) → CEO

### Business Rules

- Every data table includes `tenant_id` for multi-tenant isolation
- Employee is the central hub — almost all HR modules connect through it
- Payroll uses pessimistic locking (`SELECT FOR UPDATE`) for data integrity
- Leave policies are country-specific and job-level-specific
- RBAC uses resource + action pairs (e.g., `employees:read`, `workforce:view`)
- All lifecycle changes logged with before/after values in `employee_lifecycle_events`
- **Monitoring features are configurable per tenant** (industry profile sets defaults) **and per employee** (admin can override)
- **Desktop agent reads its policy from the server on login** — only activates what's enabled for that employee
- **Activity data uses a buffer → aggregate pattern:** raw buffer (purged after 48h) → daily summaries (retained 2 years)
- **Exception engine runs every 5 minutes** during configured work hours only
- **Non-computer industries** can disable all desktop monitoring, using biometric/manual attendance only
- **Three privacy transparency modes:** full (employees see everything), partial (see own data), covert (employer only)

## 6. Monitoring Configuration Model

```
Tenant Level (Company Settings)
├── Industry Profile (selected at signup)
│   ├── Office/IT → all monitoring ON by default
│   ├── Manufacturing → biometric/presence ON, screen/keyboard OFF
│   ├── Retail → biometric ON, device monitoring OFF
│   ├── Healthcare → minimal, compliance-focused
│   └── Custom → admin picks manually
├── Global Feature Toggles (ON/OFF per feature)
└── Employee-Level Overrides
    ├── Per employee, per department, per team, or per job family
    └── Override wins over global setting
```

## 7. WorkManage Pro Bridges

| Bridge | Direction | Purpose |
|:-------|:----------|:--------|
| **People Sync** | HR → Work | Employee profiles, roles, departments |
| **Availability** | HR → Work | Leave status, shift schedules, presence |
| **Performance** | Work → HR | Task completion rates, velocity, contributions |
| **Skills** | Bidirectional | Skill profiles ↔ task skill requirements |
| **Work Activity** | Work → HR | Time logged per task/project, active task context |

See [[external-integrations]] for API contracts.

## 8. What We Are NOT Building in Phase 1

- AI Chatbot (Nexis) — deferred to later phase
- Mobile Application (Flutter) — deferred to later phase
- WorkManage Pro features — separate team, we only build bridge interfaces
- Multi-region deployment — single region for Phase 1
- Teams Graph API deep integration — basic meeting detection via process name in Phase 1

## 9. AI Agent Instructions

- **Prioritization:** Always read this file and [[rules]] before generating any code
- **Tech Stack:** Only use .NET 9 / C# patterns. See [[tech-stack]] for full details
- **Module Boundaries:** Never violate module boundaries. See [[module-boundaries]]
- **Multi-Tenancy:** Every query must be tenant-scoped. See [[multi-tenancy]]
- **Module Details:** Each module has its own doc in `docs/architecture/modules/`. Read the specific module doc before working on it.
- **Hallucination Prevention:** If information is not in these docs, state it's unknown — do not guess
- **WorkManage Pro:** Do not build WorkManage Pro features. Only build bridge interfaces
- **Monitoring Privacy:** Always check monitoring configuration before processing activity data
