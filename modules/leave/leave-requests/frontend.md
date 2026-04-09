# Page: Leave Management

**Route:** `/hr/leave` (requests), `/hr/leave/calendar` (calendar), `/hr/leave/policies` (admin)
**Permission:** `leave:read` (view), `leave:approve` (approve/reject), `leave:manage` (policies)

## Purpose

Manage leave requests, view team leave calendar, and configure leave policies.

## Requests Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Leave Management"                               │
│ [Requests | Calendar | Policies]                             │
├─────────────────────────────────────────────────────────────┤
│ [Pending: 8] [Approved: 34] [Rejected: 3] [All]            │
├─────────────────────────────────────────────────────────────┤
│ [Search] [Department ▼] [Leave Type ▼] [Date Range]        │
├─────────────────────────────────────────────────────────────┤
│ Request Table                                               │
│ ┌──────┬──────────┬──────┬────────┬──────────┬───────────┐ │
│ │ Name │ Type     │ From │ To     │ Days     │ Status    │ │
│ ├──────┼──────────┼──────┼────────┼──────────┼───────────┤ │
│ │ J.D. │ Annual   │ 4/10 │ 4/12   │ 3        │ ⏳ Pending│ │
│ │ M.K. │ Sick     │ 4/05 │ 4/05   │ 1        │ ✅ Apprvd │ │
│ └──────┴──────────┴──────┴────────┴──────────┴───────────┘ │
│ Pagination                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Calendar Layout

```
┌─────────────────────────────────────────────────────────────┐
│ [◀ March 2026]        April 2026         [May 2026 ▶]      │
│ [Department ▼]                                              │
├─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────────────────┤
│     │ Mon │ Tue │ Wed │ Thu │ Fri │     │ Legend           │
│     │     │     │  1  │  2  │  3  │     │ █ Annual        │
│     │  6  │  7  │  8  │  9  │ 10  │     │ █ Sick          │
│     │     │ J.D.████████████│     │     │ █ Other         │
│     │ 13  │ 14  │ 15  │ 16  │ 17  │     │ ░ Public Holiday│
│     │     │     │     │ M.K.██████│     │                  │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────────────────┘
```

## Request Detail / Approval View (Sheet)

```
┌─────────────────────────────────────┐
│ Leave Request Detail                │
├─────────────────────────────────────┤
│ Employee: John Doe                  │
│ Type: Annual Leave                  │
│ From: 2026-04-10                    │
│ To: 2026-04-12                      │
│ Days: 3 (excl. weekends)           │
│ Balance: 15 remaining              │
│ Reason: Family event               │
│ Status: Pending                    │
│                                     │
│ Team Impact:                        │
│ - 2 others on leave 4/10-4/12      │
│                                     │
│ ┌─ Schedule Conflicts (3) ────────┐ │
│ │                                  │ │
│ │ At Submission:                   │ │
│ │ 🔴 Q1 Performance Review        │ │
│ │    Apr 10, 10:00 AM (high)      │ │
│ │ 🟡 Team Standup                 │ │
│ │    Apr 11, 9:00 AM (medium)     │ │
│ │ 🟡 1:1 with Manager             │ │
│ │    Apr 12, 2:00 PM (medium)     │ │
│ │                                  │ │
│ │ Current:                         │ │
│ │ 🔴 Q1 Performance Review        │ │
│ │    Apr 10, 10:00 AM (high)      │ │
│ │ 🟡 Team Standup                 │ │
│ │    Apr 11, 9:00 AM (medium)     │ │
│ │ 🟡 1:1 with Manager             │ │
│ │    Apr 12, 2:00 PM (medium)     │ │
│ │ 🆕 Sprint Planning (NEW)        │ │
│ │    Apr 10, 2:00 PM (medium)     │ │
│ └──────────────────────────────────┘ │
│                                     │
│ [Approve] [Reject]                 │
│ Comment: ____________________      │
└─────────────────────────────────────┘
```

### Conflict Panel Behavior

- **On submission form:** Fires debounced call to `GET /calendar/conflicts` when dates change. Shows collapsible warning panel. Auto-expands if conflicts found. Employee can still submit.
- **On approval view:** Shows two subsections — "At Submission" (from stored `conflict_snapshot_json`) and "Current" (live API call). New events since submission get a "NEW" badge. Removed events shown as struck-through.
- **Color coding:** Red circle = high severity (reviews, company events). Amber circle = medium (team, personal).

## Data Sources

| Component | API |
|:----------|:----|
| Request list | `GET /leave/requests?status=&department=&type=&cursor=` |
| Calendar | `GET /leave/calendar?month=&year=&department=` |
| Request detail | `GET /leave/requests/{id}` (includes `conflict_snapshot_json`) |
| Calendar conflicts | `GET /calendar/conflicts?employeeId=&startDate=&endDate=` |
| Approve/Reject | `PUT /leave/requests/{id}/approve` or `/reject` |
| Policies | `GET /leave/policies` |
| Leave balances | `GET /leave/balances/{employeeId}` |

## Interactions

- Click request → open detail sheet (shows conflict panel for manager)
- Select dates on request form → debounced conflict check, show warnings
- Approve/Reject with optional comment (conflict context visible)
- Calendar: click day → see who's on leave
- Policies tab: CRUD leave types and entitlements (admin only)

## Empty States

- **No pending requests:** "No pending leave requests. All caught up!"
- **No leave in calendar:** "No leave scheduled for this month."

## Related

- [[modules/leave/leave-requests/overview|Leave Requests Overview]]
- [[security/auth-architecture|Auth Architecture]]
- [[frontend/design-system/README|Design System]]
