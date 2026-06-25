# Module: Time Off

**Feature Folder:** `Application/Features/TimeOff`
**Phase:** 1 - Build
**Pillar:** 1 - HR Management
**Owner:** Dev 1
**Canonical balance unit:** minutes

---

## Purpose

Manages time off types, policy rules and assignment scope, employee-level entitlements, and request/approval records. Phase 1 approval routing uses Org Structure management coverage and Notifications. Workflow Engine approval routing is Phase 2.

Time Off has two user contexts in the merged customer-facing app:

- **Self-service Time Off** for any active employee, including managers requesting their own time off.
- **Management/configuration** for authorized users managing time off types, policies, entitlements, requests, and employee time off visibility.

Self-service Time Off is a personal employee function. Managed team/org Time Off visibility is a permission-based management function.

Time Off management is Company-context first. The selected Company in the topbar is the operating context for policies, schedules, departments, positions, and permission checks. Billing remains tenant-level and is outside this Company-context rule.

---

## Canonical Unit Model

Time Off is stored and calculated in **minutes** (integer).

The system does not use shift length to calculate Time Off balance or request duration in Phase 1.

Users request Time Off by entering a duration in hours/minutes, or by selecting a start/end date and time. The system converts the requested duration to minutes and stores `request_duration_minutes`.

Full-day and half-day are not canonical request modes in Phase 1. If they appear later, they are UI shortcuts only and must convert to explicit minutes before saving.

Admin enters policy entitlement in hours and minutes. The system stores the canonical value in minutes. The UI displays balances as hours and minutes (e.g., "16h 30m available"). An optional approximate day helper may be shown in the UI for readability, but it is never used for calculation or storage.

Approved Time Off stores the actual `deduction_minutes` at approval time. Later schedule changes do not automatically recalculate past approved deductions unless an authorized admin explicitly recalculates and audits the change.

Schedule does **not** own Time Off balance. Schedule decides expected work times, workdays, break duration, work mode, and whether the employee is late. Time Off decides entitlement balance, request balance, deductions, carry forward, and audit history. Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off balance or request duration in Phase 1.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview|Core HR]] | `IEmployeeService` | Employee context, hire date, Company, assignment scope |
| **Depends on** | [[modules/notifications/overview|Notifications]] | Notification service | Phase 1 approval notifications |
| **Depends on** | [[modules/calendar/overview|Calendar]] | `ICalendarConflictService` | Conflict warnings during time off submission |
| **Depends on** | [[modules/time-attendance/overview|Time & Attendance]] | Schedules | Attendance expectations and calendar availability context |
| **Consumed by** | [[modules/payroll/overview|Payroll]] | `ITimeOffService` | Time Off minutes for payroll deductions |
| **Consumed by** | [[modules/time-attendance/overview|Time & Attendance]] | `ITimeOffService` | Mark presence status as `on_leave`; late-arrival Time Off deductions |

---

## Public Interface

```csharp
public interface ITimeOffService
{
    Task<Result<TimeOffEntitlementDto>> GetEntitlementAsync(Guid employeeId, Guid timeOffTypeId, int year, CancellationToken ct);
    Task<Result<TimeOffRequestDto>> SubmitRequestAsync(CreateTimeOffRequestCommand command, CancellationToken ct);
    Task<Result<TimeOffRequestDto>> ApproveAsync(Guid requestId, CancellationToken ct);
    Task<Result<List<TimeOffRequestDto>>> GetByEmployeeAsync(Guid employeeId, int year, CancellationToken ct);
    Task<Result<int>> GetUsedMinutesAsync(Guid employeeId, Guid timeOffTypeId, int year, CancellationToken ct);
    Task<Result> DeductLateArrivalAsync(Guid employeeId, Guid timeOffTypeId, int deductionMinutes, Guid attendanceRecordId, string calculationSnapshotJson, CancellationToken ct);
}
```

---

## Database Tables

### `time_off_types`

Time Off Types define what time off exists and which request modes are allowed.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(50)` | e.g., Annual, Sick, Maternity |
| `code` | `varchar(30)` | Unique per tenant when implemented |
| `description` | `text` | Nullable |
| `is_paid` | `boolean` | Type-level classification if supported |
| `requires_document` | `boolean` | Whether supporting document is required |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

Phase 1 does not persist full-day or half-day as canonical request modes on the type. Approval, carry-forward, notice-period, max-consecutive, and entitlement rules belong to Time Off Policies.

### `time_off_policies`

Policy header and effective dating. Policies are created inside the topbar-selected Company and define rules and assignment scope for that Company. Per-time-off-type rule columns belong in `time_off_policy_rules` when a policy can cover multiple time off types.

### `time_off_policy_rules`

Rules per time off type inside a policy. Policy rules own entitlement minutes, accrual, proration, carry-forward, rollover period, eligibility, document, notice, and request limit behavior. Admin enters entitlement in hours/minutes; the system stores the canonical value in minutes.

### `time_off_policy_assignments`

Assignment scope inside the selected Company: `legal_entity_default` shown as Company default in UI, department, position, or employee override.

### `time_off_entitlements`

Employee-level entitlement output per period, stored in minutes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `period_year` | `int` | Or policy period |
| `policy_id` | `uuid` | Nullable/source policy |
| `entitlement_minutes` | `int` | Canonical entitlement in minutes |
| `used_minutes` | `int` | Updated on approval or late deduction |
| `pending_minutes` | `int` | Pending requests when stored |
| `carried_forward_minutes` | `int` | From previous period |
| `available_minutes` | `int` | Computed/stored as implemented |

### `time_off_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `start_time` | `time` | Nullable; used when the user specifies exact start time |
| `end_time` | `time` | Nullable; used when the user specifies exact end time |
| `request_duration_minutes` | `int` | Calculated request duration in minutes |
| `deduction_minutes` | `int` | Approved deduction in minutes; captured at approval time |
| `reason` | `text` | |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `approved_by_id` | `uuid` | FK -> users |
| `approved_at` | `timestamptz` | |
| `conflict_snapshot_json` | `jsonb` | Calendar conflicts at submission time |
| `document_file_id` | `uuid` | FK -> file_records, nullable |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Time Off Type vs Policy** - Time Off Type defines the kind of Time Off (name, paid/unpaid, active/inactive); Time Off Policy defines rules and assignment scope.
2. **Minute storage** - Time Off balances, deductions, carry-forward, forfeiture, and audit mutations are stored in minutes (integer). The UI displays hours and minutes.
3. **No day-based canonical balance** - Admin enters entitlement in hours/minutes. The system stores minutes. The UI may show an approximate day helper for readability, but days are never used for calculation or storage.
4. **Schedule does not own Time Off balance** - Schedule decides expected work times, workdays, and lateness. Time Off decides entitlement, deductions, carry forward, and audit. Late deduction connects Attendance to Time Off by deducting minutes from a selected Time Off type.
5. **Company context** - Time Off policy management uses the topbar-selected Company. The actor must have Time Off policy permission in that Company; creating for another Company requires switching Company context first.
6. **Schedule resolution** - schedule assignments are date-effective; lookup uses employee override, position, department, then `legal_entity_default` shown as Company default in UI.
7. **Schedule changes** - date-effective schedule changes affect future generation/accrual/deductions; past approved deductions are not recalculated automatically.
8. **Request duration** - Time Off request duration is captured directly as minutes. The UI may help the user enter duration using date/time fields, but the saved request stores `request_duration_minutes`. Full-day and half-day are not canonical request modes in Phase 1.
9. **Self-service access** - managers are not excluded from their own Time Off screen.
10. **Managed visibility** - viewing/managing others' Time Off requires scoped access.
11. **Request validation** - checks sufficient minute balance, no overlapping requests, and policy rules.
12. **Calendar conflicts** - warnings only; they do not block Time Off submission by themselves.
13. **Operational relationship** - Time Off affects availability; schedules define expected work pattern; Calendar shows Time Off/schedules/holidays/events; Attendance reflects actual presence.
14. **Late arrival deduction** - Time & Attendance Clock-in Policy late rules deduct from a configured Time Off type via `ITimeOffService.DeductLateArrivalAsync`. Every late deduction creates a balance audit entry with source `time_attendance` and the calculation snapshot.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `TimeOffRequested` | Employee submits request | [[modules/notifications/overview|Notifications]] |
| `TimeOffApproved` | Configured approver approves | Notifications, Time & Attendance, Calendar, Payroll |
| `TimeOffRejected` | Configured approver rejects | Notifications |
| `TimeOffCancelled` | Employee or authorized time_off user cancels | Notifications, Calendar, Payroll when applicable |
| `EntitlementAdjusted` | Time off entitlement recalculated or manually adjusted | Audit trail |

## Features

- [[modules/time-off/time-off-types/overview|Time Off Types]] - time off type definitions and request modes
- [[modules/time-off/time-off-policies/overview|Time Off Policies]] - policy rules and assignment scope
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]] - employee-level minute output per period
- [[modules/time-off/time-off-requests/overview|Time Off Requests]] - request submission, approval, rejection, cancellation
- [[modules/time-off/balance-audit/overview|Balance Audit]] - immutable audit trail for minute balance changes

---

## Related

- [[modules/calendar/overview|Calendar]] - time_off, holidays, schedules, and events in time context
- [[modules/time-attendance/overview|Time & Attendance]] - schedules and attendance against policy
- [[modules/payroll/overview|Payroll]] - payroll deductions and approved time_off inputs
- [[security/compliance|Compliance]] - time off balance audit trail
