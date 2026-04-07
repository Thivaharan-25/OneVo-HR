# Workforce Snapshot

**Area:** Analytics & Reporting  
**Required Permission(s):** `analytics:view`  
**Related Permissions:** `employees:read` (headcount detail)

---

## Preconditions

- Employees exist in system → [[employee-onboarding]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Current Snapshot
- **UI:** Analytics → Workforce Snapshot → org-wide summary:
  - Total headcount (active employees)
  - New hires this month/quarter
  - Terminations this month/quarter
  - Attrition rate (%)
  - Department distribution (pie chart)
  - Gender distribution
  - Average tenure
  - Average age
- **API:** `GET /api/v1/analytics/workforce-snapshot`

### Step 2: Historical Comparison
- **UI:** Select comparison period → see changes (headcount growth, department shifts, attrition trend line)

### Step 3: Drill Down
- **UI:** Click any metric → detailed view with employee list → filter and sort

### Step 4: Export
- **UI:** Export snapshot as PDF report or CSV data

## Events Triggered

- None (read-only)

## Related Flows

- [[productivity-dashboard]]
- [[report-creation]]

## Module References

- [[workforce-snapshots]]
- [[productivity-analytics]]
