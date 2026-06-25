# Module: Activity Monitoring

**Feature Folder:** `Application/Features/ActivityMonitoring`
**Phase:** 1 - Build
**Pillar:** 2 - Monitoring
**Owner:** Dev 3 (Week 3)
**Tables:** 8
**Task File:** [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]

---

## Purpose

Receives, stores, and aggregates employee activity data from the desktop agent. Tracks application usage, keyboard/mouse intensity, idle periods, meeting detection, and optional screenshots. Produces daily summaries consumed by [[modules/productivity-analytics/overview|Productivity Analytics]]. Phase 1 includes lightweight non-allowed app and idle threshold detection with alerts routed through Notifications/Inbox. Phase 2 may add configurable [[modules/exception-engine/overview|Exception Engine]] rules.

**This module is append-only for time-series tables.** Never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`.

---

## Dependencies

| Direction       | Module                     | Interface                    | Purpose                             |
| :-------------- | :------------------------- | :--------------------------- | :---------------------------------- |
| **Depends on**  | [[modules/infrastructure/overview\|Infrastructure]]         | `ITenantContext`             | Multi-tenancy                       |
| **Depends on**  | [[modules/core-hr/overview\|Core Hr]]                | `IEmployeeService`           | Employee/department context         |
| **Depends on**  | [[modules/configuration/overview\|Configuration]]          | `IConfigurationService`      | Feature toggles, retention policies, app allowlist |
| **Depends on**  | [[modules/time-attendance/overview\|Time & Attendance]]     | `ITimeAttendanceService`  | Presence window validation (only process data within active sessions) |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]]       | `IActivityMonitoringService` | Phase 2: latest activity for configurable rule evaluation |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | `IActivityMonitoringService` | Daily summaries for reports         |
| **Consumed by** | [[database/performance\|Performance]]            | `IActivityMonitoringService` | Optional productivity scores        |

---

## Public Interface

```csharp
// ONEVO.Application.Features.ActivityMonitoring/Public/IActivityMonitoringService.cs
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

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/ActivityMonitoring/Entities/
  ONEVO.Domain/Features/ActivityMonitoring/Events/

Application (CQRS):
  ONEVO.Application/Features/ActivityMonitoring/Commands/
  ONEVO.Application/Features/ActivityMonitoring/Queries/
  ONEVO.Application/Features/ActivityMonitoring/DTOs/Requests/
  ONEVO.Application/Features/ActivityMonitoring/DTOs/Responses/
  ONEVO.Application/Features/ActivityMonitoring/Validators/
  ONEVO.Application/Features/ActivityMonitoring/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/ActivityMonitoring/

API endpoints:
  ONEVO.Api/Controllers/ActivityMonitoring/ActivityMonitoringController.cs

---

## Database Tables (8)

### `activity_raw_buffer`

Temporary high-volume buffer. Data arrives from [[modules/agent-gateway/overview|Agent Gateway]], sits here until processed.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `agent_device_id` | `uuid` | FK -> registered_agents |
| `received_at` | `timestamptz` | Server receive time |
| `payload_json` | `jsonb` | Raw agent payload |

**Partitioning:** Daily via `pg_partman` on `received_at`
**Retention:** Purged after 48 hours by `PurgeRawBufferJob`
**Insert method:** `COPY` or `unnest()` for batch performance
**NEVER query this table for reporting** - use `activity_daily_summary` instead.

### `activity_snapshots`

Periodic activity data from agent (every 2-3 minutes).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `captured_at` | `timestamptz` | When agent captured this snapshot |
| `keyboard_events_count` | `int` | Key press count (NOT keystrokes content) |
| `mouse_events_count` | `int` | Mouse event count |
| `active_seconds` | `int` | Seconds with input activity |
| `idle_seconds` | `int` | Seconds without input |
| `intensity_score` | `decimal(5,2)` | 0-100 computed score |
| `foreground_process_name` | `varchar(100)` | Foreground process name (e.g., `code.exe`) |
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
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `process_name` | `varchar(100)` | e.g., `chrome.exe` - authoritative matching key |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" - display metadata only |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy - never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable - from `application_categories` |
| `is_allowed` | `boolean` | Nullable - from resolved app allowlist. `false` = violation logged |

**Indexes:** `(tenant_id, employee_id, date)`, `(tenant_id, date, application_category)`, `(tenant_id, employee_id, date, is_allowed)` (for violation queries)

### `meeting_sessions`

Detected meeting time.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `meeting_start` | `timestamptz` | |
| `meeting_end` | `timestamptz` | |
| `duration_minutes` | `int` | Computed |
| `had_camera_on` | `boolean` | Detected via process inspection |
| `had_mic_activity` | `boolean` | Detected via audio device usage |

**Phase 1:** Meeting detection is basic - process name matching (e.g., `Teams.exe`, `zoom.exe`).

### `monitoring_evidence_assets`

Policy-controlled screenshots. **RESTRICTED data classification.** Screenshots are captured only by authorized live on-demand request or automatic deviation capture when enabled by effective monitoring policy. Interval and random screenshots are not supported.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `agent_device_id` | `uuid` | Nullable FK -> registered_agents |
| `activity_snapshot_id` | `uuid` | Nullable FK -> activity_snapshots |
| `captured_at` | `timestamptz` | |
| `file_record_id` | `uuid` | FK -> file_records (blob storage) |
| `evidence_type` | `varchar(40)` | `screenshot`, `app_snapshot`, `browser_snapshot`, `idle_evidence` |
| `trigger_type` | `varchar(20)` | `on_demand`, `auto_deviation` |
| `retention_policy_id` | `uuid` | Nullable FK -> retention_policies |
| `legal_hold_id` | `uuid` | Nullable FK -> legal_holds |
| `created_at` | `timestamptz` | |

**Screenshots are stored in blob storage, NOT in the database.** Only evidence metadata lives here.
**Retention:** Per tenant retention policy (default 30 days).

### `activity_daily_summary`

Pre-aggregated daily rollup. **This is the primary table for reporting.**

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `total_active_minutes` | `int` | |
| `total_idle_minutes` | `int` | |
| `total_meeting_minutes` | `int` | |
| `active_percentage` | `decimal(5,2)` | Activity rate; not final productivity |
| `productive_app_minutes` | `int` | Active time in work-classified apps/domains |
| `personal_app_minutes` | `int` | Active time in personal-classified apps/domains |
| `unknown_app_minutes` | `int` | Active time where app/domain classification is unknown |
| `focus_minutes` | `int` | Time in 30+ minute uninterrupted productive sessions |
| `activity_score` | `decimal(5,2)` | Monitoring-derived score, 0-100 |
| `data_coverage_percentage` | `decimal(5,2)` | How complete agent/presence data is for the day |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_avg` | `decimal(5,2)` | Average intensity score |
| `keyboard_total` | `int` | Total keyboard events |
| `mouse_total` | `int` | Total mouse events |

**Retention:** 2 years (small, pre-aggregated)
**Upsert:** INSERT or UPDATE on conflict for `(tenant_id, employee_id, date)` - this is the ONLY activity table that allows UPDATE.

### `application_categories`

Tenant-configurable app categorization.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `application_name_pattern` | `varchar(255)` | Glob pattern (e.g., `*chrome*`) |
| `category` | `varchar(100)` | e.g., "Browser", "IDE", "Communication" |
| `is_productive` | `boolean` | Nullable |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

### `device_tracking`

Device interaction tracking per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `laptop_active_minutes` | `int` | |
| `estimated_mobile_minutes` | `int` | Estimated from gap analysis |
| `laptop_percentage` | `decimal(5,2)` | |
| `detection_method` | `varchar(30)` | `agent`, `manual` |

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AppAllowlistViolationDetected` | Cumulative non-allowed app usage exceeds tenant threshold | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight alert, recipient resolved by Monitoring Policy) |
| `IdleThresholdExceeded` | Aggregated idle time exceeds configured threshold | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight alert, recipient resolved by Monitoring Policy) |
| `ExceptionDetected` | Activity snapshot triggers an exception condition | Phase 2: [[modules/exception-engine/overview\|Exception Engine]] configurable rules |
| `DiscrepancyDetected` | Discrepancy detected during processing | [[modules/discrepancy-engine/overview\|Discrepancy Engine]] |
| `ActivitySnapshotReceived` | Raw data processed into snapshot | Phase 2: [[modules/exception-engine/overview\|Exception Engine]]; [[modules/identity-verification/overview\|Identity Verification]] |
| `DailySummaryAggregated` | Daily summary job completes | [[modules/productivity-analytics/overview\|Productivity Analytics]], [[modules/discrepancy-engine/overview\|Discrepancy Engine]] |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `PresenceSessionStarted` | [[modules/time-attendance/overview\|Time & Attendance]] | Begin accepting snapshots for the employee's active session |

---

## Key Business Rules

1. **Activity data is append-only.** Never UPDATE rows in `activity_snapshots`, `application_usage`, or `activity_raw_buffer`.
2. **Window titles are hashed** (SHA-256) before storage. Never store raw window titles - they may contain sensitive business data.
3. **Never log activity content** - log activity COUNTS (keyboard_events_count, mouse_events_count), application/process names needed for categorization, and hashed window titles only. Never store keystroke content, raw window titles, full URLs, page content, search queries, or screenshot contents in logs.
4. **Feature toggle check:** Before processing any data, verify the feature is enabled for this employee via `IConfigurationService`. The desktop agent checks policy on login, but the **server must double-validate**.
5. **Intensity score formula:** `(keyboard_events_count + mouse_events_count) / max_expected_events * 100`, capped at 100.
6. **Presence-window validation:** Only process activity snapshots that fall within an active presence session. Snapshots outside clock-in/clock-out, during breaks, or during approved Time Off intervals are discarded with a warning log. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]].
7. **App allowlist check:** Non-allowed app usage is only counted during active working intervals — not during breaks, not during approved Time Off, not after clock-out. During `ProcessRawBufferJob`, each `app_usage` record is checked against the employee's resolved allowlist by `process_name` (via `IConfigurationService.GetResolvedAppAllowlistAsync`). The `is_allowed` flag is set on `application_usage`. If cumulative non-allowed usage exceeds the tenant's `non_allowed_app_threshold_minutes` (Phase 1 config key), publish `AppAllowlistViolationDetected` event. The payload carries `threshold_seconds` (= config minutes × 60). Phase 2 Exception Engine rules use `violation_threshold_minutes` in `threshold_json` instead.
8. **Break time exclusion:** Activity data received during break periods is discarded. The `total_active_minutes` and `total_idle_minutes` in `activity_daily_summary` only count time within active presence windows (excluding breaks).
9. **Approved Time Off exclusion:** Activity data received during approved Time Off intervals is discarded. During approved partial-day Time Off: no idle tracking, no app tracking, no work-location evidence evaluation, no discrepancy alert for that interval. Late return from Time Off is a separate attendance/monitoring alert (`late_return_from_time_off`), not normal idle.
10. **Activity score is not productivity.** Activity Monitoring produces `activity_score` and supporting context only. Final `productivity_score` is owned by Productivity Analytics and may combine this data with WorkSync output evidence.
11. **Meeting handling:** Valid meeting minutes inside presence windows count as work context and reduce idle penalties. Low input activity during a detected meeting is not automatically low productivity.

---

## Phase 1 Monitoring Alerts

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Activity Monitoring is a Phase 1 alert producer. It creates lightweight alert/notification records and routes them through Notifications/Inbox.

**Monitoring Policy recipient resolution:**

Monitoring Policy determines who receives monitoring/verification alerts using `monitoring_alert_recipient_resolver`.

Allowed values:
- `management_coverage_availability_chain` (default)
- `reporting_manager`

`management_coverage_availability_chain` routes to the first available responsible person from the employee's active management coverage assignments:
1. Load active date-effective coverage assignments.
2. Order responsible people by configured coverage priority / responsibility weight / effective assignment order.
3. Filter to users with the required alert permission.
4. Check availability:
   - scheduled to work now, or inside the alert routing window
   - clocked in / present
   - not on approved leave
   - not marked unavailable
5. If a responsible person is scheduled but has not reached scheduled start time + `monitoring_alert_wait_for_scheduled_recipient_grace_minutes`, wait before skipping.
6. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action`.

`reporting_manager` resolves the employee's reporting manager from position hierarchy, then applies the same permission and availability checks. If unavailable and `monitoring_alert_fallback_to_management_coverage_chain` is enabled, fall back to `management_coverage_availability_chain`.

Never silently route monitoring alerts to random HR/admin users.

### Phase 1 Non-Allowed App Detection

Phase 1 non-allowed app detection is owned by Activity Monitoring, not Exception Engine.

**Process:**
1. Agent sends foreground app usage.
2. Activity Monitoring stores aggregated usage in `application_usage`.
3. Configuration resolves allowlist/blocklist by `process_name`.
4. `application_usage.is_allowed` is set:
   - `true` = allowed
   - `false` = blocked/non-allowed
   - `null` = pending review, never alert
5. Activity Monitoring groups non-allowed usage per employee/date/app.
6. If usage exceeds configured threshold, publish `AppAllowlistViolationDetected`.
7. Notifications/Inbox routes alert to recipient resolved by Monitoring Policy.

> Phase 2 may move this into configurable Exception Engine rules. Phase 1 uses Activity Monitoring lightweight detection.

### AppAllowlistViolationDetected Payload

| Field | Type | Description |
|:------|:-----|:------------|
| `employee_id` | `uuid` | |
| `date` | `date` | |
| `application_name` | `varchar(255)` | Display name |
| `process_name` | `varchar(100)` | Authoritative matching key |
| `application_category` | `varchar(100)` | |
| `total_non_allowed_seconds` | `int` | Cumulative non-allowed usage |
| `first_seen_at` | `timestamptz` | |
| `last_seen_at` | `timestamptz` | |
| `threshold_seconds` | `int` | Configured threshold that was breached |
| `allowlist_mode` | `varchar(20)` | `allowlist` or `blocklist` |
| `matched_allowlist_scope` | `varchar(30)` | Scope that resolved the violation |
| `evidence_asset_ids` | `uuid[]` | Nullable |
| `review_status` | `varchar(20)` | `new`, `acknowledged`, `dismissed`, `resolved` |

**Notification content rule:** Reviewer notification includes app name, category, duration, threshold breached, date/time range, and employee context. It must not include raw window title, keystroke content, full URLs, page content, or search queries.

### Non-Allowed App Severity Configuration

Tenant-configurable fields (stored in monitoring configuration / `tenant_settings`):

| Setting | Type | Description |
|:--------|:-----|:------------|
| `non_allowed_app_threshold_minutes` | `int` | Minutes before first alert |
| `non_allowed_app_repeat_threshold_count` | `int` | Repeat violations before escalation |
| `non_allowed_app_repeat_window_days` | `int` | Window for counting repeats |
| `non_allowed_app_low_action` | `varchar(30)` | `log_only` or `employee_reminder` |
| `non_allowed_app_high_action` | `varchar(30)` | `notify_reviewer` |
| `non_allowed_app_critical_action` | `varchar(30)` | `notify_reviewer_immediately` |
| `non_allowed_app_evidence_capture_enabled` | `boolean` | Whether to capture screenshot evidence |

**Severity rules:**
- **Low:** Below threshold or first short event; stored only or employee reminder if configured.
- **High:** Threshold exceeded; notify recipient resolved by Monitoring Policy.
- **Critical:** Repeated threshold breaches or critical app/category; notify reviewer immediately.

### Idle Alert Timing

Idle signals during the day are collected into activity snapshots and daily summaries. Phase 1 does not constantly notify managers for every idle period.

Idle review alerts are created only when configured thresholds are exceeded after aggregation, unless tenant policy explicitly enables immediate critical idle alerts.

### Idle Alert Payload

| Field | Type | Description |
|:------|:-----|:------------|
| `employee_id` | `uuid` | |
| `date` | `date` | |
| `total_idle_minutes` | `int` | |
| `longest_idle_period_minutes` | `int` | |
| `threshold_minutes` | `int` | Configured threshold that was breached |
| `presence_session_id` | `uuid` | |
| `active_work_window` | `varchar(50)` | e.g., "09:00-17:00" |
| `severity` | `varchar(20)` | `low`, `high`, `critical` |

---

## Data Pipeline

```
Agent -> Agent Gateway (202 Accepted)
  -> activity_raw_buffer (COPY/unnest, partitioned daily)
  -> ProcessRawBufferJob (Hangfire, every 2 min)
    -> 1. Presence-window validation: check snapshot falls within active presence session
       -> Outside session or during break -> discard with warning log
    -> 2. activity_snapshots (parsed, validated)
    -> 3. application_usage (aggregated per app)
       -> Check each app against resolved allowlist -> set is_allowed flag
       -> If cumulative non-allowed > threshold -> publish AppAllowlistViolationDetected
    -> 4. meeting_sessions (if meeting app detected)
    -> 5. device_tracking (daily rollup)
  -> AggregateDailySummaryJob (Hangfire, every 30 min during work hours + end of day)
    -> activity_daily_summary (INSERT or UPDATE on conflict)
    -> Only counts minutes within active presence windows (excludes breaks)
```

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/snapshots/{employeeId}` | `monitoring:view` | Activity snapshots for date range |
| GET | `/api/v1/activity/summary/{employeeId}` | `monitoring:view` | Daily summary |
| GET | `/api/v1/activity/apps/{employeeId}` | `monitoring:view` | Application usage breakdown |
| GET | `/api/v1/activity/meetings/{employeeId}` | `monitoring:view` | Meeting sessions |
| GET | `/api/v1/activity/screenshots/{employeeId}` | `monitoring:view` | Screenshot list (metadata only) |
| GET | `/api/v1/activity/screenshots/{id}/view` | `monitoring:view` | View screenshot (redirect to blob URL) |
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
| `ProcessRawBufferJob` | Every 2 min | High | Parse raw buffer -> snapshots, app usage, meetings |
| `AggregateDailySummaryJob` | Every 30 min + EOD | Default | Roll up snapshots -> daily summary |
| `PurgeRawBufferJob` | Daily 3:00 AM | Low | Drop partitions older than 48 hours |
| `PurgeExpiredMonitoringEvidenceJob` | Daily 4:00 AM | Low | Delete screenshot evidence past retention policy, unless held |
| `PurgeExpiredSnapshotsJob` | Monthly | Batch | Drop snapshot partitions older than 90 days |

---

## Important Notes

- **Data volume:** 240 rows/employee/day in snapshots. Plan queries with `tenant_id + date range` always.
- **Raw buffer is NOT for reporting.** It's a temporary staging area.
- **Retention tiers:** Raw buffer (48h) -> Snapshots (90 days) -> Daily summaries (2 years).
- **This module does NOT determine presence** - that's [[modules/time-attendance/overview|Time & Attendance]]. This module tracks what the employee is doing while present.

## Features

- [[modules/activity-monitoring/screenshots/overview|Screenshots]] - Policy-controlled on-demand and auto-deviation screenshot capture (RESTRICTED data)
- [[modules/activity-monitoring/meeting-detection/overview|Meeting Detection]] - Meeting time tracking via process name matching
- [[modules/activity-monitoring/application-tracking/overview|Application Tracking]] - Application usage categorization and time tracking
- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]] - Buffer ingestion and snapshot parsing pipeline
- [[modules/activity-monitoring/device-tracking/overview|Device Tracking]] - Device interaction tracking per day
- [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]] - Pre-aggregated daily rollup jobs
- App Allowlist Check - Checks app usage against resolved allowlist during processing, flags violations
- Self Service Api - Employee-facing API endpoints for viewing own activity data (`activity:read:self` permission)
- Presence Window Validation - Validates snapshots fall within active presence sessions, discards break-time data

---

## Related

- [[security/auth-architecture|Auth Architecture]] - Device JWT for agent data ingestion
- [[infrastructure/multi-tenancy|Multi Tenancy]] - All activity tables are tenant-scoped
- [[security/data-classification|Data Classification]] - Window titles hashed (SHA-256), screenshots are RESTRICTED
- [[security/compliance|Compliance]] - Required Legal & Privacy item must be complete before affected monitoring processing
- [[backend/messaging/event-catalog|Event Catalog]] - `ActivitySnapshotReceived`, `DailySummaryAggregated`, `ScreenshotCaptured`
- [[code-standards/logging-standards|Logging Standards]] - Log activity counts only, never content
- [[database/migration-patterns|Migration Patterns]] - Partitioned tables via pg_partman
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]] - Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/time-attendance/overview|Time & Attendance]], [[modules/exception-engine/overview|Exception Engine]] (Phase 2 configurable rules)

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.


### Screen Recording
Phase 2 will add continuous or triggered screen recording as a data collection type alongside screenshots. This requires significant storage planning, employee consent flows, and retention policy updates.

### AI-Powered Activity Classification
Phase 2 may add ML-based classification of productive vs. non-productive activity based on app usage patterns, rather than relying on manual `application_categories` configuration.
