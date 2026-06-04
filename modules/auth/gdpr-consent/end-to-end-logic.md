# Legal & Privacy Acceptance - End-to-End Logic

**Module:** Auth
**Feature:** Legal & Privacy Acceptance Tracking

---

## Record Legal Decision

### Flow

```text
POST /api/v1/legal/acceptances
  -> LegalAcceptanceController.Record(RecordLegalAcceptanceCommand)
    -> [Authenticated]
    -> LegalAcceptanceService.RecordAsync(command, ct)
      -> 1. Validate document_type, document_version, decision, required flag, and source
      -> 2. UPSERT into legal_acceptance_records
      -> 3. If item is platform-required and accepted/acknowledged:
         -> Dashboard/account gate may proceed
      -> 4. If item is collection-required and accepted/acknowledged:
         -> Affected collector may activate for this employee
      -> 5. If item is collection-required and declined/withdrawn:
         -> Disable only the affected collection category via IConfigurationService
      -> 6. Log to audit_logs: action = "legal_acceptance.recorded"
      -> Return Result.Success()
```

## Check Legal Gate

### Flow

```text
Internal call before dashboard access or activating a collector:
  -> LegalAcceptanceService.CheckGateAsync(userId, gateType, category, ct)
    -> Query legal_acceptance_records WHERE user_id, document_type, version
    -> Return allowed/block reason
```

### Key Rules

- **Terms and Privacy Notice acknowledgement are mandatory** before account activation or dashboard access.
- **WorkPulse monitoring/screenshot/biometric-photo notices are mandatory only before the affected collection category activates.**
- **Photo/biometric notice or consent is mandatory** before WorkPulse photo/biometric verification starts.
- **Acceptance records include IP address, user agent, source, document type, and version** for legal compliance.
- **Withdrawing optional collection consent, or missing a required notice,** immediately disables only the affected collection category for that employee.

## Related

- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/compliance|Compliance]]
