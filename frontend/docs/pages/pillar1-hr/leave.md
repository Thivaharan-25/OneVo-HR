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

## Request Detail (Sheet)

```
┌─────────────────────────────────┐
│ Leave Request Detail            │
├─────────────────────────────────┤
│ Employee: John Doe              │
│ Type: Annual Leave              │
│ From: 2026-04-10                │
│ To: 2026-04-12                  │
│ Days: 3 (excl. weekends)       │
│ Balance: 15 remaining          │
│ Reason: Family event           │
│ Status: Pending                │
│                                 │
│ Team Impact:                    │
│ - 2 others on leave 4/10-4/12  │
│                                 │
│ [Approve] [Reject]             │
│ Comment: ____________________  │
└─────────────────────────────────┘
```

## Data Sources

| Component | API |
|:----------|:----|
| Request list | `GET /leave/requests?status=&department=&type=&cursor=` |
| Calendar | `GET /leave/calendar?month=&year=&department=` |
| Request detail | `GET /leave/requests/{id}` |
| Approve/Reject | `PUT /leave/requests/{id}/approve` or `/reject` |
| Policies | `GET /leave/policies` |
| Leave balances | `GET /leave/balances/{employeeId}` |

## Interactions

- Click request → open detail sheet
- Approve/Reject with optional comment
- Calendar: click day → see who's on leave
- Policies tab: CRUD leave types and entitlements (admin only)

## Empty States

- **No pending requests:** "No pending leave requests. All caught up!"
- **No leave in calendar:** "No leave scheduled for this month."
