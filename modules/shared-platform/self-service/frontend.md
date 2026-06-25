# Page: Employee Self-Service

**Route:** `/my-dashboard`, `/time-off`, `/my-profile`, `/my-performance`
**Permission:** Any authenticated employee (no special permission)

## Purpose


## My Dashboard Layout

```
+-------------------------------------------------------------+
| "My Dashboard"                          [April 6, 2026]     |
+----------+----------+----------+----------+----------------+
| Hours    | Active % | Time Off | Pending  | Next Review    |
| 7h 45m   | 74.2%    | 12 days  | 1 req    | Apr 15         |
| today    | today    | remaining|          |                |
+----------+----------+----------+----------+----------------+
|                                                             |
| Today's Timeline                                            |
| 8am  9    10   11   12pm  1    2    3    4    5pm          |
| [### active ###][idle][## meeting ##][brk][### active ####] |
|                                                             |
+----------------------------+--------------------------------+
| My Application Usage       | Quick Links                     |
|                            |                                |
| VS Code      ######## 3h  | [Request Time Off]             |
| Chrome       ##### 2h     | [View Payslips]                |
| Slack        ## 45m       | [My Performance]               |
|                            |                                |
+----------------------------+--------------------------------+
| What's being tracked (transparency footer)                   |
| Your organization monitors: activity levels, app usage,      |
| meeting time. Screenshots: OFF. Identity verification: OFF.  |
| Data retained for 90 days. Questions? Contact HR.            |
+-------------------------------------------------------------+
```

## Privacy & Transparency

The **transparency footer** is critical. It shows:
- Which monitoring features are enabled for this employee
- What data is NOT collected (explicitly)
- Retention period
- Contact for questions

Content driven by `GET /configuration/monitoring/my-settings` - returns the effective monitoring config for the current employee after applying overrides.

### Privacy Mode Effects

| Mode | Self-Service Behavior |
|:-----|:---------------------|
| Full Transparency | Show all: timeline, app usage, activity %, transparency footer |
| Partial | Show: activity % and hours only. No app breakdown, no timeline. Footer says "limited data shown" |
| Covert | Self-service section hidden entirely. No indication of monitoring |

## Self-Service Pages

### My Time Off (`/time-off`)
- Own Time Off balance, request history, submit new request
- Calendar showing own Time Off + public holidays
- API: `GET /api/v1/time-off/entitlements/me`, `GET /api/v1/time-off/requests/me`

### My Profile (`/my-profile`)
- View personal info (read-only for most fields)
- Update: phone, emergency contact, address
- View bank details (masked, except last 4 digits)
- API: `GET /employees/me`, `PUT /employees/me/personal`

### My Performance (`/my-performance`)
- View own review history and current open reviews
- Self-assessment submission
- Own goals list and progress
- NO peer data, NO rankings, NO department averages
- API: `GET /performance/reviews?employeeId=me`, `GET /performance/goals?employeeId=me`

## Key Constraints

1. **No comparison data** - never show department averages, rankings, or peer activity
2. **No exception alerts** - employees don't see their own exceptions
3. **Activity data is read-only** - employees can't modify or delete their activity data
4. **Respect privacy mode** - check the mode before rendering any monitoring data
5. **Effective config** - always use the employee-specific effective config (overrides applied)

## Data Sources

| Component | API |
|:----------|:----|
| Activity summary | `GET /activity/summary/me?date=today` |
| Timeline | `GET /activity/snapshots/me?date=today` |
| App usage | `GET /activity/apps/me?date=today` |
| Monitoring config | `GET /configuration/monitoring/my-settings` |
| Time Off balance | `GET /api/v1/time-off/entitlements/me` |

## Empty States

- **Monitoring disabled:** Activity section hidden. Show only core employee widgets (Time Off, profile, performance)
- **No activity today:** "No activity recorded yet today. Data updates every few minutes."
- **Covert mode:** Entire activity section absent, with no explanation

## Related

- [[frontend/cross-cutting/authorization|Authorization]]
- [[security/auth-architecture|Auth Architecture]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]]
- [[frontend/coding-standards|Frontend Coding Standards]]
