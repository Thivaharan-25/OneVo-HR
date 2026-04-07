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
  "errors": []
}

Response 200:
{
  "status": "ok",
  "update_available": false,
  "update_url": null
}
```

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

### 6. Employee Logout

**When:** Employee logs out via MAUI tray app.

```
POST /api/v1/agent/logout
Authorization: Bearer {device_token}

Response 200
```

After logout, agent continues heartbeat but stops collecting activity data (no employee linked).

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

- [[agent-gateway|Agent Gateway Module]]
- [[heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[data-ingestion/overview|Data Ingestion]]
- [[policy-distribution/overview|Policy Distribution]]
- [[agent-registration/overview|Agent Registration]]
- [[auth-architecture]]
- [[error-handling]]
- [[multi-tenancy]]
- [[WEEK1-shared-platform]]
