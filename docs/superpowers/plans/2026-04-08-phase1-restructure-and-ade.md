# Phase 1 Restructure + ADE Setup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the brain repo's current-focus files to reflect correct Phase 1 assignments (15 modules, no Phase 2 work), fix labeling that confuses ADE agents, and create the ADE orchestrator instructions.

**Architecture:** All changes are in the brain repo (this Obsidian vault). No code repos are modified. Tasks involve creating/editing/deleting markdown files in `current-focus/`, `modules/`, and creating new ADE instruction files.

**Tech Stack:** Markdown (Obsidian-compatible), Obsidian wikilinks (`[[path|display]]`)

---

## File Map

### Files to Create
- `current-focus/DEV2-notifications.md` — New task file for Notifications module
- `current-focus/DEV3-calendar.md` — New task file for Calendar module
- `current-focus/DEV4-configuration.md` — New task file for Configuration module
- `ade/README.md` — ADE orchestrator instructions and architecture

### Files to Modify
- `current-focus/README.md` — Full rewrite with new assignments, remove dates
- `modules/payroll/overview.md` — Phase marker: 1 → 2
- `modules/calendar/overview.md` — Phase marker: 2 → 1, owner update
- `modules/notifications/overview.md` — Owner update
- `modules/configuration/overview.md` — Owner update
- All 12 remaining `current-focus/DEV*-*.md` files — Relabel Phase 1/2 → Step 1/2

### Files to Delete
- `current-focus/DEV3-payroll.md` — Payroll deferred to Phase 2
- `current-focus/DEV2-performance.md` — Performance deferred to Phase 2
- `current-focus/DEV4-supporting-bridges.md` — Dissolved; contents moved to individual task files or deferred

---

## Task 1: Update Module Overview Phase Markers

**Files:**
- Modify: `modules/payroll/overview.md` (line ~4)
- Modify: `modules/calendar/overview.md` (line ~4)
- Modify: `modules/notifications/overview.md` (line ~5)
- Modify: `modules/configuration/overview.md` (line ~5)

- [ ] **Step 1: Update Payroll phase marker**

In `modules/payroll/overview.md`, change:
```
**Phase:** 1 — Build
```
to:
```
**Phase:** 2 — Deferred
```

- [ ] **Step 2: Update Calendar phase marker and owner**

In `modules/calendar/overview.md`, change:
```
**Phase:** 2 — Deferred
```
to:
```
**Phase:** 1 — Build
```

Also update the Owner field to reflect DEV3:
```
**Owner:** Dev 3
```

- [ ] **Step 3: Update Notifications module owner**

In `modules/notifications/overview.md`, change the Owner field from Dev 4 to Dev 2:
```
**Owner:** Dev 2
```

- [ ] **Step 4: Update Configuration module owner**

In `modules/configuration/overview.md`, change the Owner field from Dev 1 to Dev 4:
```
**Owner:** Dev 4
```

- [ ] **Step 5: Verify all phase markers are consistent**

Run: `grep -H '**Phase:**' modules/*/overview.md | sort`

Expected Phase 1 (15): activity-monitoring, agent-gateway, auth, calendar, configuration, core-hr, exception-engine, identity-verification, infrastructure, leave, notifications, org-structure, productivity-analytics, shared-platform, workforce-presence

Expected Phase 2 (7): documents, expense, grievance, payroll, performance, reporting-engine, skills

- [ ] **Step 6: Commit**

```bash
git add modules/payroll/overview.md modules/calendar/overview.md modules/notifications/overview.md modules/configuration/overview.md
git commit -m "chore: update module phase markers — payroll→phase2, calendar→phase1, reassign owners"
```

---

## Task 2: Delete Deferred Task Files

**Files:**
- Delete: `current-focus/DEV3-payroll.md`
- Delete: `current-focus/DEV2-performance.md`
- Delete: `current-focus/DEV4-supporting-bridges.md`

- [ ] **Step 1: Delete DEV3-payroll.md**

```bash
git rm current-focus/DEV3-payroll.md
```

- [ ] **Step 2: Delete DEV2-performance.md**

```bash
git rm current-focus/DEV2-performance.md
```

- [ ] **Step 3: Delete DEV4-supporting-bridges.md**

This file is dissolved — Calendar goes to DEV3, Notifications goes to DEV2, Configuration goes to DEV4 (each as standalone task files created in later tasks). Documents, Grievance, Expense, and WorkManage Pro Bridges are all deferred to Phase 2.

```bash
git rm current-focus/DEV4-supporting-bridges.md
```

- [ ] **Step 4: Commit**

```bash
git add -A current-focus/
git commit -m "chore: remove deferred task files — payroll, performance, supporting-bridges dissolved"
```

---

## Task 3: Create DEV3-calendar.md

**Files:**
- Create: `current-focus/DEV3-calendar.md`

- [ ] **Step 1: Create the task file**

Write `current-focus/DEV3-calendar.md` with the following content:

```markdown
# Task: Calendar Module

**Assignee:** Dev 3
**Module:** Calendar
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel, multi-tenancy)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `calendar_events` table — unified calendar with polymorphic `source_type` + `source_id`
- [ ] Event types: `company`, `team`, `personal`, `leave`, `holiday`, `review`
- [ ] Source types: `manual`, `leave_request`, `holiday`, `review_cycle`
- [ ] Visibility levels: `public`, `team`, `private`
- [ ] CRUD endpoints: `GET/POST/PUT/DELETE /api/v1/calendar`
- [ ] `ICalendarConflictService` — detect overlapping events for employee + date range
- [ ] Conflict detection excludes `leave` and `holiday` event types
- [ ] Conflict severity: `review` and `company` = high, `team` and `personal` = medium
- [ ] `GET /api/v1/calendar/conflicts` endpoint — requires `leave:create` or `leave:approve`
- [ ] Domain events: `CalendarEventCreated`, `CalendarEventUpdated`, `CalendarEventDeleted`
- [ ] Listen for `LeaveApproved` → auto-create calendar event with `source_type=leave_request`
- [ ] Listen for `LeaveCancelled` → auto-delete corresponding calendar event
- [ ] Company holiday seeding via tenant setup
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/calendar/overview|Calendar Module]] — module architecture, public interface
- [[modules/calendar/calendar-events/overview|Calendar Events]] — table schema, API endpoints
- [[modules/calendar/conflict-detection/overview|Conflict Detection]] — ICalendarConflictService, business rules
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped events

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/
├── calendar/page.tsx         # Unified calendar view
```

### What to Build

- [ ] Unified calendar view: monthly with color-coded events (leave=blue, holiday=green, review=orange, company=purple, team=teal, personal=gray)
- [ ] Create manual calendar events (company, team, personal types)
- [ ] Edit/delete own events
- [ ] Filter by event type
- [ ] Conflict warning display when viewing date ranges with overlapping events
- [ ] PermissionGate: authenticated (all users can view), event creation based on role

### Userflows

- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]] — create calendar events
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — detect scheduling conflicts

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/calendar` | Calendar events for date range |
| POST | `/api/v1/calendar` | Create event |
| PUT | `/api/v1/calendar/{id}` | Update event |
| DELETE | `/api/v1/calendar/{id}` | Delete event |
| GET | `/api/v1/calendar/conflicts` | Conflict check for date range |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Calendar, Badge, Dialog
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel, multi-tenancy
- [[current-focus/DEV1-leave|DEV1 Leave]] — Leave module consumes ICalendarConflictService from this module
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — permission checks
```

- [ ] **Step 2: Commit**

```bash
git add current-focus/DEV3-calendar.md
git commit -m "chore: create DEV3-calendar task file — extracted from supporting-bridges, unblocks Leave"
```

---

## Task 4: Create DEV2-notifications.md

**Files:**
- Create: `current-focus/DEV2-notifications.md`

- [ ] **Step 1: Create the task file**

Write `current-focus/DEV2-notifications.md` with the following content:

```markdown
# Task: Notifications Module

**Assignee:** Dev 2
**Module:** Notifications
**Priority:** High
**Dependencies:** [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (notification scaffolding), [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] (exception alert event types)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `notification_templates` table — per event_type per channel (email, in_app, signalr)
- [ ] Template rendering via Liquid/Handlebars
- [ ] `notification_channels` table — email (Resend), in-app, SignalR
- [ ] 6-step notification pipeline: event → resolve recipients → load template → render → dispatch → log
- [ ] Event types for Workforce Intelligence: `exception.alert.created`, `exception.alert.escalated`, `verification.failed`, `agent.heartbeat.lost`, `productivity.daily.report`, `productivity.weekly.report`
- [ ] Event types for HR: `leave.requested`, `leave.approved`, `leave.rejected`, `review.cycle.started`, `onboarding.started`
- [ ] SignalR hub at `/hubs/notifications`
- [ ] SignalR channels: `notifications-{userId}`, `exception-alerts`, `workforce-live`, `agent-status`
- [ ] `GET /api/v1/notifications` — list notifications (paginated)
- [ ] `PUT /api/v1/notifications/{id}/read` — mark as read
- [ ] `PUT /api/v1/notifications/read-all` — mark all as read
- [ ] `GET/PUT /api/v1/notifications/preferences` — user notification preferences
- [ ] Domain event listeners for all registered event types
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/notifications/overview|Notifications Module]] — module architecture, pipeline, channels
- [[modules/notifications/notification-templates/overview|Notification Templates]] — template schema, rendering
- [[modules/notifications/notification-channels/overview|Notification Channels]] — channel providers
- [[modules/notifications/signalr-real-time/overview|SignalR Real-Time]] — real-time push channels
- [[backend/notification-system|Notification System]] — system-wide notification architecture

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/
├── components/topbar/notification-bell.tsx    # Notification bell in topbar
├── settings/notifications/page.tsx            # Notification preferences
```

### What to Build

- [ ] Notification bell in topbar: dropdown list of recent notifications, unread count badge
- [ ] Notification preferences page: per-event-type channel toggles (email, in-app)
- [ ] Real-time notification delivery via SignalR (`@microsoft/signalr`)
- [ ] Toast notifications for high-priority alerts
- [ ] PermissionGate: `notifications:read`, `notifications:manage`

### Userflows

- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]] — configure notification preferences
- [[Userflow/Notifications/notification-view|Notification View]] — view notifications

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/notifications` | List notifications |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| GET | `/api/v1/notifications/preferences` | Notification preferences |
| PUT | `/api/v1/notifications/preferences` | Update preferences |
| SignalR | `/hubs/notifications` | `notifications-{userId}` channel |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Badge, Dropdown, Switch
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern
- [[frontend/data-layer/state-management|State Management]] — SignalR integration with TanStack Query

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — notification scaffolding
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — exception alerts flow through notifications
- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — report-ready events delivered via notifications
```

- [ ] **Step 2: Commit**

```bash
git add current-focus/DEV2-notifications.md
git commit -m "chore: create DEV2-notifications task file — extracted from supporting-bridges"
```

---

## Task 5: Create DEV4-configuration.md

**Files:**
- Create: `current-focus/DEV4-configuration.md`

- [ ] **Step 1: Create the task file**

Write `current-focus/DEV4-configuration.md` with the following content:

```markdown
# Task: Configuration Module

**Assignee:** Dev 4
**Module:** Configuration
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (industry profile seeding), [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (tenant context)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `tenant_settings` table — timezone, date format, work hours, privacy mode
- [ ] `monitoring_feature_toggles` table — global ON/OFF per monitoring feature
- [ ] Industry profile default seeding (office_it, manufacturing, retail, healthcare, custom)
- [ ] `employee_monitoring_overrides` table — per-employee feature overrides
- [ ] Merge logic: employee override wins over tenant toggle
- [ ] Bulk override API: set by department/team/job family
- [ ] `integration_connections` table — external service connections
- [ ] `retention_policies` table — per data type retention periods
- [ ] `app_allowlist` table — application allowlist by scope (tenant, department, team, employee)
- [ ] Resolved allowlist API: merge tenant → department → team → employee scopes
- [ ] `IConfigurationService` public interface with all methods
- [ ] `GET/PUT /api/v1/config/monitoring-toggles` — feature toggles
- [ ] `GET/PUT /api/v1/config/employee-overrides` — employee overrides
- [ ] `POST /api/v1/config/employee-overrides/bulk` — bulk set overrides
- [ ] `GET/PUT /api/v1/config/retention-policies` — retention policies
- [ ] `GET/PUT /api/v1/config/tenant-settings` — tenant settings
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/configuration/overview|Configuration Module]] — module architecture, IConfigurationService
- [[modules/configuration/monitoring-toggles/overview|Monitoring Toggles]] — toggle schema, industry defaults
- [[modules/configuration/employee-overrides/overview|Employee Overrides]] — override merge logic
- [[modules/configuration/tenant-settings/overview|Tenant Settings]] — settings schema
- [[modules/configuration/retention-policies/overview|Retention Policies]] — per-type retention
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant context

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/settings/
├── monitoring/page.tsx       # Monitoring feature toggles + employee overrides
├── retention/page.tsx        # Data retention policies
├── tenant/page.tsx           # Tenant settings (timezone, work hours, etc.)
├── integrations/page.tsx     # Integration connections
```

### What to Build

- [ ] Monitoring toggles page: master toggle per feature (screenshots, app tracking, meeting detection, etc.)
- [ ] Employee override management: search employee, toggle individual features
- [ ] Bulk override: select department/team, apply overrides
- [ ] Retention policy management: per data type, retention period
- [ ] Tenant settings page: timezone, date format, work hours, privacy mode
- [ ] Integration connections: list, add, test connections
- [ ] PermissionGate: `monitoring:view-settings`, `monitoring:configure`, `settings:manage`

### Userflows

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — toggle monitoring features
- [[Userflow/Configuration/employee-override|Employee Override]] — override monitoring per employee
- [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]] — configure data retention
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — manage tenant settings

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/config/monitoring-toggles` | Feature toggles |
| PUT | `/api/v1/config/monitoring-toggles` | Update toggles |
| GET | `/api/v1/config/employee-overrides` | Employee overrides |
| PUT | `/api/v1/config/employee-overrides` | Update overrides |
| POST | `/api/v1/config/employee-overrides/bulk` | Bulk set overrides |
| GET | `/api/v1/config/retention-policies` | Retention policies |
| PUT | `/api/v1/config/retention-policies` | Update policies |
| GET | `/api/v1/config/tenant-settings` | Tenant settings |
| PUT | `/api/v1/config/tenant-settings` | Update settings |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Switch, DataTable, Dialog, Select
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — settings page layout
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — industry profile seeding
- [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] — activity monitoring reads toggles from this module
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence features gated by toggles
- [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] — identity verification toggled here
```

- [ ] **Step 2: Commit**

```bash
git add current-focus/DEV4-configuration.md
git commit -m "chore: create DEV4-configuration task file — extracted from supporting-bridges"
```

---

## Task 6: Relabel All Task Files — Phase → Step

**Files:**
- Modify: All 12 remaining `current-focus/DEV*-*.md` files (the 3 new ones already use Step 1/2)

Files to modify:
- `current-focus/DEV1-infrastructure-setup.md`
- `current-focus/DEV1-core-hr-profile.md`
- `current-focus/DEV1-leave.md`
- `current-focus/DEV1-productivity-analytics.md`
- `current-focus/DEV2-auth-security.md`
- `current-focus/DEV2-core-hr-lifecycle.md`
- `current-focus/DEV2-exception-engine.md`
- `current-focus/DEV3-org-structure.md`
- `current-focus/DEV3-workforce-presence-setup.md`
- `current-focus/DEV3-activity-monitoring.md`
- `current-focus/DEV4-shared-platform-agent-gateway.md`
- `current-focus/DEV4-workforce-presence-biometric.md`
- `current-focus/DEV4-identity-verification.md`

- [ ] **Step 1: In each file, replace `## Phase 1: Backend` with `## Step 1: Backend`**

For every file listed above, find:
```
## Phase 1: Backend
```
Replace with:
```
## Step 1: Backend
```

- [ ] **Step 2: In each file, replace `## Phase 2: Frontend` with `## Step 2: Frontend`**

For every file listed above, find:
```
## Phase 2: Frontend
```
Replace with:
```
## Step 2: Frontend
```

- [ ] **Step 3: Verify no Phase 1/Phase 2 labels remain in task files**

Run: `grep -rn 'Phase 1: Backend\|Phase 2: Frontend' current-focus/DEV*-*.md`

Expected: No results.

- [ ] **Step 4: Commit**

```bash
git add current-focus/DEV*-*.md
git commit -m "chore: relabel Phase 1/2 → Step 1/2 in all task files — prevents ADE misinterpretation"
```

---

## Task 7: Rewrite current-focus/README.md

**Files:**
- Modify: `current-focus/README.md`

- [ ] **Step 1: Replace the full content of `current-focus/README.md`**

```markdown
# Current Focus: ONEVO

**Current Phase:** Phase 1
**Team Size:** 4 developers
**Development Approach:** Agentic Development Environment (AI-assisted)

---

## How to Use This Folder

Each file below is a **self-contained task** for one developer. It includes:
1. **Step 1: Backend** — acceptance criteria, module docs links
2. **Step 2: Frontend** — pages to build, userflow links, API endpoints to consume

The dev builds backend first, then frontend for the same module. Each task file links to the relevant [[Userflow/README|Userflows]] so the AI knows the full user journey and API contracts.

---

## Task Assignment — Dev 1

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Infrastructure & Foundation | Infrastructure + SharedKernel | Critical | [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] |
| 2 | Employee Profile | CoreHR | Critical | [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] |
| 3 | Leave | Leave | High | [[current-focus/DEV1-leave|DEV1 Leave]] |
| 4 | Productivity Analytics | ProductivityAnalytics | High | [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] |

**Dev 1 Frontend Pages:** Dashboard layout, Employee list/detail/create, Leave management, Productivity reports

---

## Task Assignment — Dev 2

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Auth & Security | Auth | Critical | [[current-focus/DEV2-auth-security|DEV2 Auth Security]] |
| 2 | Employee Lifecycle | CoreHR | Critical | [[current-focus/DEV2-core-hr-lifecycle|DEV2 Core Hr Lifecycle]] |
| 3 | Exception Engine | ExceptionEngine | Critical | [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] |
| 4 | Notifications | Notifications | High | [[current-focus/DEV2-notifications|DEV2 Notifications]] |

**Dev 2 Frontend Pages:** Login/MFA/Password reset, Role/User management, Onboarding/Offboarding, Exception dashboard, Notification bell + preferences

---

## Task Assignment — Dev 3

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Org Structure | OrgStructure | Critical | [[current-focus/DEV3-org-structure|DEV3 Org Structure]] |
| 2 | Calendar | Calendar | High | [[current-focus/DEV3-calendar|DEV3 Calendar]] |
| 3 | Workforce Presence (Setup) | WorkforcePresence | Critical | [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] |
| 4 | Activity Monitoring | ActivityMonitoring | Critical | [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] |

**Dev 3 Frontend Pages:** Department/Team/Job management, Unified calendar, Shift/Holiday management, Live workforce dashboard, Activity detail/screenshots

---

## Task Assignment — Dev 4

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Shared Platform + Agent Gateway | SharedPlatform + AgentGateway | Critical | [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] |
| 2 | Configuration | Configuration | High | [[current-focus/DEV4-configuration|DEV4 Configuration]] |
| 3 | Identity Verification | IdentityVerification | High | [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] |
| 4 | Workforce Presence (Biometric) | WorkforcePresence | Critical | [[current-focus/DEV4-workforce-presence-biometric|DEV4 Workforce Presence Biometric]] |

**Dev 4 Frontend Pages:** Settings (monitoring config, tenant settings, integrations, retention), Agent management, Biometric devices, Attendance/Overtime, Verification log

---

## Task Execution Order

Tasks are numbered 1-4 per developer. **Task 1 should be built first** (it's the foundation). Tasks 2-4 proceed after task 1 is complete, but some have cross-dev dependencies noted in each task file.

### Critical Path

```
DEV1: Infrastructure Setup ──> (all other tasks depend on this)
DEV2: Auth & Security ──────> (all modules use RBAC from this)
```

These two tasks **must be completed first** before other devs can make progress.

### Cross-Dev Dependencies

```
DEV3 Calendar (task 2) ──> unblocks DEV1 Leave (task 3)
DEV3 Workforce Presence Setup (task 3) ──> unblocks DEV4 Biometric (task 4)
DEV3 Activity Monitoring (task 4) ──> unblocks DEV1 Productivity Analytics (task 4)
DEV4 Shared Platform (task 1) ──> unblocks DEV2 Notifications (task 4)
```

---

## What We Are NOT Working On Right Now

- **Payroll** — deferred to Phase 2
- **Performance** — deferred to Phase 2
- **Documents** — deferred to Phase 2
- **Grievance** — deferred to Phase 2
- **Expense** — deferred to Phase 2
- **Reporting Engine** — deferred to Phase 2
- **Skills & Learning** — deferred to Phase 2
- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **WorkManage Pro Bridges** — deferred to Phase 2
- **Desktop Agent code** — in scope, follows Agent Gateway completion (see `agent/AI_CONTEXT/`)
- **Teams Graph API deep integration** — Phase 2; Phase 1 uses process name detection
- **Meilisearch** — PostgreSQL FTS sufficient for Phase 1
- **RabbitMQ** — using in-process domain events; RabbitMQ for scale later

---

## Milestones

| Milestone | Scope | Notes |
|:----------|:------|:------|
| Foundation complete | DEV1 task 1 + DEV2 task 1 | All other tasks depend on this |
| Core modules complete | All devs task 2 | Calendar, Lifecycle, Configuration, Employee Profile |
| Extended modules complete | All devs task 3 | Leave, Exception Engine, Presence, Identity Verification |
| All Phase 1 modules complete | All devs task 4 | Productivity, Notifications, Activity Monitoring, Biometric |
| Integration testing | All devs | Buffer for cross-module testing |

---

## Frontend Phase (Per Module)

Each dev builds the frontend for their module **immediately after** completing the backend for that module. Frontend tasks are defined in each task file under "Step 2: Frontend".

### Key Frontend Resources

- [[frontend/architecture/app-structure|Frontend Structure]] — Next.js app directory layout
- [[frontend/design-system/README|Design System]] — shadcn/ui components, design tokens
- [[frontend/design-system/components/component-catalog|Component Catalog]] — all UI components
- [[frontend/data-layer/api-integration|API Integration]] — API client, error handling, pagination
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand
- [[frontend/coding-standards|Frontend Coding Standards]] — conventions

### Frontend Priority Order (if time is tight)

1. **Auth flow** — login, MFA, token management (DEV2)
2. **Dashboard layout** — sidebar, topbar, permission-based navigation (DEV1)
3. **Workforce Intelligence pages** — live dashboard, activity detail, exceptions (DEV3 + DEV2)
4. **HR pages** — employees, leave, calendar (DEV1 + DEV3)
5. **Settings** — monitoring configuration, tenant settings (DEV4)
6. **Employee self-service** — own dashboard, own leave (DEV1)

---

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[backend/module-catalog|Module Catalog]]
- [[AI_CONTEXT/rules|Rules]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[ade/README|ADE Orchestrator Instructions]]
```

- [ ] **Step 2: Verify no date references remain**

Run: `grep -n '2026-04\|2026-05\|Week [0-9]' current-focus/README.md`

Expected: No results.

- [ ] **Step 3: Commit**

```bash
git add current-focus/README.md
git commit -m "chore: rewrite current-focus README — new Phase 1 assignments, remove dates, fix labeling"
```

---

## Task 8: Remove Date References From Task Files

**Files:**
- Modify: All `current-focus/DEV*-*.md` files that contain date references

- [ ] **Step 1: Check which task files have date references**

Run: `grep -rn 'Week [0-9]\|April\|2026-04\|2026-05' current-focus/DEV*-*.md`

Note: References like "Weekly" in `DEV1-productivity-analytics.md` (e.g., `GenerateWeeklyReportsJob`, `WeeklyReportReady`, `weekly`) are feature names, NOT date references — do NOT remove these.

- [ ] **Step 2: Remove owner date references in task file headers**

In each task file that has an owner line like `**Owner:** Dev X (Week N)`, remove the `(Week N)` portion. For example:
```
**Owner:** Dev 3 (Week 2)
```
becomes:
```
**Owner:** Dev 3
```

- [ ] **Step 3: Verify no date references remain (excluding feature names)**

Run: `grep -rn 'Week [0-9]\|April\|2026-04\|2026-05' current-focus/DEV*-*.md`

Expected: No results (feature names like `Weekly` won't match `Week [0-9]`).

- [ ] **Step 4: Commit**

```bash
git add current-focus/DEV*-*.md
git commit -m "chore: remove date references from task files"
```

---

## Task 9: Update Cross-References in Remaining Task Files

**Files:**
- Modify: Task files that reference deleted files

- [ ] **Step 1: Find references to deleted task files**

Run: `grep -rn 'DEV3-payroll\|DEV2-performance\|DEV4-supporting-bridges' current-focus/`

- [ ] **Step 2: Update references**

For any file that references `DEV3-payroll`: remove the reference or replace with a note that Payroll is deferred to Phase 2.

For any file that references `DEV2-performance`: remove the reference or replace with a note that Performance is deferred to Phase 2.

For any file that references `DEV4-supporting-bridges`: replace with the correct new task file reference:
- Calendar references → `[[current-focus/DEV3-calendar|DEV3 Calendar]]`
- Notifications references → `[[current-focus/DEV2-notifications|DEV2 Notifications]]`
- Configuration references → `[[current-focus/DEV4-configuration|DEV4 Configuration]]`

- [ ] **Step 3: Also update module overview cross-references**

Run: `grep -rn 'DEV4-supporting-bridges\|DEV3-payroll\|DEV2-performance' modules/`

Update any module overviews that reference deleted task files to point to the correct new task files.

- [ ] **Step 4: Verify no broken references remain**

Run: `grep -rn 'DEV3-payroll\|DEV2-performance\|DEV4-supporting-bridges' current-focus/ modules/`

Expected: No results.

- [ ] **Step 5: Commit**

```bash
git add current-focus/ modules/
git commit -m "chore: update cross-references for restructured task files"
```

---

## Task 10: Update DEV4 Task File Ordering

**Files:**
- Modify: `current-focus/DEV4-shared-platform-agent-gateway.md`
- Modify: `current-focus/DEV4-identity-verification.md`
- Modify: `current-focus/DEV4-workforce-presence-biometric.md`

The new DEV4 order is:
1. Shared Platform + Agent Gateway (was task 1 — unchanged)
2. Configuration (new file — already created)
3. Identity Verification (was task 3 — unchanged)
4. Workforce Presence Biometric (was task 2 — **moved to task 4**)

- [ ] **Step 1: Update DEV4-workforce-presence-biometric.md dependencies**

Add a dependency note that this task now depends on DEV3 Workforce Presence Setup:
```
**Dependencies:** [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] (presence session schema)
```

Ensure the task header does NOT reference a week number.

- [ ] **Step 2: Verify DEV4 task files are consistent**

Check that each DEV4 task file header has the correct assignee and no date references:
```bash
grep -A5 '# Task:' current-focus/DEV4-*.md
```

- [ ] **Step 3: Commit**

```bash
git add current-focus/DEV4-*.md
git commit -m "chore: reorder DEV4 tasks — biometric moved to task 4, configuration added as task 2"
```

---

## Task 11: Create ADE Orchestrator Instructions

**Files:**
- Create: `ade/README.md`

- [ ] **Step 1: Create the ade directory**

```bash
mkdir -p ade
```

- [ ] **Step 2: Create `ade/README.md`**

Write `ade/README.md` with the following content:

```markdown
# ADE — Agentic Development Environment

## Overview

The ADE enables AI-assisted development. A developer says "I'm Dev N, finish my remaining tasks" and an AI orchestrator manages the work automatically.

The orchestrator lives in this brain repo. It reads task definitions, injects context into worker agents, and tracks progress via checkboxes.

---

## Repos

| Repo | Purpose | ADE Access |
|:-----|:--------|:-----------|
| **Brain repo** (this vault) | Knowledge base, task definitions, rules, specs | Read context + update checkboxes |
| **Backend repo** (.NET 9) | Backend code | Write code (Step 1) |
| **Frontend repo** (Next.js 14) | Frontend code | Write code (Step 2) |
| **Desktop Agent repo** (.NET MAUI) | Desktop agent code | Write code (DEV4 agent tasks only) |

---

## Orchestrator Flow

```
Input: dev_id, paths to brain + backend + frontend + agent repos

1. Read all task files: current-focus/DEV{dev_id}-*.md
2. Parse checkboxes — identify unchecked acceptance criteria
3. Determine task order (task # from README table)
4. For each task (SEQUENTIAL):
   a. Read the task file's "Related Tasks" section
   b. Check if cross-dev dependencies exist in the code repos
      - e.g., Does ICalendarConflictService exist in the backend repo?
   c. If dependency MISSING → SKIP (do NOT mark checkbox)
   d. If dependencies MET → Spawn worker agent
5. After all tasks processed:
   → Report: completed tasks, skipped/blocked tasks with reasons
```

### Cross-Dev Dependency Check

The orchestrator checks if required interfaces/services exist in the target code repo before spawning a worker. If a dependency is missing, the task is skipped — **checkboxes are NOT marked** for skipped tasks.

Example check: Before starting DEV1's Leave task, check if `ICalendarConflictService` exists in the backend repo. If not, skip Leave and report: "Leave blocked — Calendar module not found. Re-run after DEV3 delivers."

### Stop and Report

After completing all unblocked tasks, the orchestrator stops and reports:
```
Session complete.
  ✓ Completed: Task 1 (Infrastructure), Task 2 (Employee Profile)
  ✗ Blocked: Task 3 (Leave) — needs ICalendarConflictService from DEV3 Calendar
  ✗ Blocked: Task 4 (Productivity Analytics) — needs IActivityMonitoringService from DEV3

  Re-run after DEV3 delivers Calendar and Activity Monitoring.
```

The dev re-runs the ADE manually when blocking dependencies are delivered.

---

## Worker Agent

### Context Injection (Layered)

**Base layer (always injected):**
- `AI_CONTEXT/rules.md`
- `AI_CONTEXT/project-context.md`
- `AI_CONTEXT/tech-stack.md`
- `AI_CONTEXT/known-issues.md`

**Task-specific layer:**
- The task file (e.g., `current-focus/DEV1-leave.md`)
- All files under the module folder (e.g., `modules/leave/**`)
- All referenced userflows (e.g., `Userflow/Leave/**`)
- Related module overviews if cross-module interaction exists

### Worker Flow

```
1. Receive context (base + task layer)
2. Read unchecked acceptance criteria from task file
3. Execute Step 1: Backend
   - Write code in the BACKEND repo
   - Check off each criterion as completed
   - Commit to backend repo
4. Execute Step 2: Frontend
   - Write code in the FRONTEND repo
   - Check off each criterion as completed
   - Commit to frontend repo
5. Update checkboxes in the BRAIN repo task file
6. Return completion status to orchestrator
```

---

## Parallelism

- **Dev-scoped sequential:** Each dev's ADE session runs tasks 1 → 2 → 3 → 4 sequentially
- **Cross-dev parallel:** Multiple devs can run their ADE sessions simultaneously (different modules, no conflicts)
- **Step-scoped sequential:** Within each task, Step 1 (backend) completes before Step 2 (frontend) starts

---

## Progress Tracking

- **Checkboxes in task files** are the single source of truth
- Workers mark `- [ ]` → `- [x]` as they complete each criterion
- Orchestrator reads checkbox state to determine remaining work
- Skipped/blocked tasks leave checkboxes untouched

---

## How to Run

```
$ ade run --dev {N} --brain ./onevo-hr-brain --backend ./onevo-backend --frontend ./onevo-frontend --agent ./onevo-desktop-agent
```

Where:
- `--dev {N}` — Developer number (1-4)
- `--brain` — Path to this brain repo
- `--backend` — Path to the .NET 9 backend repo
- `--frontend` — Path to the Next.js 14 frontend repo
- `--agent` — Path to the .NET MAUI desktop agent repo (optional, only needed for DEV4)

---

## Related

- [[current-focus/README|Current Focus]] — Task assignments and dependency chain
- [[AI_CONTEXT/rules|Rules]] — AI agent coding rules
- [[AI_CONTEXT/project-context|Project Context]] — System architecture
- [[docs/superpowers/specs/2026-04-08-phase1-restructure-and-ade-design|Design Spec]] — Full design decisions and rationale
```

- [ ] **Step 3: Commit**

```bash
git add ade/
git commit -m "chore: create ADE orchestrator instructions"
```

---

## Task 12: Final Verification

- [ ] **Step 1: Verify file structure**

Run: `ls current-focus/`

Expected files:
```
DEV1-core-hr-profile.md
DEV1-infrastructure-setup.md
DEV1-leave.md
DEV1-productivity-analytics.md
DEV2-auth-security.md
DEV2-core-hr-lifecycle.md
DEV2-exception-engine.md
DEV2-notifications.md
DEV3-activity-monitoring.md
DEV3-calendar.md
DEV3-org-structure.md
DEV3-workforce-presence-setup.md
DEV4-configuration.md
DEV4-identity-verification.md
DEV4-shared-platform-agent-gateway.md
DEV4-workforce-presence-biometric.md
README.md
```

NOT present: `DEV3-payroll.md`, `DEV2-performance.md`, `DEV4-supporting-bridges.md`

- [ ] **Step 2: Verify no Phase 1/2 labels in task files**

```bash
grep -rn 'Phase 1: Backend\|Phase 2: Frontend' current-focus/
```

Expected: No results.

- [ ] **Step 3: Verify no date references**

```bash
grep -rn '2026-04\|2026-05\|Week [0-9]' current-focus/
```

Expected: No results.

- [ ] **Step 4: Verify no broken references to deleted files**

```bash
grep -rn 'DEV3-payroll\|DEV2-performance\|DEV4-supporting-bridges' current-focus/ modules/ ade/
```

Expected: No results.

- [ ] **Step 5: Verify module phase markers**

```bash
grep -H '**Phase:**' modules/*/overview.md | sort
```

Expected: 15 modules Phase 1, 7 modules Phase 2.
