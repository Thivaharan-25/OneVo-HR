# Project Context: ONEVO

> Phase 1 backend deployment rule: ONEVO has exactly one backend deployment unit, `src/ONEVO.Api/ONEVO.Api.csproj`. Customer APIs live under `/api/v1/*`; Developer Console admin APIs live under `/admin/v1/*` in the same ASP.NET Core host. `ONEVO.Admin.Api` is deprecated historical scaffold only, does not exist in the current `Onevo_Backend/src` tree, and must not be recreated or deployed as a second backend service.

## 1. Platform Overview

- **Project Name:** ONEVO
- **Short Description:** A production-grade, multi-tenant, tenant-branded SaaS platform combining HR Management, Workforce Intelligence, and optional Work/Task Management into a unified ecosystem. Customers use a ONEVO-owned tenant URL such as `{tenantSlug}.onevo.com`, with their own logo, colors, and settings.
- **Vision:** Become the go-to integrated HR + Workforce Monitoring platform for SMBs and mid-market companies.
- **Mission:** Provide accurate, automated, and unbiased visibility of employee work behaviour alongside seamless employee lifecycle management.
- **Key Stakeholders:** Product Owner, 8-member development team, enterprise clients
- **Current Status:** Active development — Phase 1 (backend first, then frontend)

## 1a. Developer Platform (Internal)

The internal Developer Platform app (`dev-console` at `console.onevo.io`) exists for ONEVO platform administration. It is **not** a customer-facing product — only ONEVO team accounts can access it. It is backed by `/admin/v1/*` endpoints inside the single `ONEVO.Api` backend host, using the platform-admin JWT issuer (`onevo-platform-admin`). See `developer-platform/overview.md` for the full specification.

---

## 2. Product Strategy

### Sales Model (Phase 1) — IMPORTANT FOR ADE

**ONEVO is NOT a self-service SaaS in Phase 1.** Customers cannot sign up themselves.

- **How tenants are acquired:** Customers contact ONEVO directly. A sales conversation happens first — this is intentional, especially because the platform includes employee activity monitoring which requires explicit company buy-in before deployment.
- **How tenants are provisioned:** After a sale is agreed, an ONEVO operator creates the tenant via the **developer console** (`console.onevo.io` -> `ONEVO.Api` `/admin/v1/*`). There is no public signup page or public tenant creation endpoint.
- **Module gating:** Each tenant is provisioned with a specific set of pillars/modules enabled. If ONEVO introduces a new module in the future, existing tenants remain on their current set unless they upgrade (pay for the new module) — then an operator enables it for them via the developer console.
- **Commercial model:** Each tenant is provisioned or upgraded onto one selected subscription plan, with optional module add-ons and resource-only add-ons where allowed.
- **Subscription pricing rule:** Reusable subscription plans define base modules, optional add-ons, resource-only add-ons, shared storage/AI allowances, and employee-count/company-size pricing tiers. Company size is part of the subscription plan pricing table, not module configuration and not a separate plan identity. During demo upgrade or onboarding the tenant owner chooses one allowed plan, monthly or annual billing, allowed add-ons, and confirms total employee count. Store calculated prices separately from overrides, and snapshot selected plan, billing cycle, confirmed employee count, selected add-ons, effective prices, shared storage, and AI token allowance.
- **Future module sales rule:** New modules must be represented in the module catalog and surfaced in the Developer Console as `available`, `quoted`, `purchased`, `subscription_included`, or `disabled` for each tenant. Do not infer access from tenant age or plan name alone.
- **Phase 2 (future, not yet designed):** ONEVO may introduce a self-service SaaS model. Until that is explicitly specced, assume all tenant lifecycle operations are operator-driven.

**ADE rule:** Never build a public tenant signup flow, public registration page, or expose `POST /api/v1/tenants` on the customer-facing API. Tenant creation is always via `/admin/v1/*` inside the single `ONEVO.Api` backend deployment.

---

ONEVO is designed around **always-included Foundation modules** plus **two sellable packages**:

| # | Module | Layer | Plan Role | Tenant Access |
|---:|---|---|---|---|
| 1 | Authentication and Authorization | Foundation | Always Included | None |
| 2 | Tenant Configuration and Onboarding | Foundation | Always Included | None |
| 3 | Roles and Permissions | Foundation | Always Included | Use only |
| 4 | Profile Management | HR Core | Plan-selected module | Full |
| 5 | Attendance and Leave Management | HR Core | Plan-selected module | Full |
| 6 | E2E Monitoring | Intelligence | Plan-selected module | View only |
| 7 | Productivity and Performance Analytics | Intelligence | Plan-selected module | View only |
| 8 | Exception Detection | Intelligence | Plan-selected module | View only |
| 9 | Overtime Management | Intelligence | Plan-selected module | Full |
| 10 | Project Management | Work Management | Plan-selected module | Full |
| 11 | Agentic Chat | Work Management | Plan-selected module | Full |
| 12 | Third Party Integrations | Work Management | Plan-selected module | Full |
| 13 | IDE Extension | Work Management | Phase 2 plan-selected module | Full |

**WorkSync (Pillar 3)** is a fully-integrated Jira/Slack-equivalent built directly inside ONEVO — same backend, same database, no external bridges.

## 3. System Architecture

### Tenant Domain Model

ONEVO uses Cloudflare DNS for the ONEVO-owned parent domain and Azure for hosting.

- Default tenant URL: `https://{tenantSlug}.onevo.com`
- DNS: Cloudflare manages `onevo.com` and wildcard `*.onevo.com`
- Hosting: wildcard traffic routes to the Azure-hosted ONEVO application
- Backend tenant resolution: request host -> subdomain slug -> tenant record
- Blocked system slugs: `www`, `api`, `console`, `admin`, `status`, `support`, `assets`, `cdn`, `mail`, `app`

Do not create or buy a new domain per tenant. Tenant access uses ONEVO-owned subdomains only.

### Three-Pillar Unified Model

```
┌──────────────────────────────────────────────────────────────────────┐
│                          ONEVO PLATFORM                              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────────┐   │
│  │  PILLAR 1    │  │   PILLAR 2       │  │   PILLAR 3          │   │
│  │  HR MGMT     │  │   WORKFORCE      │  │   WORKSYNC          │   │
│  │              │  │   INTELLIGENCE   │  │                     │   │
│  │  Core HR     │  │  Activity Mon.   │  │  Projects & Tasks   │   │
│  │  Org Struct  │  │  WF Presence     │  │  Sprint Planning    │   │
│  │  Leave       │  │  Identity Verif  │  │  OKR & Goals        │   │
│  │  Performance │  │  Exception Eng   │  │  Chat & Chat AI     │   │
│  │  Skills      │  │  Discrepancy Eng │  │  Documents & Wiki   │   │
│  │  Payroll     │  │  Productivity    │  │  Analytics          │   │
│  │              │  │  Analytics       │  │  GitHub Integration │   │
│  │  Grievance   │  │                  │  │  IDE Extension      │   │
│  │  Expense     │  │                  │  │  (tag engine +      │   │
│  └──────┬───────┘  └────────┬─────────┘  │   chat sidebar)    │   │
│         │                   │            └──────────┬──────────┘   │
│  ┌──────▼───────────────────▼────────────────────── ▼───────────┐  │
│  │                    SHARED FOUNDATION                          │  │
│  │   Auth | Notifications | Workflows | Config | Calendar        │  │
│  │   Agent Gateway | Compliance | Billing | Dev Platform         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↕ ApplicationDbContext                    │
│                        PostgreSQL (single database, ~300 tables)    │
└──────────────────────────────────────────────────────────────────────┘
              ▲                                  ▲
              │                                  │
       WorkPulse Agent                    IDE Extension
       (MSIX · Windows P1               (VS Code)
        macOS Phase 2)                  Tag engine: @entity:action
```

### Architecture Style

- **Clean Architecture + CQRS** — single deployable .NET 10 / C# 14 application with 4-layer structure
- Strict layer and feature separation enforced via namespaces and dependency rules
- Inter-module communication: Application-owned interfaces/services for normal cross-feature work; optional in-process domain events only for justified post-save side effects
- See [[backend/folder-structure|Folder Structure]] for complete solution tree

## Solution Structure

ONEVO follows **Clean Architecture + CQRS** (.NET 10 / C# 14). See [[backend/folder-structure|Folder Structure]] for the complete solution tree.

**Layers:**
- `ONEVO.Domain` - entities, value objects, business rules, optional domain events (zero external dependencies)
- `ONEVO.Application` — CQRS handlers (MediatR), interfaces, DTOs, validators
- `ONEVO.Infrastructure` — EF Core (single ApplicationDbContext, ~300 tables), JWT, BCrypt, Phase 1 `IMemoryCache`, Hangfire, SignalR
- `ONEVO.Api` — single ASP.NET Core host for customer APIs (`/api/v1/*`) and Developer Console admin APIs (`/admin/v1/*`)
- `ONEVO.Admin.Api` — deprecated historical scaffold only; does not exist in the current `Onevo_Backend/src` tree and must not be recreated or deployed as a second backend service

## 4. Key Stats

- **~300 database tables** in single ApplicationDbContext (~200 Phase 1, ~40 Phase 2)
- **~38 features** organized as folders within ONEVO.Application/Features/
- **3 pillars:** HR Management · Workforce Intelligence · WorkSync
- **90+ permissions** in RBAC system (HR tenant-level + workspace-level)
- **40+ notification events** across 3 channels
- **18 subscribable webhook events**
- **Tag engine:** `@entity:action params` syntax covers all 11 entity types × 10 action types
- **4-layer Clean Architecture** (Domain, Application, Infrastructure, API)

## 5. Core Business Logic & Domain Concepts

### Key Entities

- **Tenant** — An organization/company account (multi-tenant isolation)
- **User** — Login identity (authentication)
- **Employee** — HR identity linked 1:1 to User (the central hub entity)
- **Department** — Hierarchical org unit (unlimited nesting)
- **Position** — Phase 1 org seat, reporting, capacity, occupancy, and access-template structure
- **Legal Entity** — Company/employer entity inside a tenant; single-company tenants have one, multi-company tenants can have many
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
8. **Exception Flow:** Rule Trigger → Alert → Resolve recipient through configured resolver → Escalate if unacknowledged through escalation chain

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

Definitive policy hierarchy: tenant defaults -> scope overrides (`role`, `position`, `department`, `team`) -> employee override -> consent/disclosure gate -> Workforce Presence lifecycle gate -> resolved app allowlist -> privacy/transparency mode. The agent receives only the final resolved policy for the signed-in employee/device. Missing required consent disables desktop collection even when admin settings are enabled.

```
Tenant Level (Company Settings)
├── Industry Profile (selected during operator provisioning)
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

## 7. HR ↔ WorkSync Cross-Module Data Flows

WorkSync is Pillar 3 - there are no bridges. Cross-module flows use direct FK relationships, Application-owned interfaces/services, and optional domain events only when decoupled post-save side effects are justified.

| Flow | Direction | Mechanism |
|:-----|:----------|:----------|
| **People Sync** | HR → WorkSync | `employees.user_id` links to `workspace_members.user_id` directly |
| **Availability** | HR → WorkSync | `leave_requests` + `overtime_records` scoped via `task_id` nullable FK |
| **Productivity** | WorkSync → HR | `wms_productivity_snapshots` + `wms_daily_time_logs` in Pillar 2 |
| **Time Correlation** | WorkSync → HR | `time_logs.task_id` → `overtime_records.task_id` via domain event |
| **Skills** | Bidirectional | `skills` table shared; `workspace_id` nullable on skills |

No bridge API keys. No `wms_tenant_links`. No HTTP between pillars.

## 8. What We Are NOT Building in Phase 1

- Mobile Application (Flutter) — deferred to later phase
- macOS WorkPulse Agent — Windows only in Phase 1

---

## 9. WorkPulse Agent

The **WorkPulse Agent** is the ONEVO activity monitoring package deployed to employee devices. It is part of **Pillar 2: Workforce Intelligence** and is distributed as an **MSIX package** (Windows Phase 1). Unlike a traditional desktop application installer, it deploys silently via MDM (Intune/GPO) or through the HRMS onboarding flow with no user interaction required.

**Key difference from a desktop application:** The WorkPulse Agent is not a GUI application that users open. It is a background service package — it runs silently, surfaces only via a system tray icon, and requires zero interaction from the employee during normal operation.

**Phase 1: Windows only. Phase 2: macOS.** See [[modules/agent-gateway/agent-overview|Agent Overview]].

### Components

**Background Service (Windows Service)**

Always-on data collector running as a Windows Service — starts on boot, survives logoff, tamper-resistant.

Captures:
- Keyboard event counts (NOT keystrokes — just how many key presses)
- Mouse event counts
- Foreground application name + window title (hashed before sending)
- Idle periods (no input for configurable threshold)
- Meeting detection (Teams, Zoom, Meet process detection)
- Device active/idle cycles
- Camera/microphone activity status
- **Document tool time** — Word, Excel, PowerPoint, Figma, Photoshop (process name only)
- **Communication tool time** — Outlook, Slack, Teams active time + send event counts (count only)

**Tray App (MAUI)**

Minimal UI in the system tray providing:
- Employee login/logout (links employee identity to device)
- Photo capture for identity verification (when policy requires)
- Status indicator (connected/disconnected/syncing)
- Personal break toggle (pauses all collection during declared break)
- "What's being tracked" transparency display (per privacy mode)

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
2. Network resilience — buffer locally (SQLite), retry with exponential backoff
3. Privacy first — only collect what policy allows, hash window titles, never capture content
4. Tamper resistant — detect service stops, report to server on next heartbeat
5. Silent install — MSIX package, MDM/GPO push, no user interaction required
6. Consent first — employee must complete HRMS consent flow before agent activates

See [[modules/agent-gateway/overview|Agent Gateway]] for the server-side API contract.

---

## 10. Frontend

ONEVO has three Angular apps in one monorepo workspace: Setup / Control, Operations / Lifecycle, and the internal Developer Platform console.

### Three-App Monorepo

| App | Subdomain | Boundary | Persona | Bundle goal |
|:----|:---------|:---------|:--------|:------------|
| `setup-control-app` | `config.{tenantSlug}.onevo.com` | Tenant/company setup, legal entities, departments, positions, roles/permissions, policies, imports, add-on requests | Tenant owner, system admin, HR setup users | Configuration-heavy, setup-first |
| `operations-lifecycle-app` | `{tenantSlug}.onevo.com` | Daily employee/manager/HR/workforce operations after setup is configured | Employees, managers, HR, workforce reviewers | Operational, fast daily use |
| `dev-console` | `console.onevo.io` | Internal ONEVO Developer Platform using `/admin/v1/*` | ONEVO platform operators only | Internal tenant, entitlement, billing, rollout control |
| `shared` (library) | — | Auth, API services, design system, models, shared `TopbarComponent` | Imported by all three apps | Built once, imported by all apps |

> "Customer app users move between Setup / Control (`config.{tenantSlug}.onevo.com`) and Operations / Lifecycle (`{tenantSlug}.onevo.com`) without re-login via a parent-domain BFF cookie (`Domain=.{tenantSlug}.onevo.com`, `SameSite=Lax`). The `TopbarComponent` in the shared library renders the app switcher (permission-gated) and entity chip (multi-entity tenants only). See [[frontend/design-system/patterns/app-entity-switcher|App + Entity Switcher Pattern]]."

### Workspace Structure

```
onevo-frontend/  (Angular workspace — angular.json)
├── projects/
│   ├── setup-control-app/
│   ├── operations-lifecycle-app/
│   ├── dev-console/
│   └── shared/                      - Angular library
│       └── src/lib/
│           ├── auth/                - AuthService, AuthGuard, token handling
│           ├── api/                 - Typed HttpClient services per domain
│           ├── realtime/            - SignalR service (shared hub management)
│           ├── ui/                  - Shared Angular Material + custom components
│           ├── models/              - TypeScript interfaces/DTOs matching backend
│           └── utils/               - Date, formatting, validation helpers
```

### Key Design Principles

1. **Permission-based rendering** — every feature gated by RBAC; use `*hasPermission` directive from shared lib
2. **Real-time where it matters** — SignalR for live workforce dashboard, exception alerts
3. **Polling where it's enough** — 30 s polling for non-critical updates
4. **Desktop-first** — monitoring dashboards and analytics are primarily desktop
5. **Tenant-scoped everything** — all API calls include tenant context from JWT
6. **Feature flag aware** — UI adapts to what modules the tenant has enabled; disabled modules are hidden

### Product Packaging Affects UI

| Entitlement source | What is visible |
|:--------|:----------------|
| Foundation only | Tenant setup, auth/session surfaces, role/permission surfaces |
| Base modules in selected plan | Included module navigation and actions |
| Optional module add-ons | Add-on module navigation and actions only when selected and active |
| Resource-only add-ons | No navigation; they only increase shared storage or AI allowance |

Every route, sidebar item, and API endpoint must check tenant module entitlements. Disabled modules are hidden in Angular UI and rejected server-side with `403`.

### Backend API Consumption

The frontend consumes the ONEVO REST API at `/api/v1/*`.

- **Auth:** BFF-style HttpOnly cookie session; tenant JWTs stay backend-side for browser sessions
- **HTTP:** Angular `HttpClient` with functional interceptors for auth headers and error normalisation
- **Pagination:** Cursor-based, max 100 items
- **Errors:** RFC 7807 Problem Details
- **Real-time:** SignalR hub at `/hubs/notifications` — channels: `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status`

### Development Phase

The frontend is built AFTER the backend foundation is complete. See [[current-focus/README|Current Focus]] for timeline.

---

## 11. AI Agent Instructions

- **Prioritization:** Always read this file and [[AI_CONTEXT/rules|Rules]] before generating any code
- **Tech Stack:** See [[AI_CONTEXT/tech-stack|Tech Stack]] for full details (.NET 10 / C# 14 backend, Angular 21 three-app monorepo, Windows Service/MAUI agent)
- **Module Boundaries:** Never violate module boundaries. See [[backend/module-boundaries|Module Boundaries]]
- **Multi-Tenancy:** Every query must be tenant-scoped. See [[infrastructure/multi-tenancy|Multi Tenancy]]
- **Module Details:** Each module has its own doc in `modules/`. Read the specific module doc before working on it.
- **Hallucination Prevention:** If information is not in these docs, state it's unknown — do not guess
- **WorkSync is internal:** No bridge APIs. WorkSync features live in `Features/WorkSync/*` same as HR features
- **IDE Extension tag security:** All `@entity:action` permission checks happen server-side. Never trust client-side validation
- **Monitoring Privacy:** Always check monitoring configuration before processing activity data
- **No public signup:** Tenant provisioning is operator-only via `/admin/v1/*` inside `ONEVO.Api`. Never build a public signup/registration flow. See Section 2 (Sales Model) above.
- **Module and feature gating:** Every module-gated feature must check active tenant module entitlement, selected commercial feature keys from the subscription/custom contract, runtime feature flags, and user permissions. A tenant without Workforce Intelligence entitlement must never see `/workforce/*` routes or receive monitoring data. Feature access grants are not the commercial source of truth.
- **Sales entitlement separation:** Billing/maintenance status decides what the tenant has commercially bought; RBAC decides what a user can do inside that tenant. Keep these concepts separate and combine them only in entitlement/authorization checks.

## Related

- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[current-focus/README|Current Focus]]
- [[backend/module-catalog|Module Catalog]]
- [[AI_CONTEXT/rules|Rules]]



