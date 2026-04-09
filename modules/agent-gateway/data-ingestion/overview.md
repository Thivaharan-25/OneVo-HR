# Data Ingestion

**Module:** Agent Gateway
**Feature:** Data Ingestion

---

## Purpose

High-throughput ingestion endpoint for desktop agent data. Returns **202 Accepted** immediately and processes asynchronously.

## Key Business Rules

1. Minimal validation (schema check only, detailed validation is async).
2. Batch INSERT via `COPY` or `unnest()` for raw buffer.
3. Rate limit per device (not per user) — default 30 requests/minute/device.
4. Data routing by `type`: `activity_snapshot` → `activity_raw_buffer`, `device_session` → `device_sessions`, `verification_photo` → [[modules/identity-verification/overview|Identity Verification]].

## Ingestion Payload Schema

```json
{
  "device_id": "uuid",
  "employee_id": "uuid",
  "timestamp": "2026-04-05T10:30:00Z",
  "batch": [
    {
      "type": "activity_snapshot",
      "data": { "keyboard_events_count": 342, "mouse_events_count": 128, "active_seconds": 140, "idle_seconds": 10, "foreground_app": "Visual Studio Code" }
    },
    {
      "type": "app_usage",
      "data": { "application_name": "Google Chrome", "window_title_hash": "sha256...", "duration_seconds": 45 }
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
