# Data Ingestion

**Module:** Agent Gateway
**Feature:** Data Ingestion

---

## Purpose

High-throughput ingestion endpoint for desktop agent data. Returns **202 Accepted** immediately and processes asynchronously.

## Key Business Rules

1. Minimal validation (schema check only, detailed validation is async).
2. Batch INSERT via `COPY` or `unnest()` for raw buffer.
3. Rate limit per device (not per user) - default 30 requests/minute/device.
4. Data routing by `type`: `activity_snapshot` -> `activity_raw_buffer`, `device_session` -> `device_sessions`, `verification_photo` -> [[modules/identity-verification/overview|Identity Verification]].

## Ingestion Payload Schema

Tenant ownership is never accepted from the payload. `tenant_id`, `agent_id`, and the trusted `device_id`
come from the Device JWT (`type = agent`). The optional payload `device_id` and `employee_id` are
validation hints only: they must match the JWT device claim and the active `agent_sessions` row.

```json
{
  "device_id": "uuid",
  "employee_id": "uuid",
  "timestamp": "2026-04-05T10:30:00Z",
  "batch": [
    {
      "type": "activity_snapshot",
      "data": {
        "keyboard_events_count": 342,
        "mouse_events_count": 128,
        "active_seconds": 140,
        "idle_seconds": 10,
        "foreground_process_name": "code.exe"
      }
    },
    {
      "type": "app_usage",
      "data": {
        "process_name": "chrome.exe",
        "application_name": "Google Chrome",
        "publisher": "Google LLC",
        "executable_path_hash": "sha256...",
        "window_title_hash": "sha256...",
        "duration_seconds": 45,
        "captured_at": "2026-04-05T10:29:45Z"
      }
    },
    {
      "type": "device_session",
      "data": { "session_start": "...", "active_minutes": 2, "idle_minutes": 0 }
    }
  ]
}
```

## API Endpoints

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/ingest` | Device JWT | Submit activity data batch (202 Accepted) |

## Identity Rules

| Identity field | Source of truth | Rule |
|:---------------|:----------------|:-----|
| `tenant_id` | Device JWT claim | Never accepted from the JSON payload. Any client-sent `tenant_id` is ignored or rejected. |
| `agent_id` | Device JWT claim | Used to find `registered_agents` and write agent-scoped data. |
| `device_id` | Device JWT claim | Payload `device_id`, when present, must match this claim. |
| `employee_id` | Active `agent_sessions` row | Payload `employee_id`, when present, must match the active session for this device. |

## App Identity Rules

`process_name` is the authoritative application matching key. `application_name` is display metadata only
and must not be used for allowlist/blocklist decisions unless a legacy fallback is explicitly needed.

Examples:

| Process name | Display name |
|:-------------|:-------------|
| `chrome.exe` | Google Chrome |
| `code.exe` | Visual Studio Code |
| `teams.exe` | Microsoft Teams |

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
