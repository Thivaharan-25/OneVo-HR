# Module: Identity Verification

**Feature Folder:** `Application/Features/IdentityVerification`
**Phase:** 1 - Build
**Pillar:** 2 - Monitoring
**Owner:** Dev 4 (Week 3)
**Tables:** 7
**Task File:** [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]

---

## Purpose

Verifies employee identity via camera photo capture and biometric device matching. Configurable verification policies allow tenants to require camera photos at app/tray clock-in, app/tray clock-out, authorized on-demand review, or absence-detected identity confirmation for remote users, onsite users, both, or neither. Timed interval and random camera photo checks are not supported. Manages attendance terminals that can support face, fingerprint, card, PIN, or combined punch methods.

Photo verification uses a trusted **verification reference photo**, not a casual avatar/profile image. If no reference photo exists, the TrayApp can collect one during first agent sign-in after employee authentication and consent. That first capture is an enrollment photo, not a verification result. It becomes trusted only after approval by the configured identity-verification resolver or an explicit tenant policy that allows SSO/MFA-backed auto-approval.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext`, `IFileService` | Multi-tenancy, photo storage |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee identity and employment context |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Verification policy settings |
| **Consumed by** | [[modules/time-attendance/overview\|Time & Attendance]] | `IIdentityVerificationService` | Confirm identity for presence records |
| **Consumed by** | [[modules/notifications/overview\|Notifications]] | - (via `VerificationFailed` event) | Phase 1 lightweight verification alert, recipient resolved by Monitoring Policy |
| **Listens to** | [[modules/agent-gateway/overview\|Agent Gateway]] | `AgentCommandCompleted` event | Receives on-demand photo/screenshot results from agent |

---

## Public Interface

```csharp
// ONEVO.Application.Features.IdentityVerification/Public/IIdentityVerificationService.cs
public interface IIdentityVerificationService
{
    Task<Result<VerificationReferencePhotoDto>> StartReferencePhotoEnrollmentAsync(Guid employeeId, Guid photoFileId, Guid deviceId, CancellationToken ct);
    Task<Result<VerificationReferencePhotoDto>> ApproveReferencePhotoAsync(Guid referencePhotoId, Guid approvedById, CancellationToken ct);
    Task<Result> RejectReferencePhotoAsync(Guid referencePhotoId, Guid reviewedById, string reason, CancellationToken ct);
    Task<Result<VerificationReferencePhotoDto?>> GetActiveReferencePhotoAsync(Guid employeeId, CancellationToken ct);
    Task<Result<VerificationRecordDto>> VerifyPhotoAsync(Guid employeeId, Guid photoFileId, Guid deviceId, CancellationToken ct);
    Task<Result<VerificationPolicyDto>> GetPolicyAsync(Guid tenantId, CancellationToken ct);
    Task<Result<List<VerificationRecordDto>>> GetVerificationHistoryAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<BiometricDeviceDto>> RegisterDeviceAsync(RegisterDeviceCommand command, CancellationToken ct);
    
    // On-demand capture (triggered by manager via exception alert)
    Task<Result<VerificationRecordDto>> ProcessOnDemandCaptureAsync(Guid employeeId, Guid fileId, string captureType, Guid requestedById, Guid alertId, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/IdentityVerification/Entities/
  ONEVO.Domain/Features/IdentityVerification/Events/

Application (CQRS):
  ONEVO.Application/Features/IdentityVerification/Commands/
  ONEVO.Application/Features/IdentityVerification/Queries/
  ONEVO.Application/Features/IdentityVerification/DTOs/Requests/
  ONEVO.Application/Features/IdentityVerification/DTOs/Responses/
  ONEVO.Application/Features/IdentityVerification/Validators/
  ONEVO.Application/Features/IdentityVerification/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/IdentityVerification/

API endpoints:
  ONEVO.Api/Controllers/IdentityVerification/IdentityVerificationController.cs

---

## Database Tables (7)

### `verification_policies`

Per-tenant verification rules.

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
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `verification_records`

Each verification event.

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
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, verified_at)`, `(tenant_id, status)`

### `verification_evidence_assets`

Captured verification, clock-in/out, and failure photo evidence files. Evidence rows link to `file_records` and optionally to `verification_records`, presence sessions, attendance events, or biometric events. These files are not normal `entity_assets`. Biometric device scan results live in `biometric_events`; a photo evidence row is created only when policy also requires camera/photo capture.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `verification_record_id` | `uuid` | Nullable FK -> verification_records |
| `file_record_id` | `uuid` | FK -> file_records |
| `evidence_type` | `varchar(40)` | `identity_verification_photo`, `clock_in_photo`, `clock_out_photo`, `verification_failure_photo` |
| `trigger_type` | `varchar(20)` | `on_demand`, `clock_in`, `clock_out`, `absence_detected` |
| `captured_at` | `timestamptz` | |
| `retention_policy_id` | `uuid` | Nullable FK -> retention_policies |
| `legal_hold_id` | `uuid` | Nullable FK -> legal_holds |

### `verification_reference_photos`

Trusted employee reference images used for future photo comparisons. Reference photos are captured at first agent sign-in or supplied from a trusted HR/admin source.

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
| `created_at` | `timestamptz` | |

**Unique constraint:** `(tenant_id, employee_id) WHERE is_active = true`

### `biometric_devices`

Attendance/biometric terminals owned by a legal entity. This is the canonical table for physical attendance terminals, including direct webhook devices, vendor middleware, local gateways, polling API integrations, and manual imports. Devices may support face, fingerprint, RFID/card, PIN, or combined punch methods. Billing remains tenant-level; legal entity controls device policy ownership. Phase 1 does not assign terminals to an office-location table; the legal entity's single Company office location is stored on `legal_entities`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `device_code` | `varchar(50)` | Unique device/terminal code within the tenant |
| `device_name` | `varchar(100)` | Human-readable name |
| `vendor` | `varchar(100)` | Device manufacturer/provider |
| `model` | `varchar(100)` | Device model |
| `connection_method` | `varchar(30)` | `direct_webhook`, `vendor_middleware`, `local_gateway`, `polling_api`, `manual_import` |
| `webhook_url` | `varchar(500)` | Nullable ONEVO/device callback URL for push-style integrations |
| `vendor_middleware_url` | `varchar(500)` | Nullable local/vendor middleware or gateway URL |
| `external_device_ref` | `varchar(100)` | Vendor device identifier used by middleware, gateway, or import files |
| `api_key_encrypted` | `bytea` | HMAC/API key for terminal, vendor middleware, or local gateway |
| `supported_auth_methods` | `jsonb` | Backend-normalized capabilities, e.g. `face`, `fingerprint`, `rfid_card`, `pin` |
| `enabled_auth_methods` | `jsonb` | Tenant-enabled punch methods |
| `status` | `varchar(20)` | `active`, `offline`, `maintenance`, `disabled` |
| `last_heartbeat_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
### `biometric_enrollments`

Employee biometric enrollment. Store only the approved enrollment reference/hash metadata required for verification; raw biometric templates stay on the device/vendor system.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `enrolled_at` | `timestamptz` | |
| `consent_given` | `boolean` | GDPR/PDPA - must be true |
| `modality` | `varchar(30)` | `fingerprint`, `face`, `palm_vein`, `iris`, `other`; Phase 1 prioritizes fingerprint and face |
| `template_hash` | `varchar(128)` | Device-local biometric template reference (not the raw template itself) |
| `is_active` | `boolean` | |

### `biometric_events`

Raw clock-in/out events from terminals.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `event_type` | `varchar(20)` | `clock_in`, `clock_out`, `break_start`, `break_end` |
| `auth_method` | `varchar(40)` | `fingerprint`, `face`, `rfid_card`, `pin`, `card_plus_face`, `card_plus_fingerprint`, `manual` |
| `modality` | `varchar(30)` | Nullable; set when a biometric factor was used |
| `captured_at` | `timestamptz` | |
| `verified` | `boolean` | Device verification result |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, captured_at)`, `(biometric_device_id, captured_at)`

**Note:** Biometric events flow to [[modules/time-attendance/overview|Time & Attendance]] for presence session reconciliation.

### `biometric_audit_logs`

Tamper detection and device health.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `biometric_device_id` | `uuid` | FK -> biometric_devices |
| `event_type` | `varchar(50)` | `heartbeat`, `tamper_detected`, `firmware_update`, `error` |
| `details_json` | `jsonb` | Event-specific details |
| `recorded_at` | `timestamptz` | |

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
| `VerificationCompleted` | Successful photo or biometric match | [[modules/time-attendance/overview\|Time & Attendance]] (confirm identity for presence record) |
| `VerificationFailed` | Photo or biometric match below threshold | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight verification alert, recipient resolved by Monitoring Policy); Phase 2 may route through Exception Engine |
| `BiometricDeviceOffline` | No heartbeat from attendance/biometric terminal for 5+ minutes | [[modules/notifications/overview\|Notifications]] (alert admin) |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `AbsenceDetected` | [[modules/time-attendance/overview\|Time & Attendance]] / [[modules/activity-monitoring/overview\|Activity Monitoring]] | Request camera-photo identity confirmation when absence photo capture is enabled |

---

## Key Business Rules

1. **Verification photos are temporary** - retained for configurable period (default 30 days) then auto-deleted by `PurgeExpiredVerificationPhotosJob`. They are NOT approved reference photos.
2. **Photos are RESTRICTED data** - stored in Cloudflare R2 object storage via `file_records`, never in the database.
3. **Legal & Privacy notice/consent is mandatory** - a matching `legal_acceptance_record_id` must exist before photo/biometric verification or biometric enrollment starts.
4. **Raw biometric templates are NEVER stored in ONEVO** - only `template_hash` (a reference to the biometric device/vendor's local storage). The actual template stays on the hardware/vendor system.
5. **Verification policy respects monitoring overrides** - if an employee has `identity_verification = false` in `employee_monitoring_overrides`, skip verification even if tenant policy is active.

---

Additional photo reference rules:

6. **First agent photo can enroll the reference** - when no approved reference exists, the first TrayApp capture after sign-in creates a `verification_reference_photos` row with `pending_review`. It does not create a failed verification alert.
7. **No reference means no match** - clock-in, clock-out, on-demand, or absence-detected verification is recorded as `skipped` with `failure_reason = 'No approved verification reference photo'` until a reference is approved.
8. **Reference approval is audited** - default flow requires approval by the configured identity-verification resolver. Auto-approval is allowed only when tenant policy explicitly enables it and the employee authenticated with a trusted SSO/MFA flow.

## Phase 1 Monitoring Alerts

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Identity Verification is a Phase 1 alert producer. When a verification event requires attention, it creates a lightweight alert/notification record and routes it through Notifications/Inbox.

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

### Photo Verification Failure Notification

When photo verification fails because match confidence is below the policy threshold:
- Create/update `verification_records` with `status = failed`
- Store submitted photo in `verification_evidence_assets`
- Create a Phase 1 lightweight verification alert
- Notify the recipient resolved by Monitoring Policy through Notifications/Inbox
- Notification includes: employee, `requested_at`, `submitted_at`, `response_duration_seconds`, `match_confidence`, `failure_reason`, `trigger`, device/agent context, and evidence link

### Photo Verification Expired / No Response

When the employee does not submit before `expires_at`:
- `status = expired`
- `failure_reason = employee_did_not_respond`
- Notify reviewer only if policy says missed verification requires review

### Challenge Lifecycle Fields on `verification_records`

The following fields track the full challenge lifecycle for on-demand and absence-detected photo verification:

| Field | Type | Description |
|:------|:-----|:------------|
| `requested_at` | `timestamptz` | Nullable — when backend creates the photo challenge |
| `delivered_at` | `timestamptz` | Nullable — when agent receives the command |
| `submitted_at` | `timestamptz` | Nullable — when employee submits/captures the photo |
| `expires_at` | `timestamptz` | Nullable — challenge expiry time |
| `response_duration_seconds` | `int` | Nullable — `submitted_at - requested_at` |
| `reviewed_by_id` | `uuid` | Nullable FK -> users — reviewer who assessed the result |
| `reviewed_at` | `timestamptz` | Nullable — when reviewer assessed the result |
| `review_status` | `varchar(20)` | Nullable — `pending`, `confirmed_mismatch`, `dismissed_false_positive` |

**Lifecycle behavior:**
- `requested_at` = when backend creates the photo challenge
- `delivered_at` = when agent receives the command
- `submitted_at` = when employee submits/captures the photo
- `response_duration_seconds` = `submitted_at - requested_at`
- `expires_at` = challenge expiry time
- `status = expired` when no photo is submitted before `expires_at`
- `status = failed` when photo is submitted but confidence is below threshold
- `status = verified` when confidence meets threshold
- `review_status` tracks the reviewer's assessment of failed/expired results separately from the automated `status`

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/verification/policy` | `verification:view` | Get tenant verification policy |
| PUT | `/api/v1/verification/policy` | `verification:configure` | Update verification policy |
| GET | `/api/v1/verification/records/{employeeId}` | `verification:view` | Verification history |
| POST | `/api/v1/verification/verify` | Internal (agent) | Submit verification photo |
| POST | `/api/v1/verification/reference-photo` | Internal (agent) | Submit first-sign-in reference photo candidate |
| POST | `/api/v1/verification/reference-photo/{id}/approve` | `verification:configure` | Approve pending reference photo |
| POST | `/api/v1/verification/reference-photo/{id}/reject` | `verification:configure` | Reject pending reference photo |
| GET | `/api/v1/time-attendance/devices` | `verification:view` | List attendance/biometric devices |
| POST | `/api/v1/time-attendance/devices` | `verification:configure` | Register device |
| PUT | `/api/v1/time-attendance/devices/{id}` | `verification:configure` | Update device |
| POST | `/api/v1/biometric/enroll` | `verification:configure` | Enroll employee biometric factor |
| POST | `/api/v1/time-attendance/biometric/webhook` | HMAC-SHA256 | Receive biometric events from terminals |

---

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `PurgeExpiredVerificationPhotosJob` | Daily 2:00 AM | Delete photos past retention period |
| `CheckBiometricDeviceHealthJob` | Every 5 min | Flag devices with no heartbeat |

---

## Important Notes

- **Biometric webhook authentication** uses HMAC-SHA256 signature verification, not JWT.
- **Photo matching** in Phase 1 uses a simple comparison service. Phase 2 may add a dedicated ML matching service.
- **Time & Attendance owns biometric/attendance terminal registration, enrollment, and clock-event ingestion because those routes create presence source data. Identity Verification owns verification policy, consent rules, photo/biometric review, and identity match outcomes.

## On-Demand Capture Flow

```
Authorized reviewer sees an identity or presence review case -> clicks "Request Photo"
  -> Identity Verification publishes camera-photo capture request
  -> agent-gateway dispatches command to agent via SignalR
  -> Agent shows employee notification: "Identity verification has been requested"
  -> Agent opens camera window for photo
  -> Agent uploads to blob storage, reports completion via AgentCommandCompleted
  -> agent-gateway fires AgentCommandCompleted event
  -> identity-verification.ProcessOnDemandCaptureAsync():
    -> Creates verification_record with method='on_demand_photo', trigger='on_demand', status='pending_review'
    -> Creates verification_evidence_assets row with trigger_type='on_demand'
    -> Links to alert_id and requested_by_id
    -> Publishes OnDemandCaptureReceived event
  -> Reviewer receives notification: "Capture result available"
  -> Reviewer views result in verification detail page (side-by-side with approved reference photo)
```

**Employee notification is mandatory (GDPR).** The agent MUST show a notification before camera capture. Screenshot capture is handled by Activity Monitoring, not Identity Verification.

**Rate limit:** Max 10 capture requests per agent per hour. Prevents harassment.

## Features

- [[modules/identity-verification/verification-policies/overview|Verification Policies]] - Per-tenant verification rules (clock-in, clock-out, on-demand, absence-detected)
- [[modules/identity-verification/photo-verification/overview|Photo Verification]] - Photo capture and confidence-score matching
- On Demand Capture - Authorized reviewer-triggered camera photo capture from identity or presence review
- [[modules/identity-verification/biometric-devices/overview|Biometric Devices]] - Attendance/biometric terminal management and HMAC webhook authentication
- [[modules/identity-verification/biometric-enrollment/overview|Biometric Enrollment]] - Employee biometric enrollment with mandatory Legal & Privacy notice/consent

---

## Related

- [[security/auth-architecture|Auth Architecture]] - HMAC-SHA256 authentication for biometric device webhooks
- [[infrastructure/multi-tenancy|Multi Tenancy]] - Policies and records are tenant-scoped
- [[security/data-classification|Data Classification]] - Photos are RESTRICTED; raw biometric templates stay on device/vendor hardware only
- [[security/compliance|Compliance]] - Legal & Privacy notice/consent is mandatory before photo/biometric verification or biometric enrollment
- [[backend/messaging/event-catalog|Event Catalog]] - `VerificationFailed`, `VerificationCompleted`, `BiometricDeviceOffline`
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]] - Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/time-attendance/overview|Time & Attendance]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/exception-engine/overview|Exception Engine]] (Phase 2 configurable rules)

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.

### Face Recognition ML Matching Service
Phase 1 uses a simple photo comparison service (basic pixel/hash comparison with a confidence score). Phase 2 will replace this with a dedicated ML-based face recognition service for higher accuracy matching. This may use Azure Cognitive Services Face API or a self-hosted model. Requires evaluation of accuracy, latency, cost, and GDPR implications of biometric data processing.

### Liveness Detection
Phase 2 will add liveness detection to prevent employees from holding up a photo of themselves to the camera. Requires depth sensing or challenge-response (blink detection, head turn).

