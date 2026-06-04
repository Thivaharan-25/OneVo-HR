# Legal Entities

**Module:** Org Structure  
**Feature:** Legal Entity Setup

---

## Purpose

Legal entities are the company records inside a tenant. A single-company tenant has one legal entity. A multi-company tenant has multiple legal entities under the same tenant, such as a Sri Lankan company, UK company, and US company inside one group account.

Legal entities are first-class Phase 1 org-structure records. Departments and positions belong to one legal entity. Employees have one primary legal entity. Job titles can be shared across the tenant, but departments and positions cannot be shared across legal entities.

When a legal entity country is set, Calendar creates or updates the Phase 1 holiday calendar setting for that legal entity. Calendar admins can later disable holiday sync or choose a different calendar country from the Calendar screen without changing the legal entity registration country.

## Database Tables

### `legal_entities`
Fields: `name`, `registration_number`, `country_id`, `currency_code`, `tax_identifier`, `address_json`, `is_active`, `parent_legal_entity_id`.

`currency_code` is the legal entity's ISO 4217 operating currency. It defaults from the selected country during setup, but authorized admins can override it when the legal/commercial setup requires a different currency.

## Phase 1 Rules

- Single-company tenants get one default legal entity during setup.
- Multi-company tenants can create multiple legal entities under the same tenant.
- Departments belong to one legal entity.
- Positions belong to one legal entity.
- A position can report only to another position inside the same legal entity.
- Job titles can be shared across the tenant and selected by positions in different legal entities.
- The same person can hold assignments in more than one legal entity when needed, but each assignment still points to a legal-entity-specific position.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/legal-entities` | `org:manage` | List legal entities for the tenant |
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create a legal entity |
| PUT | `/api/v1/org/legal-entities/{id}` | `org:manage` | Update a legal entity |

## Calendar Integration

Updating a legal entity country publishes `LegalEntityCountrySet` with the tenant ID, legal entity ID, and selected country. The Calendar module consumes it to create or update legal-entity-scoped `holiday_calendar_settings` and queue country holiday import.

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/org-structure/teams/overview|Teams]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
