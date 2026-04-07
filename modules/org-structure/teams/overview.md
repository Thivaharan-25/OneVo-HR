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

- [[org-structure|Org Structure Module]]
- [[departments]]
- [[legal-entities]]
- [[cost-centers]]
- [[job-hierarchy]]
- [[multi-tenancy]]
- [[authorization]]
- [[shared-kernel]]
- [[WEEK1-org-structure]]
