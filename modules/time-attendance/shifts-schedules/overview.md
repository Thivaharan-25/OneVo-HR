# Shifts & Schedules

**Module:** Time & Attendance
**Feature:** Shifts & Schedules

---

## Purpose

Work schedule creation, public holiday calendar selection, fixed/flexible working hours, break periods, and employee/monitoring-scope assignments for Time & Attendance.

> **UI entry point:** Schedules surface under **Time & Attendance** at `/time-attendance/schedules`. Calendar may display schedule overlays, but schedule management belongs to Time & Attendance.

Schedules are Company-context records. The topbar-selected Company is the operating context for schedule creation, assignment, and permission checks. To manage schedules for another Company, the user switches Company context first and permission is checked again.

## Product Boundary

Time & Attendance contains:

- **Attendance**
- **Schedules**
- **Clock-in Policy**
- **Overtime Rules**

Do not expose **Holiday Calendar**, **Work Weeks**, or **Work Patterns** as Time & Attendance sidebar items. Work-week/work-pattern behavior is handled inside Schedules. Holiday counts open an inline holidays modal from the Schedules table.

## Schedules Screen Contract

The main Schedules table uses exactly these columns:

| Column | Meaning |
|:-------|:--------|
| Name | Schedule title |
| Workdays | Selected working days |
| Work time | Fixed time range or flexible daily duration |
| Break | Break time or break duration used in scheduled working hour calculation |
| Assigned | Count or summary of assigned members |
| Holidays | Public holiday calendar/country attached to the schedule |
| Created At | Schedule creation timestamp |
| Actions | View, edit, duplicate, assign, deactivate/delete as permitted |

## Holiday Country vs Schedule Timezone

Holiday country/calendar is a field on the work schedule. It is used **only** to fetch candidate public holidays from that country. It does not affect timezone, working time, attendance calculation, late rules, overtime, or Time Off conversion.

Schedule start/end times and break times are always interpreted in the **Company timezone** - the `timezone` field on the topbar-selected Company / legal entity record (`legal_entities.timezone`). Holiday country does not change or override this timezone.

Admins select which holidays from the pulled holiday list apply to the schedule. The system does not auto-apply every public holiday unless the admin explicitly selects all.

**Example:**

| Setting | Value |
|:--------|:------|
| Company timezone | `Asia/Colombo` |
| Schedule holiday country | United Kingdom |
| Work time | 09:00-17:00 |
| **Result** | Work starts at **09:00 Asia/Colombo**. UK holidays are the holiday source only. |

If the company wants employees to work London time, the admin must change the Company timezone to `Europe/London` on the Company / legal entity record. Changing the holiday country to United Kingdom does not move the schedule into London time.

---

## Create/Edit Work Schedule Modal

Fields:

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
- Assignment:
  - `Full company`
  - `Departments`
  - `Positions`
  - `Employees`
- Departments, Positions, and Employees use multi-select controls.
- `Default for new employee` toggle

> **All time values are interpreted in the selected Company timezone. Holiday country does not change the timezone.**

Do not use a wizard. Do not use fake quick-duration chips. Use real time inputs.

Scheduled working hours equal work time minus break time. Break is part of schedule calculation; it is not Time Off. Schedule does not own Time Off balance — Time Off balances are stored canonically in minutes and do not depend on schedule length for balance calculation. Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off balance or request duration in Phase 1.

## Holidays Modal

There is no separate **Holiday Calendar** screen under Time & Attendance. The `Holidays` table value is a clickable count/summary that opens a modal.

- Modal title: `{Country} public holidays`
- The modal starts from the list of public holidays pulled for the schedule's selected holiday country
- The admin selects which pulled holidays apply to this schedule. Unselected country holidays do not apply
- The admin can add custom/manual holidays (these are saved with `source = manual` and no `public_holiday_id`)
- Selected and manually added holidays are persisted to `work_schedule_holidays`
- Summary: holiday count (number of selected holidays stored in `work_schedule_holidays`)
- Action: `Add holiday`
- Table columns: `Holiday info`, `Date`, `Uploaded by`, `Actions`
- Add Holiday modal fields: `Title`, `Holiday Type` (`Single day` or `Multiple days`), `Date picker`

There is no separate Holiday Calendar screen under Time & Attendance. Holiday selection is managed per-schedule through this modal.

## Clock-in Policy Boundary

Clock-in Policy is a separate Time & Attendance management screen for who must clock in, location verification, progressive late Time Off deduction rules, notification to the recipient resolved by Monitoring Policy, onsite/remote verification behavior, and date-effective ranges. Scope uses the selected Company context.

Clock-in Policy can apply to `Full company`, `Departments`, `Positions`, or `Employees`. Departments, Positions, and Employees use multi-select controls. Do not ask for schedule start/end/break in Clock-in Policy; those values come from Schedules.

## Assignment and Inheritance

Schedules can be assigned to full company, department, position, or employee override inside the selected Company.

- Higher-level assignments can provide defaults.
- Department or position assignment can narrow the inherited schedule.
- Employee-specific override can replace the inherited schedule.
- Employee-specific schedule override belongs in employee detail / job details / overrides where supported.

## Database Tables

### `shifts`
Shift definitions where the implementation still stores named shifts.

### `work_schedules`
Work schedule definitions with workdays, fixed/flexible working hours, break configuration, and holiday calendar/country reference.

### `shift_assignments`
Employee shift assignment for a specific date, with optional expected work area override.

### `schedule_assignments`
Date-effective assignments to full company, departments, positions, or employee overrides.

### `public_holidays`
Country-level or tenant-level non-working days. The holiday source - pulled/imported by country code. These are candidate holidays that admins can select per schedule.

### `work_schedule_holidays`
Per-schedule holiday selections. Stores which holidays from `public_holidays` (or manually added custom holidays) the admin has selected for a specific work schedule. Only holidays present in this table apply to the schedule. Calendar may display these as holiday overlays.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-attendance/schedules` | `attendance:read` | List schedules |
| POST | `/api/v1/time-attendance/schedules` | `attendance:write` | Create schedule |
| POST | `/api/v1/time-attendance/schedules/assign` | `attendance:write` | Assign schedule to employees, positions, departments, or company context |

Legacy `/api/v1/shifts` endpoints can exist for shift-based storage, but product docs should present the primary user-facing screen as **Schedules**.

## Related

- [[modules/time-attendance/overview|Time & Attendance Module]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]]
- [[modules/time-attendance/overtime/overview|Overtime]]
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-time-attendance-setup|DEV3: Time & Attendance]]
