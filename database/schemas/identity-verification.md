# Identity Verification - Schema

**Module:** [[modules/identity-verification/overview|Identity Verification]]
**Phase:** Phase 1
**Tables:** 8

---

## `biometric_audit_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `event_type` | `varchar(50)` | `heartbeat`, `tamper_detected`, `firmware_update`, `error` |
| `details_json` | `jsonb` | Event-specific details |
| `recorded_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `biometric_device_id` -> [[#`biometric_devices`|biometric_devices]]

---

## `biometric_devices`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; required policy boundary for the device |
| `device_code` | `varchar(50)` | Unique device/terminal code within the tenant |
| `device_name` | `varchar(100)` | Human-readable name |
| `vendor` | `varchar(100)` | Device manufacturer/provider, e.g. ZKTeco, Suprema, Hikvision, Anviz, ESSL, Matrix |
| `model` | `varchar(100)` | Device model |
| `connection_method` | `varchar(30)` | `direct_webhook`, `vendor_middleware`, `local_gateway`, `polling_api`, `manual_import` |
| `webhook_url` | `varchar(500)` | Nullable ONEVO/device callback URL configured for push-style integrations |
| `vendor_middleware_url` | `varchar(500)` | Nullable local/vendor middleware or gateway URL when the terminal cannot call ONEVO directly |
| `external_device_ref` | `varchar(100)` | Vendor device identifier used by middleware, gateway, or import files |
| `api_key_encrypted` | `bytea` | HMAC/API key for terminal, vendor middleware, or local gateway; encrypted at rest via `IEncryptionService` |
| `supported_auth_methods` | `jsonb` | Backend-normalized capabilities, e.g. `face`, `fingerprint`, `rfid_card`, `pin` |
| `enabled_auth_methods` | `jsonb` | Tenant-enabled punch methods for this device |
| `status` | `varchar(20)` | `active`, `offline`, `maintenance`, `disabled` |
| `last_heartbeat_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]]

**Rule:** `biometric_devices` is the canonical table for physical attendance/biometric terminals, including face, fingerprint, RFID/card, PIN, kiosk, and combined punch devices. Device policy ownership is legal-entity based. Phase 1 does not assign terminals to an office-location table; the legal entity's single Company office location is stored on `legal_entities`. Physical terminals and their vendor middleware/local gateways use HMAC/API-key authentication, not WorkPulse Device JWT.

---

## `biometric_enrollments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `enrolled_at` | `timestamptz` |  |
| `consent_given` | `boolean` | GDPR/PDPA - must be true |
| `modality` | `varchar(30)` | `fingerprint`, `face`, `palm_vein`, `iris`, `other`; Phase 1 prioritizes fingerprint and face |
| `template_hash` | `varchar(128)` | Device-local biometric template reference (not the raw template itself) |
| `is_active` | `boolean` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `biometric_device_id` -> [[#`biometric_devices`|biometric_devices]]

---

## `biometric_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `event_type` | `varchar(20)` | `clock_in`, `clock_out`, `break_start`, `break_end` |
| `auth_method` | `varchar(40)` | `fingerprint`, `face`, `rfid_card`, `pin`, `card_plus_face`, `card_plus_fingerprint`, `manual` |
| `modality` | `varchar(30)` | Nullable; `fingerprint`, `face`, `palm_vein`, `iris`, `other` when a biometric factor was used |
| `captured_at` | `timestamptz` |  |
| `verified` | `boolean` | Device verification result |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `biometric_device_id` -> [[#`biometric_devices`|biometric_devices]]

---

## `verification_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, UNIQUE |
| `require_photo_clock_in` | `boolean` | Require camera photo at app/tray clock-in |
| `require_photo_clock_out` | `boolean` | Require camera photo at app/tray clock-out |
| `camera_photo_verification_enabled` | `boolean` | Allows authorized on-demand camera photo capture |
| `absence_photo_capture_enabled` | `boolean` | Allows camera photo capture when monitoring/presence detects an absence deviation |
| `photo_capture_context_scope` | `varchar(20)` | `remote_only`, `onsite_only`, `remote_and_onsite`, `disabled` |
| `match_threshold` | `decimal(5,2)` | Minimum confidence score to pass (default 80.0) |
| `reference_enrollment_mode` | `varchar(30)` | `manual_review` or `trusted_sso_auto_approve` |
| `block_monitoring_until_reference_approved` | `boolean` | If true, agent collection waits for approved reference |
| `is_active` | `boolean` | Master toggle |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `verification_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `verified_at` | `timestamptz` | When verification occurred |
| `method` | `varchar(20)` | `photo`, `biometric`, `on_demand_photo` |
| `match_confidence` | `decimal(5,2)` | 0-100 confidence score |
| `status` | `varchar(20)` | `pending_review`, `verified`, `failed`, `skipped`, `expired` |
| `agent_id` | `uuid` | Nullable FK -> registered_agents; set for WorkPulse/desktop-agent photo verification |
| `biometric_device_id` | `uuid` | Nullable FK -> biometric_devices; set for physical terminal/device verification |
| `failure_reason` | `varchar(255)` | Nullable - why verification failed |
| `trigger` | `varchar(20)` | `on_demand`, `clock_in`, `clock_out`, `absence_detected`, `biometric_scan` |
| `requested_by_id` | `uuid` | Nullable - FK -> users (who requested, for on-demand captures) |
| `alert_id` | `uuid` | Nullable - linked alert/notification ID (for on-demand captures triggered from a review case) |
| `requested_at` | `timestamptz` | Nullable - when backend creates the photo challenge |
| `delivered_at` | `timestamptz` | Nullable - when agent receives the command |
| `submitted_at` | `timestamptz` | Nullable - when employee submits/captures the photo |
| `expires_at` | `timestamptz` | Nullable - challenge expiry time |
| `response_duration_seconds` | `int` | Nullable - `submitted_at - requested_at` |
| `reviewed_by_id` | `uuid` | Nullable FK -> users - reviewer who assessed the result |
| `reviewed_at` | `timestamptz` | Nullable - when reviewer assessed the result |
| `review_status` | `varchar(20)` | Nullable - `pending`, `confirmed_mismatch`, `dismissed_false_positive` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `agent_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]], `biometric_device_id` -> [[#`biometric_devices`|biometric_devices]], `requested_by_id` -> [[database/schemas/infrastructure#`users`|users]], `reviewed_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Rule:** verification photos, clock-in/out photos, and failure evidence are stored in `verification_evidence_assets`, not directly on `verification_records` and not in `entity_assets`. A biometric scan creates a `biometric_events` row and a `verification_records` row with `method = biometric`, `trigger = biometric_scan`, and `biometric_device_id`; it does not automatically create a photo evidence row. WorkPulse photo verification sets `agent_id`. Physical terminal verification sets `biometric_device_id`. Do not use a polymorphic `device_id`.

---

## `verification_evidence_assets`

Camera/photo evidence files captured for identity verification, presence, or attendance workflows. These files are not normal reusable assets and must not be stored in `entity_assets`. Biometric device scan results live in `biometric_events`; only create a photo evidence row when policy also requires camera/photo capture.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `verification_record_id` | `uuid` | Nullable FK -> verification_records |
| `presence_session_id` | `uuid` | Nullable FK -> presence_sessions |
| `attendance_event_id` | `uuid` | Nullable attendance event/source ID |
| `biometric_event_id` | `uuid` | Nullable FK -> biometric_events |
| `file_record_id` | `uuid` | FK -> file_records |
| `evidence_type` | `varchar(40)` | `identity_verification_photo`, `clock_in_photo`, `clock_out_photo`, `verification_failure_photo` |
| `trigger_type` | `varchar(20)` | `on_demand`, `clock_in`, `clock_out`, `absence_detected` |
| `captured_at` | `timestamptz` | When the evidence was captured |
| `agent_id` | `uuid` | Nullable FK -> registered_agents when evidence came from WorkPulse/desktop agent |
| `biometric_device_id` | `uuid` | Nullable FK -> biometric_devices when evidence came from a physical terminal/gateway |
| `retention_policy_id` | `uuid` | Nullable FK -> retention_policies |
| `legal_hold_id` | `uuid` | Nullable FK -> legal_holds |
| `metadata` | `jsonb` | Safe non-secret metadata |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `verification_record_id` -> [[#`verification_records`|verification_records]], `biometric_event_id` -> [[#`biometric_events`|biometric_events]], `agent_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]], `biometric_device_id` -> [[#`biometric_devices`|biometric_devices]], `file_record_id` -> [[database/schemas/infrastructure#`file_records`|file_records]]

**Rules:** evidence view/download must be audit logged. Evidence deletion must respect retention policy and legal hold. Verification evidence must not be reused as profile photos, logos, or project covers. Camera-photo evidence is never random or interval-based; use `on_demand` for live reviewer-requested camera capture and `absence_detected` for automatic identity checks caused by absence/presence deviation. Photo capture can be configured for remote users, onsite users, both, or disabled.

---

## `verification_reference_photos`

Trusted employee reference images used for future photo comparisons. The preferred Phase 1 source is the employee's first TrayApp sign-in enrollment capture.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `photo_file_id` | `uuid` | FK -> file_records |
| `source` | `varchar(30)` | `agent_first_sign_in`, `hr_verified_profile`, `admin_upload` |
| `status` | `varchar(20)` | `pending_review`, `approved`, `rejected`, `replaced`, `revoked` |
| `captured_device_id` | `uuid` | Nullable FK -> registered_agents |
| `captured_at` | `timestamptz` | When the reference candidate was captured |
| `reviewed_by_id` | `uuid` | Nullable FK -> users |
| `reviewed_at` | `timestamptz` | Nullable |
| `review_comment` | `varchar(255)` | Nullable |
| `legal_acceptance_record_id` | `uuid` | FK -> legal_acceptance_records for photo/biometric notice or consent |
| `is_active` | `boolean` | Only one approved active reference per employee |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `photo_file_id` -> [[database/schemas/infrastructure#`file_records`|file_records]], `captured_device_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]], `reviewed_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Unique constraint:** `(tenant_id, employee_id) WHERE is_active = true`

**Rule:** A pending reference photo is not used for verification comparison. Verification stays `skipped`/`reference_pending` until the reference is approved or auto-approved by explicit tenant policy.

---

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
