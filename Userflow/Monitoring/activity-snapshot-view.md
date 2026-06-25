# Activity Snapshot View

**Area:** Monitoring  
**Trigger:** Manager views employee activity data (user action - view only)
**Required Permission(s):** `monitoring:view`  
**Related Permissions:** `monitoring:manage` (export raw data)

---

## Preconditions

- Activity monitoring enabled -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- Employee has agent running -> [[Userflow/Monitoring/agent-deployment|Agent Deployment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Select Employee & Date
- **UI:** Monitoring -> Activity -> select employee -> select date
- **API:** `GET /api/v1/activity/snapshots?employee_id={id}&date={date}`

### Step 2: View Activity Timeline
- **UI:** Horizontal timeline showing:
  - Application usage blocks (color-coded: work=green, communication/meeting=blue, unknown=grey, personal/non-allowed=red)
  - Idle periods
  - Meeting blocks (auto-detected from calendar + app activity)
  - Screenshots (on-demand and auto-deviation thumbnails only, click to enlarge when permitted)
  - Break periods

### Step 3: View Daily Summary
- **UI:** Summary card: activity rate, work-classified app time, total idle time, top 5 apps by duration, activity-derived score, score basis, data coverage, meeting time, first/last activity
- **API:** `GET /api/v1/activity/daily-summary?employee_id={id}&date={date}`
- **Backend:** DailySummaryService -> [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]]

### Step 4: App Usage Breakdown
- **UI:** Bar chart or table: each app with total time, category (work/communication/meeting/personal/unknown), percentage of monitored day

## Variations

### Without screenshot permission
- Timeline shows activity blocks but no screenshot thumbnails

### Date range view
- Select date range -> see aggregated daily summaries -> trend graph over period

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No data for date | Empty state | "No activity data recorded for this date" |
| Agent was offline | Partial data | "Agent offline from 14:00-16:00 - gap in data" |

## Events Triggered

- None (read-only)

## Related Flows

- [[Userflow/Monitoring/live-dashboard|Live Dashboard]]
- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]]

## Module References

- [[modules/activity-monitoring/application-tracking/overview|Application Tracking]]
- [[modules/activity-monitoring/screenshots/overview|Screenshots]]
- [[modules/activity-monitoring/meeting-detection/overview|Meeting Detection]]
- [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
