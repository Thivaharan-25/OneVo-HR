# Integrations — End-to-End Logic

**Module:** Configuration
**Feature:** External Integration Connections

---

## Add Integration

### Flow

```
POST /api/v1/settings/integrations
  -> IntegrationController.Create(CreateIntegrationCommand)
    -> [RequirePermission("settings:admin")]
    -> Validation: integration_type, config_json required
    -> IntegrationService.CreateAsync(command, ct)
      -> 1. Validate integration_type: stripe, resend, google_calendar, slack, lms
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

## Related

- [[frontend/architecture/overview|Integrations Overview]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
