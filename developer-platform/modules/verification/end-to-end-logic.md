# Identity Verification - End-to-End Logic

**Module key:** `verification`  
**Pillar:** Monitoring
**Pricing unit:** Per employee  
**Entitlement guard:** All endpoints call `IsModuleEnabledAsync(tenantId, "verification")` -> 403 `module_not_entitled` if not entitled  
**Dependency:** See [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]

---

## What This Module Does

Identity Verification confirms that the person clocking in, clocking out, or present at their workstation is actually the enrolled employee. It operates across three verification channels:

1. **Clock-in / clock-out photo** - employee submits a selfie photo when starting or ending their work session
2. **WorkPulse camera photo** - the desktop agent captures a photo for authorized on-demand reviewer request or absence-detected identity verification
3. **Biometric/attendance device scan** - a physical terminal assigned to a legal entity records a punch event when the employee uses face, fingerprint, card, PIN, or a combined method

Verification operates **standalone** - it does not require the Activity Monitoring module. Clock-in verification works even if `monitoring` is not entitled.

---

## Verification Types

| Type | `verification_records.method` | `verification_records.trigger` | Evidence row |
|:---|:---|:---|:---|
| Clock-in photo | `photo` | `clock_in` | `verification_evidence_assets.evidence_type = clock_in_photo` |
| Clock-out photo | `photo` | `clock_out` | `verification_evidence_assets.evidence_type = clock_out_photo` |
| On-demand camera photo | `on_demand_photo` | `on_demand` | `verification_evidence_assets.evidence_type = identity_verification_photo` |
| Absence-detected camera photo | `on_demand_photo` | `absence_detected` | `verification_evidence_assets.evidence_type = identity_verification_photo` |
| Biometric scan | `biometric` | `biometric_scan` | No photo evidence row; source event is `biometric_events` |

---

## Flow 1 - Clock-In Photo Verification

**Prerequisites:** `verification` module entitled. No additional config toggle required for photo collection.

1. Employee opens ONEVO customer-app and taps **Clock In**
2. App prompts for camera permission and captures a selfie
3. Photo is uploaded via `POST /tenant/v1/verification/clock-in` (multipart form with the image)
4. Backend:
   - Validates file type (JPEG/PNG, max 5 MB)
   - Checks `tenant_storage_limit_gb` -> 413 `storage_limit_exceeded` if full
   - Stores photo to file storage -> inserts `file_records` row
   - Creates `verification_records` row: `method = photo`, `trigger = clock_in`, `status = pending_review`
   - Creates `verification_evidence_assets` row with `evidence_type = clock_in_photo` and `file_record_id`
   - Publishes `ClockInPhotoSubmittedEvent`
5. A reviewer (HR or manager with `verification.records.review` permission) later opens the employee's verification history and marks the record `verified` or `failed`
6. Alternatively, an automated face-match service (Phase 2 feature - manual review only in Phase 1) marks the status

**Status values:**
- `pending_review` - submitted, not yet reviewed
- `verified` - reviewer confirmed identity
- `failed` - reviewer raised a concern

---

## Flow 2 - Clock-Out Photo Verification

Identical to clock-in flow. Endpoint: `POST /tenant/v1/verification/clock-out`.  
`verification_records.method = photo`, `verification_records.trigger = clock_out`.

Both clock-in and clock-out can be configured independently. Tenants can require photo at clock-in only, clock-out only, or both, and can scope those requirements to remote users, onsite users, both, or neither. Configuration is stored in `tenant_configuration_settings` under keys `verification.require_photo_clock_in`, `verification.require_photo_clock_out`, and `verification.photo_capture_context_scope`.

---

## Flow 3 - WorkPulse Camera Photo Verification

**Prerequisites:** `verification` module entitled AND `camera_photo_verification_enabled = true` in tenant Step 4 configuration.

> This toggle defaults to **Off**. Tenants must explicitly enable it. Subject to biometric consent and retention policy confirmation.

1. Authorized reviewer requests a camera photo, or monitoring/presence detects absence and `absence_photo_capture_enabled = true`
2. Agent captures a photo via the device camera
3. Photo uploaded to `POST /agent/v1/verification/photo-capture` (device JWT auth)
4. Backend creates `verification_records` row: `method = on_demand_photo`, `trigger = on_demand` or `absence_detected`, `status = pending_review`
5. Backend creates `verification_evidence_assets` row with `trigger_type = on_demand` or `absence_detected`
6. Alert raised when absence-detected verification is captured; on-demand captures are visible in verification history

**Without `monitoring` module:** Absence-detected photo capture is unavailable because there is no activity/presence deviation source. On-demand camera photo capture still works when `verification` is entitled and enabled.

---

## Flow 4 - Biometric Device Scan

**Prerequisites:** `verification` entitled. Biometric/attendance device registered under the employee's legal entity. Phase 1 does not assign biometric/attendance devices to office locations. Employee enrolled when the punch method includes a biometric factor.

### Device Registration

1. ONEVO operator registers a physical biometric/attendance terminal in the tenant's Verification settings
2. `POST /api/v1/time-attendance/devices` creates a `biometric_devices` row with required `legal_entity_id`, vendor/model, connection method (`direct_webhook`, `vendor_middleware`, `local_gateway`, `polling_api`, or `manual_import`), HMAC/API-key metadata, and enabled punch methods (`face`, `fingerprint`, `rfid_card`, `pin`, or combined methods)
3. Device receives a device token and is configured with the ONEVO webhook endpoint

### Employee Biometric Enrollment

1. Employee visits the HR portal or a self-service kiosk
2. Submits biometric data, such as fingerprint scan or face capture, via the enrollment endpoint
3. `POST /api/v1/time-attendance/devices/{id}/enrollments` creates a `biometric_enrollments` row with `employee_id`, `biometric_device_id`, `modality`, and encrypted template reference/hash
4. Employee is now enrollable at all registered devices for their tenant

### Scan Event

1. Employee scans at the terminal
2. Device, vendor middleware, or local gateway posts scan event to ONEVO webhook: `POST /api/v1/time-attendance/biometric/webhook`
3. Backend:
   - Validates device token
   - Normalizes the submitted punch method (`fingerprint`, `face`, `rfid_card`, `pin`, `card_plus_face`, `card_plus_fingerprint`, or `manual`)
   - Matches biometric factors against the enrolled employee when applicable
   - Creates `biometric_events` row with `auth_method` and nullable `modality`
   - Creates `verification_records` row: `method = biometric`, `trigger = biometric_scan`, `status = verified` or `failed` when a biometric factor was used
4. Failed biometric verification events count toward the `identity.verification_failed_spike` alert threshold

---

## Dashboard Alert - `identity.verification_failed_spike`

| Property | Value |
|:---|:---|
| Alert code | `identity.verification_failed_spike` |
| Source | Identity Verification module |
| Trigger | >= 3 verification failures (any type) for **different employees** within 1 hour in the same tenant |
| Auto-resolve | Failure rate drops below threshold |
| Visible in | Developer Platform Dashboard (platform operators) |
| Generated by | MediatR domain event handler on `VerificationFailedEvent` |

This alert fires regardless of whether `monitoring` or `exceptions` are entitled. It is owned entirely by the `verification` module.

---

## Configuration

| Setting | Location | Default | Notes |
|:---|:---|:---|:---|
| `verification.require_photo_clock_in` | Tenant configuration settings | `true` | Prompt for photo on clock-in |
| `verification.require_photo_clock_out` | Tenant configuration settings | `true` | Prompt for photo on clock-out |
| `verification.photo_capture_context_scope` | Tenant configuration settings | `remote_only` | Applies clock-in/out photo prompts to `remote_only`, `onsite_only`, `remote_and_onsite`, or `disabled` |
| `camera_photo_verification_enabled` | Step 4 provisioning / Tenant Management config tab | **Off** | Must be explicitly enabled for on-demand camera photo capture |
| `absence_photo_capture_enabled` | Step 4 provisioning / Tenant Management config tab | **Off** | Allows absence-detected camera photo capture when monitoring/presence detects a deviation |
| Photo retention days | Tenant configuration settings | 90 days | Verification photos older than this are automatically deleted from file storage |

---

## Behavior Without Other Intelligence Modules

| Missing module | Effect on `verification` |
|:---|:---|
| No `monitoring` | Clock-in/out photo, on-demand camera photo, and biometric scans work. Absence-detected camera photo capture is unavailable because no activity/presence deviation source exists. |
| No `exceptions` | All verification flows work fully. Verification failures generate `identity.verification_failed_spike` alerts independently via their own event handler. |
| No `monitoring` | No impact. |
| No `analytics` | Verification data is not included in cross-module analytics. The Verification module's own reports are unaffected. |

---

## Entitlement Guard Behavior

```http
POST /tenant/v1/verification/clock-in

# Tenant not entitled to verification:
HTTP 403 Forbidden
{ "error": "module_not_entitled", "module": "verification" }

# Tenant entitled, camera toggle required but off:
HTTP 422 Unprocessable Entity
{ "error": "feature_disabled", "feature": "camera_photo_verification" }
```

---

## Key Database Tables

| Table | Purpose |
|:---|:---|
| `verification_records` | All verification events: type, outcome, employee_id, recorded_at |
| `verification_evidence_assets` | Verification, clock-in/out, and failure photo evidence files linked to `file_records`; biometric scans do not automatically create photo evidence |
| `biometric_devices` | Canonical physical biometric/attendance terminal table linked to legal entities, with direct webhook/vendor middleware/local gateway/polling/manual-import connection metadata |
| `biometric_enrollments` | Per-employee biometric template (encrypted hash, not raw biometric) |
| `biometric_events` | Raw punch/scan events from biometric/attendance terminals |

---

## Permissions

| Permission code | Description |
|:---|:---|
| `verification.records.view` | View verification records for employees |
| `verification.records.review` | Approve or flag pending verification submissions |
| `verification.devices.manage` | Register, update, and decommission biometric devices |
| `verification.enrollment.manage` | Enroll or re-enroll employees in biometric devices |
| `verification.config.manage` | Update verification configuration settings |

---

## API Endpoints

| Method | Route | Description | Permission |
|:---|:---|:---|:---|
| POST | `/tenant/v1/verification/clock-in` | Submit clock-in photo | Authenticated employee (self only) |
| POST | `/tenant/v1/verification/clock-out` | Submit clock-out photo | Authenticated employee (self only) |
| GET | `/tenant/v1/verification/employees/{id}/records` | Verification history for an employee | `verification.records.view` |
| PATCH | `/tenant/v1/verification/records/{id}` | Mark record approved or flagged | `verification.records.review` |
| GET | `/api/v1/time-attendance/devices` | List attendance/biometric terminals | `attendance:read` |
| POST | `/api/v1/time-attendance/devices` | Register an attendance/biometric terminal | `attendance:write` |
| PUT | `/api/v1/time-attendance/devices/{id}` | Update an attendance/biometric terminal | `attendance:write` |
| DELETE | `/api/v1/time-attendance/devices/{id}` | Decommission an attendance/biometric terminal | `attendance:write` |
| GET | `/api/v1/time-attendance/devices/{id}/enrollments?employee_id={employeeId}` | Check enrollment status | `attendance:read` |
| POST | `/api/v1/time-attendance/devices/{id}/enrollments` | Submit biometric/device enrollment | `attendance:write` |
| POST | `/api/v1/time-attendance/biometric/webhook` | Inbound webhook from attendance/biometric terminal, vendor middleware, or local gateway | HMAC/API key (no tenant user auth, no Device JWT) |
| POST | `/agent/v1/verification/photo-capture` | Inbound on-demand or absence-detected photo from WorkPulse agent | Device JWT |

All endpoints (except webhooks) require `IsModuleEnabledAsync(tenantId, "verification")`.

---

## Storage

Verification photos count toward `tenant_storage_limit_gb`. Each photo is stored as compressed JPEG. `verification_evidence_assets.file_record_id` points to `file_records`. Photos are deleted automatically after `verification.photo_retention_days` by the data retention background job unless blocked by legal hold.

---

## Related

- [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]
- [[developer-platform/modules/monitoring/end-to-end-logic|Activity Monitoring - End-to-End Logic]]
- [[developer-platform/modules/exceptions/end-to-end-logic|Exception Engine - End-to-End Logic]]
- [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] - Step 4 camera photo toggle
