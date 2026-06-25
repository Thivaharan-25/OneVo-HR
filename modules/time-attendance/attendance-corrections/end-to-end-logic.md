# Attendance Corrections - End-to-End Logic

**Module:** Time & Attendance
**Feature:** Attendance Corrections

---

## Submit Correction

### Flow

```
POST /api/v1/time-attendance/attendance-corrections
  -> AttendanceCorrectionController.Submit(SubmitCorrectionCommand)
    -> [RequirePermission("attendance:write")]
    -> AttendanceCorrectionService.SubmitAsync(command, ct)
      -> 1. Validate employee_id/session_id, date, corrected values, reason, and actor scope
      -> 2. Validate correction_type is one of: clock_in, clock_out, break, full_day, other
      -> 3. INSERT into attendance_corrections
         -> original_value and corrected_value for audit trail
      -> 3. If policy requires approval:
           -> status = pending
         Else if authorized direct correction:
           -> apply correction
      -> 4. Trigger re-reconciliation for affected date + employee when applied
      -> 5. Publish AttendanceCorrectionRequested or AttendanceCorrected event
      -> Return Result.Success(correctionDto)
```

### Key Rules

- The attendance screen is a self-service operational screen for own attendance summary, attendance log/history, overtime requests, and correction requests.
- Managers keep their own self-attendance screen.
- Managers with scoped visibility can view employee attendance inside their allowed area.
- Preferred correction entry is row/session-level from attendance history. A top-level shortcut, if present, is secondary.
- Corrections are audited and trigger re-reconciliation when applied.

## Related

- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections Overview]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
