# Grievance Cases

**Module:** Grievance  
**Feature:** Grievance Cases

---

## Purpose

Manages employee grievance cases with anonymous reporting, investigation tracking, and resolution workflows.

## Database Tables

### `grievance_cases`
Fields: `filed_by_id` (nullable if anonymous), `against_id`, `category` (`harassment`, `discrimination`, `safety`, `policy_violation`, `other`), `severity`, `status` (`filed`, `investigating`, `resolved`, `dismissed`, `escalated`), `resolution`, `is_anonymous`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/grievances` | `grievance:read` | List cases |
| POST | `/api/v1/grievances` | `grievance:write` | File grievance |
| PUT | `/api/v1/grievances/{id}` | `grievance:manage` | Update case |
| POST | `/api/v1/grievances/{id}/resolve` | `grievance:manage` | Resolve |

## Related

- [[modules/grievance/overview|Grievance Module]] — parent module
- [[modules/grievance/disciplinary-actions/overview|Disciplinary Actions]] — actions that may result from resolved cases
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped case isolation
- [[security/auth-architecture|Auth Architecture]] — permissions: `grievance:write`, `grievance:manage`
- [[security/data-classification|Data Classification]] — sensitive PII and anonymous reporting classification
- [[security/compliance|Compliance]] — regulatory requirements for grievance handling
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
