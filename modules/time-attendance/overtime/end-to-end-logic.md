# Overtime - End-to-End Logic

**Module:** Time & Attendance
**Feature:** Overtime Requests

---

## Submit Overtime Request

### Flow

```
POST /api/v1/time-attendance/overtime
  -> OvertimeController.Submit(SubmitOvertimeCommand)
    -> [RequirePermission("attendance:write")]
    -> OvertimeService.SubmitAsync(command, ct)
      -> 1. Validate: date, expected_hours, reason
      -> 2. INSERT into overtime_records (status = 'pending')
      -> 3. Resolve one eligible owner through management coverage
      -> 4. Publish OvertimeRequested event (notify assigned owner through Notifications, or create routing issue)
      -> Return Result.Success(overtimeDto)
```

## Approve Overtime

### Flow

```
PUT /api/v1/time-attendance/overtime/{id}/approve
  -> OvertimeController.Approve(id)
    -> [RequirePermission("attendance:approve")]
    -> OvertimeService.ApproveAsync(id, ct)
      -> 1. UPDATE overtime_records: status = 'approved'
      -> 2. Add overtime_hours to payroll calculation for the period
      -> Return Result.Success()
```

### Key Rules

- **Auto-detection:** If `total_present_minutes > scheduled_minutes`, system auto-flags for overtime review.
- **Overtime flows to payroll** via `ITimeAttendanceService`.

## Related

- [[modules/time-attendance/overtime/overview|Overtime Overview]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
