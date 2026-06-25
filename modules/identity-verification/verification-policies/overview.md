# Verification Policies

**Module:** Identity Verification  
**Feature:** Verification Policies

---

## Purpose

Per-tenant verification rules controlling when and how identity verification is triggered.

Verification policy also controls reference-photo enrollment behavior for employees who sign in to the TrayApp without an approved reference photo. The default is manual review by the configured identity-verification resolver. A tenant may enable SSO/MFA-backed auto-approval only as an explicit policy choice.

## Database Tables

### `verification_policies`
Fields: `require_photo_clock_in`, `require_photo_clock_out`, `camera_photo_verification_enabled`, `absence_photo_capture_enabled`, `photo_capture_context_scope` (`remote_only`, `onsite_only`, `remote_and_onsite`, `disabled`), `match_threshold` (default 80.0), `is_active`, `reference_enrollment_mode` (`manual_review`, `trusted_sso_auto_approve`), `block_monitoring_until_reference_approved`.

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

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/verification-policies/end-to-end-logic|Verification Policies - End-to-End Logic]]
- [[modules/identity-verification/verification-policies/testing|Verification Policies - Testing]]
- [[frontend/architecture/overview|Photo Verification]]
- [[frontend/architecture/overview|Biometric Enrollment]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
