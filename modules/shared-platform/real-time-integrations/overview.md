# Real-Time & Integrations

**Module:** Shared Platform  
**Feature:** Real-Time & Integrations

---

## Purpose

SignalR connection tracking, system settings, API keys, webhooks, rate limiting, and scheduled task management.

## Database Tables

### `signalr_connections`
Active connections: `user_id`, `connection_id`, `channel` (`web`, `mobile`, `desktop_agent`), `device_type`.

### `system_settings`
Global (NOT tenant-scoped): `setting_key`, `setting_value` (jsonb).

### `api_keys`
Tenant API keys: `name`, `key_hash` (SHA-256), `key_prefix`, `scopes`, `expires_at`.

### `webhook_endpoints`
Outbound webhooks: `url`, `secret_hash`, `events` (subscribed types).

### `webhook_deliveries`
Delivery log: `event_type`, `payload`, `response_status`, `attempt_number`.

### `rate_limit_rules`
Per-endpoint limits: `endpoint_pattern`, `max_requests`, `window_seconds`.

### `scheduled_tasks`
Hangfire job metadata: `task_type`, `cron_expression`, `description`, `last_run_at`, `next_run_at`.

## Related

- [[shared-platform|Shared Platform Module]]
- [[notification-infrastructure]]
- [[hardware-terminals]]
- [[sso-authentication]]
- [[workflow-engine]]
- [[multi-tenancy]]
- [[authorization]]
- [[error-handling]]
- [[migration-patterns]]
- [[WEEK1-shared-platform]]
