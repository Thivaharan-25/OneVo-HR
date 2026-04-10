# Module: Grievance

**Namespace:** `ONEVO.Modules.Grievance`
**Phase:** 2 — Deferred
**Pillar:** Shared Foundation
**Owner:** Dev 2 (Week 4)
**Tables:** 2

> [!WARNING]
> **This module is deferred to Phase 2. Do not implement.** Case tracking is not core to the employee monitoring product. Specs are preserved here for future reference.

---

## Purpose

Manages employee grievance cases and disciplinary actions. Supports anonymous reporting, investigation tracking, and resolution workflows.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[modules/shared-platform/overview\|Shared Platform]] | Workflow engine | Resolution approval |

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

- [[modules/grievance/grievance-cases/overview|Grievance Cases]] — Grievance filing, investigation tracking, anonymous reporting
- [[modules/grievance/disciplinary-actions/overview|Disciplinary Actions]] — Disciplinary actions linked optionally to grievance cases

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All cases and actions are tenant-scoped
- [[security/compliance|Compliance]] — Case resolution and disciplinary history form a legal audit trail
- [[security/data-classification|Data Classification]] — Anonymous filings must not expose `filed_by_id`
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]]
