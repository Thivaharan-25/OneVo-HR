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

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/pensions/overview|Pensions]]
- [[payroll/allowances/overview|Allowances]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
