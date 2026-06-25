# Biometric Enrollment - End-to-End Logic

**Module:** Identity Verification
**Feature:** Biometric Enrollment

---

## Enroll Employee Biometric Factor

### Flow

```
POST /api/v1/biometric/enroll
  -> BiometricEnrollmentController.Enroll(EnrollCommand)
    -> [RequirePermission("verification:configure")]
    -> BiometricEnrollmentService.EnrollAsync(command, ct)
      -> 1. Validate employee exists
      -> 2. Check GDPR consent: consent_type = 'biometric' must be true
         -> If not consented -> Return failure("Biometric consent required")
      -> 3. Validate device_id exists and is active
      -> 4. Check for existing active enrollment on same device
      -> 5. INSERT into biometric_enrollments
         -> modality = fingerprint, face, palm_vein, iris, or other
         -> template_hash = reference to device/vendor-local biometric template
         -> consent_given = true
         -> is_active = true
      -> Return Result.Success(enrollmentDto)
```

### Key Rules

- **Raw biometric templates are NEVER stored in ONEVO** - only `template_hash` is stored as a reference to the biometric device/vendor's local storage.
- **Legal & Privacy notice/consent is mandatory** before biometric enrollment.
- **One active enrollment per employee per device and modality.**

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[frontend/architecture/overview|Biometric Enrollment Overview]]
- [[modules/identity-verification/biometric-devices/end-to-end-logic|Biometric Devices - End-to-End Logic]]
- [[modules/identity-verification/verification-policies/end-to-end-logic|Verification Policies - End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/compliance|Compliance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
