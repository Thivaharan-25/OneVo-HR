# SignalR Real-Time - End-to-End Logic

**Module:** Notifications
**Feature:** SignalR Real-Time Push

---

## Real-Time Notification Flow

### Flow

```
Domain event published (e.g., MonitoringAlertCreated)
  -> NotificationEventHandler
    -> 1. Resolve target users/roles
    -> 2. For each target user:
       -> Look up active SignalR connection in signalr_connections
       -> If connected: push message via SignalR hub
       -> If not connected: queue as in-app notification for next login

SignalR Channels:
  -> notifications-{userId}: Per-user notifications
  -> notifications-{userId}: Phase 1 monitoring/attendance alerts (authorized resolver outputs only)
  -> monitoring-live: Live monitoring status updates
  -> agent-status: Agent online/offline status
```

## Connection Management

### Flow

```
Client connects to SignalR hub:
  -> OnConnectedAsync:
    -> INSERT into signalr_connections
    -> Subscribe to user-specific and role-based channels
  -> OnDisconnectedAsync:
    -> UPDATE signalr_connections SET is_active = false
```

## Related

- [[frontend/architecture/overview|SignalR Real-Time Overview]]
- [[frontend/architecture/overview|Notification Channels]]
- [[frontend/architecture/overview|Notification Templates]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
