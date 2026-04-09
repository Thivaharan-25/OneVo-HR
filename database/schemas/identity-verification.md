# Identity Verification — Schema

**Module:** [[modules/identity-verification/overview|Identity Verification]]
**Phase:** Phase 1
**Tables:** 6

---

## `biometric_audit_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `device_id` | `uuid` | FK → biometric_devices |
| `event_type` | `varchar(50)` | `heartbeat`, `tamper_detected`, `firmware_update`, `error` |
| `details_json` | `jsonb` | Event-specific details |
| `recorded_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `device_id` → [[#`biometric_devices`|biometric_devices]]

---

## `biometric_devices`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `device_name` | `varchar(100)` | Human-readable name |
| `location_id` | `uuid` | FK → departments or custom location |
| `api_key_encrypted` | `bytea` | HMAC-SHA256 key (encrypted at rest via `IEncryptionService`) |
| `model` | `varchar(100)` | Device model |
| `is_active` | `boolean` |  |
| `last_heartbeat_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `location_id` → [[database/schemas/org-structure#`departments`|departments]]

---

## `biometric_enrollments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → biometric_devices |
| `enrolled_at` | `timestamptz` |  |
| `consent_given` | `boolean` | GDPR/PDPA — must be true |
| `template_hash` | `varchar(128)` | Fingerprint template reference (not the template itself) |
| `is_active` | `boolean` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `device_id` → [[#`biometric_devices`|biometric_devices]]

---

## `biometric_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → biometric_devices |
| `event_type` | `varchar(20)` | `clock_in`, `clock_out`, `break_start`, `break_end` |
| `captured_at` | `timestamptz` |  |
| `verified` | `boolean` | Fingerprint match result |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `device_id` → [[#`biometric_devices`|biometric_devices]]

---

## `verification_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `verify_on_login` | `boolean` | Require photo at login |
| `verify_on_logout` | `boolean` | Require photo at logout |
| `interval_minutes` | `int` | Periodic verification (0 = disabled) |
| `match_threshold` | `decimal(5,2)` | Minimum confidence score to pass (default 80.0) |
| `is_active` | `boolean` | Master toggle |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `verification_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `verified_at` | `timestamptz` | When verification occurred |
| `method` | `varchar(20)` | `photo`, `fingerprint`, `on_demand_photo`, `on_demand_screenshot` |
| `photo_file_id` | `uuid` | FK → file_records (nullable, photo method only) |
| `match_confidence` | `decimal(5,2)` | 0–100 confidence score |
| `status` | `varchar(20)` | `verified`, `failed`, `skipped`, `expired` |
| `device_type` | `varchar(20)` | `agent` or `biometric` — discriminator for polymorphic FK |
| `device_id` | `uuid` | FK → registered_agents (when `device_type = 'agent'`) or biometric_devices (when `device_type = 'biometric'`) |
| `failure_reason` | `varchar(255)` | Nullable — why verification failed |
| `trigger` | `varchar(20)` | `scheduled`, `login`, `logout`, `interval`, `on_demand` |
| `requested_by_id` | `uuid` | Nullable — FK → users (who requested, for on-demand captures) |
| `alert_id` | `uuid` | Nullable — FK → exception_alerts (linked alert, for on-demand captures) |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `photo_file_id` → [[database/schemas/infrastructure#`file_records`|file_records]], `device_id` → [[database/schemas/agent-gateway#`registered_agents`|registered_agents]], `requested_by_id` → [[database/schemas/infrastructure#`users`|users]], `alert_id` → [[database/schemas/exception-engine#`exception_alerts`|exception_alerts]]

---

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]