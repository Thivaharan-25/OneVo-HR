# Configuration — Schema

**Module:** [[modules/configuration/overview|Configuration]]
**Phase:** Phase 1
**Tables:** 6

---

## `app_allowlist_audit`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `allowlist_id` | `uuid` | FK → app_allowlists |
| `action` | `varchar(20)` | `created`, `updated`, `deleted` |
| `changed_by_id` | `uuid` | FK → users |
| `old_value_json` | `jsonb` | Previous state |
| `new_value_json` | `jsonb` | New state |
| `changed_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `allowlist_id` → [[#`app_allowlists`|app_allowlists]], `changed_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `app_allowlists`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `scope_type` | `varchar(20)` | `tenant`, `role`, `employee` |
| `scope_id` | `uuid` | Null for tenant, role_id for role, employee_id for employee |
| `application_name` | `varchar(200)` | e.g., "Microsoft Teams", "Visual Studio Code" |
| `process_name` | `varchar(100)` | e.g., "ms-teams.exe" — authoritative matching key. Nullable (backward-compatible) |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `is_allowed` | `boolean` | True = allowed during work, False = not allowed |
| `source` | `varchar(20)` | `global_catalog`, `tenant_observed`, `manual` |
| `global_catalog_id` | `uuid` | Nullable FK → global_app_catalog (if sourced from catalog) |
| `set_by_id` | `uuid` | FK → users (who configured this) |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `set_by_id` → [[database/schemas/infrastructure#`users`|users]], `global_catalog_id` → [[database/schemas/shared-platform#`global_app_catalog`|global_app_catalog]]

**Unique constraint:** `(tenant_id, scope_type, COALESCE(scope_id, uuid_nil), process_name)` — same app cannot appear twice for the same scope.

**Matching priority (ingest processor):** match by `process_name` first (case-insensitive), fallback to `application_name` exact. No match → `is_allowed = null` (pending — never triggers alerts). See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] for full resolution logic.

---

## `observed_applications`

Auto-populated by the ingest processor whenever an app is seen on an employee device. HR admins never write to this table directly — it feeds the "Discovered in Your Org" allowlist UI tab.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `application_name` | `varchar(200)` | Display name reported by agent (e.g., "Google Chrome") |
| `process_name` | `varchar(100)` | Windows exe name (e.g., "chrome.exe") — deduplication key |
| `global_catalog_id` | `uuid` | Auto-linked FK → global_app_catalog when process_name matches (nullable) |
| `first_seen_at` | `timestamptz` | When this app was first detected for this tenant |
| `last_seen_at` | `timestamptz` | Updated on every ingest that contains this app |
| `employee_count` | `int` | Unique employees who ran this app |
| `total_seconds_observed` | `bigint` | Cumulative usage time across all employees |
| `status` | `varchar(20)` | `pending` \| `added_to_allowlist` \| `dismissed` |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `global_catalog_id` → [[database/schemas/shared-platform#`global_app_catalog`|global_app_catalog]]

**Unique constraint:** `(tenant_id, process_name)` — one row per app per tenant. Ingest uses INSERT ... ON CONFLICT DO UPDATE.

**Index:** `(tenant_id, status, employee_count DESC)` — for the HR admin discovered apps list query.

---

## `employee_monitoring_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `activity_monitoring` | `boolean` | Nullable — null means inherit from tenant |
| `application_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Why this employee is different |
| `set_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `set_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `integration_type` | `varchar(50)` | `stripe`, `resend`, `google_calendar`, `slack`, `lms` |
| `config_json` | `jsonb` |  |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `monitoring_feature_toggles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `activity_monitoring` | `boolean` | Keyboard/mouse event counting |
| `application_tracking` | `boolean` | App usage tracking |
| `screenshot_capture` | `boolean` | Periodic screenshots |
| `meeting_detection` | `boolean` | Meeting time tracking |
| `device_tracking` | `boolean` | Device usage tracking |
| `identity_verification` | `boolean` | Photo verification |
| `biometric` | `boolean` | Fingerprint terminals |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `tenant_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `timezone` | `varchar(50)` | Default timezone |
| `date_format` | `varchar(20)` |  |
| `currency_code` | `varchar(3)` |  |
| `work_week_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` |
| `work_hours_start` | `time` |  |
| `work_hours_end` | `time` |  |
| `privacy_mode` | `varchar(20)` | `full_transparency`, `partial`, `covert` |
| `data_retention_days_json` | `jsonb` | Per-data-type retention settings |
| `settings_json` | `jsonb` | Extensible settings |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Messaging Tables (MassTransit Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `processed_integration_events`

Idempotency table — prevents double-processing if RabbitMQ redelivers a message.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | PK — same as `IntegrationEvent.EventId` |
| `event_type` | `varchar(200)` | |
| `processed_at` | `timestamptz` | |

---

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]