# Tenant Management

**Module:** Infrastructure  
**Feature:** Tenant Management

---

## Purpose

Operator-only tenant lifecycle management through Developer Platform. `industry_profile` sets monitoring defaults during operator provisioning. `company_size_range` is stored on the tenant as profile metadata.

## Database Tables

### `tenants`
Key columns: `name`, `slug` (UNIQUE), `industry_profile` (`office_it`, `manufacturing`, `retail`, `healthcare`, `custom`), `company_size_range`, `status` (`provisioning`, `trial`, `active`, `suspended`, `cancelled`), `subscription_plan_id`, `settings_json`.

## Key Business Rules

1. Provisioning flow: Operator creates provisioning draft -> assign plan/modules/settings/role templates -> invite owner -> activate.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/admin/v1/tenants` | Platform admin | Create draft tenant through Developer Platform |
| GET | `/api/v1/tenants/current` | Authenticated | Get current tenant |
| PUT | `/api/v1/tenants/current` | `settings:admin` | Update tenant-facing profile/settings only; full provisioning config is split across admin endpoints |

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
