# Activity Monitoring - Schema

**Module:** [[modules/activity-monitoring/overview|Activity Monitoring]]
**Phase:** Phase 1
**Tables:** 9

---

## `activity_daily_summary`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` |  |
| `total_active_minutes` | `int` |  |
| `total_idle_minutes` | `int` |  |
| `total_meeting_minutes` | `int` |  |
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
| `browser_active_minutes` | `int` | Total browser active time (from browser extension, nullable) |
| `work_browser_minutes` | `int` | Browser time on work-classified domains |
| `personal_browser_minutes` | `int` | Browser time on personal-classified domains |
| `document_time_minutes` | `int` | Word/Excel/PowerPoint/Google Docs combined time |
| `deep_focus_sessions_count` | `int` | Count of 30+ min uninterrupted sessions in one app |
| `data_source` | `varchar(20)` | `agent_windows`, `agent_mac`, `ide` |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `activity_raw_buffer`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `agent_device_id` | `uuid` | FK -> registered_agents |
| `received_at` | `timestamptz` | Server receive time |
| `payload_json` | `jsonb` | Raw agent payload |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `agent_device_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]]

---

## `activity_snapshots`

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
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `application_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `application_name_pattern` | `varchar(255)` | Glob pattern (e.g., `*chrome*`) |
| `category` | `varchar(100)` | e.g., "Browser", "IDE", "Communication" |
| `is_productive` | `boolean` | Nullable |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `application_usage`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` |  |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" |
| `process_name` | `varchar(100)` | e.g., `chrome.exe` - authoritative matching key |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy - never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable - from `application_categories` |
| `is_allowed` | `boolean` | Nullable - from resolved app allowlist. `false` = violation logged |
| `app_category_type` | `varchar(20)` | `productive`, `communication`, `meeting`, `personal`, `unknown` |
| `browser_domain` | `varchar(255)` | Nullable - populated only when browser extension active |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `device_tracking`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` |  |
| `laptop_active_minutes` | `int` |  |
| `estimated_mobile_minutes` | `int` | Estimated from gap analysis |
| `laptop_percentage` | `decimal(5,2)` |  |
| `detection_method` | `varchar(30)` | `agent`, `manual` |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `meeting_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `meeting_start` | `timestamptz` |  |
| `meeting_end` | `timestamptz` |  |
| `platform` | `varchar(20)` | `teams`, `zoom`, `meet`, `meet_browser`, `teams_browser`, `other` |
| `duration_minutes` | `int` | Computed |
| `had_camera_on` | `boolean` | Detected via process inspection |
| `had_mic_activity` | `boolean` | Detected via audio device usage |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `monitoring_evidence_assets`

Evidence files captured by the monitoring agent. These files are not normal reusable assets and must not be stored in `entity_assets`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `agent_device_id` | `uuid` | Nullable FK -> registered_agents |
| `activity_snapshot_id` | `uuid` | Nullable FK -> activity_snapshots |
| `activity_event_id` | `uuid` | Nullable source event ID |
| `captured_at` | `timestamptz` |  |
| `file_record_id` | `uuid` | FK -> file_records (blob storage) |
| `evidence_type` | `varchar(40)` | `screenshot`, `app_snapshot`, `browser_snapshot`, `idle_evidence` |
| `source` | `varchar(30)` | `agent`, `browser_extension`, `system` |
| `trigger_type` | `varchar(20)` | `on_demand`, `auto_deviation` |
| `retention_policy_id` | `uuid` | Nullable FK -> retention_policies |
| `legal_hold_id` | `uuid` | Nullable FK -> legal_holds |
| `metadata` | `jsonb` | Safe non-secret metadata |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `agent_device_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]], `activity_snapshot_id` -> [[#`activity_snapshots`|activity_snapshots]], `file_record_id` -> [[database/schemas/infrastructure#`file_records`|file_records]]

**Rules:** evidence view/download must be audit logged. Evidence deletion must respect retention policy and legal hold. Monitoring evidence must not be reused as profile photos, logos, or project covers. Screenshot capture is never random or interval-based; deviation details such as idle threshold, non-allowed app, presence/activity mismatch, or heartbeat gap live in `metadata`, not in `trigger_type`.

---

## `browser_activity`

Domain-level browser activity from the optional browser extension (Chrome/Edge/Firefox). Only domain name is stored - never URL path, page content, or search queries.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `domain` | `varchar(255)` | Domain only, e.g. `github.com` - never full URL |
| `domain_classification` | `varchar(20)` | `work`, `personal`, `meeting`, `unknown` |
| `total_seconds` | `int` | Time on this domain |
| `source` | `varchar(20)` | `chrome_ext`, `edge_ext`, `firefox_ext` |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)`

**Privacy:** URL path, page title, and search queries are NEVER stored. Domain only. Browser extension is opt-in per tenant (`browser_extension_enabled` in agent policy).

---

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/agent-gateway/browser-extension|Browser Extension]] - source of browser_activity data
- [[database/schemas/discrepancy-engine|Discrepancy Engine Schema]] - `discrepancy_events` and `work_management_daily_time_logs` (owned by Discrepancy Engine, split into separate schema file)
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
