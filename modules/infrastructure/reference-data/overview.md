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

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]]
