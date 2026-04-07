# Evaluation Engine — End-to-End Logic

**Module:** Exception Engine
**Feature:** Evaluation Engine (Rule Processor)

---

## Rule Evaluation Logic

### Flow

```
For each rule_type, the evaluation engine applies different logic:

LOW_ACTIVITY:
  -> Get last N snapshots (consecutive_snapshots from threshold)
  -> Calculate idle_percent = idle_seconds / (active_seconds + idle_seconds) * 100
  -> If idle_percent > idle_percent_max for all N consecutive snapshots -> BREACH

EXCESS_IDLE:
  -> Get current presence session
  -> Calculate continuous idle time (no keyboard/mouse events)
  -> If idle_minutes > idle_minutes_threshold -> BREACH
  -> If exclude_breaks = true: subtract break_records duration

EXCESS_MEETING:
  -> Get meeting_sessions for today
  -> Calculate meeting_percent = meeting_minutes / total_work_minutes * 100
  -> If meeting_percent > meeting_percent_max -> BREACH

NO_PRESENCE:
  -> Get employee's shift schedule for today
  -> Check presence_sessions for presence data
  -> If no presence AND minutes_since_shift_start > minutes_after_shift_start -> BREACH

BREAK_EXCEEDED:
  -> Get break_records for today
  -> If any break duration > max_break_minutes -> BREACH
  -> If break_type filter set: only check matching break types

VERIFICATION_FAILED:
  -> Triggered by VerificationFailed event from identity-verification
  -> Auto-creates alert (no polling needed)
```

### Acknowledge Alert

### Flow

```
PUT /api/v1/exceptions/alerts/{id}/acknowledge
  -> AlertController.Acknowledge(id, AcknowledgeCommand)
    -> [RequirePermission("exceptions:acknowledge")]
    -> ExceptionEngineService.AcknowledgeAlertAsync(alertId, userId, comment, ct)
      -> 1. Load alert, verify status = 'new' or 'escalated'
      -> 2. UPDATE alert status = 'acknowledged'
      -> 3. INSERT into alert_acknowledgements
         -> action = 'acknowledged', comment, acted_at
      -> 4. Publish AlertAcknowledged event
      -> Return Result.Success()

```

## Related

- [[exception-engine/evaluation-engine/overview|Evaluation Engine Overview]]
- [[exception-engine/alert-generation/overview|Alert Generation]]
- [[exception-engine/exception-rules/overview|Exception Rules]]
- [[exception-engine/escalation-chains/overview|Escalation Chains]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-exception-engine]]
