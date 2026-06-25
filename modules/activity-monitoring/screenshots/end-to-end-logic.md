# Screenshots - End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Screenshots

---

## Capture Screenshot (via Agent)

### Flow

```
Authorized user explicitly requests screenshot command, or monitoring detects a deviation while auto screenshot capture is enabled
  -> Agent Gateway creates capture_screenshot command
  -> Agent receives command through SignalR or command polling
  -> Agent captures screenshot with trigger_type = on_demand or auto_deviation
  -> POST /api/v1/agent/ingest (type: "screenshot_capture")
    -> Agent Gateway routes to ActivityMonitoring
      -> ScreenshotService.ProcessScreenshotAsync(payload, ct)
        -> 1. Check effective monitoring policy: screenshot_capture enabled for employee
        -> 2. Validate trigger_type is on_demand or auto_deviation
        -> 3. Upload image to blob storage via IFileService.UploadFileAsync()
           -> Returns file_record_id
        -> 4. INSERT into monitoring_evidence_assets:
           -> employee_id, captured_at, file_record_id, evidence_type = screenshot, trigger_type, metadata
        -> 5. Publish ScreenshotCaptured event (audit trail)
        -> Return Result.Success()
```

Interval and random screenshot capture are not supported. For `auto_deviation`, the deviation reason is stored in metadata, not as a separate trigger type.

## View Screenshot

### Flow

```
GET /api/v1/activity/screenshots/{id}/view
  -> ScreenshotController.View(id)
    -> [RequirePermission("monitoring:view")]
    -> ScreenshotService.GetScreenshotUrlAsync(id, ct)
      -> 1. Load screenshot evidence metadata from DB
      -> 2. Verify caller has access (manager of employee or admin)
      -> 3. Generate time-limited signed URL via IFileService
      -> 4. Return signed blob URL (expires in 15 min)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Screenshot capture disabled | Agent should not send; server skips if received |
| Invalid trigger type | Return 422 and do not store screenshot |
| Blob upload failure | Retry 3 times, then log error and skip |
| Screenshot not found | Return 404 |
| Signed URL expired | Client must re-request |

### Edge Cases

- **RESTRICTED data classification** - screenshots are the most sensitive data in the system.
- **Retention policy enforced** by `PurgeExpiredMonitoringEvidenceJob` (daily 4:00 AM). Default: 30 days.
- **Screenshots stored in blob storage only** - never in the database. Only evidence metadata lives in `monitoring_evidence_assets`.

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/activity-monitoring/screenshots/overview|Screenshots Overview]]
- [[modules/activity-monitoring/raw-data-processing/end-to-end-logic|Raw Data Processing - End-to-End Logic]]
- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/data-collection|Agent Data Collection]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
