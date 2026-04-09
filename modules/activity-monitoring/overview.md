# Module: Activity Monitoring

**Namespace:** `ONEVO.Modules.ActivityMonitoring`
**Phase:** 1 — Build
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 3 (Week 3)
**Tables:** 8
**Task File:** [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]

---

## Purpose

Receives, stores, and aggregates employee activity data from the desktop agent. Tracks application usage, keyboard/mouse intensity, idle periods, meeting detection, and optional screenshots. Produces daily summaries consumed by [[modules/productivity-analytics/overview|Productivity Analytics]] and [[modules/exception-engine/overview|Exception Engine]].

**This module is append-only for time-series tables.** Never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`.

---

## Dependencies

| Direction       | Module                     | Interface                    | Purpose                             |
| :-------------- | :------------------------- | :--------------------------- | :---------------------------------- |
| **Depends on**  | [[modules/infrastructure/overview|Infrastructure]]         | `ITenantContext`             | Multi-tenancy                       |
| **Depends on**  | [[modules/core-hr/overview|Core Hr]]                | `IEmployeeService`           | Employee/department context         |
| **Depends on**  | [[modules/configuration/overview|Configuration]]          | `IConfigurationService`      | Feature toggles, retention policies, app allowlist |
| **Depends on**  | [[modules/workforce-presence/overview|Workforce Presence]]     | `IWorkforcePresenceService`  | Presence window validation (only process data within active sessions) |
| **Consumed by** | [[modules/exception-engine/overview|Exception Engine]]       | `IActivityMonitoringService` | Latest activity for rule evaluation |
| **Consumed by** | [[modules/productivity-analytics/overview|Productivity Analytics]] | `IActivityMonitoringService` | Daily summaries for reports         |
| **Consumed by** | [[database/performance|Performance]]            | `IActivityMonitoringService` | Optional productivity scores        |

---

## Public Interface

```csharp
// ONEVO.Modules.ActivityMonitoring/Public/IActivityMonitoringService.cs
public interface IActivityMonitoringService
{
    Task<Result<ActivityDailySummaryDto>> GetDailySummaryAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<List<ActivitySnapshotDto>>> GetSnapshotsAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<List<ApplicationUsageDto>>> GetAppUsageAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<List<MeetingSessionDto>>> GetMeetingsAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<decimal>> GetAverageIntensityAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
}
```

---

## Database Tables (8)

### `activity_raw_buffer`

Temporary high-volume buffer. Data arrives from [[modules/agent-gateway/overview|Agent Gateway]], sits here until processed.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `agent_device_id` | `uuid` | FK → registered_agents |
| `received_at` | `timestamptz` | Server receive time |
| `payload_json` | `jsonb` | Raw agent payload |

**Partitioning:** Daily via `pg_partman` on `received_at`
**Retention:** Purged after 48 hours by `PurgeRawBufferJob`
**Insert method:** `COPY` or `unnest()` for batch performance
**NEVER query this table for reporting** — use `activity_daily_summary` instead.

### `activity_snapshots`

Periodic activity data from agent (every 2-3 minutes).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `captured_at` | `timestamptz` | When agent captured this snapshot |
| `keyboard_events_count` | `int` | Key press count (NOT keystrokes content) |
| `mouse_events_count` | `int` | Mouse event count |
| `active_seconds` | `int` | Seconds with input activity |
| `idle_seconds` | `int` | Seconds without input |
| `intensity_score` | `decimal(5,2)` | 0–100 computed score |
| `foreground_app` | `varchar(255)` | Application name (e.g., "Visual Studio Code") |
| `created_at` | `timestamptz` | |

**Partitioning:** Monthly via `pg_partman` on `captured_at`
**Retention:** 90 days
**Indexes:** `(tenant_id, employee_id, captured_at)`, `(tenant_id, captured_at)`

**Volume estimate:** ~240 rows/employee/day (one every 2-3 min for 8 hours). 500 employees = 120,000 rows/day.

### `application_usage`

Time per application per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy — never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable — from `application_categories` |
| `is_allowed` | `boolean` | Nullable — from resolved app allowlist. `false` = violation logged |

**Indexes:** `(tenant_id, employee_id, date)`, `(tenant_id, date, application_category)`, `(tenant_id, employee_id, date, is_allowed)` (for violation queries)

### `meeting_sessions`

Detected meeting time.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `meeting_start` | `timestamptz` | |
| `meeting_end` | `timestamptz` | |
| `platform` | `varchar(20)` | `teams`, `zoom`, `meet`, `other` |
| `duration_minutes` | `int` | Computed |
| `had_camera_on` | `boolean` | Detected via process inspection |
| `had_mic_activity` | `boolean` | Detected via audio device usage |

**Phase 1:** Meeting detection is basic — process name matching (e.g., `Teams.exe`, `zoom.exe`).
**Phase 2:** Microsoft Teams Graph API for rich meeting analytics.

### `screenshots`

Optional periodic screenshots. **RESTRICTED data classification.**

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `captured_at` | `timestamptz` | |
| `file_record_id` | `uuid` | FK → file_records (blob storage) |
| `trigger_type` | `varchar(20)` | `scheduled`, `random`, `manual`, `on_demand` |
| `created_at` | `timestamptz` | |

**Screenshots are stored in blob storage, NOT in the database.** Only metadata lives here.
**Retention:** Per tenant retention policy (default 30 days).

### `activity_daily_summary`

Pre-aggregated daily rollup. **This is the primary table for reporting.**

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `total_active_minutes` | `int` | |
| `total_idle_minutes` | `int` | |
| `total_meeting_minutes` | `int` | |
| `active_percentage` | `decimal(5,2)` | |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_avg` | `decimal(5,2)` | Average intensity score |
| `keyboard_total` | `int` | Total keyboard events |
| `mouse_total` | `int` | Total mouse events |

**Retention:** 2 years (small, pre-aggregated)
**Upsert:** INSERT or UPDATE on conflict for `(tenant_id, employee_id, date)` — this is the ONLY activity table that allows UPDATE.

### `application_categories`

Tenant-configurable app categorization.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `application_name_pattern` | `varchar(255)` | Glob pattern (e.g., `*chrome*`) |
| `category` | `varchar(100)` | e.g., "Browser", "IDE", "Communication" |
| `is_productive` | `boolean` | Nullable |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### `device_tracking`

Device interaction tracking per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `laptop_active_minutes` | `int` | |
| `estimated_mobile_minutes` | `int` | Estimated from gap analysis |
| `laptop_percentage` | `decimal(5,2)` | |
| `detection_method` | `varchar(30)` | `agent`, `manual` |

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ActivitySnapshotReceived` | Raw data processed into snapshot | [[modules/exception-engine/overview|Exception Engine]] (evaluate rules) |
| `DailySummaryAggregated` | Daily summary job completes | [[modules/productivity-analytics/overview|Productivity Analytics]] (build reports) |
| `ScreenshotCaptured` | Screenshot stored | Audit trail |
| `AppAllowlistViolationDetected` | Employee used non-allowed app exceeding threshold | [[modules/exception-engine/overview|Exception Engine]] (fire `non_allowed_app` rule) |

---

## Key Business Rules

1. **Activity data is append-only.** Never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`.
2. **Window titles are hashed** (SHA-256) before storage. Never store raw window titles — they may contain sensitive business data.
3. **Never log activity content** — log activity COUNTS (keyboard_events_count, mouse_events_count) but NEVER window titles, application names, or screenshot contents.
4. **Feature toggle check:** Before processing any data, verify the feature is enabled for this employee via `IConfigurationService`. The desktop agent checks policy on login, but the **server must double-validate**.
5. **Intensity score formula:** `(keyboard_events_count + mouse_events_count) / max_expected_events * 100`, capped at 100.
6. **Presence-window validation:** Only process activity snapshots that fall within an active presence session. Snapshots outside clock-in/clock-out or during breaks are discarded with a warning log. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]].
7. **App allowlist check:** During `ProcessRawBufferJob`, each `app_usage` record is checked against the employee's resolved allowlist (via `IConfigurationService.GetResolvedAppAllowlistAsync`). The `is_allowed` flag is set on `application_usage`. If cumulative non-allowed usage exceeds the tenant's `violation_threshold_minutes`, publish `AppAllowlistViolationDetected` event.
8. **Break time exclusion:** Activity data received during break periods is discarded. The `total_active_minutes` and `total_idle_minutes` in `activity_daily_summary` only count time within active presence windows (excluding breaks).

---

## Data Pipeline

```
Agent → Agent Gateway (202 Accepted)
  → activity_raw_buffer (COPY/unnest, partitioned daily)
  → ProcessRawBufferJob (Hangfire, every 2 min)
    → 1. Presence-window validation: check snapshot falls within active presence session
       → Outside session or during break → discard with warning log
    → 2. activity_snapshots (parsed, validated)
    → 3. application_usage (aggregated per app)
       → Check each app against resolved allowlist → set is_allowed flag
       → If cumulative non-allowed > threshold → publish AppAllowlistViolationDetected
    → 4. meeting_sessions (if meeting app detected)
    → 5. device_tracking (daily rollup)
  → AggregateDailySummaryJob (Hangfire, every 30 min during work hours + end of day)
    → activity_daily_summary (INSERT or UPDATE on conflict)
    → Only counts minutes within active presence windows (excludes breaks)
```

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/snapshots/{employeeId}` | `workforce:view` | Activity snapshots for date range |
| GET | `/api/v1/activity/summary/{employeeId}` | `workforce:view` | Daily summary |
| GET | `/api/v1/activity/apps/{employeeId}` | `workforce:view` | Application usage breakdown |
| GET | `/api/v1/activity/meetings/{employeeId}` | `workforce:view` | Meeting sessions |
| GET | `/api/v1/activity/screenshots/{employeeId}` | `workforce:view` | Screenshot list (metadata only) |
| GET | `/api/v1/activity/screenshots/{id}/view` | `workforce:view` | View screenshot (redirect to blob URL) |
| GET | `/api/v1/activity/categories` | `monitoring:view-settings` | Application categories |
| POST | `/api/v1/activity/categories` | `monitoring:configure` | Create/update app category |
| DELETE | `/api/v1/activity/categories/{id}` | `monitoring:configure` | Delete app category |
| GET | `/api/v1/activity/my/summary` | `activity:read:self` | Employee's own daily summary (self-service) |
| GET | `/api/v1/activity/my/apps` | `activity:read:self` | Employee's own app usage breakdown |
| GET | `/api/v1/activity/my/trends` | `activity:read:self` | Employee's own weekly/monthly trends |
| GET | `/api/v1/activity/my/meetings` | `activity:read:self` | Employee's own meeting sessions |

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ProcessRawBufferJob` | Every 2 min | High | Parse raw buffer → snapshots, app usage, meetings |
| `AggregateDailySummaryJob` | Every 30 min + EOD | Default | Roll up snapshots → daily summary |
| `PurgeRawBufferJob` | Daily 3:00 AM | Low | Drop partitions older than 48 hours |
| `PurgeExpiredScreenshotsJob` | Daily 4:00 AM | Low | Delete screenshots past retention policy |
| `PurgeExpiredSnapshotsJob` | Monthly | Batch | Drop snapshot partitions older than 90 days |

---

## Important Notes

- **Data volume:** 240 rows/employee/day in snapshots. Plan queries with `tenant_id + date range` always.
- **Raw buffer is NOT for reporting.** It's a temporary staging area.
- **Retention tiers:** Raw buffer (48h) → Snapshots (90 days) → Daily summaries (2 years).
- **This module does NOT determine presence** — that's [[modules/workforce-presence/overview|Workforce Presence]]. This module tracks what the employee is doing while present.

## Features

- [[modules/activity-monitoring/screenshots/overview|Screenshots]] — Optional periodic screenshot capture (RESTRICTED data)
- [[modules/activity-monitoring/meeting-detection/overview|Meeting Detection]] — Meeting time tracking via process name matching
- [[modules/activity-monitoring/application-tracking/overview|Application Tracking]] — Application usage categorization and time tracking
- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]] — Buffer ingestion and snapshot parsing pipeline
- [[modules/activity-monitoring/device-tracking/overview|Device Tracking]] — Device interaction tracking per day
- [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]] — Pre-aggregated daily rollup jobs
- App Allowlist Check — Checks app usage against resolved allowlist during processing, flags violations
- Self Service Api — Employee-facing API endpoints for viewing own activity data (`activity:read:self` permission)
- Presence Window Validation — Validates snapshots fall within active presence sessions, discards break-time data

---

## Related

- [[security/auth-architecture|Auth Architecture]] — Device JWT for agent data ingestion
- [[infrastructure/multi-tenancy|Multi Tenancy]] — All activity tables are tenant-scoped
- [[security/data-classification|Data Classification]] — Window titles hashed (SHA-256), screenshots are RESTRICTED
- [[security/compliance|Compliance]] — Monitoring consent required before processing
- [[backend/messaging/event-catalog|Event Catalog]] — `ActivitySnapshotReceived`, `DailySummaryAggregated`, `ScreenshotCaptured`
- [[code-standards/logging-standards|Logging Standards]] — Log activity counts only, never content
- [[database/migration-patterns|Migration Patterns]] — Partitioned tables via pg_partman
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/exception-engine/overview|Exception Engine]]

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.

### Microsoft Teams Graph API Integration
Phase 1 uses basic process name matching (`Teams.exe`, `zoom.exe`) for meeting detection. Phase 2 will integrate with the Microsoft Teams Graph API for rich meeting analytics: participant lists, meeting duration from calendar, audio/video participation status, screen sharing detection. This requires Azure AD app registration and tenant-level Graph API consent.

### Screen Recording
Phase 2 will add continuous or triggered screen recording as a data collection type alongside screenshots. This requires significant storage planning, employee consent flows, and retention policy updates.

### AI-Powered Activity Classification
Phase 2 may add ML-based classification of productive vs. non-productive activity based on app usage patterns, rather than relying on manual `application_categories` configuration.
