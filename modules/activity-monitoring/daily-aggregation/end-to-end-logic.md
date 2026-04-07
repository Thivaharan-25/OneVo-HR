# Daily Aggregation — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Daily Aggregation

---

## Aggregate Daily Summary

### Flow

```
AggregateDailySummaryJob (Hangfire, every 30 min during work hours + EOD)
  -> DailyAggregationService.AggregateAsync(tenantId, date, ct)
    -> 1. Get all employees with activity data for today
    -> 2. For each employee:
       -> a. Query activity_snapshots for the day
          -> SUM active_seconds -> total_active_minutes
          -> SUM idle_seconds -> total_idle_minutes
          -> AVG intensity_score -> intensity_avg
          -> SUM keyboard_events_count -> keyboard_total
          -> SUM mouse_events_count -> mouse_total
       -> b. Query meeting_sessions for the day
          -> SUM duration_minutes -> total_meeting_minutes
       -> c. Query application_usage for the day
          -> TOP 5 by total_seconds -> top_apps_json
       -> d. Compute active_percentage = active / (active + idle) * 100
       -> e. UPSERT into activity_daily_summary
          -> INSERT ... ON CONFLICT (tenant_id, employee_id, date) DO UPDATE
    -> 3. Publish DailySummaryAggregated event
```

## Get Daily Summary (API)

### Flow

```
GET /api/v1/activity/summary/{employeeId}?date=2026-04-05
  -> ActivityController.GetSummary(employeeId, date)
    -> [RequirePermission("workforce:view")]
    -> ActivityMonitoringService.GetDailySummaryAsync(employeeId, date, ct)
      -> Query activity_daily_summary WHERE employee_id AND date
      -> Map to ActivityDailySummaryDto
      -> Return Result.Success(summaryDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| No activity data for employee | Skip employee in aggregation, no summary row created |
| Partial day (employee left early) | Summary reflects partial data; updated on next aggregation run |
| Concurrent aggregation runs | UPSERT handles this — last writer wins with latest data |

### Edge Cases

- **activity_daily_summary is the ONLY activity table that allows UPDATE** — all others are append-only.
- **Retention:** Daily summaries kept for 2 years (small, pre-aggregated). Snapshots only 90 days.
- **Off-hours aggregation:** Job runs at end of day to finalize, but also every 30 min for near-real-time dashboard.

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[daily-aggregation/overview|Daily Aggregation Overview]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[application-tracking/end-to-end-logic|Application Tracking — End-to-End Logic]]
- [[meeting-detection/end-to-end-logic|Meeting Detection — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[retention-policies]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
