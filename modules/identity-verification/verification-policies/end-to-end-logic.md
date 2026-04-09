# Verification Policies — End-to-End Logic

**Module:** Identity Verification
**Feature:** Verification Policies

---

## Get Verification Policy

### Flow

```
GET /api/v1/verification/policy
  -> VerificationPolicyController.Get()
    -> [RequirePermission("verification:view")]
    -> VerificationPolicyService.GetPolicyAsync(tenantId, ct)
      -> Query verification_policies WHERE tenant_id
      -> Return Result.Success(policyDto)
```

## Update Verification Policy

### Flow

```
PUT /api/v1/verification/policy
  -> VerificationPolicyController.Update(UpdatePolicyCommand)
    -> [RequirePermission("verification:configure")]
    -> VerificationPolicyService.UpdateAsync(command, ct)
      -> 1. Validate match_threshold: 0-100 (recommend >= 70)
      -> 2. UPSERT into verification_policies
      -> 3. Invalidate policy cache
      -> 4. Agent picks up new policy on next poll
      -> Return Result.Success(policyDto)
```

### Key Rules

- **verify_on_login + verify_on_logout + interval_minutes** control when verification happens.
- **Policy respects employee monitoring overrides** — if `identity_verification = false` in override, skip.

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[frontend/architecture/overview|Verification Policies Overview]]
- [[modules/identity-verification/photo-verification/end-to-end-logic|Photo Verification — End-to-End Logic]]
- [[modules/identity-verification/biometric-enrollment/end-to-end-logic|Biometric Enrollment — End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/compliance|Compliance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
