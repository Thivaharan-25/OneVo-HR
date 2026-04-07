# Meeting Detection — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Meeting Detection

---

## Get Meeting Sessions

### Flow

```
GET /api/v1/activity/meetings/{employeeId}?date=2026-04-05
  -> ActivityController.GetMeetings(employeeId, date)
    -> [RequirePermission("workforce:view")]
    -> ActivityMonitoringService.GetMeetingsAsync(employeeId, date, ct)
      -> 1. Query meeting_sessions WHERE employee_id AND date range
      -> 2. Map to List<MeetingSessionDto>
         -> Include: platform, duration_minutes, had_camera_on, had_mic_activity
      -> Return Result.Success(meetingDtos)
```

## Meeting Detection Pipeline (within ProcessRawBufferJob)

### Flow

```
ProcessRawBufferJob
  -> For each activity_snapshot with foreground_app matching meeting apps:
    -> 1. Check against known patterns: Teams.exe, zoom.exe, meet.google.com
    -> 2. If new meeting detected (no open session for this platform):
       -> INSERT meeting_sessions with meeting_start = captured_at
    -> 3. If existing session and app still foreground:
       -> UPDATE meeting_end = captured_at, recalculate duration_minutes
    -> 4. If meeting app no longer foreground:
       -> Close session: set meeting_end to last snapshot with meeting app
    -> 5. Detect camera/mic via process inspection data in payload
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Unknown meeting app | Not detected — only known platforms tracked in Phase 1 |
| Overlapping meetings on different platforms | Both recorded separately |
| Agent gap (laptop sleep) | Session stays open; closed by CloseOpenSessions job at EOD |

### Edge Cases

- **Phase 1 limitation:** Detection is process-name based only. No calendar integration.
- **Phase 2:** Microsoft Teams Graph API will provide rich meeting data (participants, duration, recording status).
- **Short meetings (< 2 min):** Still recorded but flagged in aggregation as potential false positives.

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[meeting-detection/overview|Meeting Detection Overview]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[daily-aggregation/end-to-end-logic|Daily Aggregation — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
