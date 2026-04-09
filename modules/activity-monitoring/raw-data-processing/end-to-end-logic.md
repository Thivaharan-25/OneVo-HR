# Raw Data Processing — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Raw Data Processing

---

## Ingest Raw Activity Data

### Flow

```
Agent Gateway POST /api/v1/agent/ingest (202 Accepted)
  -> writes batch to activity_raw_buffer via COPY/unnest()
  -> ProcessRawBufferJob (Hangfire, every 2 min)
    -> RawDataProcessor.ProcessBatchAsync(batchId, ct)
      -> 1. Read unprocessed rows from activity_raw_buffer
      -> 2. Validate payload_json schema (discard malformed)
      -> 3. Resolve employee_id from agent_device_id via registered_agents
      -> 4. Check monitoring toggle: IConfigurationService.GetMonitoringTogglesAsync()
         -> If activity_monitoring = false for employee -> skip, log warning
      -> 5. Parse payload by type:
         -> "activity_snapshot" -> INSERT into activity_snapshots
            -> Compute intensity_score = (keyboard + mouse) / max_expected * 100, cap at 100
         -> "app_usage" -> UPSERT into application_usage
            -> Hash window_title with SHA-256 (never store raw)
            -> Lookup application_categories for is_productive flag
         -> "meeting_app_detected" -> INSERT into meeting_sessions
         -> "device_session" -> INSERT into device_sessions (workforce_presence)
      -> 6. Publish ActivitySnapshotReceived event
      -> 7. Mark raw rows as processed (or rely on partition drop)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Malformed payload_json | Skip row, log warning with agent_device_id |
| Unknown agent_device_id | Skip entire batch, return 401 on next heartbeat |
| Employee not linked to device | Skip activity rows, device_session still recorded |
| Monitoring disabled for employee | Skip all activity processing, log info |
| DB insert failure | Retry batch up to 3 times, then move to dead letter |

### Edge Cases

- **Agent sends duplicate batch:** `activity_raw_buffer` has no dedup — duplicates are dropped during snapshot insert via `(tenant_id, employee_id, captured_at)` unique constraint check.
- **Employee logs out mid-batch:** Partial data is still processed; device_session gets `session_end` set on next reconciliation.
- **Raw buffer partition drop:** `PurgeRawBufferJob` drops daily partitions older than 48h — processing must complete within this window.

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[frontend/architecture/overview|Raw Data Processing Overview]]
- [[modules/activity-monitoring/application-tracking/end-to-end-logic|Application Tracking — End-to-End Logic]]
- [[modules/activity-monitoring/meeting-detection/end-to-end-logic|Meeting Detection — End-to-End Logic]]
- [[modules/activity-monitoring/screenshots/end-to-end-logic|Screenshots — End-to-End Logic]]
- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[code-standards/logging-standards|Logging Standards]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
