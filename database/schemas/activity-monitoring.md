# Activity Monitoring — Schema

**Module:** [[modules/activity-monitoring/overview|Activity Monitoring]]
**Phase:** Phase 1
**Tables:** 9

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

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `activity_monitoring_outbox_events`

Transactional outbox — written in the same DB transaction as the business write. A background processor reads and forwards to RabbitMQ.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `event_type` | `varchar(200)` | Fully-qualified event class name |
| `payload` | `jsonb` | Serialized IntegrationEvent |
| `created_at` | `timestamptz` | |
| `processed_at` | `timestamptz` | NULL = not yet delivered to RabbitMQ |
| `retry_count` | `integer` | Default 0; max 5 |
| `last_error` | `text` | Last failure message if any |

Index: `WHERE processed_at IS NULL` on `created_at` — the outbox processor queries this.

### `processed_integration_events`

Idempotency table — prevents double-processing if RabbitMQ redelivers a message.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | PK — same as `IntegrationEvent.EventId` |
| `event_type` | `varchar(200)` | |
| `processed_at` | `timestamptz` | |

---

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/agent-gateway/browser-extension|Browser Extension]] — source of browser_activity data
- [[database/schemas/discrepancy-engine|Discrepancy Engine Schema]] — `discrepancy_events` and `wms_daily_time_logs` (owned by Discrepancy Engine, split into separate schema file)
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]