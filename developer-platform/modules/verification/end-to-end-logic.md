# Identity Verification — End-to-End Logic

**Module key:** `verification`  
**Pillar:** Workforce Intelligence (Package 1)  
**Pricing unit:** Per employee  
**Entitlement guard:** All endpoints call `IsModuleEnabledAsync(tenantId, "verification")` → 403 `module_not_entitled` if not entitled  
**Dependency:** See [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]

---

## What This Module Does

Identity Verification confirms that the person clocking in, clocking out, or present at their workstation is actually the enrolled employee. It operates across three verification channels:

1. **Clock-in / clock-out photo** — employee submits a selfie photo when starting or ending their work session
2. **WorkPulse agent spot-check (camera)** — the desktop agent captures a photo at a random or rule-triggered moment during the work session for passive identity confirmation
3. **Biometric device scan** — a physical fingerprint or face-recognition terminal at an office location records a biometric event when the employee badges in

Verification operates **standalone** — it does not require the Activity Monitoring module. Clock-in verification works even if `monitoring` is not entitled.

---

## Verification Types

| Type | `verification_records.type` value | Trigger | Photo stored |
|:---|:---|:---|:---|
| Clock-in photo | `clock_in_photo` | Employee taps "Clock In" in the ONEVO app | Yes — uploaded to file storage |
| Clock-out photo | `clock_out_photo` | Employee taps "Clock Out" in the ONEVO app | Yes — uploaded to file storage |
| Agent spot-check | `spot_check` | WorkPulse agent triggers random or absence-based camera capture | Yes — uploaded to file storage |
| Biometric scan | `biometric_scan` | Employee scans at a registered biometric device | No — biometric event only, template hash stored |

---

## Flow 1 — Clock-In Photo Verification

**Prerequisites:** `verification` module entitled. No additional config toggle required for photo collection.

1. Employee opens the ONEVO employee app and taps **Clock In**
2. App prompts for camera permission and captures a selfie
3. Photo is uploaded via `POST /tenant/v1/verification/clock-in` (multipart form with the image)
4. Backend:
   - Validates file type (JPEG/PNG, max 5 MB)
   - Checks `tenant_storage_limit_gb` → 413 `storage_limit_exceeded` if full
   - Stores photo to file storage → inserts `file_records` row
   - Creates `verification_records` row: `type = clock_in_photo`, `outcome = pending`, `photo_file_id`
   - Publishes `ClockInPhotoSubmittedEvent`
5. A reviewer (HR or manager with `verification.records.review` permission) later opens the employee's verification history and marks the record `approved` or `flagged`
6. Alternatively, an automated face-match service (Phase 2 feature — manual review only in Phase 1) marks the outcome

**Outcome values:**
- `pending` — submitted, not yet reviewed
- `approved` — reviewer confirmed identity
- `flagged` — reviewer raised a concern

---

## Flow 2 — Clock-Out Photo Verification

Identical to clock-in flow. Endpoint: `POST /tenant/v1/verification/clock-out`.  
`verification_records.type = clock_out_photo`.

Both clock-in and clock-out can be configured independently — tenants can require photo at clock-in only, clock-out only, or both. Configuration stored in `tenant_configuration_settings` under key `verification.require_photo_clock_in` and `verification.require_photo_clock_out` (default: both `true` when module is entitled).

---

## Flow 3 — WorkPulse Agent Spot-Check (Camera Photo)

**Prerequisites:** `verification` module entitled AND `camera_photo_verification_enabled = true` in tenant Step 4 configuration.

> This toggle defaults to **Off**. Tenants must explicitly enable it. Subject to biometric consent and retention policy confirmation.

1. WorkPulse agent detects a trigger condition (random interval, or absence-detected by monitoring if `monitoring` is also entitled)
2. Agent captures a photo via the device camera
3. Photo uploaded to `POST /agent/v1/verification/spot-check` (device JWT auth)
4. Backend creates `verification_records` row: `type = spot_check`, `outcome = pending`
5. Alert raised: `identity.spot_check_captured` (Info level) — visible to HR reviewer

**Without `monitoring` module:** Spot-checks cannot be absence-triggered (no activity data). They can still be triggered on a fixed time interval if the tenant has `verification` entitled and the toggle is on.

---

## Flow 4 — Biometric Device Scan

**Prerequisites:** `verification` entitled. Biometric device registered and assigned to an office location. Employee enrolled.

### Device Registration

1. ONEVO operator registers a physical biometric terminal in the tenant's Verification settings
2. `POST /tenant/v1/verification/devices` → creates `biometric_devices` row with `office_location_id` (FK to `office_locations` in the `org` Foundation module)
3. Device receives a device token and is configured with the ONEVO webhook endpoint

### Employee Biometric Enrollment

1. Employee visits the HR portal or a self-service kiosk
2. Submits biometric data (fingerprint scan / face capture) via the enrollment endpoint
3. `POST /tenant/v1/verification/employees/{id}/enroll` → creates `biometric_enrollments` row with encrypted template hash
4. Employee is now enrollable at all registered devices for their tenant

### Scan Event

1. Employee scans at the terminal
2. Device posts scan event to ONEVO webhook: `POST /webhook/v1/biometric-event`
3. Backend:
   - Validates device token
   - Matches scan against enrolled employee
   - Creates `biometric_events` row
   - Creates `verification_records` row: `type = biometric_scan`, `outcome = match` or `no_match`
4. `no_match` events count toward the `identity.verification_failed_spike` alert threshold

---

## Dashboard Alert — `identity.verification_failed_spike`

| Property | Value |
|:---|:---|
| Alert code | `identity.verification_failed_spike` |
| Source | Identity Verification module |
| Trigger | ≥ 3 verification failures (any type) for **different employees** within 1 hour in the same tenant |
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
| `camera_photo_verification_enabled` | Step 4 provisioning / Tenant Console config tab | **Off** | Must be explicitly enabled; agent spot-checks require this |
| Photo retention days | Tenant configuration settings | 90 days | Verification photos older than this are automatically deleted from file storage |

---

## Behavior Without Other Intelligence Modules

| Missing module | Effect on `verification` |
|:---|:---|
| No `monitoring` | All verification flows work fully. Clock-in/out photo, agent spot-checks (if toggle enabled), and biometric scans are all unaffected. Spot-checks cannot be absence-triggered (no activity data) but can still fire on a fixed interval. |
| No `exceptions` | All verification flows work fully. Verification failures generate `identity.verification_failed_spike` alerts independently via their own event handler. |
| No `workforce` | No impact. |
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
| `verification_records` | All verification events: type, outcome, photo_file_id, employee_id, recorded_at |
| `biometric_devices` | Physical biometric terminals linked to office locations |
| `biometric_enrollments` | Per-employee biometric template (encrypted hash, not raw biometric) |
| `biometric_events` | Raw scan events from biometric terminals |

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
| GET | `/tenant/v1/verification/devices` | List biometric devices | `verification.devices.manage` |
| POST | `/tenant/v1/verification/devices` | Register a biometric device | `verification.devices.manage` |
| DELETE | `/tenant/v1/verification/devices/{id}` | Decommission a biometric device | `verification.devices.manage` |
| GET | `/tenant/v1/verification/employees/{id}/enrollment` | Check enrollment status | `verification.enrollment.manage` |
| POST | `/tenant/v1/verification/employees/{id}/enroll` | Submit biometric enrollment | `verification.enrollment.manage` |
| POST | `/webhook/v1/biometric-event` | Inbound webhook from biometric terminal | Device JWT (no tenant user auth) |
| POST | `/agent/v1/verification/spot-check` | Inbound photo from WorkPulse agent | Device JWT |

All endpoints (except webhooks) require `IsModuleEnabledAsync(tenantId, "verification")`.

---

## Storage

Verification photos count toward `tenant_storage_limit_gb`. Each photo is stored as compressed JPEG. The `verification_records.photo_file_id` FK points to `file_records`. Photos are deleted automatically after `verification.photo_retention_days` by the data retention background job.

---

## Related

- [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]
- [[developer-platform/modules/monitoring/end-to-end-logic|Activity Monitoring — End-to-End Logic]]
- [[developer-platform/modules/exceptions/end-to-end-logic|Exception Engine — End-to-End Logic]]
- [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] — Step 4 camera photo toggle
