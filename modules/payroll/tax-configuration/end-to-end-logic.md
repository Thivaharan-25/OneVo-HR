# Tax Configuration — End-to-End Logic

**Module:** Payroll
**Feature:** Tax Configuration

---

## Configure Tax Brackets

### Flow

```
POST /api/v1/payroll/tax-config
  -> TaxConfigController.Create(CreateTaxConfigCommand)
    -> [RequirePermission("payroll:write")]
    -> TaxConfigService.CreateAsync(command, ct)
      -> 1. Validate country_id exists
      -> 2. Validate tax_brackets_json:
         -> Array of { from, to, rate } — progressive brackets
         -> Brackets must be contiguous with no gaps
      -> 3. INSERT into tax_configurations
         -> effective_from date
      -> Return Result.Success(taxConfigDto)
```

### Key Rules

- **Progressive tax brackets** — each bracket has from/to range and rate.
- **Country-specific** — different countries have different tax systems.
- **Effective dating** — new config takes effect from `effective_from`, old one stays for historical runs.

## Related

- [[payroll/tax-configuration/overview|Tax Configuration Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/pensions/overview|Pensions]]
- [[error-handling]]
- [[migration-patterns]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
