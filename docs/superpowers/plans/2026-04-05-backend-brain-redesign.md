# Backend Brain Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite all backend secondary brain documentation to reflect the two-pillar architecture (HR Management + Workforce Intelligence), 22 modules, ~138 tables, desktop agent integration, and updated WorkManage Pro bridges.

**Architecture:** The existing 18-module HR-only brain becomes a 22-module two-pillar platform. Pillar 1 (HR Management) keeps 9 existing modules with minor enhancements. Pillar 2 (Workforce Intelligence) adds 5 new modules: Workforce Presence (replaces Attendance), Activity Monitoring, Identity Verification, Exception Engine, Productivity Analytics. Shared Foundation adds Agent Gateway.

**Tech Stack:** .NET 9, PostgreSQL 16, Redis 7, Hangfire, SignalR, EF Core 9, .NET MAUI (desktop agent), Next.js 14 (frontend)

**Spec:** `docs/superpowers/specs/2026-04-05-onevo-monitoring-redesign.md`

---

### Task 1: Rewrite README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md with two-pillar architecture**

```markdown
# ONEVO — Secondary Brain

The AI-optimized knowledge base for the ONEVO development team. This is the single source of truth for architecture, conventions, and project context across all three development streams: backend, frontend, and desktop agent.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read [[project-context]] for system overview
3. Read [[current-focus]] for delivery plan and sprint priorities
4. Check [[known-issues]] before writing any code

## System Overview

**ONEVO** is a multi-tenant SaaS platform with two product pillars:
- **Pillar 1: HR Management** — Employee lifecycle, leave, performance, payroll, skills
- **Pillar 2: Workforce Intelligence** — Activity monitoring, presence tracking, identity verification, exception detection, productivity analytics
- **~138 database tables** across **22 modules**
- **.NET 9** backend (Modular Monolith)
- **.NET MAUI + Windows Service** desktop agent
- **Next.js 14** frontend (React)
- **PostgreSQL 16** with Row-Level Security
- Sellable as **HR standalone**, **HR + Workforce Intelligence**, or **Full Suite with WorkManage Pro**

## Repository Structure

```
onevo-hr-brain/
├── AI_CONTEXT/                  # Backend AI context — read FIRST
│   ├── project-context.md       # What ONEVO is, two-pillar architecture
│   ├── tech-stack.md            # .NET 9, PostgreSQL, Redis, MAUI, Next.js
│   ├── current-focus.md         # Delivery plan with developer assignments
│   ├── rules.md                 # AI agent rules for .NET/C# code generation
│   ├── known-issues.md          # Gotchas, encrypted fields, monitoring data
│   └── changelog.md             # Knowledge base update log
├── .cursor/rules/               # Cursor AI auto-injected context
├── docs/
│   ├── architecture/            # Module catalog, boundaries, multi-tenancy, messaging
│   ├── api/                     # API design, endpoints, rate limiting
│   ├── database/                # Schema conventions, migrations, performance
│   ├── security/                # Auth, data classification, compliance
│   ├── testing/                 # Test strategy
│   ├── deployment/              # CI/CD, Docker Compose
│   ├── guides/                  # Coding standards, git workflow, logging
│   └── operations/              # Observability, monitoring
├── frontend/                    # Frontend secondary brain (Next.js team)
│   ├── AI_CONTEXT/              # Frontend AI context
│   ├── .cursor/rules/           # Frontend Cursor rules
│   └── docs/                    # Architecture, design system, page specs
├── agent/                       # Desktop agent secondary brain (.NET MAUI team)
│   ├── AI_CONTEXT/              # Agent AI context
│   ├── .cursor/rules/           # Agent Cursor rules
│   └── docs/                    # Agent architecture, protocols, tamper resistance
├── tasks/                       # Sprint task tracking
├── meetings/                    # Meeting notes
└── decisions/                   # Architecture decision records
```

## Product Configurations

| Configuration | Modules Included |
|:-------------|:----------------|
| **HR Management** (standalone) | Pillar 1 + Shared Foundation |
| **HR + Workforce Intelligence** | Pillar 1 + Pillar 2 + Desktop Agent |
| **HR + Work Management** | Pillar 1 + WorkManage Pro bridges |
| **Full Suite** | All pillars + Desktop Agent + WorkManage Pro |

## Key Principles

1. **Multi-tenant by default** — 4-layer isolation on every query
2. **Module boundaries enforced** — ArchUnitNET tests prevent violations
3. **Result<T> over exceptions** — explicit error handling
4. **Async all the way** — CancellationToken on every async method
5. **PII protection** — encrypted fields, Serilog scrubbing, never log PII
6. **Monitoring is configurable** — per-tenant industry profiles, per-employee overrides
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for two-pillar architecture"
```

---

### Task 2: Rewrite AI_CONTEXT/project-context.md

**Files:**
- Modify: `AI_CONTEXT/project-context.md`

- [ ] **Step 1: Rewrite project-context.md**

Replace the entire file with content that covers:

1. **Project Overview** — ONEVO as a two-pillar platform (HR Management + Workforce Intelligence)
2. **Product Strategy** — Four selling configurations (HR standalone, HR+WI, HR+WM, Full Suite)
3. **System Architecture** — Three-layer model updated:
   - Products layer: HR Platform, Workforce Intelligence, WorkManage Pro (separate team)
   - Connectivity Bridges: People Sync, Availability, Performance, Skills, Work Activity (NEW)
   - Shared Foundation: Auth, Notifications, Workflows, Reporting Engine, Configuration, Calendar, Compliance, Billing, Agent Gateway (NEW)
4. **Architecture Style** — Same modular monolith (.NET 9) but now with 22 modules across two pillars
5. **Key Stats** — Update to: ~138 tables, 22 modules, 90+ permissions (add workforce:view, workforce:manage, exceptions:view, exceptions:manage, monitoring:configure, agent:manage, analytics:view), 40+ notification events (add monitoring events), 6 connectivity bridges
6. **Core Business Logic** — Keep existing entities + add:
   - Activity Snapshot — periodic activity data from desktop agent
   - Presence Session — unified daily presence record per employee
   - Exception Alert — anomaly detection trigger
   - Registered Agent — desktop agent linked to employee
7. **Core Processes** — Keep existing 6 processes + add:
   - Monitoring Flow: Agent Install → Register → Policy Sync → Activity Capture → Buffer → Aggregate → Exception Check → Alert/Report
   - Presence Flow: Biometric Event / Agent Heartbeat → Presence Session → Device Session → Break Detection → Payroll
   - Exception Flow: Rule Trigger → Alert → Notify Manager → Escalate (if unacknowledged) → CEO
8. **Business Rules** — Keep existing + add:
   - Monitoring features are configurable per tenant (industry profile) and per employee (overrides)
   - Desktop agent reads its policy from server on employee login
   - Activity data is buffered then aggregated (raw buffer purged after 48h)
   - Exception engine runs every 5 minutes during configured work hours only
   - Non-computer industries can disable all desktop monitoring, using biometric-only
   - Three privacy transparency modes: full, partial, covert (tenant-configurable)
9. **WorkManage Pro Bridges** — Update to include Work Activity bridge
10. **What We Are NOT Building** — Keep AI Chatbot and Mobile deferred. Add: WorkManage Pro features (other team), multi-region deployment

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/project-context.md
git commit -m "docs: rewrite project-context for two-pillar architecture with workforce intelligence"
```

---

### Task 3: Rewrite AI_CONTEXT/tech-stack.md

**Files:**
- Modify: `AI_CONTEXT/tech-stack.md`

- [ ] **Step 1: Rewrite tech-stack.md**

Keep all existing backend technologies. Add/update:

1. **Programming Languages** — Add: C# 13 for desktop agent (.NET MAUI + Windows Service)
2. **Desktop Agent Technologies** (NEW section):
   - Runtime: .NET 9 Windows Service (background collector)
   - UI: .NET MAUI (system tray app, photo capture dialogs)
   - Activity Capture: Windows API hooks (user32.dll — keyboard/mouse event counts, NOT keylogger)
   - App Detection: Process enumeration + foreground window tracking (via Win32 APIs)
   - Photo Capture: MAUI camera API
   - Communication: HttpClient with Polly resilience to Agent Gateway API
   - Packaging: MSIX installer with auto-update capability
3. **External Integrations** — Add:
   - Microsoft Teams Graph API (meeting detection, participant list) — Phase 2
   - Biometric Terminals (moved to Identity Verification module context)
4. **Architecture Patterns** — Add:
   - Time-Series Buffer Pattern: raw activity data → buffer table (partitioned by day, purged after 48h) → aggregated summaries
   - Tiered Real-Time: agent→server (2-3 min), exception engine (5 min), dashboard (30s polling / SignalR push)
5. **NOT Using in Phase 1** — Keep existing + add: Teams Graph API deep integration (basic meeting detection via process name in Phase 1)

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/tech-stack.md
git commit -m "docs: rewrite tech-stack with desktop agent and monitoring technologies"
```

---

### Task 4: Rewrite AI_CONTEXT/current-focus.md

**Files:**
- Modify: `AI_CONTEXT/current-focus.md`

- [ ] **Step 1: Rewrite current-focus.md**

Restructure the 4-week delivery plan to include Workforce Intelligence modules. Suggested restructure:

**Week 1 (Apr 7-11): Foundation & Infrastructure** — Same as before (Infrastructure, Auth, Org Structure, Shared Platform) PLUS add Agent Gateway setup and monitoring configuration tables to Dev 4's scope.

**Week 2 (Apr 14-18): Core HR + Workforce Presence** — Replace "Attendance" with "Workforce Presence". Dev 3+4 build the unified presence module (shifts, schedules, biometric, presence sessions, device sessions, break records). Dev 1+2 handle Core HR (same as before).

**Week 3 (Apr 21-25): Activity Monitoring + Identity Verification + Leave + Performance** — Dev 1: Leave (same). Dev 2: Performance (enhanced with productivity score intake). Dev 3: Activity Monitoring (snapshots, app usage, meeting detection, daily summary, raw buffer). Dev 4: Identity Verification (verification policies, records, photo capture API).

**Week 4 (Apr 28 - May 2): Exception Engine + Analytics + Payroll + Supporting** — Dev 1: Productivity Analytics + Reporting Engine. Dev 2: Exception Engine (rules, alerts, escalation, schedules). Dev 3: Payroll (same but reads from Workforce Presence). Dev 4: Supporting modules (Documents, Notifications, Grievance, Expense) + WorkManage Pro bridges (including new Work Activity bridge).

Update Definition of Done for each week to include new monitoring deliverables.

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/current-focus.md
git commit -m "docs: rewrite delivery plan with workforce intelligence modules"
```

---

### Task 5: Rewrite AI_CONTEXT/known-issues.md

**Files:**
- Modify: `AI_CONTEXT/known-issues.md`

- [ ] **Step 1: Rewrite known-issues.md**

Keep all existing gotchas. Add new ones:

- **Activity Data Volume:** `activity_snapshots` generates ~240 rows/employee/day (one every 2-3 min for 8 hours). For 500 employees = 120,000 rows/day. Use pg_partman monthly partitions. Always query with `tenant_id` + date range.

- **Raw Buffer Purge:** `activity_raw_buffer` is partitioned by day and auto-purged after 48 hours by a Hangfire daily job. Never query this table for reporting — use `activity_daily_summary` instead.

- **Agent Authentication vs User Authentication:** Desktop agents use a separate device-level JWT (issued at registration). This is NOT the same as user JWT. Agent JWT contains `device_id` + `tenant_id` but no user permissions. The employee context is linked at login time via the MAUI tray app.

- **Monitoring Feature Toggles:** Always check `monitoring_feature_toggles` (tenant-level) and `employee_monitoring_overrides` (employee-level) before processing any monitoring data. The desktop agent also checks its policy on login, but the server must double-validate.

- **Attendance → Workforce Presence Rename:** The old `Attendance` module no longer exists. It has been replaced by `Workforce Presence` (`ONEVO.Modules.WorkforcePresence`). All attendance-related tables remain but are now under this new namespace. References to "Attendance" in code should use "WorkforcePresence".

- **Screenshot Storage:** Screenshots are stored in blob storage (same as other files via `file_records`). Screenshot metadata in `screenshots` table has `file_record_id` FK. Never store screenshots in the database. Screenshots are classified as RESTRICTED data — see data-classification.

- **Identity Verification Photos:** Verification photos are temporary — retained for configurable period (default 30 days) then auto-deleted by retention job. They are NOT the same as employee profile photos.

- **Exception Engine Timing:** The exception engine only evaluates rules during configured work hours (`exception_schedules`). Off-hours activity data is still collected but does NOT trigger alerts. When writing exception rules, always check the schedule first.

- **Presence Session vs Device Session:** `presence_sessions` is ONE row per employee per day (unified from all sources). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them — presence is the summary, device sessions are the raw source.

- **organisation_id vs tenant_id (RESOLVED):** All tables now use `tenant_id` consistently. No EF Core column mapping workarounds needed.

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/known-issues.md
git commit -m "docs: rewrite known-issues with monitoring and agent gotchas"
```

---

### Task 6: Rewrite AI_CONTEXT/rules.md

**Files:**
- Modify: `AI_CONTEXT/rules.md`

- [ ] **Step 1: Rewrite rules.md**

Keep all existing rules (architecture, naming, patterns, multi-tenancy, API design, database, testing, git, logging). Add new sections:

**Workforce Intelligence Module Rules:**

1. **Activity data is append-only** — never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`. These are time-series logs. Only `activity_daily_summary` is computed (INSERT or UPDATE on conflict for the day).

2. **Agent Gateway is high-throughput** — the `/api/v1/agent/ingest` endpoint receives data every 2-3 minutes from every active agent. Use:
   - Minimal validation (schema check only, detailed validation async)
   - Batch INSERT via `COPY` or `unnest()` for raw buffer
   - Return 202 Accepted immediately, process asynchronously
   - Rate limit per device (not per user)

3. **Exception rules use JSONB thresholds** — `exception_rules.threshold_json` is a flexible JSON structure. Always validate against a known schema before evaluating. Example:
   ```json
   {"idle_percent_max": 40, "window_minutes": 60, "consecutive_snapshots": 3}
   ```

4. **Monitoring data has shorter retention** — unlike HR data (7 years), monitoring data follows:
   - Raw buffer: 48 hours
   - Snapshots: 90 days
   - Daily summaries: 2 years
   - Screenshots: per tenant retention policy (default 30 days)
   - Always check `retention_policies` before querying old data

5. **Never log activity content** — log activity COUNTS (keyboard_events_count, mouse_events_count) but NEVER log window titles, application names, or screenshot contents. These may contain sensitive business data.

6. **Desktop agent policy pattern:**
   ```csharp
   // When agent requests its policy, always merge tenant + employee override
   var tenantPolicy = await _configService.GetMonitoringTogglesAsync(tenantId, ct);
   var employeeOverride = await _configService.GetEmployeeOverrideAsync(employeeId, ct);
   var effectivePolicy = tenantPolicy.MergeWith(employeeOverride); // Override wins
   ```

**New Permissions (add to RBAC section):**
```
workforce:view, workforce:manage
exceptions:view, exceptions:manage, exceptions:acknowledge
monitoring:configure, monitoring:view-settings
agent:register, agent:manage, agent:view-health
analytics:view, analytics:export
verification:view, verification:configure
```

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/rules.md
git commit -m "docs: rewrite rules with workforce intelligence patterns and agent rules"
```

---

### Task 7: Rewrite docs/architecture/module-catalog.md

**Files:**
- Modify: `docs/architecture/module-catalog.md`

- [ ] **Step 1: Rewrite module-catalog.md**

This is the biggest rewrite. Replace the entire file with the 22-module catalog from the spec. Structure:

1. **Architecture Overview** — Update to mention two pillars + shared foundation
2. **Solution Structure** — Update to show:
   ```
   ONEVO.sln
   ├── src/
   │   ├── ONEVO.Api/
   │   ├── ONEVO.SharedKernel/
   │   ├── ONEVO.Modules.Infrastructure/
   │   ├── ONEVO.Modules.Auth/
   │   ├── ONEVO.Modules.OrgStructure/
   │   ├── ONEVO.Modules.CoreHR/
   │   ├── ONEVO.Modules.WorkforcePresence/    # Was: Attendance
   │   ├── ONEVO.Modules.ActivityMonitoring/   # NEW
   │   ├── ONEVO.Modules.IdentityVerification/ # NEW
   │   ├── ONEVO.Modules.ExceptionEngine/      # NEW
   │   ├── ONEVO.Modules.ProductivityAnalytics/# NEW
   │   ├── ONEVO.Modules.Leave/
   │   ├── ONEVO.Modules.Payroll/
   │   ├── ONEVO.Modules.Performance/
   │   ├── ONEVO.Modules.Skills/
   │   ├── ONEVO.Modules.Documents/
   │   ├── ONEVO.Modules.Notifications/
   │   ├── ONEVO.Modules.Configuration/
   │   ├── ONEVO.Modules.Calendar/
   │   ├── ONEVO.Modules.ReportingEngine/      # Was: Reports
   │   ├── ONEVO.Modules.Grievance/
   │   ├── ONEVO.Modules.Expense/
   │   ├── ONEVO.Modules.SharedPlatform/
   │   └── ONEVO.Modules.AgentGateway/         # NEW
   ```
3. **Module Registry** — 22 modules with table counts, owners, build week assignments matching the new delivery plan
4. **Module Dependency Map** — Use the updated dependency diagram from the spec
5. **Module Details** — For each of the 22 modules, document:
   - Responsibility
   - Database Tables (list all table names)
   - Public API (interface names)
   - Publishes Events
   - Consumes Events
   - Dependencies

   For the 5 NEW Pillar 2 modules and Agent Gateway, include full detail as specified in the design spec (Section 5 tables, Section 6 events and dependencies).

   For reshaped modules:
   - **WorkforcePresence**: list 12 tables (9 kept + 3 new: presence_sessions, device_sessions, break_records). Note biometric tables moved to IdentityVerification.
   - **ReportingEngine**: serves both HR and workforce reports
   - **Configuration**: add monitoring_feature_toggles, employee_monitoring_overrides
   - **Performance**: add IProductivityAnalyticsService dependency for productivity scores
   - **Payroll**: add IWorkforcePresenceService dependency for actual worked hours

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/module-catalog.md
git commit -m "docs: rewrite module catalog with 22 modules across two pillars"
```

---

### Task 8: Rewrite docs/architecture/module-boundaries.md

**Files:**
- Modify: `docs/architecture/module-boundaries.md`

- [ ] **Step 1: Rewrite module-boundaries.md**

Keep all 5 existing rules. Add new rules:

**Rule 6: Agent Gateway Is the Only Entry Point for Agent Data**

```csharp
// ALLOWED:
// AgentGateway receives raw data and routes to Activity Monitoring
using ONEVO.Modules.ActivityMonitoring.Public;
await _activityMonitoringService.IngestSnapshotAsync(snapshot, ct);

// FORBIDDEN:
// Activity Monitoring module directly exposes an API endpoint for agent data
// All agent data MUST flow through AgentGateway
```

**Rule 7: Pillar 2 Modules Read from Each Other via Public Interfaces**

```csharp
// ALLOWED: Exception Engine reads from Activity Monitoring
using ONEVO.Modules.ActivityMonitoring.Public;
var snapshots = await _activityService.GetRecentSnapshotsAsync(employeeId, ct);

// FORBIDDEN: Exception Engine directly queries activity_snapshots table
using ONEVO.Modules.ActivityMonitoring.Internal.Repositories;
```

**Rule 8: HR Modules Do Not Depend on Workforce Intelligence Modules**

The dependency is one-way: Workforce Intelligence → HR (for employee context), never HR → Workforce Intelligence. Exceptions:
- Performance MAY optionally call `IProductivityAnalyticsService` to pull productivity scores (soft dependency, feature-flag gated)
- Payroll calls `IWorkforcePresenceService` for actual worked hours (replaces old Attendance dependency)

**Rule 9: Monitoring Data Stays in Monitoring Tables**

Activity data (snapshots, app usage, screenshots) never gets written to HR tables. Aggregated insights (daily summaries, productivity scores) can be READ by HR modules via public interfaces, but the data lives in Pillar 2 tables.

Update ArchUnitNET test examples to include new modules.

Update the directory structure template to be unchanged (same pattern for all new modules).

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/module-boundaries.md
git commit -m "docs: update module boundaries with workforce intelligence rules"
```

---

### Task 9: Rewrite docs/architecture/external-integrations.md

**Files:**
- Modify: `docs/architecture/external-integrations.md`

- [ ] **Step 1: Rewrite external-integrations.md**

Keep all existing integrations. Add/update:

1. **Desktop Agent Protocol** (NEW section):
   - Agent → Server communication: HTTPS POST to `/api/v1/agent/ingest`
   - Authentication: Device JWT (RS256, issued at registration)
   - Payload format: JSON batch of activity snapshots
   - Heartbeat: GET `/api/v1/agent/heartbeat` every 60 seconds
   - Policy sync: GET `/api/v1/agent/policy` on login and every 30 minutes
   - Response: 202 Accepted (async processing)

2. **WorkManage Pro Bridges** — Add Work Activity bridge:
   ```
   | Work Activity (NEW) | Work → HR | POST /api/v1/bridges/work-activity/time-logs |
   ```
   Document the payload: `{ employeeId, taskId, projectId, timeLoggedMinutes, activeTaskTitle, loggedAt }`

3. **Biometric Terminals** — Move from Phase 2 to Identity Verification module context. Keep HMAC-SHA256 webhook verification code.

4. **Microsoft Teams Graph API** (NEW, Phase 2):
   - Purpose: Rich meeting analytics (participant list, duration, engagement)
   - Phase 1 fallback: Detect Teams process + window title for basic meeting detection
   - Auth: OAuth 2.0 (tenant-level consent)

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/external-integrations.md
git commit -m "docs: update external integrations with agent protocol and work activity bridge"
```

---

### Task 10: Update docs/architecture/shared-kernel.md

**Files:**
- Modify: `docs/architecture/shared-kernel.md`

- [ ] **Step 1: Update shared-kernel.md**

Add to the Enums section:
```
├── Enums/
│   ├── ... (existing enums)
│   ├── MonitoringFeature.cs       # ActivityTracking, AppTracking, Screenshots, MeetingDetection, DeviceTracking, PhotoVerification, Biometric
│   ├── AlertSeverity.cs           # Info, Warning, Critical
│   ├── AlertStatus.cs             # New, Acknowledged, Dismissed, Escalated
│   ├── VerificationMethod.cs      # Photo, Fingerprint
│   ├── VerificationStatus.cs      # Verified, Failed, Skipped
│   ├── PresenceSource.cs          # Biometric, Agent, Manual
│   ├── PresenceStatus.cs          # Present, Absent, Partial
│   └── IndustryProfile.cs         # OfficeIT, Manufacturing, Retail, Healthcare, Custom
```

Add to the Results section — note that `TimeSeriesEntity` base class is NOT in SharedKernel (it's specific to Activity Monitoring). Only truly shared enums go here.

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/shared-kernel.md
git commit -m "docs: update shared kernel with monitoring enums"
```

---

### Task 11: Update docs/architecture/notification-system.md

**Files:**
- Modify: `docs/architecture/notification-system.md`

- [ ] **Step 1: Update notification-system.md**

Add new notification categories:

```markdown
| `workforce` | PresenceSessionStarted, PresenceSessionEnded | In-app |
| `exceptions` | ExceptionAlertCreated, AlertEscalated | In-app + Email |
| `monitoring` | AgentRegistered, AgentHeartbeatLost, VerificationFailed | In-app + Email |
| `analytics` | DailyReportReady, WeeklyReportReady | In-app + Email |
```

Add to escalation rules section:
```markdown
### Exception-Based Escalation

Exception alerts follow a dedicated escalation chain configured per tenant:

1. Warning severity → Reporting Manager (immediate via SignalR + email)
2. Critical severity → Reporting Manager (immediate) + CEO (after configurable delay if not acknowledged)
3. Escalation delay is configurable per tenant in `escalation_chains` table

Unlike workflow-based escalation (time-based SLA), exception escalation is severity-based and uses the Exception Engine's own `escalation_chains` table, not the SharedPlatform `escalation_rules`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/notification-system.md
git commit -m "docs: update notification system with exception alerts and monitoring events"
```

---

### Task 12: Update docs/architecture/multi-tenancy.md

**Files:**
- Modify: `docs/architecture/multi-tenancy.md`

- [ ] **Step 1: Update multi-tenancy.md**

Add to "Non-tenant-scoped tables" list: `application_categories` defaults (system-provided app categories are global; tenant-specific customizations have `tenant_id`).

Add new section:

```markdown
## Agent-Level Authentication

Desktop agents use a separate authentication flow from users:

1. Agent registers with device-level JWT: `POST /api/v1/agent/register`
2. Device JWT contains: `device_id`, `tenant_id` (NO user permissions)
3. Employee links to agent at login via MAUI tray app
4. Agent data is always tenant-scoped via the device JWT's `tenant_id`
5. RLS policies apply to all monitoring tables just like HR tables

### Agent JWT Structure

```json
{
  "sub": "device-uuid",
  "tenant_id": "tenant-uuid",
  "device_name": "LAPTOP-ABC123",
  "agent_version": "1.0.0",
  "type": "agent",
  "iat": 1679616000,
  "exp": 1680220800
}
```

The `type: "agent"` claim distinguishes agent JWTs from user JWTs. Middleware routes agent requests to Agent Gateway endpoints only.
```

Add to partitioning section:
```markdown
### Monitoring Data Partitioning

| Table | Partition Strategy | Retention |
|:------|:------------------|:----------|
| `activity_raw_buffer` | Daily (by `received_at`) | 48 hours |
| `activity_snapshots` | Monthly (by `captured_at`) | 90 days |
| `biometric_events` | Monthly (by `captured_at`) | 2 years |
| `verification_records` | Monthly (by `verified_at`) | Per retention policy |
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/multi-tenancy.md
git commit -m "docs: update multi-tenancy with agent authentication and monitoring partitioning"
```

---

### Task 13: Update docs/database/README.md

**Files:**
- Modify: `docs/database/README.md`

- [ ] **Step 1: Update database README**

Update stats:
- Total Tables: ~138 across 22 modules
- Add partitioning note for monitoring tables

Add to "Encrypted Columns" table:
```markdown
| `biometric_devices` | `api_key_encrypted` | Terminal API keys |
```
(This was already in hardware_terminals but now biometric_devices is separate)

Add new section:

```markdown
## Time-Series Tables

Monitoring modules generate high-volume time-series data requiring special handling:

| Table | Write Volume | Partition | Retention | Query Pattern |
|:------|:------------|:----------|:----------|:-------------|
| `activity_raw_buffer` | ~240/employee/day | Daily | 48h | Write-only (ingestion), read by aggregator |
| `activity_snapshots` | ~240/employee/day | Monthly | 90 days | Read by Exception Engine, Analytics |
| `application_usage` | ~20/employee/day | Monthly | 90 days | Read by dashboards, reports |
| `device_sessions` | ~5/employee/day | Monthly | 90 days | Read by Workforce Presence |
| `verification_records` | ~4/employee/day | Monthly | Configurable | Read by Identity Verification logs |

These tables use `BaseTimeSeriesEntity` (defined in Activity Monitoring module, NOT SharedKernel) which omits `is_deleted` and `deleted_at` — time-series data is never soft-deleted, only expired by retention.
```

- [ ] **Step 2: Commit**

```bash
git add docs/database/README.md
git commit -m "docs: update database README with time-series tables and monitoring stats"
```

---

### Task 14: Update docs/database/performance.md

**Files:**
- Modify: `docs/database/performance.md`

- [ ] **Step 1: Update performance.md**

Add new indexes section:

```markdown
### Monitoring Indexes

```sql
-- Activity snapshots (high-volume, always queried by employee + time range)
CREATE INDEX idx_activity_snapshots_tenant_emp_time
ON activity_snapshots (tenant_id, employee_id, captured_at DESC);

-- Application usage (daily breakdown queries)
CREATE INDEX idx_app_usage_tenant_emp_date
ON application_usage (tenant_id, employee_id, date);

-- Exception alerts (active alerts dashboard)
CREATE INDEX idx_exception_alerts_tenant_status
ON exception_alerts (tenant_id, status, triggered_at DESC);

-- Presence sessions (daily lookup)
CREATE UNIQUE INDEX uq_presence_sessions_tenant_emp_date
ON presence_sessions (tenant_id, employee_id, date);

-- Device sessions (per-employee per-day)
CREATE INDEX idx_device_sessions_tenant_emp_date
ON device_sessions (tenant_id, employee_id, session_start);

-- Registered agents (lookup by employee)
CREATE UNIQUE INDEX uq_registered_agents_tenant_emp
ON registered_agents (tenant_id, employee_id) WHERE status = 'active';

-- Daily summary (report queries)
CREATE UNIQUE INDEX uq_daily_summary_tenant_emp_date
ON activity_daily_summary (tenant_id, employee_id, date);
```

Add to partitioning section:
```sql
-- Partition activity_raw_buffer by day (auto-purge after 48h)
SELECT create_parent(
    p_parent_table := 'public.activity_raw_buffer',
    p_control := 'received_at',
    p_type := 'range',
    p_interval := '1 day'
);

-- Partition activity_snapshots by month
SELECT create_parent(
    p_parent_table := 'public.activity_snapshots',
    p_control := 'captured_at',
    p_type := 'range',
    p_interval := '1 month'
);
```

Add to caching section:
```markdown
### Monitoring Cache Keys

```
onevo:{tenantId}:agent-policy:{employeeId}     → Agent monitoring policy (TTL: 30 min)
onevo:{tenantId}:presence:live                  → Current workforce presence snapshot (TTL: 30 sec)
onevo:{tenantId}:exception-rules                → Active exception rules (TTL: 5 min)
onevo:{tenantId}:workforce-snapshot:{date}      → Daily workforce snapshot (TTL: 1 hour)
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/database/performance.md
git commit -m "docs: update performance with monitoring indexes, partitioning, and cache keys"
```

---

### Task 15: Update docs/security/auth-architecture.md

**Files:**
- Modify: `docs/security/auth-architecture.md`

- [ ] **Step 1: Update auth-architecture.md**

Add new section after "MFA Support":

```markdown
## Desktop Agent Authentication

Desktop agents use a separate authentication mechanism from user login:

### Agent Registration Flow

```
Admin                    ONEVO API                  Agent Gateway
  |                        |                           |
  |-- Install agent ------>|                           |
  |   on employee laptop   |                           |
  |                        |-- POST /agent/register -->|
  |                        |   {device_name, os_ver,   |
  |                        |    tenant_api_key}         |
  |                        |<-- Device JWT + agent_id --|
  |                        |                           |
Employee                   |                           |
  |-- Login via tray app ->|                           |
  |   {email, password}    |-- Verify credentials ---->|
  |                        |<-- Link employee to agent-|
  |                        |-- GET /agent/policy ------>|
  |                        |<-- Monitoring policy ------|
```

### Agent JWT vs User JWT

| Property | User JWT | Agent JWT |
|:---------|:---------|:----------|
| Subject (`sub`) | User UUID | Device UUID |
| Contains `tenant_id` | Yes | Yes |
| Contains `permissions` | Yes (80+) | No |
| Contains `type` | Omitted (default: user) | `"agent"` |
| Lifetime | 15 minutes | 30 days (long-lived) |
| Refresh | Via refresh token | Via re-registration |
| Scope | Full API access (per permissions) | Agent Gateway endpoints only |
```

Add new permissions to the RBAC section:
```markdown
workforce:view, workforce:manage
exceptions:view, exceptions:manage, exceptions:acknowledge
monitoring:configure, monitoring:view-settings
agent:register, agent:manage, agent:view-health
analytics:view, analytics:export
verification:view, verification:configure
```

- [ ] **Step 2: Commit**

```bash
git add docs/security/auth-architecture.md
git commit -m "docs: update auth architecture with agent authentication flow"
```

---

### Task 16: Update docs/security/compliance.md

**Files:**
- Modify: `docs/security/compliance.md`

- [ ] **Step 1: Update compliance.md**

Add new section:

```markdown
## Employee Monitoring Compliance

### UK Legal Framework

Employee monitoring in the UK must comply with:
- **UK GDPR** — lawful basis for processing, transparency
- **Data Protection Act 2018** — workplace monitoring guidance
- **Human Rights Act 1998** — right to privacy (Article 8)
- **ICO Employment Practices Code** — monitoring at work guidance

### ONEVO Compliance Controls

| Requirement | Implementation |
|:------------|:--------------|
| Transparency | Three modes: full/partial/covert — configurable per tenant |
| Lawful basis | Consent capture at agent installation + employment contract reference |
| Proportionality | Per-employee feature toggles — only enable what's needed |
| Data minimization | Activity COUNTS not content; window title hashes not full titles |
| Impact assessment | DPIA template provided for tenants enabling monitoring |
| Employee access | Self-service dashboard shows own monitoring data (when transparency enabled) |
| Retention limits | Configurable per tenant, enforced by Hangfire cleanup jobs |

### Privacy Transparency Modes

| Mode | Employee Sees | Legal Risk |
|:-----|:-------------|:-----------|
| Full transparency | What's tracked + own data dashboard | Low |
| Partial | Own data dashboard, not tracking configuration | Medium |
| Covert | Nothing — employer only | High — tenant must confirm legal compliance |

### Consent Records for Monitoring

When an employee's desktop agent is activated, the system creates a consent record:

```csharp
var consent = new ConsentRecord
{
    UserId = userId,
    ConsentType = "employee_monitoring",
    ConsentVersion = "1.0",
    ConsentGivenAt = DateTimeOffset.UtcNow,
    Details = new { features = enabledFeatures, policyVersion = "1.0" }
};
```

### Screenshot & Photo Data

| Data Type | Classification | Storage | Retention | Access Control |
|:----------|:-------------|:--------|:----------|:-------------- |
| Screenshots | RESTRICTED | Blob storage (encrypted at rest) | Per tenant policy (default 30 days) | monitoring:configure permission |
| Verification photos | RESTRICTED | Blob storage (encrypted at rest) | 30 days | verification:view permission |
| Activity counts | INTERNAL | PostgreSQL | 90 days (snapshots), 2 years (summaries) | workforce:view permission |
```

- [ ] **Step 2: Commit**

```bash
git add docs/security/compliance.md
git commit -m "docs: update compliance with employee monitoring legal framework"
```

---

### Task 17: Update docs/security/data-classification.md

**Files:**
- Modify: `docs/security/data-classification.md`

- [ ] **Step 1: Update data-classification.md**

Add to "Sensitive PII" section:

```markdown
### Monitoring Data Classification

| Table | Column(s) | Classification | Log Scrubbing |
|:------|:----------|:---------------|:-------------|
| `screenshots` | `file_record_id` (points to image) | RESTRICTED | N/A (never log) |
| `verification_records` | `photo_file_id` (points to image) | RESTRICTED | N/A (never log) |
| `application_usage` | `window_title_hash` | INTERNAL | Hash only, never log raw title |
| `application_usage` | `application_name` | INTERNAL | Allowed in reports, scrubbed from debug logs |
| `activity_snapshots` | `keyboard_events_count`, `mouse_events_count` | INTERNAL | Allowed (counts only, not content) |
| `meeting_sessions` | `platform`, `duration_minutes` | INTERNAL | Allowed |
| `device_sessions` | `device_id` | INTERNAL | Allowed |
```

Add to data retention section:

```markdown
| Activity raw buffer | 48 hours | Auto-purge (Hangfire) | Performance |
| Activity snapshots | 90 days | Partition drop | Storage |
| Activity daily summaries | 2 years | Archive then delete | Compliance |
| Screenshots | Per tenant policy (default 30 days) | File deletion + metadata purge | Privacy |
| Verification photos | 30 days | File deletion + metadata purge | Privacy |
| Exception alerts | 1 year | Archive | Compliance |
```

- [ ] **Step 2: Commit**

```bash
git add docs/security/data-classification.md
git commit -m "docs: update data classification with monitoring data types"
```

---

### Task 18: Update docs/architecture/messaging/event-catalog.md

**Files:**
- Modify: `docs/architecture/messaging/event-catalog.md`

- [ ] **Step 1: Update event-catalog.md**

Replace the Attendance Events section with Workforce Presence Events:

```markdown
## Workforce Presence Events (replaces Attendance)

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `PresenceSessionStarted` | WorkforcePresence | EmployeeId, Date, Source, FirstSeenAt | Notifications (team status) |
| `PresenceSessionEnded` | WorkforcePresence | EmployeeId, Date, LastSeenAt, TotalMinutes | ActivityMonitoring (close tracking), Payroll |
| `BreakExceeded` | WorkforcePresence | EmployeeId, BreakStart, ExpectedEnd, ActualDuration | ExceptionEngine (flag) |
| `OvertimeApproved` | WorkforcePresence | EmployeeId, Hours | Payroll, Notifications |
| `AttendanceCorrected` | WorkforcePresence | EmployeeId, Date, OriginalIn, CorrectedIn | Audit |
```

Add new event sections:

```markdown
## Agent Gateway Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `AgentRegistered` | AgentGateway | DeviceId, TenantId, EmployeeId, AgentVersion | Configuration (push policy), Notifications |
| `AgentHeartbeatLost` | AgentGateway | DeviceId, EmployeeId, LastHeartbeatAt | ExceptionEngine (flag offline), Notifications |
| `AgentVersionOutdated` | AgentGateway | DeviceId, CurrentVersion, LatestVersion | Notifications (notify admin) |

## Activity Monitoring Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ActivitySnapshotReceived` | ActivityMonitoring | EmployeeId, CapturedAt, ActiveSeconds, IdleSeconds, IntensityScore | ExceptionEngine (evaluate rules) |
| `DailySummaryAggregated` | ActivityMonitoring | EmployeeId, Date, ActiveMinutes, IdleMinutes, MeetingMinutes | ProductivityAnalytics (build reports) |

## Identity Verification Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `VerificationCompleted` | IdentityVerification | EmployeeId, Method, Status, Confidence | WorkforcePresence (confirm identity) |
| `VerificationFailed` | IdentityVerification | EmployeeId, Method, Reason | ExceptionEngine (flag), Notifications (alert manager) |

## Exception Engine Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `ExceptionAlertCreated` | ExceptionEngine | AlertId, EmployeeId, RuleId, Severity, Summary | Notifications (send alert to manager) |
| `AlertEscalated` | ExceptionEngine | AlertId, EscalatedTo, DelayMinutes | Notifications (escalate to CEO) |
| `AlertAcknowledged` | ExceptionEngine | AlertId, AcknowledgedById, Action | Audit |

## Productivity Analytics Events

| Event | Publisher | Payload | Consumers |
|:------|:---------|:--------|:----------|
| `DailyReportReady` | ProductivityAnalytics | TenantId, Date, EmployeeCount | Notifications (send to managers) |
| `WeeklyReportReady` | ProductivityAnalytics | TenantId, WeekStart, Highlights | Notifications (send digest) |
| `MonthlyReportReady` | ProductivityAnalytics | TenantId, Month | Notifications (send to CEO) |
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/messaging/event-catalog.md
git commit -m "docs: update event catalog with workforce intelligence events"
```

---

### Task 19: Update .cursor/rules files

**Files:**
- Modify: `.cursor/rules/project-context.mdc`

- [ ] **Step 1: Update project-context.mdc**

Update the always-on Cursor rule to reflect:
- ONEVO is a two-pillar platform (HR Management + Workforce Intelligence)
- 22 modules, ~138 tables
- Desktop agent is part of the system (.NET MAUI + Windows Service)
- Monitoring features are configurable per tenant and per employee
- Activity data is high-volume time-series — use buffer → aggregate pattern
- Agent Gateway is the single entry point for all desktop agent data

- [ ] **Step 2: Commit**

```bash
git add .cursor/rules/project-context.mdc
git commit -m "docs: update Cursor project context rule for two-pillar architecture"
```

---

### Task 20: Final review and changelog

**Files:**
- Modify: `AI_CONTEXT/changelog.md`

- [ ] **Step 1: Update changelog**

Add entry:

```markdown
## 2026-04-05 — Major Redesign: Two-Pillar Architecture

### Added
- Pillar 2: Workforce Intelligence (5 new modules)
  - Activity Monitoring (8 tables)
  - Workforce Presence (replaces Attendance, 12 tables)
  - Identity Verification (6 tables)
  - Exception Engine (5 tables)
  - Productivity Analytics (4 tables)
- Agent Gateway module (3 tables)
- Desktop agent architecture (.NET MAUI + Windows Service)
- Monitoring configuration model (per-tenant + per-employee)
- Privacy transparency modes (full/partial/covert)
- Industry profiles for monitoring defaults
- Work Activity bridge for WorkManage Pro
- 15+ new domain events for monitoring
- New RBAC permissions for workforce intelligence
- Frontend brain directory (frontend/)
- Agent brain directory (agent/)

### Changed
- Attendance module → Workforce Presence (biometric tables moved to Identity Verification)
- Reports module → Reporting Engine (serves both pillars)
- Configuration module expanded (monitoring toggles + employee overrides)
- Performance module enhanced (accepts productivity scores)
- Payroll module enhanced (reads actual hours from Workforce Presence)
- Module count: 18 → 22
- Table count: 126 → ~138

### Removed
- Standalone Attendance module (absorbed into Workforce Presence)
```

- [ ] **Step 2: Commit**

```bash
git add AI_CONTEXT/changelog.md
git commit -m "docs: update changelog with two-pillar architecture redesign"
```

- [ ] **Step 3: Verify all files are consistent**

Read through each modified file and confirm:
- Module names are consistent (WorkforcePresence not Attendance)
- Table counts match across files
- Event names are consistent across event-catalog and module-catalog
- Permission names are consistent across rules.md and auth-architecture.md
- No references to old "18 modules" or "126 tables" remain
