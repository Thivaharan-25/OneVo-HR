# Departments

**Module:** Org Structure  
**Feature:** Departments

---

## Purpose

Hierarchical department structure via self-referencing `parent_department_id`. Handle recursive queries with CTEs.

Department management is Company-context first. The selected Company from the topbar is the user-facing operating boundary and maps internally to `legal_entity_id`.

## Database Tables

### `departments`

Fields: `legal_entity_id` (FK -> legal_entities; from selected Company), `name`, `code`, `parent_department_id` (self-referencing), `head_position_id`, `is_active`.

`name` is unique within the selected Company. `code` is a stable short identifier such as `ENG`, `HR`, or `FIN`; it is unique within the selected Company and used for imports, reports, integrations, payroll exports, and external references. Neither `name` nor `code` needs to be unique across the whole tenant; two Companies can each have an `Engineering` department.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/departments?view=tree\|flat` | `employees:read` | List departments for the selected Company (flat or tree) |
| POST | `/api/v1/org/departments` | `org:manage` | Create in selected Company |
| PUT | `/api/v1/org/departments/{id}` | `org:manage` | Update within selected Company |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/legal-entities/overview|Companies / Legal Entities]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
