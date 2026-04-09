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

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Audit Trail]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Pensions]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
