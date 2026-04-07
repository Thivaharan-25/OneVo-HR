# Screenshots — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Screenshots

---

## Capture Screenshot (via Agent)

### Flow

```
Agent captures screenshot based on policy (scheduled/random)
  -> POST /api/v1/agent/ingest (type: "screenshot")
    -> Agent Gateway routes to ActivityMonitoring
      -> ScreenshotService.ProcessScreenshotAsync(payload, ct)
        -> 1. Check monitoring toggle: screenshot_capture enabled for employee
        -> 2. Upload image to blob storage via IFileService.UploadFileAsync()
           -> Returns file_record_id
        -> 3. INSERT into screenshots table:
           -> employee_id, captured_at, file_record_id, trigger_type
        -> 4. Publish ScreenshotCaptured event (audit trail)
        -> Return Result.Success()
```

## View Screenshot

### Flow

```
GET /api/v1/activity/screenshots/{id}/view
  -> ScreenshotController.View(id)
    -> [RequirePermission("workforce:view")]
    -> ScreenshotService.GetScreenshotUrlAsync(id, ct)
      -> 1. Load screenshot metadata from DB
      -> 2. Verify caller has access (manager of employee or admin)
      -> 3. Generate time-limited signed URL via IFileService
      -> 4. Return redirect to signed blob URL (expires in 5 min)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Screenshot capture disabled | Agent should not send; server skips if received |
| Blob upload failure | Retry 3 times, then log error and skip |
| Screenshot not found | Return 404 |
| Signed URL expired | Client must re-request |

### Edge Cases

- **RESTRICTED data classification** — screenshots are the most sensitive data in the system.
- **Retention policy enforced** by `PurgeExpiredScreenshotsJob` (daily 4:00 AM). Default: 30 days.
- **Screenshots stored in blob storage only** — never in the database. Only metadata lives in `screenshots` table.

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[screenshots/overview|Screenshots Overview]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[agent-gateway|Agent Gateway Module]]
- [[event-catalog]]
- [[error-handling]]
- [[data-classification]]
- [[retention-policies]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
