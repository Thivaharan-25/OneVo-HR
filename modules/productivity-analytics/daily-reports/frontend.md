# Page: Workforce Reports

**Route:** `/workforce/reports`
**Permission:** `analytics:view`

## Purpose

Daily, weekly, and monthly workforce reports with activity rate, productivity score basis, data coverage, trend analysis, and CSV/Excel export.

## Layout

> UI labels should use "Activity rate" for active percentage and show `productivity_score_basis` beside any productivity score. Do not label active percentage as productivity.

```
┌─────────────────────────────────────────────────────────────┐
│ "Workforce Reports"  [Daily | Weekly | Monthly] [Export ▼]  │
├─────────────────────────────────────────────────────────────┤
│ [Date Range Picker] [Department Filter ▼]                   │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Avg Act% │ Avg Mtg% │ Total    │ Exceptions│ Emp Count     │
│ 72.5%    │ 18.3%    │ 3,847h   │ 47        │ 487           │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│ Trend Chart (activity rate and score basis over time)        │
│ ─ This period  ─── Previous period                          │
├─────────────────────────────────────────────────────────────┤
│ Employee Table                                              │
│ ┌────────┬──────┬────────┬────────┬────────┬─────────────┐ │
│ │ Name   │ Dept │ Hours  │ Active%│ Mtg%   │ Exceptions  │ │
│ │ (sort) │      │ (sort) │ (sort) │ (sort) │ (sort)      │ │
│ └────────┴──────┴────────┴────────┴────────┴─────────────┘ │
│ Pagination                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Tabs

- **Daily:** Single day view, per-employee breakdown
- **Weekly:** Week summary with trend vs previous week
- **Monthly:** Month summary with performance patterns, department rankings

## Export

- CSV: All visible data
- Excel: Formatted with headers, department grouping
- Triggered via `GET /analytics/export/{type}?format=csv|xlsx&filters=...`

## Data Sources

| Tab | API |
|:----|:----|
| Daily | `GET /analytics/daily/{employeeId}` or `GET /analytics/workforce?date=X` |
| Weekly | `GET /analytics/weekly/{employeeId}?weekStart=X` |
| Monthly | `GET /analytics/monthly/{employeeId}?year=X&month=X` |

## Related

- [[frontend/architecture/overview|Daily Reports Backend]]
- [[security/auth-architecture|Auth Architecture]]
- [[frontend/design-system/README|Design System]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
