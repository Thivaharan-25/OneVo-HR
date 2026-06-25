 # Module: Time & Attendance

**Feature Folder:** `Application/Features/TimeAttendance`
**Phase:** 1 - Build
**Pillar:** 2 - Monitoring
**Owner:** Dev 3 + Dev 4 (Week 2)
**Tables:** 17
**Task Files:** [[current-focus/DEV3-time-attendance-setup|DEV3: Time & Attendance]], [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]

> **Replaces the old Attendance module.** All attendance-related functionality now lives here. References to "Attendance" in code should use "TimeAttendance".


## Customer-Facing IA Boundary

The internal module namespace remains `TimeAttendance`, but the customer-facing IA is split by job:

- `Time & Attendance`: operational attendance, schedules, clock-in policy, overtime rules, row-level attendance corrections, and overtime request actions.
- `Monitoring`: live operational monitoring, alert review, device health, and monitoring visibility.
- `Calendar`: visual planning for events, holidays, schedules, Time Off, meetings, invitations, reminders, and conflicts.

Time & Attendance sub-sidebar must contain exactly:

| Label | Route | Purpose |
|---|---|---|
| Attendance | `/time-attendance/attendance` | Own attendance and scoped team attendance in one page |
| Schedules | `/time-attendance/schedules` | Work schedule management |
| Clock-in Policy | `/time-attendance/clock-in-policy` | Clock-in requirement, location, progressive late Time Off deduction rules, and notifications |
| Overtime Rules | `/time-attendance/overtime-rules` | Overtime request/approval rules |

Do not expose **Holiday Calendar**, **Work Weeks**, **Work Patterns**, **Time Tracking**, **Team Attendance**, or **Attendance Corrections** as separate Time & Attendance sidebar items. Attendance uses an in-page segmented control for `Time Tracking` (employee view, renamed from My Attendance) / `Team Attendance`; corrections are row-level actions.

Calendar remains a separate main sidebar item. Do not move Calendar under Time & Attendance.
---

## Purpose

Single source of truth for **"is this employee present and working?"** Unifies data from three sources:
1. **Biometric/attendance terminals** - clock-in/out events from face, fingerprint, card, PIN, or combined punch devices
2. **Desktop agent** - device sessions (active/idle cycles) via [[modules/agent-gateway/overview|Agent Gateway]]
3. **Policy-gated web/tray clock events** - allowed for remote/hybrid work, legal-entity policies that enable app/tray clock-in, and approved outage scenarios
4. **Manual entries** - admin corrections and overrides

Produces `presence_sessions` - one unified row per employee per day - consumed by [[modules/payroll/overview|Payroll]], [[modules/productivity-analytics/overview|Productivity Analytics]], and [[modules/exception-engine/overview|Exception Engine]].

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee context, position-derived reporting hierarchy |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Monitoring toggles, employee overrides |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `ITimeAttendanceService` | Actual worked hours for payroll runs |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | `ITimeAttendanceService` | Attendance data for reports |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `ITimeAttendanceService` | Phase 2 configurable exception rules; Phase 1 uses lightweight alerts |
| **Consumed by** | [[modules/agent-gateway/overview\|Agent Gateway]] | Domain events | Monitoring lifecycle control (start/stop/pause/resume agent) |

---

## Public Interface

```csharp
// ONEVO.Application.Features.TimeAttendance/Public/ITimeAttendanceService.cs
public interface ITimeAttendanceService
{
    Task<Result<PresenceSessionDto>> GetPresenceForDateAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<List<PresenceSessionDto>>> GetPresenceRangeAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<decimal>> GetTotalWorkedHoursAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<List<DeviceSessionDto>>> GetDeviceSessionsAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<MonitoringStatusDto>> GetLiveMonitoringStatusAsync(CancellationToken ct); // tenant-wide
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/TimeAttendance/Entities/
  ONEVO.Domain/Features/TimeAttendance/Events/

Application (CQRS):
  ONEVO.Application/Features/TimeAttendance/Commands/
  ONEVO.Application/Features/TimeAttendance/Queries/
  ONEVO.Application/Features/TimeAttendance/DTOs/Requests/
  ONEVO.Application/Features/TimeAttendance/DTOs/Responses/
  ONEVO.Application/Features/TimeAttendance/Validators/
  ONEVO.Application/Features/TimeAttendance/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/TimeAttendance/

API endpoints:
  ONEVO.Api/Controllers/TimeAttendance/TimeAttendanceController.cs

---

## Database Tables (17)

| Table | Purpose |
|:------|:--------|
| `attendance_corrections` | Employee/manager/admin attendance correction requests and approval state |
| `attendance_records` | Daily attendance summary per employee per work day |
| `break_records` | Employee break intervals (lunch, prayer, smoke, personal) |
| `clock_in_late_deduction_rules` | Progressive late-arrival Time Off deduction rules (child rows of `clock_in_policies`) |
| `clock_in_policies` | Clock-in source, verification, scope, and effective policy header |
| `device_sessions` | Laptop active/idle cycles (multiple rows per employee per day) |
| `overtime_records` | Overtime records and approval state |
| `presence_sessions` | Unified daily presence from biometric, agent, web/tray, and manual sources |
| `public_holidays` | Country or tenant-level public holidays |
| `roster_entries` | Employee roster placement for a date |
| `roster_periods` | Roster planning window |
| `schedule_assignments` | Date-effective schedule assignment to company, department, position, or employee |
| `shift_assignments` | Employee shift assignment for a date |
| `shifts` | Reusable shift definitions |
| `work_area_change_requests` | One-day expected work area change requests |
| `work_schedule_holidays` | Per-schedule selected holidays |
| `work_schedules` | Work schedule definitions with default/per-day expected work area |

See [[database/schemas/time-attendance|Time & Attendance Schema]] for full column definitions.

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `PresenceSessionStarted` | Employee clocks in through an allowed source | [[modules/agent-gateway/overview\|Agent Gateway]] (send `StartMonitoring` to agent), [[modules/activity-monitoring/overview\|Activity Monitoring]] |
| `PresenceSessionEnded` | Employee clocks out through an allowed source or auto-close | [[modules/agent-gateway/overview\|Agent Gateway]] (send `StopMonitoring` to agent) |
| `BreakExceeded` | Break exceeds allowed duration | Notifications/lightweight alerts in Phase 1; full Exception Engine rules in Phase 2 |
| `OvertimeRequested` | Employee requests overtime | [[modules/notifications/overview\|Notifications]] (Inbox approval process) |
| `OvertimeApproved` | Configured approver approves overtime request | [[modules/payroll/overview\|Payroll]] (include in payroll run) |
| `AttendanceCorrected` | Authorized attendance user corrects attendance data | Audit trail |
| `TimeOffIntervalStarted` | Approved partial-day Time Off interval begins during an active work session | [[modules/agent-gateway/overview\|Agent Gateway]] (send `PauseMonitoring(reason = approved_time_off)` to agent), [[modules/activity-monitoring/overview\|Activity Monitoring]] |
| `TimeOffIntervalEnded` | Approved partial-day Time Off interval ends (or employee returns early) | [[modules/agent-gateway/overview\|Agent Gateway]] (send `ResumeMonitoring` to agent); if employee does not return after grace, create `late_return_from_time_off` alert routed through Monitoring Policy |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `EmployeeHired` | [[modules/core-hr/overview\|Core HR]] | Create initial presence record and assign default shift for new employee |
| `TimeOffApproved` | [[modules/time-off/overview\|Time Off]] | Mark presence status as `on_leave` for the approved date range |

**Monitoring lifecycle:** The `PresenceSessionStarted`/`Ended` and `BreakStarted`/`Ended` events are the **control signals** that govern when the desktop agent collects data. No data is captured before clock-in, during breaks, or after clock-out. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]] for the full flow.

---

## Key Business Rules

1. **Presence session is computed, not directly written.** It aggregates from `attendance_records` (biometric/web/tray/outage/manual), `device_sessions` (agent), and corrections.
2. **Device sessions can overlap with biometric clock-in.** The unified `presence_sessions` deduplicates - uses earliest first_seen and latest last_seen.
3. **Break detection:** If agent reports idle > configurable threshold (default 15 min), auto-create a `break_record` with `auto_detected = true`.
4. **Overtime:** Follows Overtime Rules. Requests are sent to Inbox and approved by the one eligible owner resolved through Org Structure management coverage in Phase 1. The Phase 2 workflow/automation engine is not required for Phase 1 overtime.
5. **Data flow:** Biometric and policy-gated clock events write to `attendance_records`. Agent data arrives via [[modules/agent-gateway/overview|Agent Gateway]] -> `device_sessions`. A Hangfire job reconciles both into `presence_sessions` every 5 minutes during work hours.
6. **Clock-in source policy:** Clock-in Policy configures allowed clock-in sources by work mode and today's expected work area. For hybrid employees, the allowed clock-in source depends on today's `expected_work_area`, not just the employee's `work_mode`. Formula: `work_mode + today expected_work_area + clock-in policy = allowed clock-in action`.
   - **The tray app / web Clock In / Clock Out option is hidden** unless the employee's `work_mode` is `remote` or `hybrid`, OR the employee's legal entity (`employees.legal_entity_id -> legal_entities.agent_clock_in_enabled`) is `true`.
   - Scope of this flag: a Super Admin can set `agent_clock_in_enabled` on any legal entity within the tenant; a non-Super Admin with `attendance:manage` can only set it on the legal entity their own department belongs to.
   - **Tray/web clock-in and clock-out photo capture is policy-driven.** `photo_capture_context_scope` controls whether identity photos are required for `remote_only`, `onsite_only`, `remote_and_onsite`, or `disabled`. When required, photo capture happens every applicable time, not just on first setup.
7. **IDE extension boundary:** WorkSync and IDE time logging can create `time_logs`, but they must never create Time & Attendance clock-in/out records.

---

## Canonical Work Area Terms

Use these terms consistently across all docs:

| Term | Scope | Allowed Values | Meaning |
|:-----|:------|:---------------|:--------|
| `work_mode` | Employee-level | `onsite`, `remote`, `hybrid`, `field` | What the employee is *allowed* to do |
| `expected_work_area` | Date/shift-level | `onsite`, `remote`, `either`, `field` | Where the employee is *planned* to work today |
| `actual_work_area` | Session-level | detected from evidence | Where evidence shows the employee *is* working |

Do not use `work_type`. Hybrid only means the employee is allowed to have onsite and remote days. It does not mean the system can guess onsite or remote — the actual expected work area must come from the schedule/roster/day override.

---

## Expected Work Area Resolution

For any employee/date/shift, resolve the expected work area in this order:

1. **Approved work area change request** (`work_area_change_requests` with `status = approved` for this date)
2. **Roster entry override** (`roster_entries.expected_work_area` for this date)
3. **Shift assignment override** (`shift_assignments.expected_work_area` for this date)
4. **Schedule day setting** (per-day `expected_work_area` from `work_schedules.workdays_json`)
5. **Schedule default** (`work_schedules.default_work_area`)
6. **Employee `work_mode` fallback**

Fallback rules (level 6 only):

| work_mode | Fallback expected_work_area |
|:----------|:----------------------------|
| `onsite` | `onsite` |
| `remote` | `remote` |
| `hybrid` | `either` (only if no schedule/day/shift rule exists) |
| `field` | `field` |

Hybrid fallback to `either` is only a last-resort fallback, not the preferred planning model. Admins should configure per-day expected work areas in schedules.

---

## Work Schedules — Working Area

The Create Work Schedule modal includes a **Working Area** section after Workdays.

**Options:**

- **Same for all selected days** — applies one expected work area (`onsite`, `remote`, `either`, `field`) to all selected workdays
- **Custom by day** — shows each selected workday with a dropdown to set per-day expected work area

**Database:**

- `work_schedules.default_work_area` stores the schedule-level default
- `work_schedules.workdays_json` stores per-day expected work area when "Custom by day" is selected:

```json
{
  "monday": { "enabled": true, "expected_work_area": "onsite" },
  "tuesday": { "enabled": true, "expected_work_area": "remote" },
  "wednesday": { "enabled": true, "expected_work_area": "remote" },
  "thursday": { "enabled": true, "expected_work_area": "remote" },
  "friday": { "enabled": true, "expected_work_area": "onsite" }
}
```

**Schedule examples:**

- Pure onsite: Working Area = `Onsite` for all selected days
- Pure remote: Working Area = `Remote` for all selected days
- Hybrid: Working Area = Custom by day (Mon/Fri onsite, Tue-Thu remote)

One schedule handles all work area combinations. Do not require admins to create two schedules for one hybrid employee to split onsite and remote days.

---

## Work Area Change Request

Employees can request a one-day work area change through the Time Tracking page.

**Flow:**
1. Employee opens Time Tracking → Request → Work Area Change Request
2. Form shows: Date, Current planned work area (read-only), Requested work area, Reason, Optional attachment
3. Submit creates `work_area_change_requests` with `status = pending`
4. Routes to Inbox for approval by management coverage owner
5. If approved: today's expected_work_area changes; validation rules apply to the new work area
6. If rejected: expected work area remains unchanged; mismatch rules apply if employee works from a different location

This is distinct from `remote_work_location_change_requests` (Configuration module), which permanently changes the employee's approved remote work location profile.

---

## Clock-in Policy — Work Mode Configuration

Clock-in Policy configures allowed clock-in sources by work mode. Example configuration:

| Work Mode | Biometric | Web | Tray App | Photo Required | Notes |
|:----------|:----------|:----|:---------|:---------------|:------|
| Onsite | On | Off | Off | Off | Use biometric terminals unless fallback is active |
| Remote | Off | On | On | On | Tray/web clock-in with photo verification |
| Hybrid | On | On | On | On | Biometric onsite, tray/web when remote |
| Field | Off | On | On | Optional | Company-approved web or tray clock-in |

**Hybrid rule:** For hybrid employees, the allowed clock-in source depends on today's `expected_work_area`:

- Today `expected_work_area = onsite` → biometric preferred; web/tray only if policy allows onsite fallback
- Today `expected_work_area = remote` → web/tray app; photo required; remote location verification required

---

## Employee Web Topbar

The web customer-app topbar shows only immediate time controls:

- **Clock In** / **Clock Out**
- **Start Break** / **End Break**

Do not put the Request dropdown in the topbar. Requests live in the Time Tracking page.

**Visibility rules:**

| State | Clock In | Clock Out | Start Break | End Break |
|:------|:---------|:----------|:------------|:----------|
| Before clock-in | Show | Hide | Hide | Hide |
| After clock-in | Hide | Show | Show | Hide |
| During break | Hide | Show | Hide | Show |
| After clock-out | Show | Hide | Hide | Hide |

If the employee is onsite biometric-only: Clock In / Clock Out hidden or disabled with message "Use biometric terminal to clock in/out". If fallback is active, topbar Clock In / Clock Out becomes available.

Break is available to all employees after they are clocked in — break is an employee action during a working session.

---

## Daily Clock-In Flow

When an employee clocks in via the topbar, the system checks:

1. Who is the employee?
2. Which Company/legal_entity is active?
3. What schedule applies today?
4. What is today's `expected_work_area`? (resolved via the 6-level chain above)
5. Is the clock-in source allowed by Clock-in Policy for this work mode + expected work area?
6. Is identity verification required?
7. Is location verification required?

**On onsite day:** Expected location = Company office location. If employee clocks in from office, accepted. If employee tries remote on an onsite day, system detects mismatch, starts grace period, can prompt Work Area Change request.

**On remote day:** Expected location = approved remote work profile. If no remote profile exists, Tray App asks employee to set approved remote work location with photo verification.

**On either day:** Allow Company office OR approved remote profile.

**On field day:** No strict office/remote match. Review rules may apply separately.

---

## Partial-Day Time Off During Workday

When an employee has approved partial-day Time Off during a scheduled workday:

**Example:** Schedule 8 AM–5 PM, expected work area onsite, approved Time Off 1 PM–3 PM.

1. **8:00 AM** — Employee clocks in. Monitoring starts. Location and activity tracking active.
2. **1:00 PM** — Approved Time Off interval starts.
   - Time & Attendance opens a time_off exclusion interval
   - Agent Gateway sends `PauseMonitoring(reason = approved_time_off)`
   - Activity Monitoring ignores this interval
   - Work-location evidence is not evaluated
   - Discrepancy Engine treats this interval as explained absence
3. **Early return (e.g., 2:30 PM)** — If employee returns before Time Off ends:
   - Tray detects activity, asks "Resume work now?"
   - If confirmed: monitoring resumes at 2:30 PM, actual return time recorded
   - Original Time Off deduction remains unchanged unless admin explicitly recalculates
4. **3:00 PM** — Time Off ends:
   - System expects employee return
   - Wait configured return grace period
   - If employee does not return after grace: create `late_return_from_time_off` alert (not normal idle)
   - Route alert through Monitoring Policy
5. **If employee clocks out during Time Off:**
   - Work session closes
   - No expected return alert
   - Monitoring remains stopped

---

## Frontend - Presence Card View

The time-attendance module surfaces on the Monitoring default screen (`/monitoring`) as a live card grid.

**Card per employee shows:**
- Online status dot - sourced from this module (clocked-in, break, offline)
- Productivity score - sourced from productivity-analytics module
- Current task - sourced from WMS task module
- Agent alert banner - sourced from exception-engine (when flagged)

**Replaced:** The previous 3-tab design (Activity tab, Work Insights tab, Online Status tab) is replaced by this single card grid. Online status is embedded in each card. Productivity is embedded in each card. Activity is the drill-down at `/monitoring/employees/[employeeId]`.

**Agent escalation:** When the exception-engine or agent-gateway detects an issue (missed punch, biometric anomaly, late clock-in), the employee's card receives a red alert banner and is sorted to the top of the grid.

See [[Userflow/Time-Attendance/presence-overview|Presence Overview]] for the full flow.

---

## Frontend - Attendance Screen

**Route:** `/time-attendance/attendance`

Attendance is one page with a compact segmented control inside the page:

- `Time Tracking` is visible to every employee with own attendance access.
- `Team Attendance` is visible only when the user has team/employee visibility through management coverage or attendance permission.

Time Tracking content (renamed from My Attendance):

- Today timeline
- Clock-in/out history
- Break history
- Expected work area today
- Actual detected work area
- Approved Time Off intervals
- Attendance correction status
- Overtime status
- Work-area change request status
- Request button/dropdown with options:
  - Time Off Request
  - Overtime Request
  - Work Area Change Request (expected_work_area change for a date/shift)
  - Attendance Correction Request (clock-in/out/break/full-day attendance correction only; not for work area changes)

Attendance history columns:

| Column |
|---|
| Date |
| Scheduled time |
| Clock in |
| Clock out |
| Worked hours |
| Expected work area |
| Actual work area |
| Status |
| Actions |

Row action: `Request correction`. Do not add a large top-level correction button.

Team Attendance content:

- Search employee
- Department filter
- Date filter
- Status filter
- Attendance table

Team table columns:

| Column |
|---|
| Employee |
| Position |
| Department |
| Scheduled time |
| Clock in |
| Clock out |
| Worked hours |
| Work mode |
| Status |

---

## Clock-in Policy Screen

**Route:** `/time-attendance/clock-in-policy`

Clock-in Policy configures who must clock in, location verification, progressive late Time Off deduction rules, notification to the recipient resolved by Monitoring Policy, onsite/remote verification behavior, and optional effective dates. Schedule start/end/break values come from Schedules and must not be requested in Clock-in Policy.

**Database:** `clock_in_policies` stores the policy header (scope, source/verification behavior, effective dates). `clock_in_late_deduction_rules` stores progressive late deduction child rows referencing `clock_in_policies.id`. See [[database/schemas/time-attendance#`clock_in_policies`|clock_in_policies schema]] for full definition.

Fields:

- Applies to: `Full company`, `Departments`, `Positions`, `Employees`; Departments, Positions, and Employees use multi-select controls.
- Effective from/until: optional.
- Clock-in required: `Yes` / `No`; if `No`, selected people/positions are exempt and late handling is hidden.
- Location Verification: required `Yes` / `No`; allowed location range in meters. The same range applies to onsite office and approved remote work location.
- Office location source: Settings > General for the selected company/legal entity. Do not ask for office location or legal entity in Clock-in Policy.
- Remote: first remote clock-in captures current location automatically; later location change requires approval from one eligible owner resolved through Org Structure management coverage.
- Onsite: biometric/card/face/fingerprint can create clock-in. Browser/device location is not required at clock-in; when the device becomes active, verify device location against company office location using the allowed range.

### Late Deduction Rules (Progressive Bracket Model)

The late deduction section contains a rule list that defines progressive brackets for Time Off deduction on late arrival. No separate "grace period" field — a first rule with multiplier 0 serves as the free/no-deduction range.

**Screen content:**

- Late rule list table
- Add late rule button
- Rule rows with columns: **Late arrival minute**, **Multiplier**, **Time Off type**, **Actions**
- No scattered late fields, no old "rounding" labels, no half-day/full-day conversion, no automation wording

**Rule fields per row:**

| Field | Type | Description |
|:------|:-----|:------------|
| Late arrival minute | int | Bracket threshold in minutes; must be positive |
| Multiplier | decimal | Multiplier applied to late minutes in this bracket; 0 = no deduction (free range) |
| Time Off type | select | Time Off type to deduct from |

**Validation:**

- `late_arrival_minute` must be positive
- `multiplier` must be zero or positive
- `time_off_type_id` is required
- Duplicate `late_arrival_minute` values are not allowed within the same policy
- Rules must be sorted by `late_arrival_minute` ascending

**Bracket evaluation algorithm:**

The first rule creates the first bracket covering minute 1 through its `late_arrival_minute`. Every later rule starts from its `late_arrival_minute` and runs until the minute before the next rule. The last rule continues until the actual late minutes.

Rules with non-contiguous thresholds: minutes between a zero-multiplier bracket end and the next rule's `late_arrival_minute` remain in the no-deduction range until the next active threshold starts.

**Example 1** — Three-bracket policy (Annual Time Off):

| Rule | late_arrival_minute | multiplier | Time Off Type |
|:-----|:--------------------|:-----------|:--------------|
| 1 | 10 | 0 | Annual Time Off |
| 2 | 11 | 3 | Annual Time Off |
| 3 | 20 | 5 | Annual Time Off |

Scenario A: Employee is late by 10 minutes.
- Minutes 1–10 × multiplier 0 = 0
- **Result:** Deduct 0 minutes from Annual Time Off.

Scenario B: Employee is late by 14 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–14 × multiplier 3 = 12
- **Result:** Deduct 12 minutes from Annual Time Off.

Scenario C: Employee is late by 23 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–19 × multiplier 3 = 27
- Minutes 20–23 × multiplier 5 = 20
- **Result:** Deduct 47 minutes from Annual Time Off.

**Example 2** — Non-contiguous brackets (Sick Time Off):

| Rule | late_arrival_minute | multiplier | Time Off Type |
|:-----|:--------------------|:-----------|:--------------|
| 1 | 10 | 0 | Sick Time Off |
| 2 | 15 | 3 | Sick Time Off |

Scenario A: Employee is late by 8 minutes.
- Actual late minutes are below the first rule threshold range.
- **Result:** Deduct 0 minutes.

Scenario B: Employee is late by 13 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–13 have no higher rule yet and remain inside the no-deduction range until the next active threshold starts at 15.
- **Result:** Deduct 0 minutes.

Scenario C: Employee is late by 18 minutes.
- Minutes 1–14 are before the 15-minute deduction bracket. Deduction = 0.
- Minutes 15–18 × multiplier 3 = 12
- **Result:** Deduct 12 minutes from Sick Time Off.

### Runtime Preview

The Clock-in Policy screen includes a simple runtime preview:

- Input: example late minutes
- Output: calculated deduction by Time Off type, showing bracket calculation clearly

Preview example (if late minutes = 23, using Example 1 rules):
```
  1–10 min × 0 = 0
 11–19 min × 3 = 27
 20–23 min × 5 = 20
 Total deduction: 47 minutes from Annual Time Off
```

### Insufficient Balance

If the selected Time Off type does not have enough balance to cover the deduction:
- Record an attendance exception or balance issue on the attendance record.
- Surface the issue to the responsible manager or HR coverage owner.
- Do not silently deduct from another Time Off type.

### Manager Notification

- Field label: `Notify assigned owner when late action is applied`
- Preview: `Recipient: Management coverage owner`
- Notify for late minutes deducted and location verification failure outside range.
- Do not add HR Admin selector, Finance Admin selector, Role Group selector, or generic scope dropdown.

### What is NOT Phase 1 late handling

- Workflow/automation-based late deduction (Phase 2)
- Half-day or full-day Time Off conversion
- Fixed dropdown like 1 hour / 4 hours / end of day
- Rounded block-only model
- Day-based Time Off deduction
- Separate "grace period" field (use multiplier 0 first rule instead)
- Separate "rounding block" field

---

## Time Off Balance Interaction

Time Off balances are stored canonically in **minutes** (integer). The UI displays balances as hours and minutes (e.g., "16h 30m available"). An optional approximate day helper may be shown for readability, but days are never used for calculation or storage.

**Schedule does not own Time Off balance.** Schedule decides expected work start time, expected work end time, workdays, break duration, fixed or flexible work mode, whether the employee is late, and how many minutes late. Time Off decides entitlement balance, request balance, deductions, carry forward, and audit history.

**Late deduction connects Attendance to Time Off** by deducting minutes from a selected Time Off type via `ITimeOffService.DeductLateArrivalAsync`. Every late deduction creates a Time Off balance audit entry with source `time_attendance`, the attendance record reference, the policy rule used, and the bracket calculation snapshot.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-attendance/presence` | `attendance:read` | List presence sessions (paginated, filterable) |
| GET | `/api/v1/time-attendance/presence/{employeeId}` | `attendance:read` | Employee presence for date range |
| GET | `/api/v1/monitoring/live` | `monitoring:view` | Real-time monitoring status |
| POST | `/api/v1/time-attendance/clock-in` | `attendance:write-own` | Clock in through an allowed source |
| POST | `/api/v1/time-attendance/clock-out` | `attendance:write-own` | Clock out through an allowed source |
| POST | `/api/v1/time-attendance/breaks/start` | `attendance:write-own` | Start break and pause monitoring |
| POST | `/api/v1/time-attendance/breaks/end` | `attendance:write-own` | End break and resume monitoring |
| GET | `/api/v1/monitoring/device-sessions/{employeeId}` | `monitoring:view` | Device session detail |
| GET | `/api/v1/time-attendance/breaks/{employeeId}` | `attendance:read` | Break records |
| GET | `/api/v1/time-attendance/devices` | `attendance:read` | List biometric/monitoring devices |
| POST | `/api/v1/time-attendance/devices` | `attendance:write` | Register biometric/monitoring device |
| PUT | `/api/v1/time-attendance/devices/{id}` | `attendance:write` | Update biometric/monitoring device |
| POST | `/api/v1/time-attendance/devices/{id}/enrollments` | `attendance:write` | Enroll employees on an attendance/biometric device |
| POST | `/api/v1/time-attendance/biometric/webhook` | HMAC-SHA256 | Receive biometric clock events |
| POST | `/api/v1/time-attendance/biometric-outages` | `attendance:manage` | Enable time-limited onsite web/tray clock-in fallback |
| PUT | `/api/v1/time-attendance/biometric-outages/{id}/resolve` | `attendance:manage` | End outage fallback |
| POST | `/api/v1/time-attendance/attendance-corrections` | `attendance:write` | Submit attendance correction |
| PUT | `/api/v1/time-attendance/attendance-corrections/{id}/approve` | `attendance:approve` | Approve attendance correction |
| POST | `/api/v1/time-attendance/overtime` | `attendance:write` | Submit overtime request |
| PUT | `/api/v1/time-attendance/overtime/{id}/approve` | `attendance:approve` | Approve overtime |
| GET | `/api/v1/shifts` | `attendance:read` | List shifts |
| POST | `/api/v1/shifts` | `attendance:write` | Create shift |
| GET | `/api/v1/time-attendance/schedules` | `attendance:read` | List schedules |
| POST | `/api/v1/time-attendance/schedules` | `attendance:write` | Create schedule |
| POST | `/api/v1/time-attendance/schedules/assign` | `attendance:write` | Assign schedule to employees, positions, departments, or company context |

---

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `ReconcilePresenceSessions` | Every 5 min (work hours) | Merge biometric + agent data -> `presence_sessions` |
| `FlagUnresolvedAbsences` | Daily 10:00 AM | Flag employees with no presence data for the day |
| `CloseOpenSessions` | Daily 11:59 PM | Close any open device sessions and break records |

---

## Important Notes

- **Presence session vs device session:** `presence_sessions` is ONE row per employee per day (unified). `device_sessions` can have MULTIPLE rows per day (one per laptop active/idle cycle). Don't confuse them.
- **This module does NOT handle screenshots or app tracking** - that's [[modules/activity-monitoring/overview|Activity Monitoring]].
- **Biometric/attendance device management** is exposed through Time & Attendance routes (`/api/v1/time-attendance/devices`) because clock-in/out is a monitoring function. Identity Verification owns photo/biometric verification policy and review, but Time & Attendance owns terminal registration, enrollment, and clock event ingestion.
- **Payroll reads from this module** via `ITimeAttendanceService.GetTotalWorkedHoursAsync()`.

## Features

- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]] - Unified presence (one row/employee/day from biometric + agent + manual) - frontend: [[modules/time-attendance/presence-sessions/frontend|Frontend]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]] - Device active/idle cycle tracking (multiple rows/day per laptop)
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]] - Break records with auto-detection from agent idle threshold
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]] - Time & Attendance schedules, fixed/flexible work hours, holiday calendar selection, employee assignments
- [[modules/time-attendance/overtime/overview|Overtime]] - Overtime request and Inbox approval process (Phase 1; Workflow Engine is Phase 2)
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]] - Employee self-service and scoped manager/admin corrections to presence data

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - All presence data is tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] - `PresenceSessionStarted`, `PresenceSessionEnded`, `BreakExceeded`, `OvertimeRequested`
- [[backend/messaging/error-handling|Error Handling]] - Deduplication of biometric + agent data in reconciliation job
- [[security/compliance|Compliance]] - Presence history for payroll and legal record-keeping
- [[database/migration-patterns|Migration Patterns]] - `presence_sessions` UNIQUE on `(tenant_id, employee_id, date)`
- [[current-focus/DEV3-time-attendance-setup|DEV3: Time & Attendance]] - Presence and shift setup task file
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]] - Biometric integration task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/identity-verification/overview|Identity Verification]]

