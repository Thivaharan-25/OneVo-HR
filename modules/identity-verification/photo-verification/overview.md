# Photo Verification

**Module:** Identity Verification  
**Feature:** Photo Verification

---

## Purpose

Verifies employee identity via photo capture from desktop agent. Phase 1 uses simple comparison, Phase 2 may add ML matching.

## Database Tables

### `verification_records`
Key columns: `employee_id`, `verified_at`, `method` (`photo`, `fingerprint`), `photo_file_id`, `match_confidence` (0-100), `status` (`verified`, `failed`, `skipped`, `expired`), `device_type` (`agent`, `biometric`), `device_id`, `failure_reason`.

## Key Business Rules

1. Photos are temporary — retained for configurable period (default 30 days), then auto-deleted.
2. Photos are RESTRICTED data — stored in blob storage, never in DB.
3. Verification policy respects monitoring overrides.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `VerificationFailed` | Match below threshold | [[exception-engine]], [[notifications]] |
| `VerificationCompleted` | Successful verification | [[workforce-presence]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/verification/verify` | Internal (agent) | Submit verification photo |
| GET | `/api/v1/verification/records/{employeeId}` | `verification:view` | History |

## Related

- [[identity-verification|Identity Verification Module]]
- [[photo-verification/end-to-end-logic|Photo Verification — End-to-End Logic]]
- [[photo-verification/testing|Photo Verification — Testing]]
- [[biometric-enrollment/overview|Biometric Enrollment]]
- [[verification-policies/overview|Verification Policies]]
- [[data-classification]]
- [[compliance]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[WEEK3-identity-verification]]
