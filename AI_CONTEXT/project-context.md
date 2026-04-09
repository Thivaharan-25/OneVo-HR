# Project Context: ONEVO

## 1. Platform Overview

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
- See [[backend/module-catalog|Module Catalog]] for full module registry

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

See [[backend/external-integrations|External Integrations]] for API contracts.

## 8. What We Are NOT Building in Phase 1

- AI Chatbot (Nexis) — deferred to later phase
- Mobile Application (Flutter) — deferred to later phase
- WorkManage Pro features — separate team, we only build bridge interfaces
- Multi-region deployment — single region for Phase 1
- Teams Graph API deep integration — basic meeting detection via process name in Phase 1

---

## 9. Desktop Agent

The ONEVO Desktop Agent is a Windows application that runs on employee laptops to capture workforce activity data. It is part of **Pillar 2: Workforce Intelligence**.

### Two Components

**Background Service (Windows Service)**

Always-on data collector running as a Windows Service (`Microsoft.Extensions.Hosting.WindowsServices`) — starts on boot, survives logoff, tamper-resistant.

Captures:
- Keyboard event counts (NOT keystrokes — just how many key presses)
- Mouse event counts
- Foreground application name + window title (hashed before sending)
- Idle periods (no input for configurable threshold)
- Meeting detection (Teams, Zoom, Meet process detection)
- Device active/idle cycles
- Camera/microphone activity status

**Tray App (MAUI)**

Minimal UI in the system tray providing:
- Employee login/logout (links employee identity to device)
- Photo capture for identity verification (when policy requires)
- Status indicator (connected/disconnected/syncing)
- "What's being tracked" transparency display (per privacy mode)
- Policy display (which features are active)

**IPC Between Components**

Named Pipes (`System.IO.Pipes`) for communication between the Service and MAUI app:
- Service → MAUI: "capture photo now" (verification trigger), status updates
- MAUI → Service: employee login context, manual break start/end

### Data Flow

```
Capture → Local Buffer (SQLite) → Batch & Send → Agent Gateway
```

1. **Capture:** Win32 APIs collect raw activity data continuously
2. **Local Buffer:** SQLite stores data locally (handles offline/network issues)
3. **Batch:** Every 2-3 minutes (configurable via policy), batch buffered data
4. **Send:** POST to `/api/v1/agent/ingest` with Device JWT
5. **Server responds 202 Accepted** — processing is async on server side

### Policy-Driven Behavior

The agent does NOT decide what to track. It fetches its monitoring policy from the server:

```json
{
  "activity_monitoring": true,
  "application_tracking": true,
  "screenshot_capture": false,
  "meeting_detection": true,
  "device_tracking": true,
  "identity_verification": true,
  "verification_on_login": true,
  "verification_interval_minutes": 60,
  "idle_threshold_seconds": 300,
  "snapshot_interval_seconds": 150,
  "heartbeat_interval_seconds": 60
}
```

Policy is fetched on employee login and refreshed hourly. If a feature is `false`, the agent does NOT collect that data type.

### Authentication

The agent uses **Device JWT** — separate from user JWT:
- Issued at registration (`POST /api/v1/agent/register`)
- Contains `device_id` + `tenant_id` + `type: "agent"`
- NO user permissions — agent cannot access HR data
- Employee context is added when employee logs in via tray app

### Key Constraints

1. Minimal resource footprint — < 2% CPU, < 50MB RAM
2. Network resilience — buffer locally, retry with exponential backoff
3. Privacy first — only collect what policy allows, hash window titles
4. Tamper resistant — detect service stops, report to server
5. Silent install — MSIX package, no user interaction required

See [[modules/agent-gateway/overview|Agent Gateway]] for the server-side API contract.

---

## 10. Frontend

The ONEVO Frontend is a React/Next.js application serving as the web interface for the full platform (both pillars).

### Architecture Overview

```
Next.js 14 App Router
├── (auth)/          — Public pages (login, forgot password, MFA)
├── (dashboard)/     — Authenticated pages (sidebar + topbar layout)
│   ├── overview/    — Landing dashboard
│   ├── hr/          — Pillar 1: HR Management
│   ├── workforce/   — Pillar 2: Workforce Intelligence
│   ├── org/         — Org Structure
│   └── settings/    — Tenant Configuration
├── (employee)/      — Employee self-service (limited nav)
└── api/             — API route handlers (BFF pattern for sensitive ops)
```

### Key Design Principles

1. **Permission-based rendering** — every feature gated by RBAC permissions
2. **Real-time where it matters** — SignalR for live workforce dashboard, exception alerts
3. **Polling where it's enough** — 30s polling for non-critical updates
4. **Responsive but desktop-first** — monitoring dashboards are primarily desktop
5. **Tenant-scoped everything** — all API calls include tenant context from JWT
6. **Feature flag aware** — UI adapts to what features the tenant has enabled

### Product Configurations Affect UI

| Config | What's Visible |
|:-------|:---------------|
| HR Only | `/hr/*`, `/org/*`, `/settings/*` (no `/workforce/*`) |
| HR + Workforce Intelligence | Full UI including `/workforce/*` |
| HR + Work Management | `/hr/*` + bridge data in dashboards |
| Full Suite | Everything |

### Backend API Consumption

The frontend consumes the ONEVO REST API at `/api/v1/*`.

- **Auth:** JWT in memory (access token) + HttpOnly cookie (refresh token)
- **Pagination:** Cursor-based, max 100 items
- **Errors:** RFC 7807 Problem Details
- **Real-time:** SignalR hub at `/hubs/notifications`

### Development Phase

The frontend is built AFTER the backend foundation is complete. See [[current-focus/README|Current Focus]] for timeline.

---

## 11. AI Agent Instructions

- **Prioritization:** Always read this file and [[AI_CONTEXT/rules|Rules]] before generating any code
- **Tech Stack:** See [[AI_CONTEXT/tech-stack|Tech Stack]] for full details (.NET 9, Next.js 14, WPF/MAUI agent)
- **Module Boundaries:** Never violate module boundaries. See [[backend/module-boundaries|Module Boundaries]]
- **Multi-Tenancy:** Every query must be tenant-scoped. See [[infrastructure/multi-tenancy|Multi Tenancy]]
- **Module Details:** Each module has its own doc in `modules/`. Read the specific module doc before working on it.
- **Hallucination Prevention:** If information is not in these docs, state it's unknown — do not guess
- **WorkManage Pro:** Do not build WorkManage Pro features. Only build bridge interfaces
- **Monitoring Privacy:** Always check monitoring configuration before processing activity data

## Related

- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[current-focus/README|Current Focus]]
- [[backend/module-catalog|Module Catalog]]
- [[AI_CONTEXT/rules|Rules]]
