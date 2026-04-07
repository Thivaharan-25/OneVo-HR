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

- [[org-structure|Org Structure Module]]
- [[cost-centers]]
- [[legal-entities]]
- [[job-hierarchy]]
- [[teams]]
- [[multi-tenancy]]
- [[authorization]]
- [[shared-kernel]]
- [[migration-patterns]]
- [[WEEK1-org-structure]]
