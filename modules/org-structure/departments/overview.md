# Departments

**Module:** Org Structure  
**Feature:** Departments

---

## Purpose

Hierarchical department structure via self-referencing `parent_department_id`. Handle recursive queries with CTEs.

## Database Tables

### `departments`
Fields: `name`, `code`, `parent_department_id` (self-referencing), `head_employee_id`, `legal_entity_id`, `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/departments` | `employees:read` | List (flat or tree) |
| POST | `/api/v1/departments` | `settings:admin` | Create |
| PUT | `/api/v1/departments/{id}` | `settings:admin` | Update |

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
