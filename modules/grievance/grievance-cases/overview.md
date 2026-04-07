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

- [[grievance|Grievance Module]] — parent module
- [[disciplinary-actions]] — actions that may result from resolved cases
- [[multi-tenancy]] — tenant-scoped case isolation
- [[auth-architecture]] — permissions: `grievance:write`, `grievance:manage`
- [[data-classification]] — sensitive PII and anonymous reporting classification
- [[compliance]] — regulatory requirements for grievance handling
- [[WEEK4-supporting-bridges]] — implementation task
