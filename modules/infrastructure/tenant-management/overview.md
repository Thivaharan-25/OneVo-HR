# Tenant Management

**Module:** Infrastructure  
**Feature:** Tenant Management

---

## Purpose

Tenant provisioning and management. `industry_profile` sets monitoring defaults at signup.

## Database Tables

### `tenants`
Key columns: `name`, `slug` (UNIQUE), `industry_profile` (`office_it`, `manufacturing`, `retail`, `healthcare`, `custom`), `status` (`trial`, `active`, `suspended`, `cancelled`), `subscription_plan_id`, `settings_json`.

## Key Business Rules

1. Provisioning flow: Signup → seed default data (roles, permissions, monitoring toggles) → activate.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/tenants` | Public (signup) | Provision new tenant |
| GET | `/api/v1/tenants/current` | Authenticated | Get current tenant |
| PUT | `/api/v1/tenants/current` | `settings:admin` | Update tenant |

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]]
