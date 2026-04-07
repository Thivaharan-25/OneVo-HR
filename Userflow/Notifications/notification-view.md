# Notification View

**Area:** Notifications  
**Required Permission(s):** Any authenticated user  
**Related Permissions:** `notifications:manage` (manage org notifications)

---

## Preconditions

- User logged in with active session
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Notifications
- **UI:** Click bell icon in top navigation bar → dropdown shows unread notifications (most recent first)
- **Real-time:** New notifications appear instantly via SignalR on `notifications-{userId}` channel → [[real-time]]
- **API:** `GET /api/v1/notifications?unread=true`

### Step 2: Read & Navigate
- **UI:** Click notification → navigates to related item (e.g., leave request, performance review, alert) → notification marked as read
- **API:** `PUT /api/v1/notifications/{id}/read`
- **DB:** `notifications` — `read_at` set

### Step 3: Manage Notifications
- **UI:** "Mark All as Read" → view full notification history → filter by category → search

### Step 4: Notification Center
- **UI:** Click "View All" → full notification center page → pagination → filter by type, date, read/unread

## Variations

### Unread badge count
- Bell icon shows unread count (max "99+") → updates real-time

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| SignalR disconnected | Polling fallback | Notifications refresh on page load instead of real-time |
| No notifications | Empty state | "You're all caught up!" |

## Events Triggered

- None (consuming notifications, not producing)

## Related Flows

- [[notification-preference-setup]]
- All flows that trigger notifications

## Module References

- [[notifications]]
- [[signalr-real-time]]
- [[notification-channels]]
