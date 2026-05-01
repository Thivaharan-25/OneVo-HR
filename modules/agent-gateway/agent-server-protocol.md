# Agent-Server Protocol

## Source of Truth

All communication with the ONEVO backend goes through the Agent Gateway at `/api/v1/agent/*`.

Phase 1 Windows enrollment is login-based:

```
Install MSIX
-> Service starts and generates device_id
-> TrayApp opens sign-in
-> Backend resolves tenant/user from authenticated login
-> Backend enrolls device and creates agent session
-> Agent stores internal device credential using DPAPI / Windows Credential Manager
-> Agent fetches policy
-> Monitoring starts only when Workforce Presence lifecycle allows it
```

Employees never enter an API key, tenant key, tenant ID, or server URL. The device credential is internal to the agent and is not exposed in the UI.

---

## Endpoints

### 1. Start Enrollment

**When:** First launch after install, before a device credential exists.

```
POST /api/v1/agent/enroll/start
Content-Type: application/json

{
  "device_id": "generated-uuid-v7",
  "device_name": "DESKTOP-ABC123",
  "os_version": "Windows 11 23H2",
  "agent_version": "1.0.0",
  "enrollment_method": "tray_browser_login"
}

Response 200:
{
  "enrollment_id": "uuid",
  "auth_url": "https://app.onevo.io/agent/enroll?enrollment_id=uuid",
  "expires_at": "2026-05-01T10:30:00Z"
}
```

The TrayApp opens `auth_url` in the system browser or a secure embedded auth surface. The user signs in normally. Tenant and employee are resolved by the backend from that authenticated session.

### 2. Complete Enrollment

**When:** The sign-in flow succeeds and the TrayApp/Service receives the enrollment completion callback.

```
POST /api/v1/agent/enroll/complete
Content-Type: application/json

{
  "enrollment_id": "uuid",
  "device_id": "generated-uuid-v7",
  "authorization_code": "short-lived-code-from-auth-callback"
}

Response 201:
{
  "agent_id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "employee_name": "John Doe",
  "device_token": "eyJ...",
  "token_expires_at": "2026-05-01T18:30:00Z",
  "policy": { "...": "..." }
}
```

Server behavior:

- Validates the enrollment challenge and authenticated user.
- Resolves `tenant_id` and `employee_id`; client never supplies tenant identity manually.
- Creates or updates `registered_agents`.
- Ends any previous active `agent_sessions` row for the same `device_id`.
- Creates the new active `agent_sessions` row.
- Returns the internal device credential and current monitoring policy.

Agent behavior:

- Store `device_token` with DPAPI / Windows Credential Manager.
- Cache policy locally.
- Start heartbeat.
- Do not collect telemetry until consent and Workforce Presence lifecycle permit it.

### 3. Employee Login / Session Refresh

**When:** An enrolled device needs to resume or refresh the employee session.

```
POST /api/v1/agent/login
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "session_resume": true
}

Response 200:
{
  "employee_id": "uuid",
  "employee_name": "John Doe",
  "policy": { "...": "..." }
}
```

This endpoint is not the first enrollment path. It is used after the device already has a valid device credential. If the credential is missing, expired beyond refresh, or revoked, the TrayApp returns to `enroll/start`.

### 4. Policy Sync

**When:** On enrollment/login and every 60 minutes.

```
GET /api/v1/agent/policy
Authorization: Bearer {device_token}

Response 200:
{
  "activity_monitoring": true,
  "application_tracking": true,
  "document_tracking": true,
  "communication_tracking": true,
  "browser_extension_enabled": false,
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

Screenshot capture means the agent can accept `manual` / `on_demand` capture commands. It does not enable scheduled or random screenshot collection.

### 5. Heartbeat

**When:** Every 60 seconds, configurable via policy.

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
  "monitoring_state": "active"
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

If `has_pending_commands` is true and SignalR is disconnected, the agent immediately calls `GET /api/v1/agent/commands`.

### 6. Data Ingestion

**When:** Every 2-3 minutes, configurable via `snapshot_interval_seconds`, and only while monitoring is allowed.

```
POST /api/v1/agent/ingest
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "device_id": "uuid",
  "employee_id": "uuid",
  "timestamp": "2026-05-01T10:30:00Z",
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
        "process_name": "chrome.exe",
        "window_title_hash": "a1b2c3...",
        "duration_seconds": 45
      }
    }
  ]
}

Response 202 Accepted
```

Important rules:

- Server returns `202 Accepted` immediately; processing is async.
- Server verifies the employee has active `monitoring` consent in `gdpr_consent_records`.
- Server verifies `employee_id` matches the active `agent_sessions` row for the `device_id`.
- If consent is missing or false, the request returns `403 Forbidden`; the agent stops collection and shows consent-required / policy-blocked state in the TrayApp.

### 7. Employee Logout

**When:** Employee logs out via TrayApp or the session must be ended.

```
POST /api/v1/agent/logout
Authorization: Bearer {device_token}

Response 200
```

After logout, the agent continues heartbeat but stops collecting activity data, ends the active `agent_sessions` row, and disconnects from the SignalR command hub.

### 8. SignalR Command Hub Connection

**When:** After successful enrollment/login.

```
Connect: /hubs/agent-commands
Query: ?access_token={device_token}
```

Agent maintains this connection for the entire active session. On disconnect, it falls back to heartbeat polling for commands.

Reconnect strategy: exponential backoff `[0, 1s, 2s, 5s, 10s, 30s]`.

### 9. Fetch Pending Commands

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
      "created_at": "2026-05-01T10:30:00Z",
      "expires_at": "2026-05-01T10:35:00Z"
    }
  ]
}
```

### 10. Acknowledge Command

```
POST /api/v1/agent/commands/{commandId}/ack
Authorization: Bearer {device_token}

Response 200
```

### 11. Complete Command

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

## Ingest Payload Validation

The ingest endpoint validates every batch before queueing it. Violations return `422 Unprocessable Entity`.

| Field | Rule | Rejection reason |
|:------|:-----|:----------------|
| `batch` array length | Max 200 items per request | Prevents oversized payloads |
| `timestamp` | Within +/-10 minutes of server UTC time | Rejects replayed or far-future payloads |
| `batch[].type` | One of `activity_snapshot`, `app_usage`, `meeting`, `device_session`, `document_usage`, `communication_usage`, `screenshot_capture`, `verification_photo` | Rejects unknown type strings |
| `keyboard_events_count` | Integer, 0-50,000 | Physical sanity limit |
| `mouse_events_count` | Integer, 0-100,000 | Physical sanity limit |
| `active_seconds` | Integer, 0-`snapshot_interval_seconds` | Cannot exceed collection window |
| `idle_seconds` | Integer, 0-`snapshot_interval_seconds` | Cannot exceed collection window |
| `active_seconds + idle_seconds` | <= `snapshot_interval_seconds` + 5 | Sum cannot exceed interval plus tolerance |
| `duration_seconds` | Integer, 0-`snapshot_interval_seconds` | Cannot exceed collection window |
| `application_name` | Max 200 characters, non-empty | Prevents oversized strings |
| `process_name` | Max 100 characters, non-empty | Used for allowlist matching |
| `window_title_hash` | Exactly 64 hex characters | Validates SHA-256 hash |
| `employee_id` | Must match active `agent_sessions` record for this `device_id` | Enforces employee-device binding |

## Error Handling

| Status | Meaning | Agent Action |
|:-------|:--------|:-------------|
| 200/201/202 | Success | Continue normally |
| 401 | Device credential expired or revoked | Stop syncing, return to enrollment |
| 403 | Agent revoked, consent missing, or policy blocked | Stop collection, show TrayApp error/state |
| 429 | Rate limited | Honor `Retry-After` header |
| 5xx | Server error | Exponential backoff, max 30s |
| Network error | Server unreachable | Buffer locally, retry on next cycle |

## Compression

For batches > 1KB, use gzip compression:

```
Content-Encoding: gzip
```

## Rate Limits

Server enforces 30 requests/minute/device. Normal operation is much lower: heartbeat every 60s and ingest every 150s.

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/agent-gateway/agent-installer|Agent Installer]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]]
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
