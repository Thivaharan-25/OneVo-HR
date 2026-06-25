# Integrations - End-to-End Logic

**Module:** Configuration
**Feature:** External Integration Connections
**Phase:** Phase 2

---

## Add Integration

### Flow

```
POST /api/v1/settings/integrations
  -> IntegrationController.Create(CreateIntegrationCommand)
    -> [RequirePermission("settings:admin")]
    -> Validation: integration_type, config_json required
    -> IntegrationService.CreateAsync(command, ct)
      -> 1. Validate integration_type: Phase 2 generic/legacy tenant integrations only, e.g. peoplehr, slack, lms
      -> 2. Encrypt credentials via IEncryptionService (AES-256)
      -> 3. INSERT into integration_connections
         -> status = 'active'
      -> 4. Test connection (async, non-blocking)
         -> If fails -> UPDATE status = 'error'
      -> 5. Log to audit_logs
      -> Return Result.Success(integrationDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Unknown integration_type | Return 422 |
| Connection test failure | Integration created with status = 'error' |
| Duplicate integration type | Return 409 (one per type per tenant) |
| PeopleHR API key lacks selected scope | Phase 2 only. Save connection as active only for detected scopes; migration preflight blocks unavailable areas |

**Phase rule:** This generic connection flow is Phase 2 only.

**Dedicated provider rule:** Phase 1 providers Stripe, PayHere, Paddle, Resend, Google Calendar, and Outlook Calendar are not created through this flow. Use payment gateway setup, notification channel/service key setup, or Calendar OAuth connection flows instead.

## Related

- [[frontend/architecture/overview|Integrations Overview]]
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
