# Biometric Enrollment

**Module:** Identity Verification  
**Feature:** Biometric Enrollment

---

## Purpose

Employee fingerprint enrollment with mandatory GDPR/PDPA consent. Templates are NEVER stored in ONEVO — only a hash reference.

## Database Tables

### `biometric_enrollments`
Fields: `employee_id`, `device_id`, `enrolled_at`, `consent_given` (must be true), `template_hash` (reference only), `is_active`.

### `biometric_events`
Raw clock-in/out events: `event_type` (`clock_in`, `clock_out`, `break_start`, `break_end`), `captured_at`, `verified`.

## Key Business Rules

1. `consent_given` must be `true` before enrollment (GDPR/PDPA).
2. Fingerprint templates NEVER stored in ONEVO — only `template_hash`.
3. Biometric events flow to [[workforce-presence]] for presence reconciliation.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/biometric/enroll` | `verification:configure` | Enroll fingerprint |
| POST | `/api/v1/biometric/webhook` | HMAC-SHA256 | Receive biometric events |

## Related

- [[identity-verification|Identity Verification Module]]
- [[biometric-enrollment/end-to-end-logic|Biometric Enrollment — End-to-End Logic]]
- [[biometric-enrollment/testing|Biometric Enrollment — Testing]]
- [[biometric-devices/overview|Biometric Devices]]
- [[verification-policies/overview|Verification Policies]]
- [[data-classification]]
- [[compliance]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[WEEK3-identity-verification]]
