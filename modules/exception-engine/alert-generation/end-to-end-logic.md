# Alert Generation — End-to-End Logic

**Module:** Exception Engine
**Feature:** Alert Generation

---

## Exception Engine Evaluation

### Flow

```
ExceptionEngineEvaluationJob (Hangfire, every 5 min during work hours)
  -> ExceptionEvaluationService.EvaluateAsync(tenantId, ct)
    -> 1. Check exception_schedules: is it within active hours?
       -> If not -> skip evaluation, return
    -> 2. Load all active exception_rules for tenant
    -> 3. For each rule:
       -> a. Determine target employees (all / department / team / specific)
       -> b. For each employee:
          -> Check monitoring enabled: IConfigurationService
             -> If disabled -> skip
          -> Fetch relevant data based on rule_type:
             -> low_activity: IActivityMonitoringService.GetSnapshotsAsync()
             -> excess_idle: IWorkforcePresenceService.GetDeviceSessionsAsync()
             -> no_presence: IWorkforcePresenceService.GetPresenceForDateAsync()
             -> break_exceeded: break_records query
          -> Evaluate threshold_json against fetched data
          -> If breached:
             -> Check for existing active alert (dedup: same rule + employee + status != acknowledged)
             -> If no existing alert:
                -> Capture data_snapshot_json (evidence)
                -> INSERT into exception_alerts (status = 'new')
                -> Publish ExceptionAlertCreated event
    -> 4. Done
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid threshold_json on rule | Skip rule, log warning |
| Data service unavailable | Skip evaluation cycle, retry on next run |
| Duplicate alert (dedup) | Skip — existing active alert covers this condition |

## Related

- [[frontend/architecture/overview|Alert Generation Overview]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[frontend/architecture/overview|Exception Rules]]
- [[frontend/architecture/overview|Escalation Chains]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
