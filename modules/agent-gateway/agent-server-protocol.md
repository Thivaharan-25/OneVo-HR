# Agent-Server Protocol

## Endpoints

All communication with the ONEVO backend goes through the Agent Gateway at `/api/v1/agent/*`.

### 1. Registration

**When:** First launch after install.

```
POST /api/v1/agent/register
Content-Type: application/json
X-Tenant-Key: {tenant_api_key}

{
  "device_id": "generated-uuid-v7",
  "device_name": "DESKTOP-ABC123",
  "os_version": "Windows 11 23H2",
  "agent_version": "1.0.0"
}

Response 201:
{
  "agent_id": "uuid",
  "device_token": "eyJ...",  // Device JWT
  "token_expires_at": "2026-04-06T10:30:00Z"
}
```

Store `device_token` via DPAPI. Use for all subsequent requests.

### 2. Employee Login

**When:** Employee logs in via MAUI tray app.

```
POST /api/v1/agent/login
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "..."
}

Response 200:
{
  "employee_id": "uuid",
  "employee_name": "John Doe",
  "policy": { ... }  // Full monitoring policy
}
```

The response includes the monitoring policy — cache it locally.

### 3. Policy Sync

**When:** On login (already in login response) + every 60 minutes.

```
GET /api/v1/agent/policy
Authorization: Bearer {device_token}

Response 200:
{
  "activity_monitoring": true,
  "application_tracking": true,
  "screenshot_capture": false,
  "meeting_detection": true,
  "device_tracking": true,
  "identity_verification": true,
  "verification_on_login": true,
  "verification_on_logout": false,
  "verification_interval_minutes": 60,
  "idle_threshold_seconds": 300,
  "snapshot_interval_seconds": 150,
  "heartbeat_interval_seconds": 60
}
```

### 4. Heartbeat

**When:** Every 60 seconds (configurable via policy).

```
POST /api/v1/agent/heartbeat
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "device_id": "uuid",
  "agent_version": "1.0.0",
  "cpu_usage": 1.5,
  "memory_mb": 42,
  "buffer_count": 15,
  "errors": [],
  "monitoring_state": "active"  // "active", "paused", "stopped", "idle"
}

Response 200:
{
  "status": "ok",
  "update_available": false,
  "update_url": null,
  "has_pending_commands": true,
  "pending_command_count": 1
}
```

If `has_pending_commands` is true AND agent is not connected via SignalR, agent should immediately call `GET /api/v1/agent/commands` to fetch pending commands. This is the fallback mechanism.

If no heartbeat for 5 minutes, server fires `AgentHeartbeatLost` event.

### 5. Data Ingestion

**When:** Every 2-3 minutes (configurable via `snapshot_interval_seconds`).

```
POST /api/v1/agent/ingest
Authorization: Bearer {device_token}
Content-Type: application/json

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
        "foreground_app": "Visual Studio Code"
      }
    },
    {
      "type": "app_usage",
      "data": {
        "application_name": "Google Chrome",
        "window_title_hash": "a1b2c3...",
        "duration_seconds": 45
      }
    }
  ]
}

Response 202 Accepted
```

**Important:** Server returns 202 immediately. Processing is async. Do NOT wait for processing confirmation.

**GDPR Consent Gate:** Before processing any batch, the server verifies that the employee has an active `monitoring` consent record in `gdpr_consent_records`. If missing or `consented = false`, the request is rejected with `403 Forbidden`. The agent must stop collection and show a consent-required prompt in the tray app. See [[modules/auth/gdpr-consent/overview|GDPR Consent]] for the full gate flow.

**Ingest Payload Validation — Server-Side Rules:**

The ingest endpoint validates every batch before queuing it. Violations return `422 Unprocessable Entity`.

| Field | Rule | Rejection reason |
|:------|:-----|:----------------|
| `batch` array length | Max 200 items per request | Prevents oversized payloads from overwhelming the queue |
| `timestamp` (root) | Must be within ±10 minutes of server UTC time | Rejects replayed or far-future payloads |
| `batch[].type` | Must be one of: `activity_snapshot`, `app_usage`, `meeting`, `device_session`, `screenshot_capture`, `verification_photo` | Rejects unknown type strings |
| `keyboard_events_count` | Integer, 0–50,000 | Physical limit: ~400 WPM × 150s ≈ 15,000 keystrokes max realistic |
| `mouse_events_count` | Integer, 0–100,000 | Physical limit: generous ceiling for fast movers |
| `active_seconds` | Integer, 0–`snapshot_interval_seconds` | Cannot exceed the collection window |
| `idle_seconds` | Integer, 0–`snapshot_interval_seconds` | Cannot exceed the collection window |
| `active_seconds + idle_seconds` | ≤ `snapshot_interval_seconds` + 5 (5s tolerance) | Sum cannot exceed the snapshot interval |
| `duration_seconds` (app_usage) | Integer, 0–`snapshot_interval_seconds` | Cannot exceed the collection window |
| `application_name` | Max 200 characters, non-empty | Prevents oversized strings |
| `window_title_hash` | Exactly 64 hex characters (SHA-256) | Validates hash integrity |
| `employee_id` | Must match active `agent_sessions` record for this `device_id` | See Employee-Device Binding in [[modules/agent-gateway/data-collection\|Data Collection]] |

**Implementation note:** Use a `FluentValidation` validator on `IngestBatchRequest`. The `snapshot_interval_seconds` comes from the agent's current policy stored server-side in `agent_policies` — look it up by `device_id` from the Device JWT.

### 6. Employee Logout

**When:** Employee logs out via MAUI tray app.

```
POST /api/v1/agent/logout
Authorization: Bearer {device_token}

Response 200
```

After logout, agent continues heartbeat but stops collecting activity data (no employee linked). Agent disconnects from SignalR command hub.

### 7. SignalR Command Hub Connection

**When:** Immediately after successful employee login.

```
Connect: /hubs/agent-commands
Query: ?access_token={device_token}
```

Agent maintains this connection for the entire session. On disconnect, falls back to heartbeat polling for commands.

**Reconnect strategy:** Same as frontend — exponential backoff [0, 1s, 2s, 5s, 10s, 30s].

### 8. Fetch Pending Commands (Fallback)

**When:** On heartbeat response with `has_pending_commands: true` AND SignalR disconnected.

```
GET /api/v1/agent/commands
Authorization: Bearer {device_token}

Response 200:
{
  "commands": [
    {
      "id": "uuid",
      "type": "capture_screenshot",
      "payload": { "reason": "Manager verification request" },
      "created_at": "2026-04-05T10:30:00Z",
      "expires_at": "2026-04-05T10:35:00Z"
    }
  ]
}
```

### 9. Acknowledge Command

**When:** Agent receives and starts processing a command.

```
POST /api/v1/agent/commands/{commandId}/ack
Authorization: Bearer {device_token}

Response 200
```

### 10. Complete Command

**When:** Agent finishes executing a command.

```
POST /api/v1/agent/commands/{commandId}/complete
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "success": true,
  "result": {
    "screenshot_url": "https://storage.onevo.io/captures/uuid.jpg"
  }
}

Response 200
```

If command failed:
```json
{
  "success": false,
  "error": "Camera access denied by user"
}
```

## Error Handling

| Status | Meaning | Agent Action |
|:-------|:--------|:-------------|
| 200/201/202 | Success | Continue normally |
| 401 | JWT expired or revoked | Stop syncing, prompt re-registration in tray app |
| 403 | Agent revoked | Stop all activity, show error in tray app |
| 429 | Rate limited | Honor `Retry-After` header |
| 5xx | Server error | Exponential backoff (2s, 4s, 8s, max 30s) |
| Network error | Server unreachable | Buffer locally, retry on next cycle |

## Compression

For batches > 1KB, use gzip compression:
```
Content-Encoding: gzip
```

## Rate Limits

Server enforces: 30 requests/minute/device. Agent should space requests naturally (heartbeat every 60s, ingest every 150s = ~1.4 req/min normal operation).

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[frontend/architecture/overview|Heartbeat Monitoring]]
- [[frontend/architecture/overview|Data Ingestion]]
- [[frontend/architecture/overview|Policy Distribution]]
- [[frontend/architecture/overview|Agent Registration]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
