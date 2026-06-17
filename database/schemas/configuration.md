# Configuration — Schema

**Module:** [[modules/configuration/overview|Configuration]]
**Phase:** Phase 1
**Tables:** 11

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
| `process_name` | `varchar(100)` | e.g., "ms-teams.exe" — authoritative matching key |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `is_allowed` | `boolean` | True = allowed during work, False = not allowed |
| `source` | `varchar(20)` | `global_catalog`, `tenant_observed`, `manual` |
| `global_catalog_id` | `uuid` | Nullable FK → global_app_catalog (if sourced from catalog) |
| `set_by_id` | `uuid` | FK → users (who configured this) |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `set_by_id` → [[database/schemas/infrastructure#`users`|users]], `global_catalog_id` → [[database/schemas/shared-platform#`global_app_catalog`|global_app_catalog]]

**Unique constraint:** `(tenant_id, scope_type, COALESCE(scope_id, uuid_nil), process_name)` — same app cannot appear twice for the same scope.

**Matching rule (ingest processor):** match by `process_name` case-insensitively. `application_name` is display metadata only and is not authoritative for allowlist/blocklist decisions. No `process_name` match → `is_allowed = null` (pending — never triggers alerts). See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] for full resolution logic.

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
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Why this employee is different |
| `set_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `set_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `monitoring_policy_overrides`

Scope-level monitoring feature overrides for role, department, team, and position policies. This table fills the gap between tenant-wide defaults and per-employee exceptions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `scope_type` | `varchar(30)` | `role`, `department`, `team`, `position` |
| `scope_id` | `uuid` | FK to the corresponding scope table; validated by application logic |
| `activity_monitoring` | `boolean` | Nullable - null means inherit |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable; command eligibility only, never scheduled capture |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Why this scope differs from tenant default |
| `set_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `set_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Unique constraint:** `(tenant_id, scope_type, scope_id)` - one override row per scope.

**Resolution:** tenant defaults -> role -> position -> department -> team -> employee override. Only non-null fields override inherited values. Consent and Workforce Presence lifecycle gates are applied after this table is merged.

---

## `work_locations`

Legal entity workplaces configured by Admin / HR admin for office, branch, remote-allowed, or field work.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(150)` | e.g., `Colombo Office` |
| `location_type` | `varchar(30)` | `office`, `branch`, `remote_allowed`, `field` |
| `allowed_wifi_ssids_json` | `jsonb` | Optional display/matching hints |
| `allowed_bssid_hashes_json` | `jsonb` | Recommended; hashed access point IDs |
| `allowed_gateway_hashes_json` | `jsonb` | Recommended; hashed router/gateway IDs |
| `allowed_public_ip_ranges_json` | `jsonb` | CIDR ranges |
| `allowed_vpn_ip_ranges_json` | `jsonb` | Optional approved VPN egress ranges |
| `default_grace_period_minutes` | `int` | Nullable; falls back to tenant/rule default |
| `default_alert_severity` | `varchar(20)` | Nullable; `info`, `warning`, `critical` |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Rule:** At least one verification method must be configured: BSSID/gateway hash, public IP range, or approved VPN range.

---

## `employee_work_location_settings`

Employee work mode and assigned office/remote enforcement settings.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `work_mode` | `varchar(30)` | `office`, `remote`, `hybrid`, `field`, `no_enforcement` |
| `primary_work_location_id` | `uuid` | Nullable FK -> work_locations |
| `work_location_verification_enabled` | `boolean` | Employee-level resolved setting |
| `grace_period_minutes` | `int` | Nullable override |
| `photo_challenge_on_mismatch` | `boolean` | Default true when enforcement is enabled |
| `set_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

---

## `employee_remote_work_profiles`

Locked remote workplace profile captured from the employee's approved remote clock-in.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `status` | `varchar(20)` | `pending_capture`, `active`, `archived`, `rejected` |
| `captured_at` | `timestamptz` | When profile was captured |
| `public_ip` | `inet` | Nullable; IP may change by ISP |
| `wifi_ssid` | `varchar(255)` | Nullable |
| `wifi_bssid_hash` | `varchar(100)` | Nullable |
| `gateway_mac_hash` | `varchar(100)` | Nullable |
| `vpn_detected` | `boolean` | Default false |
| `coarse_location_json` | `jsonb` | Nullable; permission-based only |
| `verification_record_id` | `uuid` | FK -> verification_records |
| `approved_by_id` | `uuid` | Nullable FK -> users |
| `created_at` | `timestamptz` |  |
| `archived_at` | `timestamptz` | Nullable |

**Unique constraint:** `(tenant_id, employee_id) WHERE status = 'active'` - only one active remote workplace profile by default.

---

## `remote_work_location_change_requests`

Employee requests to replace a locked remote workplace profile.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `current_profile_id` | `uuid` | Nullable FK -> employee_remote_work_profiles |
| `reason` | `text` | Employee-provided reason |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `captured`, `expired` |
| `requested_at` | `timestamptz` |  |
| `reviewed_by_id` | `uuid` | Nullable FK -> users |
| `reviewed_at` | `timestamptz` | Nullable |
| `review_comment` | `text` | Nullable |
| `new_profile_id` | `uuid` | Nullable FK -> employee_remote_work_profiles |

---

## `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `integration_type` | `varchar(50)` | `peoplehr`, `stripe`, `payhere`, `resend`, `google_calendar`, `slack`, `lms` |
| `config_json` | `jsonb` |  |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` |  |

**PeopleHR note:** `peoplehr` credentials are used by the DataImport PeopleHR migration flow. The API key must be encrypted at rest, masked in UI, and validated through API permission preflight before any migration run. Full raw staging and audit tables are defined in [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]].

**Payment gateway note:** Payment provider billing API keys, merchant secrets, and webhook secrets should use `payment_gateway_configs` in the Shared Platform schema when used for subscription or invoice collection.

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `monitoring_feature_toggles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `activity_monitoring` | `boolean` | Keyboard/mouse event counting |
| `application_tracking` | `boolean` | App usage tracking |
| `document_tracking` | `boolean` | Document tool time tracking |
| `communication_tracking` | `boolean` | Communication tool active time and send counts |
| `screenshot_capture` | `boolean` | Screenshot command eligibility; never scheduled in Phase 1 |
| `meeting_detection` | `boolean` | Meeting time tracking |
| `device_tracking` | `boolean` | Device usage tracking |
| `work_location_verification` | `boolean` | Network-based work-location compliance |
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

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]


