# Exception Dashboard

**Area:** Exception Engine  
**Required Permission(s):** `exceptions:view`  
**Related Permissions:** `analytics:view` (trend analysis)

---

## Preconditions

- Exception rules active → [[exception-rule-setup]]
- Alerts generated → [[alert-review]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Dashboard
- **UI:** Sidebar → Exceptions → Dashboard
- **API:** `GET /api/v1/exceptions/dashboard`

### Step 2: View Overview
- **UI:** Cards showing:
  - Total active alerts (by severity: critical/high/medium/low)
  - Alerts this week vs last week (trend arrow)
  - Average time to acknowledge
  - Top triggered rules (bar chart)
  - Top employees by alert count

### Step 3: Filter & Drill Down
- **UI:** Filter by: department, date range, severity, rule type → click any chart element to see individual alerts
- Links: [[alert-review]]

### Step 4: Export
- **UI:** Export dashboard data → PDF report or CSV
- Links: [[data-export]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No alerts exist | Empty state | "No exceptions detected — all clear" |

## Events Triggered

- None (read-only dashboard)

## Related Flows

- [[exception-rule-setup]]
- [[alert-review]]
- [[productivity-dashboard]]

## Module References

- [[exception-engine]]
- [[alert-generation]]
- [[exception-rules]]
