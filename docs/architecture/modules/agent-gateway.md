# Module: Agent Gateway

**Namespace:** `ONEVO.Modules.AgentGateway`
**Pillar:** Shared Foundation
**Owner:** Dev 4 (Week 1)
**Tables:** 3
**Task File:** [[WEEK1-shared-platform]] (Agent Gateway section)

---

## Purpose

High-throughput ingestion API for the desktop agent. Handles agent registration, heartbeat monitoring, policy distribution, and activity data ingestion. This is the **only entry point** for desktop agent data into the ONEVO backend.

Agent Gateway uses **device-level JWT authentication**, separate from user JWT. See [[auth-architecture]] for details.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[auth]] | `ITokenService` | Issue device JWT at registration |
| **Depends on** | [[configuration]] | `IConfigurationService` | Build monitoring policy for agent |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Link employee to device at login |
| **Consumed by** | [[activity-monitoring]] | — (writes to raw buffer) | Raw activity data |
| **Consumed by** | [[workforce-presence]] | — (writes device sessions) | Device session data |
| **Consumed by** | [[identity-verification]] | — (routes verification photos) | Photo verification requests |

---

## Public Interface

```csharp
// ONEVO.Modules.AgentGateway/Public/IAgentGatewayService.cs
public interface IAgentGatewayService
{
    Task<Result<RegisteredAgentDto>> GetAgentByDeviceIdAsync(Guid deviceId, CancellationToken ct);
    Task<Result<AgentPolicyDto>> GetAgentPolicyAsync(Guid agentId, CancellationToken ct);
    Task<Result<bool>> IsAgentOnlineAsync(Guid agentId, CancellationToken ct);
}
```

---

## Database Tables (3)

### `registered_agents`

Desktop agents registered to employees.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees (nullable — set at employee login) |
| `device_id` | `uuid` | Unique device identifier (generated at install) |
| `device_name` | `varchar(100)` | Computer hostname |
| `os_version` | `varchar(50)` | e.g., "Windows 11 23H2" |
| `agent_version` | `varchar(20)` | e.g., "1.0.0" |
| `registered_at` | `timestamptz` | |
| `last_heartbeat_at` | `timestamptz` | Updated every 60s |
| `status` | `varchar(20)` | `active`, `inactive`, `revoked` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Indexes:** `(tenant_id, device_id)` UNIQUE, `(tenant_id, status)`, `(tenant_id, employee_id)`

### `agent_policies`

Policy pushed to each agent — defines what features are enabled for the linked employee.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `policy_json` | `jsonb` | See policy schema below |
| `last_synced_at` | `timestamptz` | When agent last fetched this policy |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Policy JSON schema:**

```json
{
  "activity_monitoring": true,
  "application_tracking": true,
  "screenshot_capture": false,
  "screenshot_interval_minutes": 10,
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

Policy is computed by merging: `monitoring_feature_toggles` (tenant) → `employee_monitoring_overrides` (employee). Override wins.

### `agent_health_logs`

Agent uptime, errors, tamper detection.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `reported_at` | `timestamptz` | |
| `cpu_usage` | `decimal(5,2)` | Agent process CPU% |
| `memory_mb` | `int` | Agent process memory |
| `errors_json` | `jsonb` | Recent errors array |
| `tamper_detected` | `boolean` | Service stopped/modified |

**Indexes:** `(agent_id, reported_at)`

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AgentRegistered` | New device registered | [[configuration]] (push initial policy) |
| `AgentHeartbeatLost` | No heartbeat for 5+ minutes | [[exception-engine]] (flag offline agent) |
| `AgentRevoked` | Admin revokes agent access | Agent receives 401 on next request |

---

## Key Business Rules

1. **High-throughput ingestion.** The `/agent/ingest` endpoint receives data every 2-3 minutes from every active agent:
   - Minimal validation (schema check only, detailed validation is async)
   - Batch INSERT via `COPY` or `unnest()` for raw buffer
   - Return **202 Accepted** immediately, process asynchronously
   - Rate limit per device (not per user)
2. **Device JWT ≠ User JWT.** Agent JWT contains `device_id` + `tenant_id` but NO user permissions. The `type: "agent"` claim distinguishes them. See [[auth-architecture]].
3. **Employee linking:** Device is registered with `employee_id = null`. When employee logs in via MAUI tray app, the device is linked: `employee_id` is set.
4. **Policy merge pattern:**
   ```csharp
   var tenantPolicy = await _configService.GetMonitoringTogglesAsync(tenantId, ct);
   var employeeOverride = await _configService.GetEmployeeOverrideAsync(employeeId, ct);
   var effectivePolicy = tenantPolicy.MergeWith(employeeOverride); // Override wins
   ```
5. **Heartbeat monitoring:** Agents send heartbeat every 60 seconds. If no heartbeat for 5 minutes, fire `AgentHeartbeatLost` event.

---

## API Endpoints

All agent endpoints use device JWT authentication (not user JWT).

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/register` | Tenant API key | Register new device, receive device JWT |
| POST | `/api/v1/agent/heartbeat` | Device JWT | Update `last_heartbeat_at`, report health |
| GET | `/api/v1/agent/policy` | Device JWT | Fetch current monitoring policy |
| POST | `/api/v1/agent/ingest` | Device JWT | Submit activity data batch (202 Accepted) |
| POST | `/api/v1/agent/login` | Device JWT + employee credentials | Link employee to device |
| POST | `/api/v1/agent/logout` | Device JWT | Unlink employee from device |

### Ingestion Payload Schema

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
        "foreground_app": "Visual Studio Code"
      }
    },
    {
      "type": "app_usage",
      "data": {
        "application_name": "Google Chrome",
        "window_title_hash": "sha256...",
        "duration_seconds": 45
      }
    },
    {
      "type": "device_session",
      "data": {
        "session_start": "...",
        "active_minutes": 2,
        "idle_minutes": 0
      }
    }
  ]
}
```

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `DetectOfflineAgentsJob` | Every 5 min | High | Find agents with `last_heartbeat_at` > 5 min ago, fire `AgentHeartbeatLost` |
| `CleanupRevokedAgentsJob` | Daily 3:00 AM | Low | Remove health logs for revoked agents older than 30 days |

---

## Important Notes

- **This is the ONLY ingestion endpoint for agent data.** All agent data flows through `/api/v1/agent/ingest`.
- **Rate limiting:** Per device, not per user. Default: 30 requests/minute/device.
- **Data routing:** The ingestion handler routes different `type` values to different modules: `activity_snapshot` → `activity_raw_buffer`, `device_session` → `device_sessions`, `verification_photo` → [[identity-verification]].
- **Agent does NOT have HR permissions.** It cannot read employee profiles, leave data, or any HR information.

See also: [[module-catalog]], [[activity-monitoring]], [[workforce-presence]], [[identity-verification]], [[auth]]
