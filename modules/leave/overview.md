# Module: Leave

**Namespace:** `ONEVO.Modules.Leave`
**Phase:** 1 — Build
**Pillar:** 1 — HR Management
**Owner:** Dev 1 (Week 3)
**Tables:** 5
**Task File:** [[current-focus/DEV1-leave|DEV1: Leave]]

---

## Purpose

Manages leave types, country/level-specific policies with versioning, entitlement calculation, and request/approval workflows. Integrates with [[modules/shared-platform/overview|Shared Platform]] workflow engine for approval routing.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview|Core Hr]] | `IEmployeeService` | Employee context, hire date for entitlement |
| **Depends on** | [[modules/org-structure/overview|Org Structure]] | `IOrgStructureService` | Job level/country for policy matching |
| **Depends on** | [[modules/shared-platform/overview|Shared Platform]] | Workflow engine | Approval routing |
| **Depends on** | [[modules/calendar/overview|Calendar]] | `ICalendarConflictService` | Check calendar conflicts during leave submission |
| **Consumed by** | [[modules/payroll/overview|Payroll]] | `ILeaveService` | Leave days for payroll deductions |
| **Consumed by** | [[modules/workforce-presence/overview|Workforce Presence]] | `ILeaveService` | Mark presence status as `on_leave` |

---

## Public Interface

```csharp
public interface ILeaveService
{
    Task<Result<LeaveEntitlementDto>> GetEntitlementAsync(Guid employeeId, Guid leaveTypeId, int year, CancellationToken ct);
    Task<Result<LeaveRequestDto>> SubmitRequestAsync(CreateLeaveRequestCommand command, CancellationToken ct);
    Task<Result<LeaveRequestDto>> ApproveAsync(Guid requestId, CancellationToken ct);
    Task<Result<List<LeaveRequestDto>>> GetByEmployeeAsync(Guid employeeId, int year, CancellationToken ct);
    Task<Result<decimal>> GetUsedDaysAsync(Guid employeeId, Guid leaveTypeId, int year, CancellationToken ct);
}
```

---

## Database Tables (5)

### `leave_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "Annual", "Sick", "Maternity" |
| `is_paid` | `boolean` | |
| `requires_approval` | `boolean` | |
| `requires_document` | `boolean` | Medical certificate etc. |
| `max_consecutive_days` | `int` | Nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `leave_policies`

Country/level-specific with versioning via `superseded_by_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `leave_type_id` | `uuid` | FK → leave_types |
| `country_id` | `uuid` | FK → countries (nullable — global) |
| `job_level_id` | `uuid` | FK → job_levels (nullable — all levels) |
| `annual_entitlement_days` | `decimal(5,1)` | |
| `carry_forward_max_days` | `decimal(5,1)` | |
| `carry_forward_expiry_months` | `int` | |
| `accrual_method` | `varchar(20)` | `annual`, `monthly`, `daily` |
| `proration_method` | `varchar(20)` | `calendar_days`, `working_days` |
| `superseded_by_id` | `uuid` | Self-referencing — versioning chain |
| `effective_from` | `date` | |
| `created_at` | `timestamptz` | |

**To find active policy:** `WHERE superseded_by_id IS NULL` for the given leave type + country + job level.

### `leave_entitlements`

Calculated entitlement per employee per year.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `year` | `int` | |
| `total_days` | `decimal(5,1)` | Based on policy + proration |
| `used_days` | `decimal(5,1)` | Updated on approval |
| `carried_forward_days` | `decimal(5,1)` | From previous year |
| `remaining_days` | `decimal(5,1)` | Computed |

### `leave_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `total_days` | `decimal(5,1)` | Excluding weekends/holidays |
| `reason` | `text` | |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `approved_by_id` | `uuid` | FK → users |
| `approved_at` | `timestamptz` | |
| `conflict_snapshot_json` | `jsonb` | Calendar conflicts at submission time (nullable) — see [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]] |
| `document_file_id` | `uuid` | FK → file_records (nullable) |
| `created_at` | `timestamptz` | |

### `leave_balances_audit`

Audit trail for balance changes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `change_type` | `varchar(20)` | `accrual`, `deduction`, `carry_forward`, `forfeiture`, `adjustment` |
| `days_changed` | `decimal(5,1)` | Positive or negative |
| `balance_after` | `decimal(5,1)` | |
| `reason` | `varchar(255)` | |
| `created_at` | `timestamptz` | |

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `LeaveRequested` | Employee submits request | [[modules/notifications/overview|Notifications]] (notify manager) |
| `LeaveApproved` | Manager approves | [[modules/notifications/overview|Notifications]], [[modules/workforce-presence/overview|Workforce Presence]] (update status) |
| `LeaveRejected` | Manager rejects | [[modules/notifications/overview|Notifications]] |
| `LeaveCancelled` | Employee/manager cancels | [[modules/notifications/overview|Notifications]], entitlement adjustment |

---

## Key Business Rules

1. **Leave policy versioning** — `leave_policies` has a `superseded_by_id` column forming a chain. Active policy: `WHERE superseded_by_id IS NULL` for the given leave type + country + job level.
2. **Request validation** — checks sufficient balance, no overlapping requests, max consecutive days.
3. **Calendar conflict detection** — on submission, `ICalendarConflictService.GetConflictsForDateRangeAsync()` checks for overlapping calendar events (meetings, reviews, team events). Conflicts are **warnings only** — they do not block submission or approval. The conflict snapshot is stored as `conflict_snapshot_json` on the leave request so the approving manager can see what the employee saw at submission time. The manager also sees a live re-check for any events added after submission. See [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]].

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/leave/types` | `leave:read` | List leave types |
| POST | `/api/v1/leave/types` | `leave:manage` | Create leave type |
| GET | `/api/v1/leave/policies` | `leave:manage` | List policies |
| POST | `/api/v1/leave/policies` | `leave:manage` | Create policy |
| GET | `/api/v1/leave/entitlements/{employeeId}` | `leave:read` | Get entitlements |
| POST | `/api/v1/leave/requests` | `leave:create` | Submit request |
| PUT | `/api/v1/leave/requests/{id}/approve` | `leave:approve` | Approve |
| PUT | `/api/v1/leave/requests/{id}/reject` | `leave:approve` | Reject |
| GET | `/api/v1/leave/requests/me` | `leave:read-own` | Own requests |
| GET | `/api/v1/leave/calendar` | `leave:read` | Team leave calendar |

## Features

- [[modules/leave/leave-types/overview|Leave Types]] — Leave type definitions (paid/unpaid, document requirements)
- [[modules/leave/leave-policies/overview|Leave Policies]] — Country/job-level policies with versioning (`superseded_by_id`)
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — Calculated entitlement per employee per year
- [[modules/leave/leave-requests/overview|Leave Requests]] — Request submission, approval, rejection workflow — frontend: [[modules/leave/leave-requests/frontend|Frontend]]
- [[modules/leave/balance-audit/overview|Balance Audit]] — Immutable audit trail for all balance changes

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All leave data is tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`
- [[backend/messaging/error-handling|Error Handling]] — Calendar conflicts are warnings only; never block submission
- [[security/compliance|Compliance]] — Leave balance audit trail for legal record-keeping
- [[database/migration-patterns|Migration Patterns]] — Policy versioning via `superseded_by_id` self-referencing chain
- [[current-focus/DEV1-leave|DEV1: Leave]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/payroll/overview|Payroll]], [[modules/workforce-presence/overview|Workforce Presence]]
