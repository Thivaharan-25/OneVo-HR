# GDPR Consent — End-to-End Logic

**Module:** Auth
**Feature:** GDPR Consent Tracking

---

## Record Consent

### Flow

```
POST /api/v1/auth/consent
  -> ConsentController.RecordConsent(RecordConsentCommand)
    -> [Authenticated]
    -> ConsentService.RecordAsync(command, ct)
      -> 1. Validate consent_type: data_processing, biometric, monitoring, marketing
      -> 2. UPSERT into gdpr_consent_records
         -> ON CONFLICT (tenant_id, user_id, consent_type) DO UPDATE
         -> SET consented = @value, consented_at = now, ip_address = @ip
      -> 3. If consent_type = "monitoring" AND consented = true:
         -> Monitoring features can now activate for this employee
      -> 4. If consent_type = "monitoring" AND consented = false:
         -> Disable all monitoring for this employee via IConfigurationService
      -> 5. Log to audit_logs: action = "consent.recorded"
      -> Return Result.Success()
```

## Check Consent

### Flow

```
Internal call (e.g., before activating monitoring):
  -> ConsentService.HasConsentAsync(userId, consentType, ct)
    -> Query gdpr_consent_records WHERE user_id AND consent_type
    -> Return consented = true/false
```

### Key Rules

- **Monitoring consent is mandatory** before any monitoring features activate.
- **Biometric consent is mandatory** before fingerprint enrollment (GDPR/PDPA requirement).
- **Consent records include IP address** for legal compliance.
- **Withdrawing monitoring consent** immediately disables all monitoring for that employee.

## Related

- [[gdpr-consent|Overview]]
- [[authentication]]
- [[audit-logging]]
- [[authorization]]
- [[event-catalog]]
- [[error-handling]]
- [[compliance]]
