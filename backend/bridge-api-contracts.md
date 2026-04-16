# Bridge API Contracts — WorkManage Pro ↔ ONEVO

**Purpose:** Canonical request/response schemas for all 5 WorkManage Pro bridge endpoints. This is the contract the WMS team builds against.

## Authentication

WorkManage Pro authenticates using **OAuth 2.0 Client Credentials** — not a static API key.

### Registration
Super Admin registers WorkManage Pro in ONEVO Settings → Integrations. ONEVO generates a `client_id` (UUID) and `client_secret` (48-byte base64, shown once, stored only as Argon2id hash).

### Step 1 — Get a Token
```
POST /api/v1/auth/bridge/token   (public — no auth header)
Content-Type: application/json

{
  "client_id": "uuid",
  "client_secret": "...",
  "tenant_id": "uuid"
}
```

Response:
```json
{ "access_token": "jwt", "token_type": "Bearer", "expires_in": 3600 }
```

Tokens expire after 1 hour. Request a new one when it expires (no refresh token — just re-authenticate).

### Step 2 — Call Bridge Endpoints
```
Authorization: Bearer <bridge_jwt>
Content-Type: application/json
```

The bridge JWT carries:
- `aud: "onevo-bridge"` — distinct from user tokens (`aud: "onevo-api"`)
- `type: "bridge"` — bridge middleware checks this claim
- `bridges: ["people-sync", "availability"]` — scoped to allowed bridges for this client
- `tenant_id: "uuid"` — tenant context set automatically by middleware

### Validation Rules
| Case | Response |
|:-----|:---------|
| User JWT sent to bridge endpoint | `403` — wrong audience |
| Bridge JWT for wrong bridge name | `403` — not in `bridges` claim |
| Expired token | `401` |
| Missing token | `401` |

---

## Bridge 1 — People Sync (HR → WMS)

**Direction:** WMS polls ONEVO
**Endpoint:** `GET /api/v1/bridges/people-sync/employees`
**Phase:** 1

### Query Parameters

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `updatedSince` | `ISO8601 datetime` | No | Return only employees modified after this timestamp. Omit for full sync. |
| `page` | `int` | No | Page number (1-based). Default: 1 |
| `pageSize` | `int` | No | Items per page. Max: 100. Default: 50 |

### Response `200 OK`

```json
{
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "full_name": "Amara Nwosu",
      "email": "amara.nwosu@company.com",
      "status": "active",
      "department_id": "uuid-of-department",
      "department_name": "Engineering",
      "team": "Backend",
      "job_title": "Senior Software Engineer",
      "job_family": "Engineering",
      "role_name": "Team Lead",
      "wms_role_identifier": "team_lead",
      "direct_manager_id": "uuid-of-manager",
      "is_department_head": false,
      "hire_date": "2023-03-15",
      "last_modified_at": "2026-04-14T09:22:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 128,
    "has_next": true,
    "next_cursor": "2026-04-14T09:22:00Z"
  }
}
```

### `status` values

| Value | Meaning |
|:------|:--------|
| `active` | Employed, full access |
| `on_leave` | Currently on approved leave |
| `suspended` | Access suspended (admin action) |
| `deactivated` | Terminated — WMS must revoke access |

### `wms_role_identifier` values

Sourced from `wms_role_mappings` table. Configured by tenant admin. Examples:

| Value | Typical ONEVO Role |
|:------|:-----------------|
| `admin` | HR Admin / IT Admin |
| `manager` | Department Manager / Team Lead |
| `employee` | Standard Employee |
| `contractor` | Contractor |

> If no WMS role mapping is configured for a role, `wms_role_identifier` is `null`. WMS should default to `employee` in this case.

### `department_id` / `department_name`

`department_id` is a stable UUID — use this as the grouping key in WMS, not `department_name`. The name can change in ONEVO (e.g. "Engineering" → "Technology"); the UUID never changes.

### `is_department_head`

`true` when this employee is the designated head of their department (sourced from `departments.head_employee_id`). WMS uses this to scope department-level views:

- Department head sees all employees where `direct_manager_id` chains back to their own `id`, across any depth
- Department head sees all WMS projects assigned to those employees
- Only one employee per department will have `is_department_head: true` at any time

### Error responses

| Status | Code | When |
|:-------|:-----|:-----|
| `401` | `BRIDGE_KEY_INVALID` | Key missing or revoked |
| `403` | `BRIDGE_SCOPE_INSUFFICIENT` | Key lacks `bridges:read` scope |
| `429` | `RATE_LIMIT_EXCEEDED` | >100 requests/minute |

### Delta sync pattern

WMS should store the `last_modified_at` of the most recent employee received, then call `?updatedSince=<stored_timestamp>` on subsequent syncs. ONEVO returns only records modified after that timestamp. For initial full sync, omit `updatedSince`.

---

## Bridge 2 — Availability (HR → WMS)

**Direction:** WMS polls ONEVO
**Endpoint:** `GET /api/v1/bridges/availability/{employeeId}`
**Phase:** 1

### Path Parameters

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `employeeId` | `uuid` | ONEVO employee ID |

### Query Parameters

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `from` | `date (YYYY-MM-DD)` | No | Start of leave period range. Default: today |
| `to` | `date (YYYY-MM-DD)` | No | End of leave period range. Default: today + 90 days |

### Response `200 OK`

```json
{
  "employee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "as_of": "2026-04-15T10:00:00Z",
  "presence_status": "present",
  "clock_in_at": "2026-04-15T09:06:00Z",
  "clock_out_at": null,
  "shift": {
    "start": "09:00",
    "end": "17:30",
    "expected_daily_hours": 8.0,
    "timezone": "Asia/Kuala_Lumpur"
  },
  "leave_periods": [
    {
      "leave_type": "Annual Leave",
      "start_date": "2026-04-28",
      "end_date": "2026-04-30",
      "total_days": 3,
      "status": "approved"
    }
  ],
  "public_holidays": [
    {
      "date": "2026-05-01",
      "name": "Labour Day"
    },
    {
      "date": "2026-05-25",
      "name": "Wesak Day"
    }
  ]
}
```

### `clock_in_at` / `clock_out_at`

| Field | Value when |
|:------|:-----------|
| `clock_in_at` | Populated once employee clocks in today. `null` before clock-in or on non-working days. |
| `clock_out_at` | Populated once employee clocks out. `null` while still clocked in, or if employee hasn't clocked in. |

Both fields are sourced from ONEVO's Workforce Presence module (`presence_sessions` table). WMS should use these for "clock-in / clock-out markers" in its calendar view.

### `presence_status` values

| Value | Meaning |
|:------|:--------|
| `present` | Checked in / active today |
| `absent` | Marked absent (no check-in, no approved leave) |
| `on_leave` | On approved leave today |
| `holiday` | Public holiday for employee's location |
| `weekend` | Outside working days per shift schedule |
| `unknown` | No data yet for today (before shift start) |

> `leave_periods` contains only `approved` leave requests. Pending or rejected requests are not included.

### Error responses

| Status | Code | When |
|:-------|:-----|:-----|
| `404` | `EMPLOYEE_NOT_FOUND` | ID not found in this tenant |
| `404` | `NO_SHIFT_CONFIGURED` | Employee has no shift schedule assigned |

---

## Bridge 3 — Work Activity (WMS → HR)

**Direction:** WMS pushes to ONEVO
**Endpoint:** `POST /api/v1/bridges/work-activity/time-logs`
**Phase:** 1

### Request Body

```json
{
  "submitted_at": "2026-04-15T23:55:00Z",
  "logs": [
    {
      "employee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "task_id": "TASK-1042",
      "project_id": "PROJ-88",
      "date": "2026-04-15",
      "logged_minutes": 120,
      "active_task_at": "2026-04-15T14:30:00Z"
    },
    {
      "employee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "task_id": "TASK-1051",
      "project_id": "PROJ-88",
      "date": "2026-04-15",
      "logged_minutes": 45,
      "active_task_at": null
    }
  ]
}
```

### Request fields

| Field | Type | Required | Notes |
|:------|:-----|:---------|:------|
| `submitted_at` | `ISO8601 datetime` | Yes | WMS batch submission timestamp |
| `logs[].employee_id` | `uuid` | Yes | Must exist in ONEVO for this tenant |
| `logs[].task_id` | `string` | Yes | WMS task identifier (opaque to ONEVO) |
| `logs[].project_id` | `string` | Yes | WMS project identifier (opaque to ONEVO) |
| `logs[].date` | `date (YYYY-MM-DD)` | Yes | Work date |
| `logs[].logged_minutes` | `int` | Yes | Minutes logged on this task/date. Must be > 0 |
| `logs[].active_task_at` | `ISO8601 datetime` | No | Timestamp of most recent activity on this task |

### Batch limits

- Max 500 log entries per request
- Multiple entries for the same `employee_id` + `date` are **summed** into `wms_daily_time_logs.total_logged_minutes`
- `active_task_at` stored as the latest value across all logs for same `employee_id` + `date`

### Response `202 Accepted`

```json
{
  "accepted": 2,
  "rejected": 0,
  "rejected_entries": []
}
```

If some entries fail validation:

```json
{
  "accepted": 1,
  "rejected": 1,
  "rejected_entries": [
    {
      "index": 1,
      "employee_id": "unknown-uuid",
      "reason": "EMPLOYEE_NOT_FOUND"
    }
  ]
}
```

### Idempotency

Re-submitting logs for the same `employee_id` + `date` **overwrites** (upsert) the existing `wms_daily_time_logs` row. WMS can safely resend a full day's data without duplicating. Include all logs for the day in each submission.

### How ONEVO uses this data

The **Discrepancy Engine** reads `wms_daily_time_logs.total_logged_minutes` each night and compares it with:
1. Agent-reported active minutes (`activity_daily_summary.active_minutes`)
2. Calendar events booked for that day

If no WMS data exists for a day, `wms_logged_minutes = 0` and only the calendar cross-reference is used.

---

## Bridge 4 — Productivity Metrics (WMS → HR)

**Direction:** WMS pushes to ONEVO
**Endpoint:** `POST /api/v1/bridges/productivity-metrics/snapshots`
**Phase:** 2

### Request Body

```json
{
  "employee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "period_type": "monthly",
  "period_start": "2026-04-01",
  "period_end": "2026-04-30",
  "tasks_completed": 24,
  "tasks_on_time": 20,
  "on_time_delivery_rate": 83.33,
  "productivity_score": 78.5,
  "active_projects_count": 3,
  "velocity_story_points": 42
}
```

### Request fields

| Field | Type | Required | Notes |
|:------|:-----|:---------|:------|
| `employee_id` | `uuid` | Yes | Must exist in ONEVO for this tenant |
| `period_type` | `string` | Yes | `daily`, `weekly`, `monthly` |
| `period_start` | `date (YYYY-MM-DD)` | Yes | First day of period |
| `period_end` | `date (YYYY-MM-DD)` | Yes | Last day of period |
| `tasks_completed` | `int` | Yes | Total tasks completed. Must be ≥ 0 |
| `tasks_on_time` | `int` | Yes | Tasks completed by deadline. Must be ≤ `tasks_completed` |
| `on_time_delivery_rate` | `decimal` | Yes | `(tasks_on_time / tasks_completed) * 100`. 0 if no tasks. |
| `productivity_score` | `decimal` | Yes | WMS composite score 0.00–100.00 |
| `active_projects_count` | `int` | Yes | Projects employee was active in during this period |
| `velocity_story_points` | `int` | No | Story points completed. Null if WMS doesn't use story points. |

### Response `202 Accepted`

```json
{
  "snapshot_id": "uuid",
  "employee_id": "uuid",
  "period_type": "monthly",
  "period_start": "2026-04-01",
  "stored_at": "2026-04-30T23:59:00Z"
}
```

### Idempotency

Re-submitting a snapshot for the same `employee_id` + `period_type` + `period_start` **overwrites** the existing record. WMS can safely correct a previously submitted snapshot.

### How ONEVO uses this data

- `GetProductivityScoreAsync()` combines this score with agent-based activity score when the Performance module creates a review
- Visible only to users with `analytics:view` (managers, HR admin) — never directly exposed to the employee
- Stored in `wms_productivity_snapshots` in the Productivity Analytics module

### Heatmap data ownership

Both ONEVO and WMS can display employee activity heatmaps. They measure different things and are both correct:

| Heatmap | Where shown | What it measures |
|:--------|:-----------|:----------------|
| **ONEVO Activity Heatmap** | ONEVO Workforce Intelligence dashboard | Keyboard/mouse activity, app usage — from WorkPulse Agent |
| **WMS Task Heatmap** | WMS Performance Monitoring | Task updates, work logged, project activity — from WMS task data |

A manager may see different numbers between the two (e.g., ONEVO shows 7hrs active, WMS shows 5hrs on tasks). Both are correct — the gap is time spent on non-task work (emails, meetings, reading docs). Product documentation and manager onboarding materials should explain this distinction to avoid confusion.

---

## Bridge 5a — Skills Read (ONEVO → WMS)

**Direction:** WMS polls ONEVO
**Endpoint:** `GET /api/v1/bridges/skills/{employeeId}`
**Phase:** 2

### Response `200 OK`

```json
{
  "employee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "skills": [
    {
      "skill_id": "uuid",
      "skill_name": "React",
      "category": "Frontend Development",
      "proficiency_level": 3,
      "proficiency_label": "Proficient",
      "status": "validated",
      "source": "manager_validated",
      "last_validated_at": "2026-03-10T00:00:00Z"
    },
    {
      "skill_id": "uuid",
      "skill_name": "TypeScript",
      "category": "Frontend Development",
      "proficiency_level": 2,
      "proficiency_label": "Developing",
      "status": "pending",
      "source": "self_declared",
      "last_validated_at": null
    }
  ]
}
```

### `proficiency_level` scale

| Level | Label |
|:------|:------|
| 1 | Beginner |
| 2 | Developing |
| 3 | Proficient |
| 4 | Advanced |
| 5 | Expert |

### `status` values

| Value | Meaning |
|:------|:--------|
| `validated` | Confirmed by manager or assessment |
| `pending` | Self-declared, awaiting validation |
| `expired` | Previously validated, now expired |

### `source` values

| Value | Meaning |
|:------|:--------|
| `self_declared` | Employee added this skill |
| `manager_validated` | Manager confirmed |
| `wms_observed` | WMS flagged a gap (may indicate skill weaker than declared) |
| `assessment_result` | Phase 2 — formal assessment result |

> WMS should use `status: "validated"` skills for task assignment matching. Skills with `status: "pending"` or `source: "wms_observed"` should be treated as unconfirmed.

---

## Bridge 5b — Skill Gap Report (WMS → ONEVO)

**Direction:** WMS pushes to ONEVO
**Endpoint:** `POST /api/v1/bridges/skills/{employeeId}/gap-report`
**Phase:** 2

### Request Body

```json
{
  "skill_id": "uuid",
  "observed_at": "2026-04-15",
  "task_ids": ["TASK-1042", "TASK-1051", "TASK-1063"],
  "note": "Employee completed 3 tasks tagged React but had repeated issues — submitted PRs required major revision each time"
}
```

### Request fields

| Field | Type | Required | Notes |
|:------|:-----|:---------|:------|
| `skill_id` | `uuid` | Yes | Must match a skill in ONEVO's `skills` table |
| `observed_at` | `date` | Yes | When the gap was observed |
| `task_ids` | `string[]` | Yes | WMS task IDs providing evidence. Min 1, max 20. |
| `note` | `string` | Yes | Human-readable explanation. Max 500 chars. |

### Response `201 Created`

```json
{
  "validation_request_id": "uuid",
  "employee_id": "uuid",
  "skill_id": "uuid",
  "skill_name": "React",
  "status": "pending_review",
  "assigned_to_manager_id": "uuid"
}
```

### What happens in ONEVO

1. `employee_skills` row for this skill is updated: `source = "wms_observed"`, `status = "pending"`
2. A `skill_validation_requests` entry is created, flagging the gap for manager review
3. The Skills dashboard surfaces this item at the top with a "WMS gap flag" indicator
4. Manager sees: **"WorkManage Pro flagged a skill gap in React — 3 tasks indicate repeated issues"**
5. Manager can approve (downgrade proficiency), reject (keep current), or request more evidence

### Error responses

| Status | Code | When |
|:-------|:-----|:-----|
| `404` | `SKILL_NOT_FOUND` | `skill_id` does not exist for this tenant |
| `409` | `GAP_ALREADY_PENDING` | An unresolved gap report already exists for this employee + skill |

---

## Rate Limits

All bridge endpoints share the following limits per tenant per bridge key:

| Limit | Value |
|:------|:------|
| Requests per minute | 100 |
| Requests per hour | 2,000 |
| Max batch size (Work Activity) | 500 entries |
| Max batch size (Productivity Metrics) | 1 snapshot per request |

Rate limit headers returned on every response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1744757400
```

---

## Common Error Format (RFC 7807)

All errors follow Problem Details:

```json
{
  "type": "https://api.onevo.com/errors/bridge-key-invalid",
  "title": "Bridge Key Invalid",
  "status": 401,
  "detail": "The provided bridge key has been revoked or does not exist.",
  "traceId": "00-abc123-def456-00"
}
```

---

## Versioning

All bridge endpoints are versioned under `/api/v1/`. Breaking changes will be released under `/api/v2/` with at least 90 days overlap. ONEVO will notify the WMS team via email when a deprecation is scheduled.

---

## Related

- [[backend/external-integrations|External Integrations]] — Bridge endpoint registry (summary table)
- [[current-focus/WMS-bridge-integration|WMS Bridge Integration]] — Implementation task plan
- [[modules/shared-platform/wms-tenant-provisioning|WMS Tenant Provisioning]] — How bridge keys are created
- [[database/schemas/activity-monitoring|Activity Monitoring Schema]] — `wms_daily_time_logs` table
- [[database/schemas/productivity-analytics|Productivity Analytics Schema]] — `wms_productivity_snapshots` table
- [[modules/skills/overview|Skills Module]] — `employee_skills.source` column + `skill_validation_requests`
- [[docs/phase-compatibility-guide|Phase Compatibility Guide]] — Phase 1→2 transition safety
