# SignalR Real-Time

**Module:** Notifications  
**Feature:** SignalR Real-Time

---

## Purpose

Real-time push notifications via SignalR channels.

## SignalR Channels

| Channel | Purpose |
|:--------|:--------|
| `notifications-{userId}` | Per-user in-app notifications |
| `exception-alerts` | Exception alerts (managers/admins) |
| `workforce-live` | Live workforce status updates |
| `agent-status` | Agent online/offline status |

## Related

- [[modules/notifications/overview|Notifications Module]]
- [[frontend/architecture/overview|Notification Channels]]
- [[frontend/architecture/overview|Notification Templates]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
