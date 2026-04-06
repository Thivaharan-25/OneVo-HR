# Module: Workforce Presence

**Namespace:** `ONEVO.Modules.WorkforcePresence`
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 3 + Dev 4 (Week 2)
**Tables:** 12
**Task Files:** [[WEEK2-workforce-presence-setup]], [[WEEK2-workforce-presence-biometric]]

> **Replaces the old Attendance module.** All attendance-related functionality now lives here. References to "Attendance" in code should use "WorkforcePresence".

---

## Purpose

Single source of truth for **"is this employee present and working?"** Unifies data from three sources:
1. **Biometric terminals** — clock-in/out events from fingerprint devices
2. **Desktop agent** — device sessions (active/idle cycles) via [[agent-gateway]]
3. **Manual entries** — admin corrections and overrides

Produces `presence_sessions` — one unified row per employee per day — consumed by [[payroll]], [[productivity-analytics]], and [[exception-engine]].

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee context, manager hierarchy |
| **Depends on** | [[configuration]] | `IConfigurationService` | Monitoring toggles, employee overrides |
| **Consumed by** | [[payroll]] | `IWorkforcePresenceService` | Actual worked hours for payroll runs |
| **Consumed by** | [[productivity-analytics]] | `IWorkforcePresenceService` | Attendance data for reports |
| **Consumed by** | [[exception-engine]] | `IWorkforcePresenceService` | Idle detection, absence anomalies |

---

## Public Interface

```csharp
// ONEVO.Modules.WorkforcePresence/Public/IWorkforcePresenceService.cs
public interface IWorkforcePresenceService
{
    Task<Result<PresenceSessionDto>> GetPresenceForDateAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<List<PresenceSessionDto>>> GetPresenceRangeAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<decimal>> GetTotalWorkedHoursAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<List<DeviceSessionDto>>> GetDeviceSessionsAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<WorkforceStatusDto>> GetLiveWorkforceStatusAsync(CancellationToken ct); // tenant-wide
}
```

---

## Database Tables (12)

### Kept from Old Attendance (9 tables)

| Table | Purpose |
|:------|:--------|
| `shifts` | Shift definitions (morning, evening, night, flexible) |
| `work_schedules` | Weekly schedule patterns |
| `employee_shift_assignments` | Which employee is on which shift |
| `holidays` | Company and country holidays |
| `schedule_templates` | Reusable schedule templates |
| `employee_work_schedules` | Employee-specific schedule overrides |
| `attendance_records` | Legacy clock-in/out records (biometric source) |
| `overtime_requests` | Overtime request + approval workflow |
| `attendance_corrections` | Manager corrections to attendance data |

### New Tables (3)

#### `presence_sessions`

Unified presence — **one row per employee per day**. Combines biometric + agent data.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | The work day |
| `first_seen_at` | `timestamptz` | First sign of presence (any source) |
| `last_seen_at` | `timestamptz` | Last sign of presence |
| `total_present_minutes` | `int` | Computed from all sources |
| `total_break_minutes` | `int` | Sum of break records |
| `source` | `varchar(20)` | `biometric`, `agent`, `manual`, `mixed` |
| `status` | `varchar(20)` | `present`, `absent`, `partial`, `on_leave` |
| `created_at` | `timestamptz` | Audit |
| `updated_at` | `timestamptz` | Audit |

**Indexes:** `(tenant_id, employee_id, date)` UNIQUE, `(tenant_id, date)`, `(tenant_id, status)`

#### `device_sessions`

Tracks designated laptop active vs idle. **Multiple rows per employee per day** (one per active/idle cycle).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → registered_agents |
| `session_start` | `timestamptz` | When active period began |
| `session_end` | `timestamptz` | When active period ended (null if ongoing) |
| `active_minutes` | `int` | Minutes with input activity |
| `idle_minutes` | `int` | Minutes without input |
| `active_percentage` | `decimal(5,2)` | `active / (active + idle) * 100` |

**Indexes:** `(tenant_id, employee_id, session_start)`, `(device_id)`

#### `break_records`

Tracks breaks (lunch, prayer, smoke, etc.).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `break_start` | `timestamptz` | |
| `break_end` | `timestamptz` | Null if ongoing |
| `break_type` | `varchar(30)` | `lunch`, `prayer`, `smoke`, `personal`, `other` |
| `auto_detected` | `boolean` | True if detected by agent idle threshold |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, break_start)`

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `PresenceSessionStarted` | First activity detected for employee today | [[notifications]] (team online status) |
| `PresenceSessionEnded` | No activity for configurable threshold | [[activity-monitoring]] (close day tracking) |
| `BreakExceeded` | Break exceeds allowed duration | [[exception-engine]] (flag long break) |
| `OvertimeRequested` | Employee requests overtime | [[notifications]] (approval workflow) |
| `AttendanceCorrected` | Manager corrects attendance | Audit trail |

---

## Key Business Rules

1. **Presence session is computed, not directly written.** It aggregates from `attendance_records` (biometric), `device_sessions` (agent), and manual corrections.
2. **Device sessions can overlap with biometric clock-in.** The unified `presence_sessions` deduplicates — uses earliest first_seen and latest last_seen.
3. **Break detection:** If agent reports idle > configurable threshold (default 15 min), auto-create a `break_record` with `auto_detected = true`.
4. **Overtime:** Must be pre-approved via workflow or auto-flagged when `total_present_minutes > scheduled_minutes`.
5. **Data flow:** Biometric events arrive via webhook → `attendance_records`. Agent data arrives via [[agent-gateway]] → `device_sessions`. A Hangfire job reconciles both into `presence_sessions` every 5 minutes during work hours.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/presence` | `attendance:read` | List presence sessions (paginated, filterable) |
| GET | `/api/v1/workforce/presence/{employeeId}` | `attendance:read` | Employee presence for date range |
| GET | `/api/v1/workforce/presence/live` | `workforce:view` | Real-time workforce status |
| GET | `/api/v1/workforce/device-sessions/{employeeId}` | `workforce:view` | Device session detail |
| GET | `/api/v1/workforce/breaks/{employeeId}` | `attendance:read` | Break records |
| POST | `/api/v1/workforce/corrections` | `attendance:write` | Submit attendance correction |
| POST | `/api/v1/workforce/overtime` | `attendance:write` | Submit overtime request |
| PUT | `/api/v1/workforce/overtime/{id}/approve` | `attendance:approve` | Approve overtime |
| GET | `/api/v1/shifts` | `attendance:read` | List shifts |
| POST | `/api/v1/shifts` | `attendance:write` | Create shift |
| GET | `/api/v1/schedules` | `attendance:read` | List schedules |
| POST | `/api/v1/schedules` | `attendance:write` | Create schedule |

---

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `ReconcilePresenceSessions` | Every 5 min (work hours) | Merge biometric + agent data → `presence_sessions` |
| `FlagUnresolvedAbsences` | Daily 10:00 AM | Flag employees with no presence data for the day |
| `CloseOpenSessions` | Daily 11:59 PM | Close any open device sessions and break records |

---

## Important Notes

- **Presence session vs device session:** `presence_sessions` is ONE row per employee per day (unified). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them.
- **This module does NOT handle screenshots or app tracking** — that's [[activity-monitoring]].
- **Biometric device management** is in [[identity-verification]], not here. This module only consumes biometric events.
- **Payroll reads from this module** via `IWorkforcePresenceService.GetTotalWorkedHoursAsync()`.

See also: [[module-catalog]], [[activity-monitoring]], [[agent-gateway]], [[identity-verification]]
