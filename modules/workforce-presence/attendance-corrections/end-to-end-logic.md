# Attendance Corrections — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Attendance Corrections

---

## Submit Correction

### Flow

```
POST /api/v1/workforce/corrections
  -> CorrectionController.Submit(SubmitCorrectionCommand)
    -> [RequirePermission("attendance:write")]
    -> CorrectionService.SubmitAsync(command, ct)
      -> 1. Validate: employee_id, date, corrected values
      -> 2. INSERT into attendance_corrections
         -> original_value and corrected_value for audit trail
      -> 3. Trigger re-reconciliation:
         -> ReconcilePresenceSessions for affected date + employee
      -> 4. Publish AttendanceCorrected event (audit trail)
      -> Return Result.Success(correctionDto)
```

### Key Rules

- **Corrections override both biometric and agent data** — they are the highest-priority source.
- **Re-reconciliation** runs immediately after correction to update `presence_sessions`.
- **Audit trail** via `attendance_corrections` table shows what was changed and by whom.

## Related

- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections Overview]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
