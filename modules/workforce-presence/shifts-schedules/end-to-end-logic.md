# Shifts & Schedules — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Shifts & Schedules

---

## Create Shift

### Flow

```
POST /api/v1/shifts
  -> ShiftController.Create(CreateShiftCommand)
    -> [RequirePermission("attendance:write")]
    -> ShiftService.CreateAsync(command, ct)
      -> 1. Validate: name, start_time, end_time, type (morning/evening/night/flexible)
      -> 2. INSERT into shifts
      -> Return Result.Success(shiftDto)
```

## Assign Employee to Schedule

### Flow

```
POST /api/v1/schedules/assign
  -> ScheduleController.Assign(AssignScheduleCommand)
    -> [RequirePermission("attendance:write")]
    -> ScheduleService.AssignAsync(command, ct)
      -> 1. Validate employee and shift exist
      -> 2. INSERT into employee_shift_assignments
      -> 3. If employee_work_schedules override exists, it takes precedence
      -> Return Result.Success()
```

### Key Rules

- **Schedule templates** allow bulk assignment of shift patterns.
- **Employee-specific overrides** in `employee_work_schedules` take precedence over standard assignments.

## Related

- [[modules/workforce-presence/shifts-schedules/overview|Shifts & Schedules Overview]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
