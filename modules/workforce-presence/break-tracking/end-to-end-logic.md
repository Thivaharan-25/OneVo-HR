# Break Tracking — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Break Tracking

---

## Record Break

### Flow

```
Break is either auto-detected or manually created:

Auto-Detection (from device_sessions):
  -> If idle > configured threshold -> INSERT break_records (auto_detected = true)

Manual Entry:
POST /api/v1/workforce/breaks
  -> BreakController.Start(StartBreakCommand)
    -> [Authenticated]
    -> BreakService.StartAsync(command, ct)
      -> INSERT into break_records
         -> break_type: lunch, prayer, smoke, personal, other
         -> break_end = null (ongoing)
      -> Return Result.Success(breakDto)

End Break:
PUT /api/v1/workforce/breaks/{id}/end
  -> BreakController.End(id)
    -> UPDATE break_end = now
    -> If duration > allowed break time:
       -> Publish BreakExceeded event
       -> Exception engine may create alert
```

### Key Rules

- **Auto-detected breaks** are created when agent reports idle time exceeding configured threshold.
- **Break duration tracked** against allowed break time per shift for exception detection.

## Related

- [[break-tracking|Break Tracking Overview]]
- [[device-sessions]]
- [[presence-sessions]]
- [[shifts-schedules]]
- [[event-catalog]]
- [[error-handling]]
