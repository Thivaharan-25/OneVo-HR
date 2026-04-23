# Unified Platform Architecture Plan
**Status:** Design Freeze Candidate | **Date:** 2026-04-21 | **Author:** Architecture Session

> **Purpose:** This document is the single source of truth for how ONEVO and WMS coexist as one platform. Both teams must agree on this before writing a single line of backend code. Disagreements here become 6-month refactors later.

---

## 0. The Correct Mental Model

### What We're Actually Building

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ONEVO PLATFORM                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ONEVO FRONTEND (Next.js)                   │  │
│  │                                                              │  │
│  │  ┌──────────────────┐   ┌──────────────────────────────────┐ │  │
│  │  │   HR Sidebar      │   │   Workforce Sidebar              │ │  │
│  │  │  (Pillar 1 UI)    │   │  (Pillar 2 + WMS UI)            │ │  │
│  │  │                   │   │                                  │ │  │
│  │  │  Leave            │   │  Workforce Presence              │ │  │
│  │  │  Performance      │   │  Activity Monitoring             │ │  │
│  │  │  Skills           │   │  ─────────────────               │ │  │
│  │  │  Payroll          │   │  Projects (WMS)                  │ │  │
│  │  │  Org Structure    │   │  Tasks (WMS)                     │ │  │
│  │  │  Documents        │   │  Sprints (WMS)                   │ │  │
│  │  └──────────────────┘   │  Time Tracking (WMS)             │ │  │
│  │                          │  Chat (WMS)                      │ │  │
│  │                          │  OKR (WMS)                       │ │  │
│  │                          └──────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         │                     │                     │
│              ┌──────────▼──────┐   ┌──────────▼──────────┐        │
│              │  ONEVO Backend   │   │    WMS Backend       │        │
│              │  (.NET 9)        │◄──►  (WMS Team's stack) │        │
│              │                  │   │                      │        │
│              │  HR, Workforce,  │   │  Projects, Tasks,    │        │
│              │  Auth, Payroll,  │   │  Sprints, Chat,      │        │
│              │  Notifications,  │   │  OKR, Analytics      │        │
│              │  File Storage    │   │                      │        │
│              └──────────────────┘   └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

**Key facts:**
- WMS team builds and owns their backend
- ONEVO team builds the WMS frontend that lives inside this platform (Workforce sidebar)
- ONEVO team builds and owns their backend (HR + Workforce Intelligence + shared infra)
- The two backends talk via defined bridge API contracts
- The ONEVO frontend consumes BOTH backends — it knows which APIs to call for which sections
- **No code starts until both teams agree on the contracts in this document**

---

## 1. Entity Ownership Map — The Ground Truth

This is the canonical answer to "who owns what entity." Duplication = data conflicts. Every entity lives in exactly one backend.

### ONEVO OWNS (Canonical — WMS reads these via bridge)

| Entity | ONEVO Table | Notes |
|--------|-------------|-------|
| Organization/Company | `tenants` | WMS calls this "workspace" in UI — it's the same row |
| User Identity | `users` | Authentication identity for ALL products. One login. |
| HR Record | `employees` | Always created even for WMS-only (identity anchor), but HR fields null/hidden |
| Departments | `departments` | ONEVO is hierarchical (unlimited nesting). WMS reads via People Sync. |
| Org Teams | `teams` | ONEVO organizational teams (department sub-groups). WMS reads via People Sync. |
| Roles | `roles` | One role system. WMS maps ONEVO roles → WMS permissions via `wms_role_mappings`. |
| Permissions | `role_permissions`, `employee_permission_grants` | ONEVO permission model. |
| Skills Catalog | `skills`, `skill_categories` | ONEVO is canonical. WMS reads via Skills bridge. |
| Employee Skills | `employee_skills` | WMS reads validated skills for resource matching. |
| Leave Records | `leave_requests`, `leave_balances` | WMS reads blocked days via Availability bridge. |
| Shifts & Schedules | `shift_templates`, `employee_schedules` | WMS reads for capacity planning. |
| Public Holidays | `calendar_events` (type=public_holiday) | WMS reads for sprint date adjustment. |
| Overtime Entries | `overtime_entries` | ONEVO calculates from WMS time logs + presence. WMS never stores overtime. |
| Payroll | All payroll tables | WMS has zero payroll tables. Payroll is purely ONEVO. |
| Notifications | `notifications`, `notification_deliveries` | Unified inbox. WMS pushes notification events to ONEVO. |
| File Storage Metadata | `file_assets`, `file_versions` | Both teams upload to same blob bucket. ONEVO holds metadata. |
| Tenant Config / Branding | `tenant_configurations` | Industry profile, branding, feature flags. |
| Performance Reviews | All performance tables (Phase 2) | WMS provides productivity input scores, ONEVO runs the review. |

### WMS OWNS (WMS Backend — ONEVO reads these via WMS API)

| Entity | WMS Table | Notes |
|--------|-----------|-------|
| Projects | `projects` | ONEVO frontend reads to display in sidebar. |
| Project Members | `project_members` | Who is on which project (references ONEVO employee_id). |
| Epics | `epics` | |
| Milestones | `milestones` | |
| Tasks / Issues | `tasks` | Core WMS entity. References ONEVO employee_id for assignees. |
| Task Assignments | `task_assignees` | References ONEVO employee_id. |
| Bug Reports | `bug_reports` | |
| Sprints | `sprints` | |
| Boards | `boards`, `board_views` | |
| Roadmap | `roadmaps`, `roadmap_items` | |
| Releases / Versions | `versions`, `release_calendar` | |
| Task Time Logs | `time_logs` | WMS stores. Posts to ONEVO Work Activity bridge. |
| Timesheets | `timesheets`, `timesheet_entries` | WMS manages. Not ONEVO's concern. |
| Timer Sessions | `timer_sessions` | |
| Resource Plans | `resource_plans`, `capacity_snapshots` | WMS allocates project resources. ONEVO provides skill data. |
| Chat Channels | `channels`, `channel_members` | |
| Messages | `messages`, `dm_channels` | |
| Comments | `comments`, `reactions`, `mentions` | |
| Wiki Pages | `wiki_pages`, `wiki_versions` | Project documentation. |
| WMS Documents | `wms_documents`, `document_versions` | Project docs (NOT HR documents — those are ONEVO). |
| OKR / Goals | `objectives`, `key_results`, `okr_updates` | Business objectives. Links to ONEVO Performance goals in Phase 2. |
| WMS Reminders | `reminders`, `reminder_schedules` | WMS stores, delivers via ONEVO notification API. |
| WMS Activity Log | `wms_activity_logs` | Project-level activity (task moved, comment added). Not ONEVO audit log. |
| WMS Integrations | `integrations`, `webhooks` | WMS-side external integrations (GitHub, Figma, etc.). |
| WMS Dashboards | `dashboards`, `chart_widgets` | WMS analytics. |
| Forms | `forms`, `form_submissions` | |
| Productivity Scores | Computed by WMS, pushed to ONEVO | See bridge contracts below. |

### CONFLICT RESOLUTIONS — These were the hard decisions

| Conflict | Decision | Reason |
|----------|----------|--------|
| WMS `WORKSPACE` | → ONEVO `tenants` | Same concept. WMS uses ONEVO tenant_id as workspace_id. No WMS workspace table. |
| WMS `AUTH_ACCOUNT` | → ONEVO `users` | One login. WMS validates ONEVO JWTs. Zero WMS auth tables. |
| WMS `ROLE` | → ONEVO `roles` | One role per org. `wms_role_mappings` translates ONEVO roles → WMS permissions. |
| WMS `DEPARTMENT` | → ONEVO `departments` | ONEVO is richer (hierarchical). WMS reads via People Sync bridge. |
| WMS `TEAM` (project teams) | **WMS OWNS** as `wms_project_teams` | Different concept from ONEVO org teams. WMS ad-hoc project teams ≠ org hierarchy. |
| WMS `SKILL` + `USER_SKILL` | → ONEVO `skills` + `employee_skills` | ONEVO is canonical. WMS reads via Skills bridge. No WMS skill tables. |
| WMS `NOTIFICATION` | → ONEVO Notifications | ONEVO is canonical. WMS calls ONEVO notification push endpoint. |
| WMS `FILE_ASSET` | → ONEVO `file_assets` | Same blob storage. ONEVO holds metadata. WMS stores file URLs referencing same bucket. |
| WMS `AUDIT_LOG` (auth) | → ONEVO `audit_logs` | Auth/security events only in ONEVO. WMS project activity → `wms_activity_logs`. |
| WMS `OVERTIME_ENTRY` | **Does not exist in WMS** | ONEVO calculates overtime from WMS time logs + presence data. WMS never touches overtime. |
| WMS `OBJECTIVE`/`KEY_RESULT` (OKR) | **WMS OWNS** | Business objectives. ONEVO Performance module has HR development goals. Different purpose. Phase 2: link them. |
| WMS `DOCUMENT` (project docs) | **WMS OWNS** as `wms_documents` | ONEVO `documents` = HR docs (contracts, policies). WMS docs = project wikis, specs. |
| WMS `REMINDER` | **WMS OWNS** for storage | WMS stores schedules. ONEVO delivers via notification API. No conflict. |
| WMS `TIMESHEET` | **WMS OWNS** | Project timesheets ≠ payroll hours. ONEVO payroll uses presence hours. Bridge for overlap. |

---

## 2. CoreHR as Selective Base

CoreHR always exists in every tenant. What changes per product tier is which **sections** of CoreHR are active.

```
CoreHR Sections + What Activates Them:

Section                      | WMS Only | HR Tier | Full Suite | Always
─────────────────────────────────────────────────────────────────────
user_identity (name, avatar) |    ✓     |    ✓    |     ✓      |   ✓
org_assignment (dept, team)  |    ✓     |    ✓    |     ✓      |   ✓
employee_shell (employee_id) |    ✓     |    ✓    |     ✓      |   ✓  ← anchor for WMS
direct_reports_hierarchy     |    ✓     |    ✓    |     ✓      |   ✓  ← task scoping in WMS
employee_lifecycle           |    ✗     |    ✓    |     ✓      |
salary_management            |    ✗     |    ✓    |     ✓      |
employment_contract          |    ✗     |    ✓    |     ✓      |
onboarding_workflow          |    ✗     |    ✓    |     ✓      |
offboarding_workflow         |    ✗     |    ✓    |     ✓      |
emergency_contacts           |    ✗     |    ✓    |     ✓      |
leave_eligibility            |    ✗     |    ✓    |     ✓      |
```

**WMS-only customers:** An `employees` row is created for every user (we need `employee_id` as the universal person identifier). But it contains only: id, user_id, department_id, team_id, manager_id, display_name, avatar_url, timezone, job_title. All salary/lifecycle/leave columns are null and all CoreHR UI sections are hidden.

---

## 3. Product Configuration Matrix (Option C)

```
TIER                     | Core | HR Pillar | Workforce | WMS  | Bridges
─────────────────────────────────────────────────────────────────────────
HR Management            |  ✓   |     ✓     |     ✗     |  ✗   |   ✗
Work Management          |  ✓   |     ✗     |     ✗     |  ✓   |  partial¹
HR + Workforce Intel     |  ✓   |     ✓     |     ✓     |  ✗   |   ✗
HR + Work Management     |  ✓   |     ✓     |     ✗     |  ✓   |  all 5²
Full Suite               |  ✓   |     ✓     |     ✓     |  ✓   |  all 5
─────────────────────────────────────────────────────────────────────────

Core (always): Infrastructure + Auth + CoreHR identity + Notifications + SharedPlatform

Add-ons within HR Pillar: Payroll, Performance, Advanced Skills, Documents
Add-ons within WMS: Resource Management, OKR, Chat, Advanced Analytics

¹ WMS-only gets People Sync (read employee list) but no Availability/Payroll bridges
² All 5 bridges active: People Sync, Availability, Skills, Work Activity, Productivity Metrics
```

---

## 4. Common Infrastructure (ONEVO Builds, WMS Consumes)

Both teams must agree on these before sprint 1.

### 4.1 Authentication — ONEVO is canonical

**JWT format (RS256):**
```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "employee_id": "employee-uuid",
  "email": "user@company.com",
  "permissions": ["leave:read", "tasks:write", "payroll:view"],
  "wms_access": true,
  "exp": 1714000000,
  "iss": "onevo-auth"
}
```

**WMS uses:**
- Same JWT — validates with ONEVO's public key (exposed at `GET /api/v1/auth/.well-known/jwks.json`)
- No WMS login page, no WMS auth tables, no WMS refresh tokens
- `employee_id` in JWT = the foreign key WMS uses for task assignees, time logs, etc.
- `wms_access: true` = this tenant has WMS enabled

**Both teams agree:** When ONEVO rotates keys, WMS gets notified via webhook.

### 4.2 Notifications — ONEVO is canonical

WMS pushes notification events to ONEVO. ONEVO delivers them (in-app, email, push).

**WMS calls:**
```
POST /api/v1/notifications/external
Authorization: Bearer {bridge_api_key}
{
  "tenant_id": "tenant-uuid",
  "recipient_employee_id": "employee-uuid",
  "event_type": "task_assigned" | "task_due_soon" | "sprint_starting" | "mention" | ...,
  "title": "You've been assigned Task #123",
  "body": "Project Alpha — Fix login bug",
  "action_url": "/workforce/wms/tasks/task-uuid",
  "priority": "normal" | "high",
  "metadata": { "task_id": "...", "project_id": "..." }
}
```

ONEVO's Notifications module routes it through the normal delivery pipeline (email, in-app, push). The user sees one notification inbox — ONEVO handles all deliveries.

### 4.3 File Storage — Shared Bucket, ONEVO Holds Metadata

Both backends upload to the same blob storage bucket (Railway/S3), scoped by tenant prefix:
```
bucket/
  {tenant_id}/
    hr/           ← ONEVO HR documents, avatars
    wms/          ← WMS task attachments, project files
    agent/        ← WorkPulse Agent screenshots
```

ONEVO exposes a pre-signed upload URL endpoint:
```
POST /api/v1/files/upload-url
{ "scope": "wms", "file_name": "design.fig", "mime_type": "..." }
→ { "upload_url": "...", "file_asset_id": "uuid", "expires_in": 300 }
```

WMS uses this URL to upload. `file_asset_id` is then stored in WMS tables referencing the file.

**Why:** One storage billing, one ACL policy, one expiry management system.

### 4.4 Calendar — Frontend Merge, No Shared DB

ONEVO calendar holds HR events. WMS holds project events. They're different and should stay separate. The ONEVO frontend calendar view aggregates both:

```typescript
// ONEVO frontend — unified calendar view
const [hrEvents] = useQuery('/api/v1/calendar/events')          // ONEVO API
const [wmsEvents] = useQuery('${WMS_API}/calendar/events')      // WMS API
const unified = mergeAndSort([...hrEvents, ...wmsEvents])
```

No shared calendar DB table. No sync job. Frontend aggregation is enough.

### 4.5 Reminders — WMS Stores, ONEVO Delivers

WMS stores reminder schedules in their own `reminders` table. When a reminder fires, WMS calls the ONEVO notification push endpoint (4.2 above). The user sees it in their ONEVO notification inbox.

---

## 5. Bridge API Contracts — The Design Freeze Line

**No code starts until both teams sign off on these.**

### 5.1 ONEVO → WMS (What We Provide)

#### People Sync — Employee List
```
GET /api/v1/bridges/people-sync/employees
Headers: X-Bridge-Key: {bridge_api_key}

Response:
{
  "employees": [
    {
      "employee_id": "uuid",
      "user_id": "uuid",
      "display_name": "Sarah Chen",
      "email": "sarah@company.com",
      "avatar_url": "https://...",
      "timezone": "Asia/Kuala_Lumpur",
      "department_id": "uuid",
      "department_name": "Engineering",
      "team_id": "uuid",
      "team_name": "Backend Team",
      "job_title": "Senior Engineer",
      "manager_employee_id": "uuid",
      "employment_type": "full_time",
      "hire_date": "2024-01-15",
      "is_active": true,
      "wms_role_permissions": ["project:create", "task:assign", "sprint:manage"],
      "skill_ids": ["uuid1", "uuid2"]
    }
  ],
  "last_updated": "2026-04-21T10:00:00Z"
}
```
**When to call:** WMS polls daily at midnight. ONEVO also pushes via webhook on EmployeeCreated, EmployeePromoted, EmployeeTransferred, EmployeeTerminated.

#### Availability — Blocked Days + Shift Hours
```
GET /api/v1/bridges/availability/{employee_id}?from=2026-05-01&to=2026-05-31
Headers: X-Bridge-Key: {bridge_api_key}

Response:
{
  "employee_id": "uuid",
  "availability": {
    "leave_periods": [
      { "start_date": "2026-05-10", "end_date": "2026-05-12", "type": "annual", "status": "approved" }
    ],
    "public_holidays": [
      { "date": "2026-05-01", "name": "Labour Day" }
    ],
    "shift": {
      "daily_start": "09:00",
      "daily_end": "17:00",
      "expected_daily_hours": 7,
      "working_days": ["monday","tuesday","wednesday","thursday","friday"]
    },
    "presence_today": "present",
    "capacity_pct_this_period": 78
  }
}
```
**When to call:** Before assigning tasks, before sprint planning, when building capacity views.

#### Skills — Validated Employee Skills
```
GET /api/v1/bridges/skills/{employee_id}
Headers: X-Bridge-Key: {bridge_api_key}

Response:
{
  "employee_id": "uuid",
  "skills": [
    { "skill_id": "uuid", "name": "React", "category": "Frontend", "proficiency": "advanced", "validated_at": "2026-01-15" },
    { "skill_id": "uuid", "name": "TypeScript", "category": "Frontend", "proficiency": "expert", "validated_at": "2026-02-01" }
  ]
}
```

#### Leave Impact — Will This Employee Be Available?
```
GET /api/v1/bridges/leave-impact/{employee_id}?start_date=2026-05-01&end_date=2026-05-14
Headers: X-Bridge-Key: {bridge_api_key}

Response:
{
  "employee_id": "uuid",
  "will_be_absent": true,
  "absent_days": ["2026-05-10", "2026-05-11", "2026-05-12"],
  "expected_available_hours": 49,
  "open_task_ids": ["uuid1", "uuid2"]
}
```
**When to call:** WMS displays this when a manager tries to assign a task during a period.

### 5.2 WMS → ONEVO (What WMS Provides)

#### Work Activity — Daily Task Time Logs
```
POST /api/v1/bridges/work-activity/time-logs
Headers: X-Bridge-Key: {bridge_api_key}

Body:
{
  "tenant_id": "uuid",
  "date": "2026-04-21",
  "entries": [
    {
      "employee_id": "uuid",
      "task_id": "wms-task-uuid",
      "task_title": "Fix login bug",
      "project_id": "wms-project-uuid",
      "project_name": "Project Alpha",
      "duration_mins": 360,
      "is_completed": true
    },
    {
      "employee_id": "uuid",
      "task_id": "wms-task-uuid-2",
      "task_title": "Code review for PR #45",
      "project_id": "wms-project-uuid",
      "project_name": "Project Alpha",
      "duration_mins": 180,
      "is_completed": true
    }
  ]
}
```
**When to post:** WMS posts daily at EOD (23:00) per tenant, and on task completion.
**ONEVO uses for:** Overtime engine, Discrepancy Engine, Productivity Analytics.

#### Productivity Metrics — Monthly Scores
```
POST /api/v1/bridges/productivity-metrics
Headers: X-Bridge-Key: {bridge_api_key}

Body:
{
  "tenant_id": "uuid",
  "period_type": "monthly",
  "period_start": "2026-04-01",
  "period_end": "2026-04-30",
  "metrics": [
    {
      "employee_id": "uuid",
      "tasks_completed": 34,
      "tasks_on_time": 29,
      "on_time_delivery_rate": 85.3,
      "productivity_score": 78.5,
      "velocity_story_points": 42,
      "active_projects": 3
    }
  ]
}
```
**When to post:** WMS posts at end of each week (weekly) and end of each month (monthly).
**ONEVO uses for:** Performance appraisal composite score, bonus recommendations.

---

## 6. Key Automation Flows

### 6.1 Overtime Detection → Payroll (The Main Example)

**Scenario:** Employee has 7h standard day. WMS logs: Task A completed (6h) + Task B completed (3h) = 9h. Employee's agent/biometric shows they stayed 2h past shift end.

```
STEP 1 — WMS posts time logs at EOD
POST /api/v1/bridges/work-activity/time-logs
  entries: [Task A: 360mins, Task B: 180mins] for employee_id

STEP 2 — ONEVO Overtime Engine runs (Hangfire job: 23:30 every weekday)
  a. Fetch employee shift today: shift_end = 17:00, standard_hours = 7h
  b. Fetch WMS task logs today: 360 + 180 = 540 mins = 9h
  c. Fetch agent presence today: clock-in 09:00, clock-out 19:00 = 10h
     OR biometric: in 09:00, out 19:00
  d. Overtime = actual_presence_end (19:00) - shift_end (17:00) = 2h
  e. Corroboration: WMS task logs (9h) > standard (7h) ✓ — confirms why they stayed
  f. Create overtime_entry:
     employee_id, date, minutes=120, source="wms_task_completion",
     wms_task_refs=["task-a-id","task-b-id"], status="pending"

STEP 3 — Manager Approval (or auto-approval if policy allows)
  Manager sees overtime request in ONEVO → approves
  overtime_entry.status = "approved"

STEP 4 — Payroll Month-End Run
  Standard hours this month:
    work_days = 22
    public_holidays = 1  (from ONEVO calendar_events)
    billable_days = 21
    standard_hours = 21 × 7 = 147h

  Overtime this month (from overtime_entries):
    Apr 21: 2h (task completion)
    Apr 15: 3h (sprint deadline)
    Apr 8:  3h (release deployment)
    Total: 8h overtime

  Unpaid leave this month (from leave_requests):
    Apr 10: 1 day unpaid
    Apr 17: 1 day unpaid
    Total: 2 days = 14h

  Performance bonus (from bonus_grants approved by manager):
    Q1 target achieved → $500

  Calculation:
    hourly_rate = $4,900 / 147h = $33.33/h
    base        = $4,900.00
    overtime    = 8h × $33.33 × 1.5 = $400.00
    bonus       = $500.00
    unpaid_deduction = 14h × $33.33 = -$466.67
    NET = $5,333.33

STEP 5 — Payroll Slip

  EARNINGS (+)
  ├─ Base Salary (21 days × 7h = 147h @ $33.33/h)       $4,900.00
  ├─ Overtime (8h @ $50/h — 1.5× rate)                    $400.00
  │   ├─ Apr 21: 2h — Task A + Task B completion
  │   ├─ Apr 15: 3h — Sprint Alpha deadline
  │   └─ Apr 8:  3h — Release deployment
  └─ Performance Bonus                                      $500.00
      └─ Reason: Q1 OKR target achieved (Manager approved)

  DEDUCTIONS (-)
  └─ Unpaid Leave (2 days = 14h @ $33.33/h)              -$466.67
      ├─ Apr 10: Personal leave (unpaid)
      └─ Apr 17: Personal leave (unpaid)

  NET PAY                                                 $5,333.33
```

### 6.2 Leave → WMS Task Availability (Automatic)

```
Employee requests leave Apr 10-12
  → Manager approves in ONEVO
  → ONEVO fires: LeaveApprovedEvent

ONEVO WMS Bridge handler reacts:
  → Calls WMS webhook: POST {wms_webhook}/leave-approved
    { employee_id, start_date, end_date, leave_type }
  → WMS frontend shows warning on any task assigned to this employee in that date range
  → WMS sprint planner highlights capacity gap
  → Sprint capacity calculation auto-reduces available hours for this employee
```

### 6.3 Employee Created → WMS Access Provisioned (Automatic)

```
HR Admin hires employee in ONEVO
  → EmployeeCreated domain event fires
  → People Sync bridge handler:
    POST {wms_webhook}/employee-sync
    { employee_id, user_id, email, department_id, role_id, wms_permissions }
  → WMS creates user record referencing ONEVO employee_id
  → Employee can now log in with their ONEVO credentials and access WMS immediately
  → No manual WMS account setup
```

### 6.4 Employee Terminated → WMS Access Revoked (Automatic)

```
HR Admin triggers termination in ONEVO
  → EmployeeTerminated domain event fires
  → People Sync bridge handler:
    POST {wms_webhook}/employee-offboarded
    { employee_id, effective_date }
  → WMS deactivates user, reassigns open tasks to manager
  → JWT invalidated by ONEVO (employee_id flagged as terminated)
  → WMS access dropped on next API call (JWT validation fails)
```

### 6.5 Productivity Score → Performance Appraisal (Automatic)

```
WMS posts monthly productivity metrics
  → ONEVO stores in wms_productivity_snapshots

Performance review cycle starts (Phase 2)
  → Performance module reads IProductivityAnalyticsService:
    - Agent-based score: keyboard activity, app usage, presence consistency
    - WMS-based score: on_time_delivery_rate, productivity_score, velocity
  → Composite score = weighted average of both
  → Shown to manager during appraisal as "Work Intelligence Score"
  → Manager approves performance bonus
  → Bonus written to bonus_grants table
  → Payroll picks it up in next run (see Flow 6.1)
```

### 6.6 Skill Gap Signal → HR Action (Phase 2, Automatic)

```
WMS observes: Employee repeatedly fails skill requirements for assigned tasks
  → WMS posts: POST /api/v1/bridges/skills/{employee_id}/gap-report
    { skill_id, observed_gap_level, task_evidence_ids[] }
  → ONEVO writes to employee_skills with source="wms_observed"
  → Skills dashboard surfaces: "WMS-observed gap in React (Advanced required)"
  → HR can trigger: course assignment, mentorship pairing, skill reassessment
```

---

## 7. Integration Registry — What Auto-Connects When Both Modules Enabled

```
Module A              + Module B               → Auto-enabled integration
─────────────────────────────────────────────────────────────────────────────
Leave                 + WorkforcePresence       → Approved leave marks shift as absent
Leave                 + WMS                     → Leave approved → WMS capacity warning
Leave                 + Payroll                 → Approved unpaid leave → payroll deduction
WorkforcePresence     + ActivityMonitoring      → Presence session correlates agent snapshots
WorkforcePresence     + WMS (time logs)         → Overtime engine: presence + task logs → overtime_entry
ActivityMonitoring    + ExceptionEngine         → Agent snapshots → anomaly rule evaluation
WMS (time logs)       + Payroll                 → Overtime entries from WMS data → payroll line item
WMS (productivity)    + Performance             → Monthly WMS scores → appraisal composite input
WMS (productivity)    + Payroll                 → Approved bonus_grant → payroll bonus line item
CoreHR                + WMS                     → EmployeeCreated/Terminated → WMS access provision/revoke
Skills                + WMS (resource)          → ONEVO validated skills → WMS resource matching
```

Each row is implemented as: Module A publishes domain event → Integration handler (in Module B or bridge layer) reacts → Module B updates its state. The handler only runs if both modules are enabled for the tenant.

---

## 8. Module Independence Framework

Each optional module follows this contract:

```
Module contract:
  1. STANDALONE: Works with only Mandatory Core (Infrastructure + Auth + CoreHR identity)
  2. INTEGRATION: Registers event handlers for other modules' events when both are active
  3. GRACEFUL DEGRADATION: If paired module is disabled, module still works, just fewer features

Example — Leave module:
  Standalone: Leave requests work without Payroll, without WMS
  + Payroll:  LeaveApproved → PayrollAdjustment handler activates
  + WMS:      LeaveApproved → WMS capacity warning handler activates
  + WorkforcePresence: LeaveApproved → shift marked absent
  Missing any of these: Leave still processes correctly, that integration just skips
```

**Integration activation rule:** A handler is registered only if `ModuleRegistry.IsEnabled(tenantId, requiredModule)` returns true. This is checked at startup per tenant and cached in Redis.

---

## 9. Industry Profile System

Industry profiles are database-driven. Adding a new industry = insert a row. Zero code change.

```sql
-- industry_profiles table
{
  slug: "information_technology",
  display_name: "Information Technology",
  module_config: [
    { module: "core-hr",              visible: true, order: 1, required: true,  defaults: {} },
    { module: "leave",                visible: true, order: 2, required: false, defaults: { accrual_type: "monthly" } },
    { module: "workforce-presence",   visible: true, order: 3, required: false, defaults: { mode: "agent-based" } },
    { module: "activity-monitoring",  visible: true, order: 4, required: false, defaults: { screenshot_capture: false } },
    { module: "wms",                  visible: true, order: 5, required: false, defaults: {} },
    { module: "payroll",              visible: true, order: 6, required: false, defaults: {} },
    { module: "performance",          visible: true, order: 7, required: false, defaults: {} }
  ],
  monitoring_defaults: { mode: "full", privacy_transparency: "partial", idle_threshold_secs: 300 }
}

-- manufacturing
{
  slug: "manufacturing",
  module_config: [
    { module: "core-hr",             visible: true, order: 1, required: true },
    { module: "workforce-presence",  visible: true, order: 2, required: true, defaults: { mode: "biometric" } },
    { module: "leave",               visible: true, order: 3, required: false },
    { module: "payroll",             visible: true, order: 4, required: false },
    { module: "activity-monitoring", visible: false },  ← hidden, irrelevant
    { module: "wms",                 visible: false }   ← hidden by default
  ],
  monitoring_defaults: { mode: "biometric-only", privacy_transparency: "full" }
}

-- healthcare
{
  slug: "healthcare",
  module_config: [
    { module: "core-hr",             visible: true, order: 1, required: true },
    { module: "leave",               visible: true, order: 2, required: true },
    { module: "workforce-presence",  visible: true, order: 3, required: true, defaults: { mode: "biometric" } },
    { module: "documents",           visible: true, order: 4 },  ← compliance docs prominent
    { module: "activity-monitoring", visible: false },
    { module: "payroll",             visible: true, order: 5 }
  ],
  monitoring_defaults: { mode: "minimal", privacy_transparency: "full" }
}

-- retail
{
  slug: "retail",
  module_config: [
    { module: "core-hr",             visible: true, order: 1, required: true },
    { module: "workforce-presence",  visible: true, order: 2, required: true, defaults: { mode: "biometric" } },
    { module: "leave",               visible: true, order: 3 },
    { module: "payroll",             visible: true, order: 4 },
    { module: "activity-monitoring", visible: false },  ← no desktops
    { module: "performance",         visible: false }
  ],
  monitoring_defaults: { mode: "biometric-only" }
}
```

Tenants can change their industry profile from settings. When changed: ONEVO recalculates module visibility + defaults, updates Redis cache, frontend reflects new sidebar on next load.

---

## 10. Platform Admin (Same App — Special Role)

> **Update:** The `/platform-admin` concept has been promoted to a separate standalone app — see `developer-platform/overview.md` for the full specification.

~~Lives inside the ONEVO frontend at `/platform-admin`, guarded by `platform:admin` permission (only ONEVO team accounts get this, never customers).~~

~~**Phase 1 scope (minimal, ship early):**~~
~~- Tenant list: name, plan, status, employee count, created date~~
~~- Per-tenant: feature flags override, subscription status, last login~~
~~- Billing sync: Stripe plan → tenant tier (auto-synced via Stripe webhooks)~~
~~- Impersonate tenant: "View as this tenant's super admin" (for support)~~
~~- Suspend / unsuspend tenant~~

~~**Not in Phase 1:** System health dashboard (use Grafana which is already in tech stack), log viewer, infrastructure metrics. These come in Phase 2 as operational needs become clear.~~

---

## 11. MVP Slice — Build This First

The goal of the MVP is to prove ONE complete automation flow end-to-end: hire employee → assign WMS task → overtime detected → shows on payroll breakdown.

**MVP scope:**

```
ONEVO Backend (MVP):
├── Infrastructure: tenants, users, file_assets, countries
├── Auth: JWT (RS256), sessions, MFA, roles, permissions
├── OrgStructure: departments, teams, job_families (basic)
├── CoreHR: employee identity layer only (hire → employee shell created)
├── Leave: leave types, policies, requests, approvals
├── WorkforcePresence: shifts, schedules, biometric/agent clock-in
├── SharedPlatform: feature_flags, module_registry, industry_profiles (IT only)
├── Notifications: unified inbox + WMS push endpoint
└── Payroll foundation: standard hours calc + overtime entries + basic slip

ONEVO Backend (MVP bridges):
├── People Sync: GET /api/v1/bridges/people-sync/employees
├── Availability: GET /api/v1/bridges/availability/{employee_id}
└── Work Activity: POST /api/v1/bridges/work-activity/time-logs

WMS Backend (MVP — WMS team):
├── Auth: JWT validation using ONEVO public key
├── Projects: basic project + members
├── Tasks: create, assign, complete
└── Time Logs: log time per task, post to ONEVO Work Activity bridge at EOD

ONEVO Frontend (MVP):
├── Auth flow (login, MFA, forgot password)
├── HR sidebar: Employee list, Leave requests, Basic org chart
├── Workforce sidebar: Shift view, Presence dashboard
├── WMS sidebar: Task list, basic board view (consuming WMS API)
└── Payroll slip view: one employee, one month, shows breakdown

PROVE: Assign task in WMS → employee logs 9h → presence shows 2h overtime → payroll slip shows overtime line with task reference
```

---

## 12. Build Phase Plan

### Phase 0 — Design Freeze (2 weeks, no code)
**Both teams deliver:**
- [ ] Sign off on entity ownership table (Section 1 of this doc)
- [ ] Agree on JWT format (Section 4.1)
- [ ] Agree on notification push schema (Section 4.2)
- [ ] Agree on file storage approach (Section 4.3)
- [ ] Agree on all bridge request/response schemas (Section 5)
- [ ] Agree on bridge API key management (how issued, rotated, revoked)
- [ ] WMS team defines their webhook format (for ONEVO to call when events happen)

**Output:** This document + `backend/bridge-api-contracts.md` updated → Design Freeze signed

### Phase 1 — Common Infrastructure (Weeks 1-2, ONEVO team)
```
Infrastructure module: tenants, users, file_assets, countries, industry_profiles table
Auth module: JWT (RS256), sessions, MFA, roles, permissions, audit_logs
Notifications module: in-app, email (Resend), push, WMS push endpoint
SharedPlatform: feature_flags, module_registry, subscription plans
AgentGateway: device registration, JWT, policy endpoint (needed by WorkPulse)
```

**Deliverable to WMS team:** JWT public key endpoint + notification push endpoint

### Phase 2 — CoreHR + OrgStructure (Weeks 2-3, ONEVO team)
```
OrgStructure: departments (hierarchical), teams, job_families, job_levels
CoreHR: employee identity layer (create employee shell on user invite)
CoreHR full: lifecycle, salary, contracts (if HR tier enabled)
People Sync bridge: GET /api/v1/bridges/people-sync/employees (LIVE)
```

**Deliverable to WMS team:** People Sync endpoint is live — WMS can now pull employees

### Phase 3 — HR Operational Modules (Weeks 3-5, ONEVO team)
```
Leave: types, policies, entitlements, requests, approvals
WorkforcePresence: shifts, schedules, biometric events, agent presence
Availability bridge: GET /api/v1/bridges/availability/{id} (LIVE)
Leave Impact bridge: GET /api/v1/bridges/leave-impact/{id} (LIVE)
```

**Deliverable to WMS team:** Availability + Leave Impact bridges live — WMS sprint planning can show blocked days

### Phase 4 — Payroll + Overtime Engine (Weeks 5-7, ONEVO team)
```
Payroll module: salary calculation, overtime rate policies, deductions
Overtime Engine: Hangfire job (EOD) — reads WMS time logs + presence → overtime_entries
Work Activity bridge: POST /api/v1/bridges/work-activity/time-logs (LIVE)
Payroll slip: breakdown with INCREASED/DECREASED sections + reasons
```

**Deliverable to WMS team:** Work Activity bridge is live — WMS can start posting time logs

### Phase 5 — WMS Modules (Weeks 3-8, WMS team + ONEVO frontend)
```
WMS team builds: Auth (JWT validation), Projects, Tasks, Time Logs, Planning
ONEVO frontend: WMS task views, board, sprint planner (consuming WMS API)
Notification integration: WMS calls ONEVO push endpoint for task events
```

### Phase 6 — Extended Modules (Weeks 8-12)
```
ONEVO: Skills (full), ActivityMonitoring, ExceptionEngine, IdentityVerification
ONEVO: ProductivityAnalytics, wms_productivity_snapshots, Productivity Metrics bridge
WMS: Resource Management, OKR, Chat, Collaboration modules
ONEVO frontend: WMS resource, OKR, chat views
```

### Phase 7 — Performance + Bonus Loop (Weeks 12-14)
```
ONEVO: Performance module (Phase 2) — reads wms_productivity_snapshots + agent scores
ONEVO: bonus_grants table + approval flow → payroll integration
ONEVO: Payroll slip shows: performance bonus with reason, linked to review cycle
```

### Phase 8 — Industry Profiles + Multi-Industry (Weeks 14-16)
```
Manufacturing profile: biometric presence, shift focus, WMS hidden by default
Healthcare profile: compliance docs prominent, minimal monitoring
Retail profile: biometric + shifts, no desktop monitoring
Industry switcher in tenant settings (changeable, re-evaluates module config)
```

### Phase 9 — Platform Admin (Weeks 16-17)
```
/platform-admin route (guarded by platform:admin permission)
Tenant management: list, view, suspend/unsuspend
Feature flag override per tenant (for sales/support use)
Billing sync: Stripe webhooks → tenant plan updates
Impersonation: view as tenant super admin
```

---

## 13. Questions That Must Be Answered in Phase 0 Meeting

These cannot be decided by ONEVO team alone:

1. **Bridge API Key:** How does ONEVO issue the bridge API key to WMS? Is it per-tenant (each tenant has its own bridge key) or per-system (one key for all WMS-to-ONEVO calls)? Per-tenant is more secure.

2. **WMS Webhook URL:** When ONEVO needs to push to WMS (e.g., EmployeeCreated), where does it call? WMS needs to provide a webhook endpoint and its own auth (shared secret or API key).

3. **Error Handling:** If WMS posts time logs and ONEVO is down, does WMS retry? What's the retry policy? Need to agree: exponential backoff, max 3 retries, 24h TTL.

4. **WMS employee_id format:** WMS task assignees reference ONEVO's `employee_id` (UUID). WMS team must use `employee_id` (not `user_id`, not email) as the foreign key for all cross-system references.

5. **Tenant linkage:** When a customer buys both HR + WMS, how are the tenants linked? ONEVO creates tenant first → generates `tenant_id` → shares with WMS → WMS stores `onevo_tenant_id` as their workspace reference. WMS team must store this.

6. **Bridge call frequency limits:** What is the WMS polling rate for People Sync? Agreement needed: max 1 poll/hour, ONEVO pushes webhooks for real-time changes.

---

*This document is living — update it when decisions change. Do not build against a version of this without confirming it's the latest.*
