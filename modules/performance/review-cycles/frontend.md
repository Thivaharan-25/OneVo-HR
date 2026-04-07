# Page: Performance Management

**Route:** `/hr/performance` (cycles), `/hr/performance/goals` (goals), `/hr/performance/[id]` (review detail)
**Permission:** `performance:read` (view), `performance:manage` (create cycles, manage)

## Purpose

Manage performance review cycles, individual goals, and view review details. Optionally includes productivity data from Workforce Intelligence.

## Review Cycles Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Performance"                 [+ Create Cycle]  │
│ [Review Cycles | Goals]                                     │
├─────────────────────────────────────────────────────────────┤
│ Active Cycles                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Q1 2026 Review                                          │ │
│ │ Period: Jan - Mar 2026  │  Due: Apr 15  │  Status: Open │ │
│ │ Progress: ████████░░ 78% complete (380/487)             │ │
│ │ [View Reviews]                                          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Annual 2025 Review                                      │ │
│ │ Period: Full Year 2025  │  Due: Jan 31  │  Completed    │ │
│ │ Progress: ██████████ 100% complete                      │ │
│ │ [View Reviews]                                          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Review Detail Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back  "Q1 2026 Review — John Doe"                        │
├──────────┬──────────┬──────────┬───────────────────────────┤
│ Rating   │ Status   │ Reviewer │ Due Date                   │
│ 4.2/5    │ Draft    │ Jane S.  │ Apr 15                     │
├──────────┴──────────┴──────────┴───────────────────────────┤
│                                                             │
│ Self Assessment                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Goals achieved: 4/5                                     │ │
│ │ Key accomplishments: ...                                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Manager Assessment                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Performance Rating: [1-5 scale]                         │ │
│ │ Strengths: ________________________                     │ │
│ │ Areas for improvement: ____________                     │ │
│ │ Comments: _________________________                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Productivity Data (if enabled) ──────────────────────┐  │
│ │ Avg Active %: 76.2%  │  Avg Hours: 8.1h/day          │  │
│ │ Trend: ↑ 3% vs previous quarter                       │  │
│ │ Top Apps: VS Code (40%), Chrome (25%), Teams (20%)     │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
│ [Save Draft] [Submit Review]                                │
└─────────────────────────────────────────────────────────────┘
```

**Productivity Data section** only visible if:
1. Review cycle has `include_productivity_data = true`
2. User has `analytics:view` permission
3. Monitoring is enabled for the employee

## Data Sources

| Component | API |
|:----------|:----|
| Cycle list | `GET /performance/cycles` |
| Cycle reviews | `GET /performance/cycles/{id}/reviews?status=&department=` |
| Review detail | `GET /performance/reviews/{id}` |
| Goals | `GET /performance/goals?employeeId=` |
| Productivity data | `GET /analytics/monthly/{employeeId}?year=&month=` |
| Submit review | `PUT /performance/reviews/{id}` |

## Interactions

- Click cycle → list of reviews for that cycle (filterable by department, status)
- Click review → detail page with self-assessment and manager form
- Goals tab: CRUD goals, link to review cycles
- Productivity section is read-only, pulled from ProductivityAnalytics module

## Empty States

- **No cycles:** "No performance review cycles. Create one to get started."
- **No productivity data:** "Productivity data not available for this employee." (monitoring disabled or data not yet collected)

## Related

- [[review-cycles|Review Cycles Overview]]
- [[auth-architecture]]
- [[design-system]]
