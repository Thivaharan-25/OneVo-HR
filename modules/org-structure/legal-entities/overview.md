# Legal Entities

**Module:** Org Structure  
**Feature:** Legal Entities  
**Phase:** 1

---

## Purpose

Legal entities model the companies inside a tenant. ONEVO Phase 1 supports both:

- Single-company tenant: one tenant with one legal entity.
- Multi-company tenant: one tenant with multiple legal entities.

Legal entity is the boundary for departments, positions, employee primary employment context, leave policy assignment, attendance policy assignment, and payroll/legal setup where enabled.

## Phase 1 Rules

- Departments belong to one legal entity.
- Positions belong to one legal entity.
- Positions cannot be shared across legal entities.
- A position can report only to another position inside the same legal entity.
- Job titles can be shared across the tenant.
- A person can hold assignments in more than one legal entity when needed, but each assignment points to a legal-entity-specific position.
- Root positions with no reporting manager are allowed.

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
| GET | `/api/v1/org/legal-entities` | `org:read` | List legal entities |
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create legal entity |
| PUT | `/api/v1/org/legal-entities/{id}` | `org:manage` | Update legal entity |

## Related

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
