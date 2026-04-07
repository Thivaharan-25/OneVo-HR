# Overtime — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Overtime Requests

---

## Submit Overtime Request

### Flow

```
POST /api/v1/workforce/overtime
  -> OvertimeController.Submit(SubmitOvertimeCommand)
    -> [RequirePermission("attendance:write")]
    -> OvertimeService.SubmitAsync(command, ct)
      -> 1. Validate: date, expected_hours, reason
      -> 2. INSERT into overtime_requests (status = 'pending')
      -> 3. Trigger workflow engine for approval
         -> IWorkflowService.CreateInstanceAsync("OvertimeRequest", requestId)
      -> 4. Publish OvertimeRequested event (notify manager)
      -> Return Result.Success(overtimeDto)
```

## Approve Overtime

### Flow

```
PUT /api/v1/workforce/overtime/{id}/approve
  -> OvertimeController.Approve(id)
    -> [RequirePermission("attendance:approve")]
    -> OvertimeService.ApproveAsync(id, ct)
      -> 1. UPDATE overtime_requests: status = 'approved'
      -> 2. Add overtime_hours to payroll calculation for the period
      -> Return Result.Success()
```

### Key Rules

- **Auto-detection:** If `total_present_minutes > scheduled_minutes`, system auto-flags for overtime review.
- **Overtime flows to payroll** via `IWorkforcePresenceService`.

## Related

- [[overtime|Overtime Overview]]
- [[presence-sessions]]
- [[shifts-schedules]]
- [[attendance-corrections]]
- [[event-catalog]]
- [[error-handling]]
