# WEEK3: Identity Verification Module

**Status:** Planned
**Priority:** High
**Assignee:** Dev 4
**Sprint:** Week 3 (Apr 21-25)
**Module:** IdentityVerification

## Description

Implement verification policies, photo capture API, biometric matching integration, and verification records. The photo verification flow is: agent captures photo → sends to server → server compares against employee profile photo → creates verification record.

## Acceptance Criteria

- [ ] `verification_policies` table — per-tenant config (login/logout/interval, match threshold)
- [ ] `verification_records` table — each verification event with confidence score
- [ ] Photo verification endpoint: agent sends photo → compare against employee avatar → return match result
- [ ] Match confidence scoring (0–100), threshold from policy (default 80.0)
- [ ] Verification statuses: `verified`, `failed`, `skipped`, `expired`
- [ ] Failure reason tracking for failed verifications
- [ ] `IIdentityVerificationService` public interface implementation
- [ ] Domain events: `VerificationFailed` → [[exception-engine]] + [[notifications]], `VerificationCompleted` → [[workforce-presence]]
- [ ] Verification respects monitoring overrides — skip if `identity_verification = false` for employee
- [ ] `PurgeExpiredVerificationPhotosJob` (daily 2 AM) — delete photos past retention period
- [ ] Verification photos are RESTRICTED data, stored in blob storage
- [ ] Verification photos are temporary (default 30 days retention) — NOT employee profile photos
- [ ] `CheckBiometricDeviceHealthJob` (every 5 min) — flag offline devices
- [ ] Phase 1: simple photo comparison. Phase 2: ML matching service.
- [ ] Unit tests ≥80% coverage

## Related

- [[identity-verification]] — module architecture
- [[configuration]] — monitoring overrides (skip verification if disabled for employee)
- [[workforce-presence]] — VerificationCompleted confirms presence
- [[data-classification]] — verification photos are RESTRICTED
- [[multi-tenancy]] — per-tenant verification policies
- [[WEEK1-auth-security]] — verification triggered at login/logout
- [[WEEK1-shared-platform]] — agent gateway is the photo capture source
- [[WEEK2-workforce-presence-biometric]] — biometric_devices table originated here
- [[WEEK2-workforce-presence-setup]] — presence sessions updated on VerificationCompleted
- [[WEEK4-exception-engine]] — VerificationFailed triggers exception alert (verification_failed rule type)
- [[WEEK4-supporting-bridges]] — notifications module delivers VerificationFailed alerts
