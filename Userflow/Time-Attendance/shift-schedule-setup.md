# Shift & Schedule Setup

**Area:** Time & Attendance / Time & Attendance
**Trigger:** Authorized user creates a work schedule and assigns employees (user action - configuration)
**Required Permission(s):** `attendance:write`
**Related Permissions:** scoped attendance assignment permission

---

## Preconditions

- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- A Company is selected in the topbar.
- A public holiday country/calendar is selected per work schedule. This is the holiday source only and does not affect the Company timezone.

## Navigation Boundary

Time & Attendance contains exactly these operational screens:

- **Attendance**
- **Schedules**
- **Clock-in Policy**
- **Overtime Rules**

Do not document **Holiday Calendar**, **Work Weeks**, or **Work Patterns** as active standalone screens. Older work-week/work-pattern behavior is handled inside **Schedules**. Public holidays are reached from the Schedules table `Holidays` count/modal.

## Schedules Screen

The main schedule table uses exactly these columns:

| Column | Meaning |
|:-------|:--------|
| Name | Schedule title |
| Workdays | Selected working days |
| Work time | Fixed time range or flexible daily duration |
| Break | Break time or break duration used in scheduled working hour calculation |
| Working Area | Default or per-day expected work area setting |
| Assigned | Count or summary of assigned members |
| Holidays | Public holiday calendar/country attached to the schedule |
| Created At | Schedule creation timestamp |
| Actions | View, edit, duplicate, assign, deactivate/delete as permitted |

## Flow Steps

### Step 1: Open Schedules
- **UI:** Time & Attendance -> Schedules -> "Create Work Schedule"
- **API:** `GET /api/v1/time-attendance/schedules`

### Step 2: Create Work Schedule
- **UI modal fields:**
  - `Title` (required)
  - `Public holiday country/calendar` - holiday source only; does not affect timezone
  - `Workdays`
  - `Work hour type`: `Fixed work hour` or `Flexible work hour`
  - Fixed work hour:
    - `Start time`
    - `End time`
    - `Break start time`
    - `Break end time`
  - Flexible work hour:
    - `Daily duration hours/minutes`
    - `Break duration hours/minutes`
  - **Working Area** (after Workdays):
    - `Same for all selected days` — dropdown: Onsite / Remote / Either / Field
    - `Custom by day` — each selected workday shows a dropdown: Onsite / Remote / Either / Field
    - Example (Custom by day for hybrid schedule):
      - Monday: Onsite
      - Tuesday: Remote
      - Wednesday: Remote
      - Thursday: Remote
      - Friday: Onsite
    - One schedule handles all work area combinations. Do not require admins to create two schedules for one hybrid employee to split onsite and remote days.
  - Assignment:
    - `Full company`
    - `Departments`
    - `Positions`
    - `Employees`
  - Departments, Positions, and Employees use multi-select controls.
  - `Default for new employee` toggle
- **Note:** All time values are interpreted in the selected Company timezone (`legal_entities.timezone`). Holiday country does not change the timezone.
- **API:** `POST /api/v1/time-attendance/schedules`
- **Backend:** ScheduleService.CreateAsync() -> [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- **DB:** `work_schedules`

Do not use a wizard. Do not use fake quick-duration chips for working time. Use real time inputs.

Scheduled working hours equal work time minus break time. Break is part of schedule calculation; it is not Time Off. Schedule does not own Time Off balance — Time Off balances are stored canonically in minutes and do not depend on schedule length for balance calculation. Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off balance or request duration in Phase 1.

### Step 3: Assign to Employees or Time & Attendance Scope
- **UI:** Select assignment targets: Full company, Departments, Positions, or Employees inside the selected Company.
- **API:** `POST /api/v1/time-attendance/schedules/assign`
- **DB:** `schedule_assignments`

Schedules can inherit from higher-level assignments. A Company default can apply broadly, department or position assignment can narrow it, and employee-specific override can replace the inherited schedule. Where employee-specific overrides exist, document them in employee detail / job details / overrides, not as a separate hidden screen.

### Step 4: Holidays Modal
- **UI:** Click the `Holidays` count/summary in the Schedules table.
- **Modal title:** `{Country} public holidays`
- The modal shows holidays available from the selected holiday country on this schedule.
- The admin selects only the holidays that apply to this schedule. Not all public holidays from the country are forced onto the schedule.
- **Modal content:** selected holiday count, `Add holiday` button, and table columns `Holiday info`, `Date`, `Uploaded by`, `Actions`.
- **Add Holiday modal:** `Title`, `Holiday Type` (`Single day` or `Multiple days`), `Date picker`.

### Step 5: Confirmation
- Employees see assigned schedules in **Attendance** and **Calendar**.
- Schedule time determines late/early flags and overtime thresholds. Schedule times are interpreted in the Company timezone (`legal_entities.timezone`).
- Public holidays come from the schedule's selected holiday country. Admin-selected holidays apply; they are not auto-applied unless the admin explicitly selects all.

## Clock-in Policy Boundary

Clock-in policy is a separate Time & Attendance management screen. It owns:

- Who must clock in.
- Location verification and allowed range.
- Progressive late Time Off deduction rules (bracket model with multiplier per threshold).
- Notification to the recipient resolved by Monitoring Policy.
- Onsite/remote verification behavior.
- Date-effective ranges.
- Applies to: Full company, Departments, Positions, Employees.

Do not ask for schedule start/end/break in Clock-in Policy; those values come from Schedules.

## Variations

### Rotating schedules
- Rotating behavior can be configured inside Schedules; it is not a separate Work Patterns screen.

### Holiday overrides
- Each schedule has its own holiday country/calendar. The admin selects which holidays from that country apply. Holiday country is for holiday selection only - it does not affect the Company timezone or schedule time interpretation.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Overlapping schedule assignment | Validation fails | "Employee already has a schedule for this time" |
| Break exceeds work duration | Validation fails | "Break cannot exceed work duration" |
| Missing public holiday calendar | Validation fails when required by policy | "Select a public holiday calendar" |

## Events Triggered

- `ScheduleCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `ScheduleAssigned` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- [[Userflow/Time-Attendance/overtime-management|Overtime Management]]
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]

## Module References

- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[modules/time-attendance/overview|Time & Attendance]]

## Connection to Work Management

Schedule data from this flow feeds directly into WMS Resource Management:

- **Capacity baseline:** Each employee's scheduled hours per day/week become the capacity baseline in WMS Resource Planning (`CAPACITY_SNAPSHOT`).
- **Overtime threshold:** When an employee's WMS time logs exceed scheduled hours, the excess is flagged as potential overtime. The overtime entry (`OVERTIME_ENTRY`) is created automatically when the timesheet is approved.
- **Availability for sprint planning:** Resource management uses scheduled hours to determine how many hours an employee can realistically be allocated to a project sprint.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] and [[Userflow/Work-Management/resource-flow|Resource Management Flow]].
