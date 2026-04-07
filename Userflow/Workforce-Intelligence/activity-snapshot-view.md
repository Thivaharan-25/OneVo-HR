# Activity Snapshot View

**Area:** Workforce Intelligence  
**Required Permission(s):** `workforce:view`  
**Related Permissions:** `workforce:manage` (export raw data)

---

## Preconditions

- Activity monitoring enabled → [[monitoring-configuration]]
- Employee has agent running → [[agent-deployment]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Select Employee & Date
- **UI:** Workforce → Activity → select employee → select date
- **API:** `GET /api/v1/activity/snapshots?employee_id={id}&date={date}`

### Step 2: View Activity Timeline
- **UI:** Horizontal timeline showing:
  - Application usage blocks (color-coded: productive=green, neutral=grey, unproductive=red)
  - Idle periods
  - Meeting blocks (auto-detected from calendar + app activity)
  - Screenshots (thumbnails at intervals, click to enlarge)
  - Break periods

### Step 3: View Daily Summary
- **UI:** Summary card: total productive hours, total idle time, top 5 apps by duration, productivity score (%), meeting time, first/last activity
- **API:** `GET /api/v1/activity/daily-summary?employee_id={id}&date={date}`
- **Backend:** DailySummaryService → [[daily-aggregation]]

### Step 4: App Usage Breakdown
- **UI:** Bar chart or table: each app with total time, category (productive/neutral/unproductive), percentage of day

## Variations

### Without screenshot permission
- Timeline shows activity blocks but no screenshot thumbnails

### Date range view
- Select date range → see aggregated daily summaries → trend graph over period

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No data for date | Empty state | "No activity data recorded for this date" |
| Agent was offline | Partial data | "Agent offline from 14:00-16:00 — gap in data" |

## Events Triggered

- None (read-only)

## Related Flows

- [[live-dashboard]]
- [[monitoring-configuration]]
- [[exception-rule-setup]]
- [[productivity-dashboard]]

## Module References

- [[application-tracking]]
- [[screenshots]]
- [[meeting-detection]]
- [[daily-aggregation]]
- [[activity-monitoring]]
