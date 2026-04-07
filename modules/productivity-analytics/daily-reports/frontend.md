# Page: Workforce Reports

**Route:** `/workforce/reports`
**Permission:** `analytics:view`

## Purpose

Daily, weekly, and monthly productivity reports with trend analysis and CSV/Excel export.

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ "Workforce Reports"  [Daily | Weekly | Monthly] [Export ▼]  │
├─────────────────────────────────────────────────────────────┤
│ [Date Range Picker] [Department Filter ▼]                   │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Avg Act% │ Avg Mtg% │ Total    │ Exceptions│ Emp Count     │
│ 72.5%    │ 18.3%    │ 3,847h   │ 47        │ 487           │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│ Trend Chart (active % over time)                            │
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

- [[productivity-analytics/daily-reports/overview|Daily Reports Backend]]
- [[auth-architecture]]
- [[design-system]]
- [[WEEK4-productivity-analytics]]
