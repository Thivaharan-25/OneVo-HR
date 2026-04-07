# Module: Grievance

**Namespace:** `ONEVO.Modules.Grievance`
**Pillar:** Shared Foundation
**Owner:** Dev 2 (Week 4)
**Tables:** 2

---

## Purpose

Manages employee grievance cases and disciplinary actions. Supports anonymous reporting, investigation tracking, and resolution workflows.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[shared-platform]] | Workflow engine | Resolution approval |

---

## Database Tables (2)

### `grievance_cases`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `filed_by_id` | `uuid` | FK → employees (nullable if anonymous) |
| `against_id` | `uuid` | FK → employees (nullable) |
| `category` | `varchar(30)` | `harassment`, `discrimination`, `safety`, `policy_violation`, `other` |
| `description` | `text` | |
| `severity` | `varchar(20)` | `low`, `medium`, `high`, `critical` |
| `status` | `varchar(20)` | `filed`, `investigating`, `resolved`, `dismissed`, `escalated` |
| `resolution` | `text` | |
| `resolved_by_id` | `uuid` | FK → users |
| `resolved_at` | `timestamptz` | |
| `is_anonymous` | `boolean` | |
| `created_at` | `timestamptz` | |

### `disciplinary_actions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `grievance_id` | `uuid` | FK → grievance_cases (nullable) |
| `action_type` | `varchar(30)` | `verbal_warning`, `written_warning`, `suspension`, `termination` |
| `description` | `text` | |
| `effective_date` | `date` | |
| `issued_by_id` | `uuid` | FK → users |
| `acknowledged_at` | `timestamptz` | Employee acknowledgement |
| `created_at` | `timestamptz` | |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/grievances` | `grievance:read` | List cases |
| POST | `/api/v1/grievances` | `grievance:write` | File grievance |
| PUT | `/api/v1/grievances/{id}` | `grievance:manage` | Update case |
| POST | `/api/v1/grievances/{id}/resolve` | `grievance:manage` | Resolve |
| GET | `/api/v1/disciplinary/{employeeId}` | `grievance:read` | Disciplinary history |
| POST | `/api/v1/disciplinary` | `grievance:manage` | Issue disciplinary action |

## Features

- [[grievance-cases]] — Grievance filing, investigation tracking, anonymous reporting
- [[disciplinary-actions]] — Disciplinary actions linked optionally to grievance cases

---

## Related

- [[multi-tenancy]] — All cases and actions are tenant-scoped
- [[compliance]] — Case resolution and disciplinary history form a legal audit trail
- [[data-classification]] — Anonymous filings must not expose `filed_by_id`
- [[WEEK4-supporting-bridges]] — Implementation task file

See also: [[module-catalog]], [[core-hr]]
