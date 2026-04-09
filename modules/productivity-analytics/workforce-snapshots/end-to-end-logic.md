# Workforce Snapshots — End-to-End Logic

**Module:** Productivity Analytics
**Feature:** Workforce Snapshots

---

## Get Workforce Snapshot

### Flow

```
GET /api/v1/analytics/workforce?date=2026-04-05
  -> AnalyticsController.GetWorkforceSnapshot(date)
    -> [RequirePermission("analytics:view")]
    -> ProductivityAnalyticsService.GetWorkforceSnapshotAsync(date, ct)
      -> Query workforce_snapshot WHERE date
      -> Return: total_employees, active_count, avg_active_percentage,
         total_exceptions, department_breakdown_json
      -> Return Result.Success(snapshotDto)
```

### Key Rules

- **Includes ALL active employees** — even those with monitoring disabled (they show presence data only).
- **For real-time data, use workforce-presence** `GetLiveWorkforceStatusAsync()` — snapshots are historical.
- **Department breakdown** allows drill-down into per-department metrics.

## Related

- [[frontend/architecture/overview|Workforce Snapshots Overview]]
- [[frontend/architecture/overview|Daily Reports]]
- [[frontend/architecture/overview|Monthly Reports]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
