# OKR & Goals

**Module:** WorkSync
**Feature:** OKR & Goals
**Namespace:** `WorkSync.OKR`
**Owner:** DEV5
**Tables:** 3

---

## Purpose

OKR (Objectives and Key Results) provides goal-setting and tracking at workspace level. Objectives define the goal; key results define measurable outcomes. Check-ins are periodic progress updates to key results.

---

## Database Tables

### `objectives`
Key columns: `workspace_id`, `tenant_id`, `title`, `description`, `owner_id`, `status` (`on_track`, `at_risk`, `off_track`, `completed`, `cancelled`), `start_date`, `end_date`, `progress` (computed: avg of key_results progress), `quarter` (e.g. `2026-Q2`), `parent_objective_id` (nullable — nested objectives).

### `key_results`
Key columns: `objective_id`, `workspace_id`, `title`, `owner_id`, `result_type` (`percentage`, `numeric`, `currency`, `boolean`), `start_value`, `target_value`, `current_value`, `unit`, `status`, `progress` (computed: `(current_value - start_value) / (target_value - start_value) * 100`).

### `okr_check_ins`
Time-series progress updates. Key columns: `key_result_id`, `previous_value`, `new_value`, `note`, `created_by_id`, `created_at`.

Each check-in updates `key_results.current_value` and recalculates `objectives.progress`.

---

## Key Business Rules

1. OKRs are workspace-scoped — not tenant-scoped directly.
2. OKR progress cascades: key_results progress updates → objective `progress` field recalculated.
3. Check-ins are the only way to update `key_results.current_value` — never update directly.
4. `result_type = boolean`: current_value is 0 (false) or 1 (true), target_value is always 1.
5. Quarter field is free-form string — no DB constraint, but convention is `YYYY-Qn`.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `OKRCheckInAddedEvent` | Check-in created | Recalculate objective progress |
| `ObjectiveCompletedEvent` | Objective status → completed | Notifications |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/objectives` | `okr:read` | List objectives |
| POST | `/api/v1/workspaces/{wsId}/objectives` | `okr:write` | Create objective |
| GET | `/api/v1/objectives/{id}` | `okr:read` | Get objective + key results |
| PATCH | `/api/v1/objectives/{id}` | `okr:write` | Update objective |
| POST | `/api/v1/objectives/{id}/key-results` | `okr:write` | Add key result |
| POST | `/api/v1/key-results/{id}/check-ins` | `okr:write` | Add check-in |

---

## Related

- [[modules/work-management/foundation/overview|Foundation]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]] — objectives/key_results/okr_check_ins in OKR section
- [[Userflow/Work-Management/goals-okr-flow.md|OKR User Flow]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 3]]
