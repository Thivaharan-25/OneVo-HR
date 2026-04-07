# Device Tracking — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Device Tracking

---

## Track Device Usage

### Flow

```
ProcessRawBufferJob (processes device_session data from raw buffer)
  -> DeviceTrackingService.ProcessDeviceDataAsync(employeeId, date, ct)
    -> 1. Query device_sessions for employee for the day
       -> SUM active_minutes -> laptop_active_minutes
    -> 2. Estimate mobile usage from gap analysis:
       -> If presence_session shows employee present but no laptop activity
       -> estimated_mobile_minutes = gap_minutes
    -> 3. Compute laptop_percentage = laptop / (laptop + mobile) * 100
    -> 4. UPSERT into device_tracking
       -> (tenant_id, employee_id, date) unique
    -> 5. Set detection_method = 'agent'
```

## Get Device Tracking Data (API)

### Flow

```
GET /api/v1/activity/summary/{employeeId}?date=2026-04-05
  -> (Included in daily summary response as device split data)
  -> ActivityMonitoringService.GetDailySummaryAsync includes device_tracking query
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| No device sessions for day | No device_tracking row created |
| Multiple devices for one employee | Sum across all devices |
| Manual attendance (no agent) | detection_method = 'manual', laptop_active_minutes = 0 |

### Edge Cases

- **Mobile estimation is approximate** — based on presence gaps, not actual mobile tracking.
- **Multiple devices:** If employee uses both desktop and laptop, sessions from both contribute to `laptop_active_minutes`.

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[device-tracking/overview|Device Tracking Overview]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[daily-aggregation/end-to-end-logic|Daily Aggregation — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
