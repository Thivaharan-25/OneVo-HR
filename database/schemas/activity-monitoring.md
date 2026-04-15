# Activity Monitoring — Schema

**Module:** [[modules/activity-monitoring/overview|Activity Monitoring]]
**Phase:** Phase 1
**Tables:** 11

---

## `activity_daily_summary`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` |  |
| `total_active_minutes` | `int` |  |
| `total_idle_minutes` | `int` |  |
| `total_meeting_minutes` | `int` |  |
| `active_percentage` | `decimal(5,2)` |  |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_avg` | `decimal(5,2)` | Average intensity score |
| `keyboard_total` | `int` | Total keyboard events |
| `mouse_total` | `int` | Total mouse events |
| `browser_active_minutes` | `int` | Total browser active time (from browser extension, nullable) |
| `work_browser_minutes` | `int` | Browser time on work-classified domains |
| `personal_browser_minutes` | `int` | Browser time on personal-classified domains |
| `document_time_minutes` | `int` | Word/Excel/PowerPoint/Google Docs combined time |
| `communication_time_minutes` | `int` | Outlook/Slack/Teams combined active time |
| `deep_focus_sessions_count` | `int` | Count of 30+ min uninterrupted sessions in one app |
| `data_source` | `varchar(20)` | `agent_windows`, `agent_mac`, `ide` |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `activity_raw_buffer`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `agent_device_id` | `uuid` | FK → registered_agents |
| `received_at` | `timestamptz` | Server receive time |
| `payload_json` | `jsonb` | Raw agent payload |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `agent_device_id` → [[database/schemas/agent-gateway#`registered_agents`|registered_agents]]

---

## `activity_snapshots`

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
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `application_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `application_name_pattern` | `varchar(255)` | Glob pattern (e.g., `*chrome*`) |
| `category` | `varchar(100)` | e.g., "Browser", "IDE", "Communication" |
| `is_productive` | `boolean` | Nullable |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `application_usage`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` |  |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy — never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable — from `application_categories` |
| `is_allowed` | `boolean` | Nullable — from resolved app allowlist. `false` = violation logged |
| `app_category_type` | `varchar(20)` | `productive`, `communication`, `meeting`, `personal`, `unknown` |
| `browser_domain` | `varchar(255)` | Nullable — populated only when browser extension active |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `device_tracking`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` |  |
| `laptop_active_minutes` | `int` |  |
| `estimated_mobile_minutes` | `int` | Estimated from gap analysis |
| `laptop_percentage` | `decimal(5,2)` |  |
| `detection_method` | `varchar(30)` | `agent`, `manual` |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `meeting_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `meeting_start` | `timestamptz` |  |
| `meeting_end` | `timestamptz` |  |
| `platform` | `varchar(20)` | `teams`, `zoom`, `meet`, `meet_browser`, `teams_browser`, `other` |
| `duration_minutes` | `int` | Computed |
| `had_camera_on` | `boolean` | Detected via process inspection |
| `had_mic_activity` | `boolean` | Detected via audio device usage |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `screenshots`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `captured_at` | `timestamptz` |  |
| `file_record_id` | `uuid` | FK → file_records (blob storage) |
| `trigger_type` | `varchar(20)` | `manual`, `on_demand` — NEVER scheduled or random (GDPR) |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `file_record_id` → [[database/schemas/infrastructure#`file_records`|file_records]]

---

## `browser_activity`

Domain-level browser activity from the optional browser extension (Chrome/Edge/Firefox). Only domain name is stored — never URL path, page content, or search queries.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `domain` | `varchar(255)` | Domain only, e.g. `github.com` — never full URL |
| `domain_classification` | `varchar(20)` | `work`, `personal`, `meeting`, `unknown` |
| `total_seconds` | `int` | Time on this domain |
| `source` | `varchar(20)` | `chrome_ext`, `edge_ext`, `firefox_ext` |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)`

**Privacy:** URL path, page title, and search queries are NEVER stored. Domain only. Browser extension is opt-in per tenant (`browser_extension_enabled` in agent policy).

---

## `discrepancy_events`

Daily discrepancy detection results — comparing HR active time (from agent) vs WMS-reported task time vs calendar-explained time. Used by the Discrepancy Engine to flag inflated or under-reported work.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `hr_active_minutes` | `int` | Ground truth from `activity_daily_summary` |
| `wms_logged_minutes` | `int` | What employee logged in WMS task time |
| `calendar_minutes` | `int` | Explained time from `calendar_events` (meetings, OOO) |
| `unaccounted_minutes` | `int` | Computed: `hr_active - wms_logged - calendar`. Negative = under-reporter |
| `severity` | `varchar(20)` | `none`, `low`, `high`, `critical` — based on tenant threshold config |
| `threshold_minutes` | `int` | Tenant-configured acceptable gap (default 60 min) |
| `notified_manager` | `boolean` | Whether manager was alerted |
| `notified_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)`, `(tenant_id, severity, date)`

**Visibility:** Discrepancy data is visible ONLY to the reporting manager and HR Admin. Employee never sees their own discrepancy record — only their personal activity timeline. Enforced at query level, not just UI level.

**Severity thresholds (default):**
- `none` — unaccounted gap < 30 min
- `low` — 30–60 min gap (automated reminder to employee to log time)
- `high` — 60–180 min gap (manager notified privately)
- `critical` — 180+ min gap (escalated to HR Admin)

---

## `wms_daily_time_logs`

WMS-submitted task time per employee per day. Consumed by the Discrepancy Engine as the `wms_logged_minutes` data stream. Populated via the Work Activity bridge (`POST /api/v1/bridges/work-activity/time-logs`). Upserted — re-submission for same employee + date overwrites.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `total_logged_minutes` | `int` | Aggregated from all task log entries for this day |
| `active_task_at` | `timestamptz` | Most recent active task timestamp (nullable — real-time context) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)` UNIQUE

**Note:** If no WMS integration exists, this table stays empty. Discrepancy Engine skips it gracefully (`wms_logged_minutes = 0`, only calendar cross-reference used).

---

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/discrepancy-engine/overview|Discrepancy Engine]] — reads this schema to produce discrepancy_events
- [[modules/agent-gateway/browser-extension|Browser Extension]] — source of browser_activity data
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]