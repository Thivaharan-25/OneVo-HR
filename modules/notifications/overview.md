# Module: Notifications

**Namespace:** `ONEVO.Modules.Notifications`
**Pillar:** Shared Foundation
**Owner:** Dev 4 (Week 4)
**Tables:** 2

---

## Purpose

Centralized notification pipeline for the entire platform. Handles in-app notifications, email (via Resend), and real-time push (via SignalR). **Enhanced** to support exception engine alerts and escalation notifications from Pillar 2.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | All modules | — (via domain events) | Notification delivery |

---

## Public Interface

```csharp
public interface INotificationService
{
    Task SendAsync(SendNotificationCommand command, CancellationToken ct);
    Task<Result<List<NotificationDto>>> GetUnreadAsync(Guid userId, CancellationToken ct);
    Task MarkReadAsync(Guid notificationId, CancellationToken ct);
}
```

---

## Database Tables (2)

### `notification_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `event_type` | `varchar(50)` | e.g., `leave.approved`, `exception.alert.created`, `alert.escalated` |
| `channel` | `varchar(20)` | `email`, `in_app`, `push`, `signalr` |
| `subject_template` | `varchar(255)` | |
| `body_template` | `text` | Liquid/Handlebars template |
| `is_active` | `boolean` | |

### `notification_channels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `channel_type` | `varchar(20)` | `email`, `slack`, `webhook` |
| `config_json` | `jsonb` | Channel-specific config |
| `credentials_encrypted` | `bytea` | API keys etc. |
| `is_active` | `boolean` | |

---

## Notification Pipeline

See [[notification-system]] for the full 6-step pipeline:
1. Domain event published → 2. Handler resolves recipients → 3. Load template → 4. Render → 5. Dispatch per channel → 6. Log delivery

**New event types for Workforce Intelligence:**
- `exception.alert.created` — New exception alert
- `exception.alert.escalated` — Alert escalated to next level
- `verification.failed` — Identity verification failed
- `agent.heartbeat.lost` — Agent went offline
- `productivity.daily.report` — Daily report ready
- `productivity.weekly.report` — Weekly report ready

---

## SignalR Channels

| Channel | Purpose |
|:--------|:--------|
| `notifications-{userId}` | Per-user in-app notifications |
| `exception-alerts` | Exception alerts (managers/admins) |
| `workforce-live` | Live workforce status updates |
| `agent-status` | Agent online/offline status |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/notifications` | `notifications:read` | List notifications |
| PUT | `/api/v1/notifications/{id}/read` | `notifications:read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | `notifications:read` | Mark all as read |
| GET | `/api/v1/notifications/preferences` | `notifications:read` | User preferences |
| PUT | `/api/v1/notifications/preferences` | `notifications:manage` | Update preferences |

## Features

- [[notification-templates]] — Per-channel, per-event templates (Liquid/Handlebars)
- [[notification-channels]] — Channel provider configuration (email, Slack, webhook)
- [[signalr-real-time]] — Real-time push channels (`exception-alerts`, `workforce-live`, `agent-status`)

---

## Related

- [[multi-tenancy]] — All templates and channels are tenant-scoped
- [[event-catalog]] — `exception.alert.created`, `verification.failed`, `agent.heartbeat.lost`, `productivity.daily.report`
- [[error-handling]] — Delivery failures logged per channel; retry logic
- [[WEEK4-supporting-bridges]] — Implementation task file

See also: [[module-catalog]], [[notification-system]], [[exception-engine]]
