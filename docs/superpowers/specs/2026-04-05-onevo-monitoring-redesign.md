# ONEVO Platform Redesign — Workforce Intelligence + HR Management

**Date:** 2026-04-05
**Status:** Design approved, pending implementation
**Scope:** Full secondary brain redesign (backend + frontend + agent brains)

---

## 1. Problem Statement

The current ONEVO secondary brain documents a traditional HR Management SaaS (126 tables, 18 modules). A key client requires workforce monitoring and productivity intelligence — real-time activity tracking, idle detection, application usage monitoring, meeting time analysis, device tracking, identity verification, exception-based alerting, and executive dashboards.

The current architecture lacks:
- Real-time activity monitoring (keyboard/mouse tracking)
- Application/tool usage tracking
- Idle time detection and measurement
- Meeting time analysis
- Device usage tracking
- Photo/biometric identity verification at intervals
- Exception detection engine with anomaly alerting
- Workforce productivity dashboards
- Exception-based escalation system

The redesign integrates monitoring as a first-class pillar alongside HR, rather than bolting it on.

---

## 2. Product Architecture — Two Pillars

ONEVO becomes a two-pillar platform with a shared foundation:

```
ONEVO PLATFORM
├── Pillar 1: HR Management
│   Core HR, Org Structure, Leave, Performance, Skills & Learning,
│   Payroll, Documents, Grievance, Expense
│
├── Pillar 2: Workforce Intelligence
│   Activity Monitoring, Workforce Presence (replaces Attendance),
│   Identity Verification, Exception Engine, Productivity Analytics
│
├── Shared Foundation
│   Auth, Notifications, Workflows, Reporting Engine, Configuration,
│   Calendar, Compliance, Billing, Agent Gateway (NEW)
│
└── Connectivity Bridges
    People Sync, Availability, Performance, Skills,
    Work Activity (NEW — for WorkManage Pro integration)
```

### External Components

- **Desktop Agent** (.NET Windows Service + MAUI tray app) — installed on employee laptops, captures activity data
- **WorkManage Pro** (separate product, separate team) — project/task management, connected via bridges

### Selling Configurations

| Configuration | What's Included |
|:-------------|:----------------|
| HR Management (standalone) | Pillar 1 + Shared Foundation |
| HR + Workforce Intelligence | Pillar 1 + Pillar 2 + Shared Foundation + Desktop Agent |
| HR + Work Management | Pillar 1 + Shared Foundation + WorkManage Pro bridges |
| Full Suite | All pillars + bridges + Desktop Agent + WorkManage Pro |

---

## 3. Monitoring Configuration Model

Monitoring features are granular and configurable at two levels:

### Tenant Level (Company Settings)

**Industry profiles** (selected at signup, sets defaults):
- Office/IT — all monitoring features ON by default
- Manufacturing — biometric/presence ON, screen/keyboard OFF
- Retail — biometric ON, device monitoring OFF
- Healthcare — minimal, compliance-focused
- Custom — admin picks everything manually

**Global feature toggles:**
- Activity Monitoring (keyboard/mouse) ON/OFF
- Application Tracking ON/OFF
- Screenshot Capture ON/OFF
- Meeting Time Detection ON/OFF
- Device Usage Tracking ON/OFF
- Identity Verification (photo) ON/OFF
- Biometric (fingerprint) ON/OFF

### Employee Level (Overrides)

Admins can override per employee, per department, per team, or per job family:
- Employee A (office IT worker) → all features ON
- Employee B (warehouse worker) → biometric only
- Employee C (CEO) → exempt, all OFF
- Employee D → custom selection

The desktop agent reads its policy from the server on login and only activates what's enabled for that specific employee.

### Privacy Configuration

Three transparency modes (per tenant):
- **Full transparency** — employees see what's tracked and their own data
- **Partial transparency** — employees see own data but not tracking rules
- **Covert** — employer only (tenant must confirm legal compliance)

---

## 4. Module Catalog — 22 Modules, ~138 Tables

### Pillar 1: HR Management (9 modules)

| # | Module | Change from Original | Tables |
|:--|:-------|:--------------------|:-------|
| 1 | Infrastructure | Minor — add industry_profile to tenants | 4 |
| 2 | Auth & Security | Unchanged | 8 |
| 3 | Org Structure | Unchanged | 8 |
| 4 | Core HR | Unchanged | 13 |
| 5 | Leave | Unchanged | 5 |
| 6 | Performance | Enhanced — receives productivity scores from Workforce Intelligence | 7 |
| 7 | Skills & Learning | Unchanged | 15 |
| 8 | Payroll | Enhanced — receives actual hours from Workforce Presence | 11 |
| 9 | Documents | Unchanged | 5 |

### Pillar 2: Workforce Intelligence (5 modules — new/reshaped)

| # | Module | Purpose | Tables |
|:--|:-------|:--------|:-------|
| 10 | Workforce Presence | Replaces old Attendance. Unifies biometric clock-in, desktop agent presence, shifts, schedules, overtime, corrections. Single source of "is this person present?" | 12 |
| 11 | Activity Monitoring | Receives raw data from desktop agent — app usage, keyboard/mouse metrics, idle periods, meeting detection, screenshots | 8 |
| 12 | Identity Verification | Photo verification at login/logout/intervals, biometric fingerprint matching, verification policies | 6 |
| 13 | Exception Engine | Anomaly detection rules, threshold triggers, alert generation, escalation chains | 5 |
| 14 | Productivity Analytics | Aggregates Pillar 2 data into daily/weekly/monthly reports, workforce dashboards, trends | 4 |

### Shared Foundation (8 modules)

| # | Module | Change from Original | Tables |
|:--|:-------|:--------------------|:-------|
| 15 | Shared Platform | Enhanced — monitoring policy config, industry profiles | 21 |
| 16 | Notifications | Enhanced — exception alerts, escalation notifications | 2 |
| 17 | Configuration | Enhanced — monitoring toggles, per-employee overrides | 5 |
| 18 | Calendar | Unchanged | 1 |
| 19 | Reporting Engine | Reshaped — serves both HR and workforce reports | 3 |
| 20 | Grievance | Unchanged | 2 |
| 21 | Expense | Unchanged | 3 |
| 22 | Agent Gateway | NEW — desktop agent data ingestion, agent registration, policy distribution | 3 |

**Grand Total: 22 modules, ~138 tables**

---

## 5. Database Schema — New & Reshaped Tables

### Module 10: Workforce Presence (12 tables)

**Kept from old Attendance (9 tables):**
`shifts`, `work_schedules`, `employee_shift_assignments`, `holidays`, `schedule_templates`, `employee_work_schedules`, `attendance_records`, `overtime_requests`, `attendance_corrections`

**New tables (3):**

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `presence_sessions` | Unified presence — one row/employee/day, combines biometric + agent data | `employee_id`, `tenant_id`, `date`, `first_seen_at`, `last_seen_at`, `total_present_minutes`, `source` (biometric/agent/manual), `status` (present/absent/partial) |
| `device_sessions` | Tracks designated laptop active vs idle | `employee_id`, `tenant_id`, `device_id`, `session_start`, `session_end`, `active_minutes`, `idle_minutes`, `active_percentage` |
| `break_records` | Tracks breaks (lunch, prayer, smoke, etc.) | `employee_id`, `tenant_id`, `break_start`, `break_end`, `break_type`, `auto_detected` (boolean) |

**Moved to Identity Verification:** `biometric_devices`, `biometric_enrollments`, `biometric_events`, `biometric_audit_logs`

### Module 11: Activity Monitoring (8 tables)

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `activity_snapshots` | Periodic activity data from agent (every 2-3 min) | `employee_id`, `tenant_id`, `captured_at`, `keyboard_events_count`, `mouse_events_count`, `active_seconds`, `idle_seconds`, `intensity_score` (0-100) |
| `application_usage` | Time per application | `employee_id`, `tenant_id`, `date`, `application_name`, `application_category`, `window_title_hash`, `total_seconds`, `is_productive` (nullable boolean) |
| `meeting_sessions` | Detected meeting time | `employee_id`, `tenant_id`, `meeting_start`, `meeting_end`, `platform` (teams/zoom/meet), `duration_minutes`, `had_camera_on`, `had_mic_activity` |
| `screenshots` | Optional periodic screenshots | `employee_id`, `tenant_id`, `captured_at`, `file_record_id`, `trigger_type` (scheduled/random/manual) |
| `activity_daily_summary` | Pre-aggregated daily rollup (Hangfire) | `employee_id`, `tenant_id`, `date`, `total_active_minutes`, `total_idle_minutes`, `total_meeting_minutes`, `active_percentage`, `top_apps_json`, `intensity_avg`, `keyboard_total`, `mouse_total` |
| `application_categories` | Tenant-configurable app categorization | `tenant_id`, `application_name_pattern`, `category`, `is_productive`, `created_by_id` |
| `device_tracking` | Device interaction tracking | `employee_id`, `tenant_id`, `date`, `laptop_active_minutes`, `estimated_mobile_minutes`, `laptop_percentage`, `detection_method` |
| `activity_raw_buffer` | Temporary high-volume buffer (partitioned, auto-purged after aggregation) | `agent_device_id`, `tenant_id`, `received_at`, `payload_json` |

**Storage strategy:**
- `activity_raw_buffer` — partitioned by day, purged after 48h
- `activity_snapshots` — partitioned by month, retained 90 days
- `activity_daily_summary` — retained indefinitely (small, pre-aggregated)
- `screenshots` — files in blob storage, metadata per retention policy

### Module 12: Identity Verification (6 tables)

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `verification_policies` | Per-tenant verification rules | `tenant_id`, `verify_on_login`, `verify_on_logout`, `interval_minutes`, `is_active` |
| `verification_records` | Each verification event | `employee_id`, `tenant_id`, `verified_at`, `method` (photo/fingerprint), `photo_file_id`, `match_confidence`, `status` (verified/failed/skipped), `device_id` |
| `biometric_devices` | Fingerprint terminals (moved from Attendance) | `tenant_id`, `device_name`, `location_id`, `api_key_encrypted`, `is_active`, `last_heartbeat_at` |
| `biometric_enrollments` | Employee fingerprint enrollment | `employee_id`, `tenant_id`, `device_id`, `enrolled_at`, `consent_given`, `template_hash` |
| `biometric_events` | Raw clock-in/out events from terminals | `employee_id`, `tenant_id`, `device_id`, `event_type` (clock_in/clock_out/break_start/break_end), `captured_at`, `verified` |
| `biometric_audit_logs` | Tamper detection, device health | `device_id`, `tenant_id`, `event_type`, `details_json`, `recorded_at` |

### Module 13: Exception Engine (5 tables)

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `exception_rules` | Configurable anomaly detection rules | `tenant_id`, `rule_name`, `rule_type` (low_activity/excess_idle/unusual_pattern/excess_meeting), `threshold_json`, `severity` (info/warning/critical), `is_active`, `applies_to` (all/department/employee) |
| `exception_alerts` | Generated alerts | `tenant_id`, `employee_id`, `rule_id`, `triggered_at`, `severity`, `summary`, `data_snapshot_json`, `status` (new/acknowledged/dismissed/escalated) |
| `escalation_chains` | Notification routing by severity | `tenant_id`, `severity`, `step_order`, `notify_role` (reporting_manager/hr/ceo), `delay_minutes` |
| `alert_acknowledgements` | Audit trail | `alert_id`, `acknowledged_by_id`, `action` (acknowledged/dismissed/escalated/noted), `comment`, `acted_at` |
| `exception_schedules` | When engine runs checks | `tenant_id`, `check_interval_minutes`, `active_from_time`, `active_to_time`, `active_days_json`, `timezone` |

### Module 14: Productivity Analytics (4 tables)

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `daily_employee_report` | One row/employee/day | `employee_id`, `tenant_id`, `date`, `total_hours`, `active_hours`, `idle_hours`, `meeting_hours`, `active_percentage`, `top_apps_json`, `intensity_score`, `device_split_json`, `exceptions_count`, `anomaly_flags_json` |
| `weekly_employee_report` | Weekly aggregation | Same + `week_start`, `trend_vs_previous_week_json` |
| `monthly_employee_report` | Monthly aggregation | Same + `month`, `performance_pattern_json`, `comparative_rank_in_department` |
| `workforce_snapshot` | Tenant-wide daily metrics | `tenant_id`, `date`, `total_employees`, `active_count`, `avg_active_percentage`, `avg_meeting_percentage`, `total_exceptions`, `top_exception_types_json` |

### Module 22: Agent Gateway (3 tables)

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `registered_agents` | Desktop agents registered to employees | `employee_id`, `tenant_id`, `device_id`, `device_name`, `os_version`, `agent_version`, `registered_at`, `last_heartbeat_at`, `status` (active/inactive/revoked) |
| `agent_policies` | Policy pushed to each agent | `agent_id`, `tenant_id`, `policy_json`, `last_synced_at` |
| `agent_health_logs` | Agent uptime, errors, tamper detection | `agent_id`, `tenant_id`, `reported_at`, `cpu_usage`, `memory_mb`, `errors_json`, `tamper_detected` |

### Configuration Module — New Tables (2)

| Table | Purpose |
|:------|:--------|
| `monitoring_feature_toggles` | Global tenant-level ON/OFF per feature |
| `employee_monitoring_overrides` | Per-employee feature overrides |

---

## 6. Module Dependencies & Data Flows

### Desktop Agent → Dashboard Flow

```
Desktop Agent (.NET Windows Service + MAUI tray app)
  │ Every 2-3 min: activity batch (keyboard/mouse counts, active app, idle periods)
  │ On event: photo verification capture
  ▼
Agent Gateway
  │ Authenticate device JWT → validate payload → route to modules
  ├──► Activity Monitoring (raw buffer → snapshots → app usage → meetings)
  ├──► Workforce Presence (device sessions → presence sessions → breaks)
  └──► Identity Verification (photo match → verification record)
         │
         ▼
Exception Engine (every 5 min)
  │ Evaluate rules against latest Activity Monitoring + Workforce Presence data
  │ Generate alerts when thresholds breached
  └──► Notifications (SignalR push + email to manager, escalate to CEO if unacknowledged)
         │
         ▼
Productivity Analytics (Hangfire scheduled: daily/weekly/monthly)
  │ Aggregate from Activity Monitoring + Workforce Presence + CoreHR
  └──► Reporting Engine (dashboard API + CSV/Excel export)
```

### Real-Time Data Tiers

| Tier | Frequency | What |
|:-----|:----------|:-----|
| Agent → Server | Every 2-3 minutes | Batched activity data |
| Exception Engine | Every 5 minutes | Rule evaluation against latest data |
| Dashboard refresh | 30-second polling or SignalR push | Live workforce status |
| Reports | Hangfire scheduled jobs | Daily/weekly/monthly aggregation |

### Domain Events — Workforce Intelligence

| Source | Event | Consumers |
|:-------|:------|:----------|
| Agent Gateway | `AgentRegistered` | Configuration (push policy) |
| Agent Gateway | `AgentHeartbeatLost` | Exception Engine (flag offline) |
| Activity Monitoring | `ActivitySnapshotReceived` | Exception Engine (evaluate rules) |
| Activity Monitoring | `DailySummaryAggregated` | Productivity Analytics (build reports) |
| Workforce Presence | `PresenceSessionStarted` | Notifications (team online status) |
| Workforce Presence | `PresenceSessionEnded` | Activity Monitoring (close day tracking) |
| Workforce Presence | `BreakExceeded` | Exception Engine (flag long break) |
| Identity Verification | `VerificationFailed` | Exception Engine, Notifications (alert manager) |
| Identity Verification | `VerificationCompleted` | Workforce Presence (confirm identity) |
| Exception Engine | `ExceptionAlertCreated` | Notifications (send alert) |
| Exception Engine | `AlertEscalated` | Notifications (escalate to CEO) |
| Productivity Analytics | `DailyReportReady` | Notifications (send summary to managers) |
| Productivity Analytics | `WeeklyReportReady` | Notifications (send weekly digest) |

### Sync Dependencies (Direct Service Calls)

| Caller | Calls | Why |
|:-------|:------|:----|
| Activity Monitoring | `IEmployeeService` (CoreHR) | Employee context for activity data |
| Exception Engine | `IActivityMonitoringService` | Read latest activity to evaluate rules |
| Exception Engine | `IWorkforcePresenceService` | Read presence for idle detection |
| Productivity Analytics | `IActivityMonitoringService` | Daily summaries for aggregation |
| Productivity Analytics | `IWorkforcePresenceService` | Attendance data |
| Productivity Analytics | `IEmployeeService` (CoreHR) | Employee/department context |
| Agent Gateway | `IConfigurationService` | Fetch monitoring policy for employee |
| Payroll | `IWorkforcePresenceService` | Actual worked hours |
| Performance | `IProductivityAnalyticsService` | Productivity scores for reviews |

---

## 7. WorkManage Pro Bridge — Updated

When a customer buys both HR + Work Management:

| Bridge | Direction | Data | API |
|:-------|:----------|:-----|:----|
| People Sync | HR → Work | Employee profiles, roles, departments | `GET /bridges/people-sync/employees` |
| Availability | HR → Work | Leave status, shift schedules, presence | `GET /bridges/availability/{employeeId}` |
| Performance | Work → HR | Task completion rates, velocity, contributions | `POST /bridges/performance/metrics` |
| Skills | Bidirectional | Skill profiles / task skill requirements | `GET/POST /bridges/skills/{employeeId}` |
| Work Activity (NEW) | Work → HR | Time logged per task/project, active task context | `POST /bridges/work-activity/time-logs` |

**What HR needs from Work Management:**
1. Task time logs — hours per task, correlate with app usage
2. Project assignments — current projects per employee
3. Task completion metrics — velocity, completion rate for Performance reviews
4. Active task identifier — which task is being worked on (real-time dashboard context)

---

## 8. Desktop Agent Design

### Technology

- **.NET Windows Service** — always-on background collector (activity, app usage, idle detection)
- **.NET MAUI tray app** — minimal UI for photo verification prompts, status indicator, login

### Agent Responsibilities

1. Capture keyboard/mouse event counts (not keystrokes — just counts for intensity)
2. Track foreground application name + window title
3. Detect idle periods (no input for configurable threshold)
4. Detect meeting applications (Teams, Zoom, Meet) and camera/mic status
5. Capture photos for identity verification (when policy requires)
6. Track device active time
7. Batch and send data to Agent Gateway every 2-3 minutes
8. Read monitoring policy from server (what features are enabled for this employee)
9. Auto-start on system boot, run as Windows Service (tamper-resistant)
10. Heartbeat every 60 seconds to Agent Gateway

### Agent Authentication

- Device-level JWT issued at registration
- Employee logs in via MAUI tray app → links device to employee
- Agent sends device JWT + employee context with each batch
- If agent goes offline (no heartbeat for 5 min) → Agent Gateway fires `AgentHeartbeatLost` event

### Agent Brain Location

`onevo-hr-brain/agent/` — contains architecture docs, coding standards, and known issues for agent development.

---

## 9. Frontend Architecture

### Tech Stack

| Category | Technology | Why |
|:---------|:-----------|:----|
| Framework | Next.js 14+ (App Router) | Server components for dashboards, Vercel-native |
| Styling | Tailwind CSS | Utility-first, design system friendly |
| Components | shadcn/ui | Unstyled/composable, enterprise-grade, no vendor lock |
| Charts | Recharts + Tremor | Lightweight React charts + dashboard blocks |
| Server state | TanStack Query v5 | API caching, mutations, optimistic updates |
| Client state | Zustand | Sidebar, filters, UI preferences |
| Real-time | SignalR client | Live dashboard, alerts |
| Forms | React Hook Form + Zod | Validation mirrors backend FluentValidation |
| URL state | nuqs | Filters and pagination in URL |
| Testing | Vitest + React Testing Library + Playwright | Unit + integration + E2E |

### Route Structure

```
app/
├── (auth)/                       # Public — no sidebar
│   ├── login/
│   ├── forgot-password/
│   └── mfa/
├── (dashboard)/                  # Authenticated — sidebar + topbar
│   ├── overview/                 # Landing dashboard
│   ├── hr/                       # Pillar 1
│   │   ├── employees/
│   │   ├── leave/
│   │   ├── performance/
│   │   ├── payroll/
│   │   ├── skills/
│   │   ├── documents/
│   │   ├── grievance/
│   │   └── expense/
│   ├── workforce/                # Pillar 2
│   │   ├── live/                 # Real-time workforce dashboard
│   │   ├── activity/             # Employee activity detail
│   │   ├── reports/              # Daily/weekly/monthly
│   │   ├── exceptions/           # Alert management
│   │   └── verification/         # Identity verification logs
│   ├── org/                      # Org structure
│   │   ├── departments/
│   │   ├── teams/
│   │   └── job-families/
│   └── settings/                 # Tenant config
│       ├── general/
│       ├── monitoring/           # Feature toggles + overrides
│       ├── notifications/
│       ├── integrations/
│       └── billing/
├── (employee-self-service)/      # Employee-facing (limited nav)
│   ├── my-dashboard/             # Own activity data
│   ├── my-leave/
│   ├── my-profile/
│   └── my-performance/
```

### Key Pages — Workforce Intelligence

**Live Workforce Dashboard** (`/workforce/live`):
- Headline metrics: total employees, active count, idle count, on leave, absent
- Department breakdown with active percentages
- Activity heatmap (hourly intensity)
- Active exceptions panel (real-time via SignalR)
- Filterable employee list with status, active%, top app, time since login
- Auto-refreshes via SignalR push or 30s polling

**Employee Activity Detail** (`/workforce/activity/[employeeId]`):
- Day summary: hours worked, active%, meeting time, intensity score
- Timeline bar (full day: active/idle/break/meeting segments)
- Application usage breakdown with time and percentages
- Activity intensity line chart (hourly)
- Meeting log with mic/camera indicators
- Device usage split (laptop % vs mobile estimate %)

**Reports** (`/workforce/reports`):
- Daily: headline metrics, key observations (auto-generated, exception-based), department summary table
- Weekly: same + trend charts, week-over-week comparison
- Monthly: same + performance patterns, comparative insights
- All reports downloadable as CSV/Excel

**Exception Management** (`/workforce/exceptions`):
- Active alerts list with severity, employee, rule triggered, timestamp
- Acknowledge/dismiss/escalate actions
- Alert history and audit trail
- Filter by severity, department, rule type, date range

**Monitoring Settings** (`/settings/monitoring`):
- Industry profile selector
- Global feature toggles (ON/OFF per feature)
- Identity verification policy (login/logout/interval config)
- Exception rules with threshold configuration
- Escalation chain editor
- Privacy/transparency mode selector
- Data retention period
- Employee override management (individual + bulk by department/team/job family)

**Employee Self-Service** (`/my-dashboard`):
- Own day summary (hours, active%, meetings, intensity)
- Own timeline and app usage
- Weekly trend chart
- "What's being tracked" transparency footer (changes per privacy setting)
- No comparison with colleagues, no rankings, no exception alerts

### Permission-Based Rendering

```typescript
<PermissionGate permission="workforce:view">
  <WorkforceDashboard />
</PermissionGate>

<PermissionGate permission="exceptions:manage">
  <ExceptionAlertActions />
</PermissionGate>
```

### SignalR Channels

| Channel | Data | UI Update |
|:--------|:-----|:----------|
| `workforce-live` | Presence changes, active/idle transitions | Live dashboard cards |
| `exception-alerts` | New exception alerts | Toast + badge count |
| `activity-feed` | Activity snapshots (admin drill-down) | Employee detail live update |
| `agent-status` | Agent online/offline | Agent health indicator |

### Frontend Brain Location

`onevo-hr-brain/frontend/` — contains AI context, architecture docs, design system, page specs, coding standards.

---

## 10. Files to Create/Rewrite

### Backend Brain (root of repo — rewrite existing files)

| File | Action |
|:-----|:-------|
| `AI_CONTEXT/project-context.md` | Rewrite |
| `AI_CONTEXT/tech-stack.md` | Rewrite |
| `AI_CONTEXT/current-focus.md` | Rewrite |
| `AI_CONTEXT/known-issues.md` | Rewrite |
| `AI_CONTEXT/rules.md` | Rewrite |
| `docs/architecture/module-catalog.md` | Rewrite |
| `docs/architecture/module-boundaries.md` | Rewrite |
| `docs/architecture/external-integrations.md` | Rewrite |
| `docs/architecture/shared-kernel.md` | Update |
| `docs/architecture/notification-system.md` | Update |
| `docs/architecture/multi-tenancy.md` | Update |
| `docs/database/README.md` | Update |
| `docs/database/performance.md` | Update |
| `docs/security/auth-architecture.md` | Update |
| `docs/security/compliance.md` | Update |
| `docs/security/data-classification.md` | Update |
| `README.md` | Rewrite |

### Frontend Brain (`frontend/` — all new)

| File | Action |
|:-----|:-------|
| `frontend/AI_CONTEXT/project-context.md` | Create |
| `frontend/AI_CONTEXT/tech-stack.md` | Create |
| `frontend/AI_CONTEXT/current-focus.md` | Create |
| `frontend/AI_CONTEXT/rules.md` | Create |
| `frontend/AI_CONTEXT/known-issues.md` | Create |
| `frontend/AI_CONTEXT/changelog.md` | Create |
| `frontend/.cursor/rules/project-context.mdc` | Create |
| `frontend/.cursor/rules/coding-standards.mdc` | Create |
| `frontend/.cursor/rules/ai-behavior.mdc` | Create |
| `frontend/docs/architecture/README.md` | Create |
| `frontend/docs/architecture/app-structure.md` | Create |
| `frontend/docs/architecture/state-management.md` | Create |
| `frontend/docs/architecture/api-integration.md` | Create |
| `frontend/docs/architecture/real-time.md` | Create |
| `frontend/docs/architecture/monitoring-data-flow.md` | Create |
| `frontend/docs/design-system/README.md` | Create |
| `frontend/docs/design-system/component-catalog.md` | Create |
| `frontend/docs/design-system/layout-patterns.md` | Create |
| `frontend/docs/design-system/data-visualization.md` | Create |
| `frontend/docs/design-system/color-tokens.md` | Create |
| `frontend/docs/design-system/typography.md` | Create |
| `frontend/docs/pages/README.md` | Create |
| `frontend/docs/pages/pillar2-workforce/live-dashboard.md` | Create |
| `frontend/docs/pages/pillar2-workforce/employee-activity.md` | Create |
| `frontend/docs/pages/pillar2-workforce/reports.md` | Create |
| `frontend/docs/pages/pillar2-workforce/exceptions.md` | Create |
| `frontend/docs/pages/pillar2-workforce/settings.md` | Create |
| `frontend/docs/pages/pillar1-hr/*.md` | Create (key pages) |
| `frontend/docs/pages/shared/*.md` | Create |
| `frontend/docs/security/auth-flow.md` | Create |
| `frontend/docs/security/rbac-frontend.md` | Create |
| `frontend/docs/guides/coding-standards.md` | Create |
| `frontend/docs/guides/testing.md` | Create |
| `frontend/README.md` | Create |

### Agent Brain (`agent/` — all new)

| File | Action |
|:-----|:-------|
| `agent/AI_CONTEXT/project-context.md` | Create |
| `agent/AI_CONTEXT/tech-stack.md` | Create |
| `agent/AI_CONTEXT/rules.md` | Create |
| `agent/AI_CONTEXT/known-issues.md` | Create |
| `agent/.cursor/rules/project-context.mdc` | Create |
| `agent/.cursor/rules/coding-standards.mdc` | Create |
| `agent/docs/architecture/README.md` | Create |
| `agent/docs/architecture/data-collection.md` | Create |
| `agent/docs/architecture/agent-server-protocol.md` | Create |
| `agent/docs/architecture/tamper-resistance.md` | Create |
| `agent/docs/architecture/photo-capture.md` | Create |
| `agent/README.md` | Create |
