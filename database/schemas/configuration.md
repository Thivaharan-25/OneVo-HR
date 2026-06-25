# Configuration - Schema

**Module:** [[modules/configuration/overview|Configuration]]
**Phase:** Phase 1
**Tables:** 12

---

## `app_allowlist_audit`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `allowlist_id` | `uuid` | FK -> app_allowlists |
| `action` | `varchar(20)` | `created`, `updated`, `deleted` |
| `changed_by_id` | `uuid` | FK -> users |
| `old_value_json` | `jsonb` | Previous state |
| `new_value_json` | `jsonb` | New state |
| `changed_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `allowlist_id` -> [[#`app_allowlists`|app_allowlists]], `changed_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `app_allowlists`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `scope_type` | `varchar(20)` | `tenant`, `role`, `employee` |
| `scope_id` | `uuid` | Null for tenant, role_id for role, employee_id for employee |
| `application_name` | `varchar(200)` | e.g., "Microsoft Teams", "Visual Studio Code" |
| `process_name` | `varchar(100)` | e.g., "ms-teams.exe" - authoritative matching key |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `is_allowed` | `boolean` | True = allowed during work, False = not allowed |
| `source` | `varchar(20)` | `global_catalog`, `tenant_observed`, `manual` |
| `global_catalog_id` | `uuid` | Nullable FK -> global_app_catalog (if sourced from catalog) |
| `set_by_id` | `uuid` | FK -> users (who configured this) |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `set_by_id` -> [[database/schemas/infrastructure#`users`|users]], `global_catalog_id` -> [[database/schemas/shared-platform#`global_app_catalog`|global_app_catalog]]

**Unique constraint:** `(tenant_id, scope_type, COALESCE(scope_id, uuid_nil), process_name)` - same app cannot appear twice for the same scope.

**Matching rule (ingest processor):** match by `process_name` case-insensitively. `application_name` is display metadata only and is not authoritative for allowlist/blocklist decisions. No `process_name` match -> `is_allowed = null` (pending - never triggers alerts). See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] for full resolution logic.

---

## `observed_applications`

Auto-populated by the ingest processor whenever an app is seen on an employee device. HR admins never write to this table directly - it feeds the "Discovered in Your Org" allowlist UI tab.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `application_name` | `varchar(200)` | Display name reported by agent (e.g., "Google Chrome") |
| `process_name` | `varchar(100)` | Windows exe name (e.g., "chrome.exe") - deduplication key |
| `global_catalog_id` | `uuid` | Auto-linked FK -> global_app_catalog when process_name matches (nullable) |
| `first_seen_at` | `timestamptz` | When this app was first detected for this tenant |
| `last_seen_at` | `timestamptz` | Updated on every ingest that contains this app |
| `employee_count` | `int` | Unique employees who ran this app |
| `total_seconds_observed` | `bigint` | Cumulative usage time across all employees |
| `status` | `varchar(20)` | `pending` \| `added_to_allowlist` \| `dismissed` |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `global_catalog_id` -> [[database/schemas/shared-platform#`global_app_catalog`|global_app_catalog]]

**Unique constraint:** `(tenant_id, process_name)` - one row per app per tenant. Ingest uses INSERT ... ON CONFLICT DO UPDATE.

**Index:** `(tenant_id, status, employee_count DESC)` - for the HR admin discovered apps list query.

---

## `employee_monitoring_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `activity_monitoring` | `boolean` | Nullable - null means inherit from tenant |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable; allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | `boolean` | Nullable; allows automatic screenshot capture when monitoring detects a deviation |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Why this employee is different |
| `set_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `set_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `monitoring_policy_overrides`


| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `scope_type` | `varchar(30)` | `role`, `position`, `department` |
| `scope_id` | `uuid` | FK to the corresponding scope table; validated by application logic |
| `activity_monitoring` | `boolean` | Nullable - null means inherit |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable; allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | `boolean` | Nullable; allows automatic screenshot capture when monitoring detects a deviation |
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

---

## `monitoring_alert_policy`

Tenant-level Monitoring Policy configuration controlling how monitoring alert recipients are resolved. One row per tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, UNIQUE |
| `monitoring_alert_recipient_resolver` | `varchar(50)` | `management_coverage_availability_chain` (default) or `reporting_manager` |
| `monitoring_alert_wait_for_scheduled_recipient_grace_minutes` | `int` | Minutes to wait for a scheduled recipient before skipping (default: 15) |
| `monitoring_alert_fallback_to_management_coverage_chain` | `boolean` | When `reporting_manager` resolver is selected, fall back to management coverage availability chain if reporting manager is unavailable (default: true) |
| `monitoring_alert_unresolved_routing_action` | `varchar(30)` | `create_routing_issue` (default) or `leave_unassigned` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

**Resolution algorithm (`management_coverage_availability_chain`):**
1. Load active date-effective management coverage assignments for the employee
2. Order eligible responsible people by configured coverage priority / responsibility weight / effective assignment order
3. Filter to users with the required alert permission (`monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review`, or the relevant alert-specific permission)
4. Check availability: person is scheduled to work now (or inside the alert routing window), person has clocked in / is present, person is not on approved leave, person is not marked unavailable
5. If a responsible person is scheduled but has not reached scheduled start time + `monitoring_alert_wait_for_scheduled_recipient_grace_minutes`, wait until that window closes before skipping
6. If scheduled start + grace passes and they have not clocked in, skip and route to next eligible available responsible person
7. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action` — never silently route to random HR/admin

**Resolution algorithm (`reporting_manager`):**
1. Resolve reporting manager from position hierarchy
2. Check required alert permission
3. Check availability (same scheduled/clocked-in/leave/unavailable rules)
4. If unavailable, follow `monitoring_alert_fallback_to_management_coverage_chain`
5. If still unresolved, follow `monitoring_alert_unresolved_routing_action`

**Data dependencies for routing:** management coverage assignments, employee schedule, clock-in/presence state, approved leave / unavailable state, permission checks.

---

## `employee_work_location_settings`

Employee work mode and work-location verification settings. Phase 1 does not expose separate work-location CRUD and does not assign separate location rows. Onsite verification resolves the employee's primary Company and compares evidence against that Company's single office location stored on `legal_entities`. Remote verification compares against the employee's approved remote work location profile.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `work_mode` | `varchar(30)` | `onsite`, `remote`, `hybrid`, `field` |
| `work_location_verification_enabled` | `boolean` | Employee-level resolved setting |
| `grace_period_minutes` | `int` | Nullable override |
| `photo_challenge_on_mismatch` | `boolean` | Default true when enforcement is enabled |
| `set_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

---

## `employee_remote_work_profiles`

Approved remote work location profile captured from the employee's first approved remote clock-in.

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

**Unique constraint:** `(tenant_id, employee_id) WHERE status = 'active'` - only one active approved remote work location profile in Phase 1.

---

## `remote_work_location_change_requests`

Employee requests to replace an approved remote work location profile. Approval is resolved through Org Structure management coverage to one eligible owner with the required permission.

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

## `integration_connections` - Phase 2

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `integration_type` | `varchar(50)` | Phase 2 generic or legacy tenant integrations only, e.g. `peoplehr`, `slack`, `lms` |
| `config_json` | `jsonb` |  |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` |  |

**Phase rule:** This generic connection table is Phase 2 only. Phase 1 integrations use dedicated provider tables and do not write to `integration_connections`.

**PeopleHR note:** `peoplehr` credentials are Phase 2 and used by the DataImport PeopleHR migration flow. The API key must be encrypted at rest, masked in UI, and validated through API permission preflight before any migration run. Full raw staging and audit tables are defined in [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]].

**Dedicated provider note:** `integration_connections` is not the source of truth for Stripe, PayHere, Resend, Google Calendar, or Outlook Calendar credentials. Payment provider secrets use `payment_gateway_credentials`; non-secret gateway metadata stays in `payment_gateway_configs`; Resend email configuration uses `platform_service_keys` and/or `notification_channels`; user-level calendar OAuth tokens use `external_calendar_connections`.

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `monitoring_feature_toggles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, UNIQUE |
| `activity_monitoring` | `boolean` | Keyboard/mouse event counting |
| `application_tracking` | `boolean` | App usage tracking |
| `document_tracking` | `boolean` | Document tool time tracking |
| `communication_tracking` | `boolean` | Communication tool active time and send counts |
| `screenshot_capture` | `boolean` | Allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | `boolean` | Allows automatic screenshot capture when monitoring detects a deviation |
| `meeting_detection` | `boolean` | Meeting time tracking |
| `device_tracking` | `boolean` | Device usage tracking |
| `work_location_verification` | `boolean` | Network-based work-location compliance |
| `identity_verification` | `boolean` | Photo verification |
| `biometric` | `boolean` | Biometric/attendance terminals |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `tenant_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, UNIQUE |
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

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]


