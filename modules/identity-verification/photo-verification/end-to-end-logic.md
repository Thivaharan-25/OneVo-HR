# Photo Verification — End-to-End Logic

**Module:** Identity Verification
**Feature:** Photo Verification

---

## Verify Employee Photo

### Flow

```
POST /api/v1/verification/verify (Internal — called by agent via gateway)
  -> VerificationController.Verify(VerifyPhotoCommand)
    -> Auth: Device JWT (routed from agent-gateway)
    -> VerificationService.VerifyPhotoAsync(employeeId, photoFileId, deviceId, ct)
      -> 1. Check verification policy is active for tenant
      -> 2. Check employee override: identity_verification not disabled
      -> 3. Load employee profile photo from core-hr
      -> 4. Compare captured photo vs profile photo
         -> Phase 1: Simple comparison service (basic similarity)
         -> Phase 2: ML-based facial recognition
      -> 5. Calculate match_confidence (0-100)
      -> 6. INSERT into verification_records
         -> method = 'photo', status based on threshold:
            -> match_confidence >= match_threshold -> 'verified'
            -> match_confidence < match_threshold -> 'failed'
      -> 7. If failed:
         -> Publish VerificationFailed event
         -> Exception engine creates alert, notifications sent to manager
      -> 8. If verified:
         -> Publish VerificationCompleted event
         -> Workforce presence confirms identity
      -> Return Result.Success(verificationDto)
```

### Key Rules

- **Verification photos are RESTRICTED data** — stored in blob storage, retained for configurable period only.
- **Default match threshold: 80.0%** — configurable per tenant in verification_policies.

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[frontend/architecture/overview|Photo Verification Overview]]
- [[modules/identity-verification/verification-policies/end-to-end-logic|Verification Policies — End-to-End Logic]]
- [[modules/identity-verification/biometric-enrollment/end-to-end-logic|Biometric Enrollment — End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
