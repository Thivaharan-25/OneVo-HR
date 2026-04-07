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

- [[notifications|Notifications Module]]
- [[notifications/notification-channels/overview|Notification Channels]]
- [[notifications/signalr-real-time/overview|SignalR Real-Time]]
- [[event-catalog]]
- [[notification-system]]
- [[multi-tenancy]]
- [[WEEK4-supporting-bridges]]
