# Verification Policies

**Module:** Identity Verification  
**Feature:** Verification Policies

---

## Purpose

Per-tenant verification rules controlling when and how identity verification is triggered.

## Database Tables

### `verification_policies`
Fields: `verify_on_login`, `verify_on_logout`, `interval_minutes` (0 = disabled), `match_threshold` (default 80.0), `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/verification/policy` | `verification:view` | Get policy |
| PUT | `/api/v1/verification/policy` | `verification:configure` | Update policy |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `PurgeExpiredVerificationPhotosJob` | Daily 2:00 AM | Delete photos past retention |

## Related

- [[identity-verification|Identity Verification Module]]
- [[verification-policies/end-to-end-logic|Verification Policies — End-to-End Logic]]
- [[verification-policies/testing|Verification Policies — Testing]]
- [[photo-verification/overview|Photo Verification]]
- [[biometric-enrollment/overview|Biometric Enrollment]]
- [[data-classification]]
- [[compliance]]
- [[multi-tenancy]]
- [[WEEK3-identity-verification]]
