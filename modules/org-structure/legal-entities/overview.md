# Company Registration Profile

**Module:** Org Structure  
**Feature:** Company Registration Profile

---

## Purpose

The company registration profile stores the current tenant's registration, country, currency, and address information. It is not a way to model multiple operating companies inside one tenant. Separate operating companies must be provisioned as separate tenants and linked through [[modules/shared-platform/company-connections/overview|Company Connections]] when cross-company workflows are needed.

When the company country is set, Calendar creates a Phase 1 holiday calendar setting that defaults to the company country. Calendar admins can later disable holiday sync or choose a different calendar country from the Calendar screen without changing the registration profile country.

## Database Tables

### `company_registration_profiles`
Fields: `name`, `registration_number`, `country_id`, `currency_code`, `address_json`, `is_active`.

`currency_code` is the company's ISO 4217 operating currency. It defaults from the selected country during provisioning, but operators can override it when the legal/commercial setup requires a different currency.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/company-profile` | `settings:admin` | Get current tenant registration profile |
| PUT | `/api/v1/company-profile` | `settings:admin` | Update current tenant registration profile |

## Calendar Integration

Updating the company country publishes `CompanyProfileCountrySet` with the tenant ID and selected country. The Calendar module consumes it to create or update `holiday_calendar_settings` and queue country holiday import.

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/org-structure/teams/overview|Teams]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
