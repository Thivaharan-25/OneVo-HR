 # Module: Workforce Presence

**Feature Folder:** `Application/Features/WorkforcePresence`
**Phase:** 1 â€” Build
**Pillar:** 2 â€” Workforce Intelligence
**Owner:** Dev 3 + Dev 4 (Week 2)
**Tables:** 12
**Task Files:** [[current-focus/DEV3-workforce-presence-setup|DEV3: Workforce Presence]], [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]

> **Replaces the old Attendance module.** All attendance-related functionality now lives here. References to "Attendance" in code should use "WorkforcePresence".

---

## Purpose

Single source of truth for **"is this employee present and working?"** Unifies data from three sources:
1. **Biometric terminals** â€” clock-in/out events from fingerprint devices
2. **Desktop agent** â€” device sessions (active/idle cycles) via [[modules/agent-gateway/overview|Agent Gateway]]
3. **Policy-gated web/tray clock events** - allowed for remote/hybrid work and approved outage scenarios
4. **Manual entries** - admin corrections and overrides

Produces `presence_sessions` â€” one unified row per employee per day â€” consumed by [[modules/payroll/overview|Payroll]], [[modules/productivity-analytics/overview|Productivity Analytics]], and [[modules/exception-engine/overview|Exception Engine]].

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee context, position-derived reporting hierarchy |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Monitoring toggles, employee overrides |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `IWorkforcePresenceService` | Actual worked hours for payroll runs |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | `IWorkforcePresenceService` | Attendance data for reports |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IWorkforcePresenceService` | Idle detection, absence anomalies |
| **Consumed by** | [[modules/agent-gateway/overview\|Agent Gateway]] | Domain events | Monitoring lifecycle control (start/stop/pause/resume agent) |

---

## Public Interface

```csharp
// ONEVO.Application.Features.WorkforcePresence/Public/IWorkforcePresenceService.cs
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

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/WorkforcePresence/Entities/
  ONEVO.Domain/Features/WorkforcePresence/Events/

Application (CQRS):
  ONEVO.Application/Features/WorkforcePresence/Commands/
  ONEVO.Application/Features/WorkforcePresence/Queries/
  ONEVO.Application/Features/WorkforcePresence/DTOs/Requests/
  ONEVO.Application/Features/WorkforcePresence/DTOs/Responses/
  ONEVO.Application/Features/WorkforcePresence/Validators/
  ONEVO.Application/Features/WorkforcePresence/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/WorkforcePresence/

API endpoints:
  ONEVO.Api/Controllers/WorkforcePresence/WorkforcePresenceController.cs

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
| `attendance_records` | Clock-in/out source records from biometric, web, tray, outage override, or manual correction |
| `overtime_requests` | Overtime request + approval workflow |
| `attendance_corrections` | Manager corrections to attendance data |

### New Tables (3)

#### `presence_sessions`

Unified presence â€” **one row per employee per day**. Combines biometric + agent data.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
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
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `device_id` | `uuid` | FK â†’ registered_agents |
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
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `break_start` | `timestamptz` | |
| `break_end` | `timestamptz` | Null if ongoing |
| `break_type` | `varchar(30)` | `lunch`, `prayer`, `smoke`, `personal`, `other` |
| `auto_detected` | `boolean` | True if detected by agent idle threshold |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, break_start)`

---

## Domain Events (intra-module â€” MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | â€” | â€” |

## Cross-Module Events (cross-module â€” MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `PresenceSessionStarted` | Employee clocks in through an allowed source | [[modules/agent-gateway/overview\|Agent Gateway]] (send `StartMonitoring` to agent), [[modules/activity-monitoring/overview\|Activity Monitoring]] |
| `PresenceSessionEnded` | Employee clocks out through an allowed source or auto-close | [[modules/agent-gateway/overview\|Agent Gateway]] (send `StopMonitoring` to agent) |
| `BreakExceeded` | Break exceeds allowed duration | [[modules/exception-engine/overview\|Exception Engine]] (flag long break) |
| `OvertimeRequested` | Employee requests overtime | [[modules/notifications/overview\|Notifications]] (approval workflow) |
| `OvertimeApproved` | Configured approver approves overtime request | [[modules/payroll/overview\|Payroll]] (include in payroll run) |
| `AttendanceCorrected` | Authorized attendance user corrects attendance data | Audit trail |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `EmployeeHired` | [[modules/core-hr/overview\|Core HR]] | Create initial presence record and assign default shift for new employee |
| `LeaveApproved` | [[modules/leave/overview\|Leave]] | Mark presence status as `on_leave` for the approved date range |

**Monitoring lifecycle:** The `PresenceSessionStarted`/`Ended` and `BreakStarted`/`Ended` events are the **control signals** that govern when the desktop agent collects data. No data is captured before clock-in, during breaks, or after clock-out. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]] for the full flow.

---

## Key Business Rules

1. **Presence session is computed, not directly written.** It aggregates from `attendance_records` (biometric/web/tray/outage/manual), `device_sessions` (agent), and corrections.
2. **Device sessions can overlap with biometric clock-in.** The unified `presence_sessions` deduplicates â€” uses earliest first_seen and latest last_seen.
3. **Break detection:** If agent reports idle > configurable threshold (default 15 min), auto-create a `break_record` with `auto_detected = true`.
4. **Overtime:** Must be pre-approved via workflow or auto-flagged when `total_present_minutes > scheduled_minutes`.
5. **Data flow:** Biometric and policy-gated clock events write to `attendance_records`. Agent data arrives via [[modules/agent-gateway/overview|Agent Gateway]] -> `device_sessions`. A Hangfire job reconciles both into `presence_sessions` every 5 minutes during work hours.
6. **Clock-in source policy:** Office employees clock in through biometric terminals only, unless their legal entity has `agent_clock_in_enabled = true` (which allows all employees in that entity to clock in/out via web or tray app). Remote employees always clock in/out via the tray app. Hybrid employees use biometric when onsite and tray when remote. Field employees follow their legal entity's policy. Onsite tray clock-in (non-remote) is only available when the employee's legal entity has `agent_clock_in_enabled = true` or an active biometric outage override exists.
   - **The tray app / web Clock In / Clock Out option is hidden** unless the employee's `work_type` is `remote` or `hybrid`, OR the employee's legal entity (`employees.legal_entity_id -> legal_entities.agent_clock_in_enabled`) is `true`.
   - Scope of this flag: a Super Admin can set `agent_clock_in_enabled` on any legal entity within the tenant; a non-Super Admin with `attendance:manage` can only set it on the legal entity their own department belongs to.
   - **Remote tray clock-in and clock-out each require a webcam photo** (identity verification). Photo is captured every time â€” not just on first setup.
7. **IDE extension boundary:** WorkSync and IDE time logging can create `time_logs`, but they must never create Workforce Presence clock-in/out records.

---

## Frontend â€” Presence Card View

The workforce-presence module surfaces on the Workforce pillar default screen (`/workforce`) as a live card grid.

**Card per employee shows:**
- Online status dot â€” sourced from this module (clocked-in, break, offline)
- Productivity score â€” sourced from productivity-analytics module
- Current task â€” sourced from WMS task module
- Agent alert banner â€” sourced from exception-engine (when flagged)

**Replaced:** The previous 3-tab design (Activity tab, Work Insights tab, Online Status tab) is replaced by this single card grid. Online status is embedded in each card. Productivity is embedded in each card. Activity is the drill-down at `/workforce/[employeeId]`.

**Agent escalation:** When the exception-engine or agent-gateway detects an issue (missed punch, biometric anomaly, late clock-in), the employee's card receives a red alert banner and is sorted to the top of the grid.

See [[Userflow/Workforce-Presence/presence-overview|Presence Overview]] for the full flow.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/presence` | `attendance:read` | List presence sessions (paginated, filterable) |
| GET | `/api/v1/workforce/presence/{employeeId}` | `attendance:read` | Employee presence for date range |
| GET | `/api/v1/workforce/presence/live` | `workforce:view` | Real-time workforce status |
| POST | `/api/v1/workforce/clock-in` | `attendance:write-own` | Clock in through an allowed source |
| POST | `/api/v1/workforce/clock-out` | `attendance:write-own` | Clock out through an allowed source |
| POST | `/api/v1/workforce/breaks/start` | `attendance:write-own` | Start break and pause monitoring |
| POST | `/api/v1/workforce/breaks/end` | `attendance:write-own` | End break and resume monitoring |
| GET | `/api/v1/workforce/device-sessions/{employeeId}` | `workforce:view` | Device session detail |
| GET | `/api/v1/workforce/breaks/{employeeId}` | `attendance:read` | Break records |
| GET | `/api/v1/workforce/devices` | `attendance:read` | List biometric/workforce devices |
| POST | `/api/v1/workforce/devices` | `attendance:write` | Register biometric/workforce device |
| PUT | `/api/v1/workforce/devices/{id}` | `attendance:write` | Update biometric/workforce device |
| POST | `/api/v1/workforce/devices/{id}/enrollments` | `attendance:write` | Enroll employees on a biometric device |
| POST | `/api/v1/workforce/biometric/webhook` | HMAC-SHA256 | Receive biometric clock events |
| POST | `/api/v1/workforce/biometric-outages` | `attendance:manage` | Enable time-limited onsite web/tray clock-in fallback |
| PUT | `/api/v1/workforce/biometric-outages/{id}/resolve` | `attendance:manage` | End outage fallback |
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
| `ReconcilePresenceSessions` | Every 5 min (work hours) | Merge biometric + agent data â†’ `presence_sessions` |
| `FlagUnresolvedAbsences` | Daily 10:00 AM | Flag employees with no presence data for the day |
| `CloseOpenSessions` | Daily 11:59 PM | Close any open device sessions and break records |

---

## Important Notes

- **Presence session vs device session:** `presence_sessions` is ONE row per employee per day (unified). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them.
- **This module does NOT handle screenshots or app tracking** â€” that's [[modules/activity-monitoring/overview|Activity Monitoring]].
- **Biometric device management** is exposed through Workforce Presence routes (`/api/v1/workforce/devices`) because clock-in/out is a workforce function. Identity Verification owns photo/fingerprint verification policy and review, but Workforce Presence owns terminal registration, enrollment, and clock event ingestion.
- **Payroll reads from this module** via `IWorkforcePresenceService.GetTotalWorkedHoursAsync()`.

## Features

- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]] â€” Unified presence (one row/employee/day from biometric + agent + manual) â€” frontend: [[modules/workforce-presence/presence-sessions/frontend|Frontend]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]] â€” Device active/idle cycle tracking (multiple rows/day per laptop)
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]] â€” Break records with auto-detection from agent idle threshold
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]] â€” Shift definitions, weekly schedule patterns, employee assignments
- [[modules/workforce-presence/overtime/overview|Overtime]] â€” Overtime request and approval workflow
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]] â€” Manager corrections to presence data

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” All presence data is tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] â€” `PresenceSessionStarted`, `PresenceSessionEnded`, `BreakExceeded`, `OvertimeRequested`
- [[backend/messaging/error-handling|Error Handling]] â€” Deduplication of biometric + agent data in reconciliation job
- [[security/compliance|Compliance]] â€” Presence history for payroll and legal record-keeping
- [[database/migration-patterns|Migration Patterns]] â€” `presence_sessions` UNIQUE on `(tenant_id, employee_id, date)`
- [[current-focus/DEV3-workforce-presence-setup|DEV3: Workforce Presence]] â€” Presence and shift setup task file
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]] â€” Biometric integration task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/identity-verification/overview|Identity Verification]]

