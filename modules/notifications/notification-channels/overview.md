# Notification Channels

**Module:** Notifications  
**Feature:** Notification Channels

---

## Purpose

Channel provider configuration (email via Resend, Slack, webhooks).

## Database Tables

### `notification_channels`
Fields: `channel_type` (`email`, `slack`, `webhook`), `config_json`, `credentials_encrypted`, `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/notifications` | `notifications:read` | List notifications |
| PUT | `/api/v1/notifications/{id}/read` | `notifications:read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | `notifications:read` | Mark all read |
| GET | `/api/v1/notifications/preferences` | `notifications:read` | Preferences |
| PUT | `/api/v1/notifications/preferences` | `notifications:manage` | Update preferences |

## Related

- [[notifications|Notifications Module]]
- [[notifications/notification-templates/overview|Notification Templates]]
- [[notifications/signalr-real-time/overview|SignalR Real-Time]]
- [[event-catalog]]
- [[notification-system]]
- [[multi-tenancy]]
- [[WEEK4-supporting-bridges]]
