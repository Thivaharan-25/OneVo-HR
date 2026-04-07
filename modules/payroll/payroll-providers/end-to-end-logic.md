# Payroll Providers — End-to-End Logic

**Module:** Payroll
**Feature:** Payroll Providers

---

## Register Provider

### Flow

```
POST /api/v1/payroll/providers
  -> PayrollProviderController.Create(CreateProviderCommand)
    -> [RequirePermission("payroll:write")]
    -> PayrollProviderService.CreateAsync(command, ct)
      -> 1. Validate provider_type: internal, adp, oracle
      -> 2. Encrypt credentials via IEncryptionService
      -> 3. INSERT into payroll_providers
      -> 4. Create payroll_connection linking provider to legal_entity
      -> Return Result.Success(providerDto)
```

### Key Rules

- **Credentials are encrypted at rest** — never stored in plaintext.
- **One provider per legal entity** via payroll_connections.

## Related

- [[payroll/payroll-providers/overview|Payroll Providers Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[error-handling]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
