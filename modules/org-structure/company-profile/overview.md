# Companies

**Module:** Org Structure  
**Feature:** Company Setup

---

## Purpose

Companies are the operating records inside a tenant. Internally, Company records are stored in `legal_entities`. A single-company tenant has one Company. A multi-company tenant has multiple Companies under the same tenant, such as a Sri Lankan company, UK company, and US company inside one group account.

Companies are first-class Phase 1 org-structure records. Departments and positions belong to one Company. Employees have one primary Company. Departments and positions cannot be shared across Companies.

When a Company country is set, Calendar creates or updates the Phase 1 holiday calendar setting for that Company for Calendar display purposes. Calendar admins can later disable holiday sync or choose a different Calendar display country from the Calendar screen without changing the Company registration country. This Calendar holiday setting is separate from work schedule holiday country, which is configured per-schedule in Time & Attendance > Schedules. Neither Calendar holiday settings nor schedule holiday country affect the Company timezone (`legal_entities.timezone`).

## Database Tables

### `legal_entities`
Fields: `name`, `registration_number`, `country_id`, `currency_code`, `tax_identifier`, `address_json`, `is_active`, `parent_legal_entity_id`.

`currency_code` is the Company's ISO 4217 operating currency. It defaults from the selected country during setup, but authorized admins can override it when the legal/commercial setup requires a different currency.

## Phase 1 Rules

- Single-company tenants get one default Company during setup.
- Multi-company tenants can create multiple Companies under the same tenant.
- Departments belong to one Company.
- Positions belong to one Company.
- A position can report only to another position inside the same Company.
- The same person can hold assignments in more than one Company when needed, but each assignment still points to a Company-specific position.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/legal-entities` | `org:manage` | List Companies for the tenant |
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create a Company |
| PUT | `/api/v1/org/legal-entities/{id}` | `org:manage` | Update a Company |

## Calendar Integration

Updating a Company country publishes `LegalEntityCountrySet` with the tenant ID, internal legal entity ID, and selected country. The Calendar module consumes it to create or update Company-scoped `holiday_calendar_settings` for Calendar display and queue country holiday import. This does not affect work schedule holiday country (per-schedule in Time & Attendance) or the Company timezone.

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
