# Notification View

**Area:** Notifications  
**Trigger:** User opens notification panel (user action - view only)
**Required Permission(s):** Any authenticated user  
**Related Permissions:** `notifications:manage` (manage org notifications)

---

## Notification Channels

| Channel | Purpose | Content |
|:--------|:--------|:--------|
| **Notification Bell** (topbar) | FYI updates - no action needed | "John was promoted", "Policy updated", system announcements |
| **Inbox** (sidebar) | Phase 1 actionable items - needs your decision | Time Off approvals, expense reviews, skill validations, attendance corrections, overtime approvals, remote location change requests |

Users should never have to check two places for the same thing. Each notification routes to exactly one channel based on whether it requires action.

## Preconditions

- User logged in with active session
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Notifications
- **UI:** Click bell icon in top navigation bar -> dropdown shows unread FYI notifications (most recent first)
- **Real-time:** New notifications appear instantly via SignalR on `notifications-{userId}` channel -> [[backend/real-time|Real-Time Architecture]]
- **API:** `GET /api/v1/notifications?unread=true`

### Step 2: Read & Navigate
- **UI:** Click notification -> navigates to related item and marks notification as read
- **API:** `PUT /api/v1/notifications/{id}/read`
- **DB:** `notifications` - `read_at` set

### Step 3: Manage Notifications
- **UI:** "Mark All as Read" -> view full notification history -> filter by category -> search

### Step 4: Notification Center
- **UI:** Click "View All" -> full notification center page -> pagination -> filter by type, date, read/unread

## Variations

### Unread badge count
- Bell icon shows unread FYI count (max "99+") -> updates real-time
- Inbox badge shows unresolved actionable count and is handled by [[Userflow/Notifications/inbox|Inbox]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| SignalR disconnected | Polling fallback | Notifications refresh on page load instead of real-time |
| No notifications | Empty state | "You're all caught up!" |

## Events Triggered

- None (consuming notifications, not producing)

## Related Flows

- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]]
- [[Userflow/Notifications/inbox|Inbox]]
- All flows that trigger notifications

## Module References

- [[modules/notifications/overview|Notifications]]
- [[modules/notifications/signalr-real-time/overview|Signalr Real Time]]
- [[modules/notifications/notification-channels/overview|Notification Channels]]
