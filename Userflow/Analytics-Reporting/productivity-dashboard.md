# Productivity Dashboard

**Area:** Analytics & Reporting  
**Required Permission(s):** `analytics:view`  
**Related Permissions:** `analytics:export` (download data)

---

## Preconditions

- Activity monitoring running → [[monitoring-configuration]]
- Daily aggregation processed → [[activity-snapshot-view]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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
- **UI:** Top productive apps, top unproductive apps, app category distribution → [[application-tracking]]

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

- [[activity-snapshot-view]]
- [[workforce-snapshot]]
- [[data-export]]

## Module References

- [[daily-reports]]
- [[weekly-reports]]
- [[monthly-reports]]
- [[productivity-analytics]]
