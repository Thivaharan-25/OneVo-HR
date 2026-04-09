# Inbox

The personal action center — everything waiting for YOUR decision, in one place.

## Preconditions

- User is authenticated
- User has `approvals:read` permission

## Flow Steps

### Step 1: Open Inbox
- **Navigate:** Sidebar → Inbox (badge shows unresolved count)
- **UI:** Single-column list sorted by urgency then date

### Step 2: Review Items
- **UI:** Each item shows: icon, title, source (who submitted), timestamp, action buttons
- **Item types:**
  - Leave requests → Approve / Reject
  - Expense claims → Approve / Reject / Request Info
  - Onboarding sign-offs → Complete / Defer
  - Transfer/promotion requests → Approve / Reject
  - Assigned tasks → View / Complete
  - Mentions → View context

### Step 3: Take Action
- **UI:** Click action button → inline confirmation or slide-over detail panel
- Bulk approve/reject available for similar items (e.g., 5 leave requests)
- Completed items move to "Done" section (collapsible, below active items)

### Step 4: Empty State
- **UI:** "You're all caught up" with illustration. No pending items.

## Distinction from Notification Bell

- **Inbox** = actionable (needs your decision)
- **Bell** = informational (FYI updates, no action needed)

## Related Flows

- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Expense/expense-approval|Expense Approval]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/notifications/overview|Notifications Module]]
