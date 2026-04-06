# Module: Leave

**Namespace:** `ONEVO.Modules.Leave`
**Pillar:** 1 — HR Management
**Owner:** Dev 1 (Week 3)
**Tables:** 5
**Task File:** [[WEEK3-leave]]

---

## Purpose

Manages leave types, country/level-specific policies with versioning, entitlement calculation, and request/approval workflows. Integrates with [[shared-platform]] workflow engine for approval routing.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee context, hire date for entitlement |
| **Depends on** | [[org-structure]] | `IOrgStructureService` | Job level/country for policy matching |
| **Depends on** | [[shared-platform]] | Workflow engine | Approval routing |
| **Consumed by** | [[payroll]] | `ILeaveService` | Leave days for payroll deductions |
| **Consumed by** | [[workforce-presence]] | `ILeaveService` | Mark presence status as `on_leave` |

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
| `LeaveRequested` | Employee submits request | [[notifications]] (notify manager) |
| `LeaveApproved` | Manager approves | [[notifications]], [[workforce-presence]] (update status) |
| `LeaveRejected` | Manager rejects | [[notifications]] |
| `LeaveCancelled` | Employee/manager cancels | [[notifications]], entitlement adjustment |

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

See also: [[module-catalog]], [[core-hr]], [[payroll]], [[workforce-presence]]
