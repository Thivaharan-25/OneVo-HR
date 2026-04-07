# Reference Data

**Module:** Infrastructure  
**Feature:** Reference Data

---

## Purpose

Global reference data (not tenant-scoped).

## Database Tables

### `countries`
Fields: `name`, `code` (ISO 3166-1 alpha-3), `phone_code`, `currency_code`.

**No `tenant_id`** — global reference data.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/countries` | Authenticated | List countries |

## Related

- [[infrastructure|Infrastructure Module]]
- [[file-management]]
- [[tenant-management]]
- [[user-management]]
- [[shared-kernel]]
- [[migration-patterns]]
- [[WEEK1-infrastructure-setup]]
