# Page: Overview Dashboard

**Route:** `/overview`
**Permission:** Authenticated (content varies by role)

## Purpose

Landing page after login. Shows a role-appropriate summary of HR and Workforce Intelligence data. Adapts based on user permissions and tenant monitoring configuration.

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ "Good morning, Jane"                     [April 6, 2026]    │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Employees│ On Leave │ Pending  │ Active   │ Exceptions     │
│ 487      │ 41       │ 12 tasks │ 342      │ 7 ⚠️           │
│          │          │          │ (70.2%)  │                │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│ ┌─── Quick Actions ──────────────────────────────────────┐  │
│ │ [Approve Leave (8)] [Review Exceptions (3)]            │  │
│ │ [Pending Reviews (5)] [View Live Dashboard]            │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                             │
├───────────────────────────┬─────────────────────────────────┤
│ Recent Activity           │ Upcoming                         │
│                           │                                  │
│ • J.D. leave approved     │ • Apr 10: 3 employees on leave  │
│ • Payroll run calculated  │ • Apr 15: Q1 reviews due        │
│ • 2 new exceptions        │ • Apr 30: Payroll processing    │
│ • New hire: Alex T.       │                                  │
│                           │                                  │
├───────────────────────────┴─────────────────────────────────┤
│ Department Activity (bar chart)     │ if WI enabled          │
│ Engineering ████████████ 82%        │                        │
│ Sales       ██████████ 71%          │                        │
│ Support     ████████ 65%            │                        │
└─────────────────────────────────────────────────────────────┘
```

## KPI Cards — Visibility by Role/Config

| Card | Visible When |
|:-----|:-------------|
| Employees | Always (count varies by scope: own team for Manager, all for HR Admin) |
| On Leave | `leave:read` |
| Pending Tasks | Always (own pending approvals/actions) |
| Active Now | `workforce:view` AND monitoring enabled |
| Exceptions | `exceptions:view` AND monitoring enabled |
| Department Activity | `workforce:view` AND monitoring enabled |

## Data Sources

| Component | API |
|:----------|:----|
| Employee count | `GET /employees/count` |
| Leave summary | `GET /leave/summary?date=today` |
| Pending tasks | `GET /workflow/my-pending` |
| Workforce status | `GET /workforce/presence/live` (if permitted) |
| Exception count | `GET /exceptions/alerts?status=new` (if permitted) |
| Recent activity | `GET /audit/recent?limit=10` |
| Upcoming events | `GET /calendar/upcoming?days=30` |

## Interactions

- Quick action buttons navigate to relevant pages
- KPI cards are clickable → navigate to detail page
- Department chart → navigate to `/workforce/live?department=X`

## Empty States

- **New tenant (no employees):** "Welcome to ONEVO! Start by adding your first employee."
- **Monitoring disabled:** Workforce Intelligence cards hidden entirely (not grayed out)
- **No permissions for WI:** Same as disabled — cards not shown

## Related

- [[frontend/cross-cutting/authorization|Authorization]]
- [[security/auth-architecture|Auth Architecture]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]]
- [[frontend/coding-standards|Frontend Coding Standards]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
