# Module: Identity Verification

**Namespace:** `ONEVO.Modules.IdentityVerification`
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 4 (Week 3)
**Tables:** 6
**Task File:** [[WEEK3-identity-verification]]

---

## Purpose

Verifies employee identity via photo capture and biometric fingerprint matching. Configurable verification policies allow tenants to require identity checks at login, logout, and/or at timed intervals. Manages biometric terminal hardware (fingerprint readers).

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext`, `IFileService` | Multi-tenancy, photo storage |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee profile photos for matching |
| **Depends on** | [[configuration]] | `IConfigurationService` | Verification policy settings |
| **Consumed by** | [[workforce-presence]] | `IIdentityVerificationService` | Confirm identity for presence records |
| **Consumed by** | [[exception-engine]] | — (via `VerificationFailed` event) | Alert on failed verifications |

---

## Public Interface

```csharp
// ONEVO.Modules.IdentityVerification/Public/IIdentityVerificationService.cs
public interface IIdentityVerificationService
{
    Task<Result<VerificationRecordDto>> VerifyPhotoAsync(Guid employeeId, Guid photoFileId, Guid deviceId, CancellationToken ct);
    Task<Result<VerificationPolicyDto>> GetPolicyAsync(Guid tenantId, CancellationToken ct);
    Task<Result<List<VerificationRecordDto>>> GetVerificationHistoryAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<BiometricDeviceDto>> RegisterDeviceAsync(RegisterDeviceCommand command, CancellationToken ct);
}
```

---

## Database Tables (6)

### `verification_policies`

Per-tenant verification rules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `verify_on_login` | `boolean` | Require photo at login |
| `verify_on_logout` | `boolean` | Require photo at logout |
| `interval_minutes` | `int` | Periodic verification (0 = disabled) |
| `match_threshold` | `decimal(5,2)` | Minimum confidence score to pass (default 80.0) |
| `is_active` | `boolean` | Master toggle |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `verification_records`

Each verification event.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `verified_at` | `timestamptz` | When verification occurred |
| `method` | `varchar(20)` | `photo`, `fingerprint` |
| `photo_file_id` | `uuid` | FK → file_records (nullable, photo method only) |
| `match_confidence` | `decimal(5,2)` | 0–100 confidence score |
| `status` | `varchar(20)` | `verified`, `failed`, `skipped`, `expired` |
| `device_type` | `varchar(20)` | `agent` or `biometric` — discriminator for polymorphic FK |
| `device_id` | `uuid` | FK → registered_agents (when `device_type = 'agent'`) or biometric_devices (when `device_type = 'biometric'`) |
| `failure_reason` | `varchar(255)` | Nullable — why verification failed |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, verified_at)`, `(tenant_id, status)`

### `biometric_devices`

Fingerprint terminals (moved from old Attendance module).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `device_name` | `varchar(100)` | Human-readable name |
| `location_id` | `uuid` | FK → departments or custom location |
| `api_key_encrypted` | `bytea` | HMAC-SHA256 key (encrypted at rest via `IEncryptionService`) |
| `model` | `varchar(100)` | Device model |
| `is_active` | `boolean` | |
| `last_heartbeat_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `biometric_enrollments`

Employee fingerprint enrollment.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → biometric_devices |
| `enrolled_at` | `timestamptz` | |
| `consent_given` | `boolean` | GDPR/PDPA — must be true |
| `template_hash` | `varchar(128)` | Fingerprint template reference (not the template itself) |
| `is_active` | `boolean` | |

### `biometric_events`

Raw clock-in/out events from terminals.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → biometric_devices |
| `event_type` | `varchar(20)` | `clock_in`, `clock_out`, `break_start`, `break_end` |
| `captured_at` | `timestamptz` | |
| `verified` | `boolean` | Fingerprint match result |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, captured_at)`, `(device_id, captured_at)`

**Note:** Biometric events flow to [[workforce-presence]] for presence session reconciliation.

### `biometric_audit_logs`

Tamper detection and device health.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `device_id` | `uuid` | FK → biometric_devices |
| `event_type` | `varchar(50)` | `heartbeat`, `tamper_detected`, `firmware_update`, `error` |
| `details_json` | `jsonb` | Event-specific details |
| `recorded_at` | `timestamptz` | |

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `VerificationFailed` | Photo/fingerprint match below threshold | [[exception-engine]], [[notifications]] (alert manager) |
| `VerificationCompleted` | Successful verification | [[workforce-presence]] (confirm identity) |
| `BiometricDeviceOffline` | No heartbeat for 5+ minutes | [[notifications]] (alert admin) |

---

## Key Business Rules

1. **Verification photos are temporary** — retained for configurable period (default 30 days) then auto-deleted by `PurgeExpiredVerificationPhotosJob`. They are NOT employee profile photos.
2. **Photos are RESTRICTED data** — stored in blob storage via `file_records`, never in the database.
3. **Biometric consent is mandatory** — `consent_given` must be `true` before enrollment. This is a GDPR/PDPA requirement.
4. **Fingerprint templates are NEVER stored in ONEVO** — only `template_hash` (a reference to the biometric device's local storage). The actual template stays on the hardware.
5. **Verification policy respects monitoring overrides** — if an employee has `identity_verification = false` in `employee_monitoring_overrides`, skip verification even if tenant policy is active.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/verification/policy` | `verification:view` | Get tenant verification policy |
| PUT | `/api/v1/verification/policy` | `verification:configure` | Update verification policy |
| GET | `/api/v1/verification/records/{employeeId}` | `verification:view` | Verification history |
| POST | `/api/v1/verification/verify` | Internal (agent) | Submit verification photo |
| GET | `/api/v1/biometric/devices` | `verification:view` | List biometric devices |
| POST | `/api/v1/biometric/devices` | `verification:configure` | Register device |
| PUT | `/api/v1/biometric/devices/{id}` | `verification:configure` | Update device |
| POST | `/api/v1/biometric/enroll` | `verification:configure` | Enroll employee fingerprint |
| POST | `/api/v1/biometric/webhook` | HMAC-SHA256 | Receive biometric events from terminals |

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
- **This module owns biometric hardware** — [[workforce-presence]] only consumes the events generated here.

## Features

- [[verification-policies]] — Per-tenant verification rules (login, logout, interval)
- [[photo-verification]] — Photo capture and confidence-score matching
- [[biometric-devices]] — Fingerprint terminal management and HMAC webhook authentication
- [[biometric-enrollment]] — Employee fingerprint enrollment with mandatory GDPR consent

---

## Related

- [[auth-architecture]] — HMAC-SHA256 authentication for biometric device webhooks
- [[multi-tenancy]] — Policies and records are tenant-scoped
- [[data-classification]] — Photos are RESTRICTED; fingerprint templates stored on device hardware only
- [[compliance]] — `consent_given` mandatory for biometric enrollment (GDPR/PDPA)
- [[event-catalog]] — `VerificationFailed`, `VerificationCompleted`, `BiometricDeviceOffline`
- [[WEEK3-identity-verification]] — Implementation task file

See also: [[module-catalog]], [[workforce-presence]], [[agent-gateway]], [[exception-engine]]
