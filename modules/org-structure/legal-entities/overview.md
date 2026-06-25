# Companies / Legal Entities

**Module:** Org Structure  
**Feature:** Company Setup  
**Phase:** 1

---

## Purpose

Companies are the user-facing operating records inside a tenant. Internally, Company records are stored in `legal_entities`. ONEVO Phase 1 supports both:

- Single-company tenant: one tenant with one Company.
- Multi-company tenant: one tenant with multiple Companies.

Company is the boundary for departments, positions, employee primary employment context, Time Off policy assignment, attendance policy assignment, and payroll/legal setup where enabled.

## Phase 1 Rules

- Departments belong to one Company.
- Positions belong to one Company.
- Positions cannot be shared across Companies.
- A position can report only to another position inside the same Company.
- Employee primary employment assignment belongs to one primary Company.
- Additional authority assignments may exist across Companies, but they do not change primary employment policy source.
- One employee cannot hold two active employment assignments inside the same Company; use transfer or promotion instead.
- Root positions with no reporting manager are allowed.

## Why Company Matters

Company affects departments, positions, onboarding, Time Off policy assignment, schedule / attendance policy assignment, import validation, reporting-line boundaries, and payroll/legal setup where enabled. It is not decorative. Internally this boundary maps to `legal_entity_id`.

## Database Table

### `legal_entities`

Key fields:

- `tenant_id`
- `parent_legal_entity_id`
- `name`
- `registration_number`
- `tax_identifier`
- `country_id`
- `currency_code`
- `address_json`
- `is_active`

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/legal-entities` | `org:read` | List Companies |
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create Company |
| PUT | `/api/v1/org/legal-entities/{id}` | `org:manage` | Update Company |

## Related

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/departments/overview|Departments]]
- [[Userflow/Org-Structure/legal-entity-setup|Company Setup]]
