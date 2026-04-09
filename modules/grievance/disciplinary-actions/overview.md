# Disciplinary Actions

**Module:** Grievance  
**Feature:** Disciplinary Actions

---

## Purpose

Manages disciplinary actions linked to grievance cases.

## Database Tables

### `disciplinary_actions`
Fields: `employee_id`, `grievance_id` (nullable), `action_type` (`verbal_warning`, `written_warning`, `suspension`, `termination`), `description`, `effective_date`, `issued_by_id`, `acknowledged_at`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/disciplinary/{employeeId}` | `grievance:read` | History |
| POST | `/api/v1/disciplinary` | `grievance:manage` | Issue action |

## Related

- [[modules/grievance/overview|Grievance Module]] — parent module
- [[modules/grievance/grievance-cases/overview|Grievance Cases]] — cases that may trigger disciplinary actions
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped disciplinary records
- [[security/auth-architecture|Auth Architecture]] — permission: `grievance:manage`
- [[security/data-classification|Data Classification]] — sensitivity of disciplinary records
- [[security/compliance|Compliance]] — regulatory requirements for disciplinary procedures
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
