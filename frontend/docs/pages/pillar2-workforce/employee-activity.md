# Page: Employee Activity Detail

**Route:** `/workforce/activity/[employeeId]`
**Permission:** `workforce:view`

## Purpose

Deep dive into a single employee's activity for a specific day. Shows timeline, app usage, meetings, intensity, and device split.

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back  "John Doe — Activity Detail"  [Date Picker: Today] │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Hours    │ Active % │ Meeting  │ Intensity│ Exceptions     │
│ 8h 12m   │ 78.5%    │ 2h 15m   │ 72/100   │ 0              │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│ Day Timeline                                                │
│ 8am  9    10   11   12pm  1    2    3    4    5pm          │
│ [███ active ███][idle][██ meeting ██][brk][███ active ███]  │
│                                                             │
├────────────────────────────────┬────────────────────────────┤
│ Application Usage              │ Intensity Over Time         │
│                                │                            │
│ VS Code      ████████ 3h 15m  │  100 ─                     │
│ Chrome       █████ 2h 02m     │   75 ─  ╱╲    ╱╲          │
│ Teams        ████ 1h 45m      │   50 ─╱    ╲╱    ╲        │
│ Slack        ██ 0h 48m        │   25 ─               ╲     │
│ Other        █ 0h 22m         │    0 ─────────────────      │
│                                │    8am  10  12  2pm  4pm   │
├────────────────────────────────┴────────────────────────────┤
│ Meeting Log                                                 │
│ ┌──────┬────────┬──────┬────────┬───────┐                  │
│ │ Time │ Dur.   │ App  │ Camera │ Mic   │                  │
│ │10:00 │ 45 min │ Teams│ ✅     │ ✅    │                  │
│ │14:30 │ 30 min │ Zoom │ ❌     │ ✅    │                  │
│ └──────┴────────┴──────┴────────┴───────┘                  │
├─────────────────────────────────────────────────────────────┤
│ Device Usage: Laptop 92% | Mobile (est.) 8%                 │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

| Component | API |
|:----------|:----|
| KPI Cards | `GET /activity/summary/{employeeId}?date={date}` |
| Timeline | `GET /activity/snapshots/{employeeId}?date={date}` |
| App Usage | `GET /activity/apps/{employeeId}?date={date}` |
| Intensity Chart | Same as snapshots (chart from snapshot data) |
| Meeting Log | `GET /activity/meetings/{employeeId}?date={date}` |
| Device Split | Included in daily summary |

## Interactions

- Date picker to navigate between days
- Click app in usage chart → filter timeline by that app
- Hover on timeline segment → tooltip with start/end time + duration
- Navigate to employee HR profile via header link

## Permission Check

- Only show if user has `workforce:view`
- Self-service (`/my-dashboard`) shows own data without `workforce:view`
- Employee self-service shows NO comparison data, NO rankings
