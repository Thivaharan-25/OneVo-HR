# Payroll Providers

**Module:** Payroll  
**Feature:** Payroll Providers

---

## Purpose

External payroll system connections.

## Database Tables

### `payroll_providers`
Fields: `name`, `provider_type` (`internal`, `adp`, `oracle`), `credentials_encrypted`, `is_active`.

### `payroll_connections`
Links provider to legal entity: `provider_id`, `legal_entity_id`, `config_json`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/payroll/providers` | `payroll:read` | List providers |

## Related

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/pensions/overview|Pensions]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
