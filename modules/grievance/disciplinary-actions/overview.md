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

- [[grievance|Grievance Module]] — parent module
- [[grievance-cases]] — cases that may trigger disciplinary actions
- [[multi-tenancy]] — tenant-scoped disciplinary records
- [[auth-architecture]] — permission: `grievance:manage`
- [[data-classification]] — sensitivity of disciplinary records
- [[compliance]] — regulatory requirements for disciplinary procedures
- [[WEEK4-supporting-bridges]] — implementation task
