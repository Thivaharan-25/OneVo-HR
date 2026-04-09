# Teams

**Module:** Org Structure  
**Feature:** Teams

---

## Purpose

Teams within departments with team leads and member tracking.

## Database Tables

### `teams`
Fields: `name`, `department_id`, `team_lead_id`, `is_active`.

### `team_members`
Join table: `team_id`, `employee_id`, `joined_at`. PK: `(team_id, employee_id)`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/teams` | `employees:read` | List teams |
| POST | `/api/v1/teams` | `settings:admin` | Create team |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
