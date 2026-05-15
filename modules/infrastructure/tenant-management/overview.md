# Tenant Management

**Module:** Infrastructure  
**Feature:** Tenant Management

---

## Purpose

Operator-only tenant lifecycle management through Developer Platform. `industry_profile` sets monitoring defaults during operator provisioning. Country, registration/profile name, registration number, company size, timezone, and currency are tenant profile metadata.

## Database Tables

### `tenants`
Key columns: `name`, `slug` (UNIQUE), `primary_contact_email`, `country_code`, `industry_profile` (`office_it`, `manufacturing`, `retail`, `healthcare`, `custom`), `registration_profile_name`, `registration_number`, `company_size_range`, `timezone`, `currency_code`, `status` (`provisioning`, `trial`, `active`, `suspended`, `cancelled`), `subscription_plan_id`, `settings_json`.

## Key Business Rules

1. Tenant creation flow: Operator creates customer profile draft -> assigns commercial plan/payment terms in Step 2 -> uses the tenant card Manage/Configure action to confirm entitled modules, apply roles/templates/settings, configure required module setup services, optionally invite owner, and activate.
2. Tenant profile creation collects company/profile details, country, timezone, currency, and registration/profile data, but it does not create `legal_entities` records. Separate companies are separate tenants; the same owner email can accept invitations for more than one tenant without merging tenant data.

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
