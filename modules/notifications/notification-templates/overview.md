# Notification Templates

**Module:** Notifications  
**Feature:** Notification Templates

---

## Purpose

Per-channel notification templates using Liquid/Handlebars rendering.

## Database Tables

### `notification_templates`
Key columns: `event_type` (e.g., `leave.approved`, `exception.alert.created`), `channel` (`email`, `in_app`, `push`, `signalr`), `subject_template`, `body_template`, `is_active`.

## New Event Types for Workforce Intelligence

- `exception.alert.created` — New exception alert
- `exception.alert.escalated` — Alert escalated
- `verification.failed` — Identity verification failed
- `agent.heartbeat.lost` — Agent went offline
- `productivity.daily.report` / `productivity.weekly.report` — Reports ready

## Related

- [[modules/notifications/overview|Notifications Module]]
- [[frontend/architecture/overview|Notification Channels]]
- [[frontend/architecture/overview|SignalR Real-Time]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
