# Tenant Management

**Module:** Infrastructure  
**Feature:** Tenant Management

---

## Purpose

Operator-only tenant lifecycle management through Developer Platform. `industry_profile` sets monitoring defaults during operator provisioning. Country, registration/profile name, registration number, company size, timezone, and currency are tenant profile metadata.

## Database Tables

### `tenants`
Key columns: `name`, `slug` (UNIQUE), `primary_contact_email`, `country_code`, `industry_profile` (`office_it`, `manufacturing`, `retail`, `healthcare`, `custom`), `registration_profile_name`, `registration_number`, `company_size_range`, `timezone`, `currency_code`, `status` (`provisioning`, `trial`, `trial_expired`, `pending_payment`, `active`, `suspended`, `cancelled`), `subscription_plan_id`, `settings_json`.

Status meanings: `provisioning` = operator draft, `trial` = demo/trial tenant with active trial period, `trial_expired` = trial period ended without upgrade, `pending_payment` = first invoice generated and unpaid, `active` = tenant fully operational after successful first payment, `suspended` = temporarily disabled, `cancelled` = permanently deactivated.

## Key Business Rules

1. Tenant creation flow: Operator creates customer profile draft -> assigns commercial plan/payment terms in Step 2 -> uses the tenant card Manage/Configure action to select entitled modules, apply roles/templates/settings, configure required module setup services, optionally invite owner, and generate the first invoice. Tenants move to `pending_payment`; they become `active` only after first payment succeeds.
2. Tenant profile creation collects company/profile details, country, timezone, currency, and registration/profile data, but it does not create deprecated registration-profile records. Activation/setup seeding creates one primary legal entity. Additional operating companies under the same customer account are added as legal entities inside the tenant.

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
