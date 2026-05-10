# Legal Entities

**Module:** Org Structure  
**Feature:** Legal Entities

---

## Purpose

Company legal entities with registration, country, currency, and address information.

When a legal entity is created, Calendar creates a Phase 1 holiday calendar setting that defaults to the legal entity country. Calendar admins can later disable holiday sync or choose a different calendar country from the Calendar screen without changing the legal entity country.

## Database Tables

### `legal_entities`
Fields: `name`, `registration_number`, `country_id`, `currency_code`, `address_json`, `is_active`.

`currency_code` is the legal entity's ISO 4217 operating currency. It defaults from the selected country during provisioning or legal-entity creation, but operators can override it when the legal/commercial setup requires a different currency.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/legal-entities` | `settings:admin` | List |
| POST | `/api/v1/legal-entities` | `settings:admin` | Create |

## Calendar Integration

`POST /api/v1/legal-entities` publishes `LegalEntityCreated` with the selected country. The Calendar module consumes it to create `holiday_calendar_settings` and queue country holiday import.

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/org-structure/teams/overview|Teams]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
