# Departments

**Module:** Org Structure  
**Feature:** Departments

---

## Purpose

Hierarchical department structure via self-referencing `parent_department_id`. Handle recursive queries with CTEs.

## Database Tables

### `departments`
Fields: `legal_entity_id` (FK → legal_entities), `name`, `code`, `parent_department_id` (self-referencing), `head_position_id`, `is_active`.

`name` is unique within the legal entity. `code` is a stable short identifier such as `ENG`, `HR`, or `FIN`; it is unique within the legal entity and used for imports, reports, integrations, payroll exports, and external references. Neither `name` nor `code` needs to be unique across the whole tenant — two legal entities can each have an `Engineering` department.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/departments?legalEntityId={id}&view=tree\|flat` | `employees:read` | List departments for a legal entity (flat or tree) |
| POST | `/api/v1/org/departments` | `org:manage` | Create |
| PUT | `/api/v1/org/departments/{id}` | `org:manage` | Update |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/org-structure/teams/overview|Teams]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]


