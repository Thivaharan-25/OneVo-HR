# Shifts & Schedules - End-to-End Logic

**Module:** Time & Attendance
**Feature:** Shifts & Schedules

---

## Create Work Schedule

### Flow

```
POST /api/v1/time-attendance/schedules
  -> ScheduleController.Create(CreateScheduleCommand)
    -> [RequirePermission("attendance:write")]
    -> Resolve selected Company from topbar/company context
    -> Load selected Company timezone (legal_entities.timezone)
    -> Verify actor has attendance:write in selected Company
    -> ScheduleService.CreateAsync(command, ct)
      -> 1. Validate title, workdays, break settings, and assignment target
      -> 2. Validate holiday_country_code separately from timezone
            Holiday country is the holiday source only - never used for timezone conversion
      -> 3. Validate work_hour_type:
            fixed    -> require start_time, end_time, break_start_time, break_end_time
            flexible -> require daily_duration_hours/minutes and break_duration_hours/minutes
      -> 4. Store schedule times as local time values interpreted against selected Company timezone
      -> 5. Validate real time values and calculate scheduled working hours as work time minus break time
      -> 6. Store holiday_country_code as holiday source reference
      -> 7. INSERT into work_schedules
      -> 8. Load candidate public holidays for the selected holiday_country_code
      -> 9. Persist admin-selected holidays into work_schedule_holidays:
            - For each selected country holiday: source = country_public_holiday, public_holiday_id set, date/name copied
            - For each manual custom holiday added by admin: source = manual, public_holiday_id null, date/name entered
            - Holidays not selected by the admin are not inserted - they do not apply to this schedule
            - The system never auto-applies all country holidays unless the admin explicitly selects all
      -> 10. If default_for_new_employee is supported, mark default within selected Company scope
      -> Return Result.Success(scheduleDto)
```

> **Rule:** Holiday country is never used for timezone conversion. Schedule times are interpreted in `legal_entities.timezone` for the selected Company.

### UI Contract

The Schedules table columns are: **Name**, **Workdays**, **Work time**, **Break**, **Assigned**, **Holidays**, **Created At**, **Actions**.

Do not expose Holiday Calendar, Work Weeks, or Work Patterns as active standalone screens. Rotating/multi-week behavior belongs inside Schedules. Clicking the Holidays count opens the `{Country} public holidays` modal.

## Assign Employees to Schedule

### Flow

```
POST /api/v1/time-attendance/schedules/assign
  -> ScheduleController.Assign(AssignScheduleCommand)
    -> [RequirePermission("attendance:write")]
    -> ScheduleService.AssignAsync(command, ct)
      -> 1. Validate schedule exists
      -> 2. Validate selected Full company, Departments, Positions, or Employees are inside selected Company and within actor authority
      -> 3. INSERT assignment rows
      -> 4. Apply inheritance: company default -> department -> position -> employee override where supported
      -> 5. Employee-specific overrides take precedence over broader scope assignment
      -> Return Result.Success()
```

### Key Rules

- **Schedules** are the user-facing management surface.
- **Company context** comes from the topbar. Schedule create/update/assignment actions are limited to the selected Company and require permission in that Company.
- **Clock-in Policy** is separate and owns who must clock in, location verification, progressive late Time Off deduction rules, notification to the recipient resolved by Monitoring Policy, onsite/remote verification behavior, and date-effective ranges.
- **Clock-in eligibility** can vary by full company, department, position, or employee where supported.
- **Public holidays** come from the schedule's selected holiday country/calendar. The admin selects which holidays from that country apply. Holiday country is for holiday selection only - it does not affect timezone.
- **Schedule timezone** is the Company timezone (`legal_entities.timezone`). All schedule start/end/break times are interpreted in the Company timezone.
- **No fake quick-duration chips** for schedule time. Use real time inputs.

## Related

- [[modules/time-attendance/shifts-schedules/overview|Shifts & Schedules Overview]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]]
- [[modules/time-attendance/overtime/overview|Overtime]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
