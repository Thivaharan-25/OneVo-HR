# Tax Configuration

**Module:** Payroll  
**Feature:** Tax Configuration

---

## Purpose

Country-specific progressive tax brackets.

## Database Tables

### `tax_configurations`
Fields: `country_id`, `tax_brackets_json` (progressive brackets), `effective_from`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/payroll/tax-config` | `payroll:read` | Tax configuration |

## Related

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Pensions]]
- [[frontend/architecture/overview|Allowances]]
- [[frontend/architecture/overview|Audit Trail]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
