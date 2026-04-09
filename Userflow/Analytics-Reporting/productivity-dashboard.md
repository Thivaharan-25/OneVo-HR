# Productivity Dashboard

**Area:** Analytics & Reporting  
**Required Permission(s):** `analytics:view`  
**Related Permissions:** `analytics:export` (download data)

---

## Preconditions

- Activity monitoring running → [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Daily aggregation processed → [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Dashboard
- **UI:** Sidebar → Analytics → Productivity → select period: Day / Week / Month
- **API:** `GET /api/v1/analytics/productivity?period={period}`

### Step 2: View Org-Wide Metrics
- **UI:** Dashboard cards:
  - Avg productive hours per employee
  - Org productivity score (%)
  - Total meeting hours
  - Total idle hours
  - Trend comparison (this period vs previous)

### Step 3: Department Breakdown
- **UI:** Bar chart → departments ranked by avg productivity → click department → see team-level breakdown → click team → see individual employees
- **API:** `GET /api/v1/analytics/productivity?group_by=department`

### Step 4: App Usage Analysis
- **UI:** Top productive apps, top unproductive apps, app category distribution → [[modules/activity-monitoring/application-tracking/overview|Application Tracking]]

### Step 5: Export
- **UI:** Export → CSV/Excel/PDF with current filters and period

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No data for period | Empty | "No activity data available for this period" |
| Insufficient data | Warning | "Data from only 3 out of 50 employees — results may be incomplete" |

## Events Triggered

- None (read-only)

## Related Flows

- [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]]
- [[Userflow/Analytics-Reporting/workforce-snapshot|Workforce Snapshot]]
- [[Userflow/Analytics-Reporting/data-export|Data Export]]

## Module References

- [[modules/productivity-analytics/daily-reports/overview|Daily Reports]]
- [[modules/productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[modules/productivity-analytics/monthly-reports/overview|Monthly Reports]]
- [[modules/productivity-analytics/overview|Productivity Analytics]]
