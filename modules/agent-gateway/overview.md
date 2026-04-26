# Module: Agent Gateway

**Namespace:** `ONEVO.Modules.AgentGateway`
**Phase:** 1 — Build
**Pillar:** Shared Foundation
**Owner:** Dev 4 (Week 1)
**Tables:** 4
**Task File:** [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] (Agent Gateway section)

---

## Purpose

High-throughput ingestion API and **bidirectional command channel** for the desktop agent. Handles agent registration, heartbeat monitoring, policy distribution, activity data ingestion, and **server-to-agent command dispatch**. This is the **only entry point** for desktop agent data into the ONEVO backend, and the **only channel** for pushing commands back to agents.

Agent Gateway uses **device-level JWT authentication**, separate from user JWT. See [[security/auth-architecture|Auth Architecture]] for details.

**Bidirectional communication:**
- **Agent → Server:** REST API (register, login, heartbeat, ingest, logout)
- **Server → Agent:** SignalR hub (`/hubs/agent-commands`) for real-time command push (remote capture, monitoring lifecycle, policy refresh)

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/auth/overview\|Auth]] | `ITokenService` | Issue device JWT at registration |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Build monitoring policy for agent |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Link employee to device at login |
| **Consumed by** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | — (writes to raw buffer) | Raw activity data |
| **Consumed by** | [[modules/workforce-presence/overview\|Workforce Presence]] | — (writes device sessions) | Device session data |
| **Consumed by** | [[modules/identity-verification/overview\|Identity Verification]] | — (routes verification photos) | Photo verification requests |
| **Listens to** | [[modules/workforce-presence/overview\|Workforce Presence]] | `PresenceSessionStarted/Ended`, `BreakStarted/Ended` | Controls agent monitoring lifecycle |
| **Listens to** | [[modules/exception-engine/overview\|Exception Engine]] | `RemoteCaptureRequested` | Dispatches capture command to agent |

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

// ONEVO.Modules.AgentGateway/Public/IAgentCommandService.cs
public interface IAgentCommandService
{
    /// <summary>Send a command to a specific agent via SignalR. Returns false if agent is offline.</summary>
    Task<Result<bool>> SendCommandAsync(Guid agentId, AgentCommand command, CancellationToken ct);
    /// <summary>Get pending commands for an agent (fallback if SignalR disconnects).</summary>
    Task<Result<IReadOnlyList<AgentCommandDto>>> GetPendingCommandsAsync(Guid agentId, CancellationToken ct);
}
```

---

## Database Tables (4)

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
  "heartbeat_interval_seconds": 60,
  "app_allowlist": {
    "mode": "allowlist",
    "apps": [
      { "name": "Microsoft Teams", "category": "communication", "is_allowed": true },
      { "name": "Visual Studio Code", "category": "development", "is_allowed": true },
      { "name": "Google Chrome", "category": "browser", "is_allowed": true }
    ],
    "alert_on_violation": true,
    "violation_threshold_minutes": 5
  }
}

// Note: screenshot_capture = false by default. No screenshot_interval — screenshots are
// ONLY triggered via remote command (manual/on_demand). Never scheduled or automated.
```

Policy is computed by merging three tiers: `monitoring_feature_toggles` (tenant default) → `role_app_policies` (role override) → `employee_monitoring_overrides` (employee override). Most specific wins. See [[modules/configuration/employee-overrides/overview|App Allowlist Configuration]].

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

### `agent_commands`

Pending and completed commands sent from server to agent.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `command_type` | `varchar(50)` | `capture_screenshot`, `capture_photo`, `start_monitoring`, `stop_monitoring`, `pause_monitoring`, `resume_monitoring`, `refresh_policy` |
| `requested_by` | `uuid` | FK → users (manager/CEO who initiated) |
| `payload_json` | `jsonb` | Command-specific parameters |
| `status` | `varchar(20)` | `pending`, `delivered`, `completed`, `failed`, `expired` |
| `created_at` | `timestamptz` | When command was created |
| `delivered_at` | `timestamptz` | When agent acknowledged receipt |
| `completed_at` | `timestamptz` | When agent reported completion |
| `result_json` | `jsonb` | Result data (e.g., screenshot URL, error message) |
| `expires_at` | `timestamptz` | Auto-expire if not delivered (default: 5 min) |

**Indexes:** `(agent_id, status)`, `(tenant_id, command_type, created_at)`

**Expiry:** Hangfire job cleans up `pending` commands older than `expires_at`. If agent was offline when command was sent, it's expired — manager must re-request.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `AgentRegistered` | `agent.gateway.registered` | New device registered | [[modules/configuration/overview\|Configuration]] (push initial policy) |
| `AgentHeartbeatLost` | `agent.gateway.heartbeat_lost` | No heartbeat for 5+ minutes | [[modules/exception-engine/overview\|Exception Engine]] (flag offline agent) |
| `AgentRevoked` | `agent.gateway.revoked` | Admin revokes agent access | Agent receives 401 on next request |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `EmployeeOffboarded` | `core-hr.employee.offboarded` | [[modules/core-hr/overview\|Core HR]] | Revoke agent registration for offboarded employee |

---

## Key Business Rules

1. **High-throughput ingestion.** The `/agent/ingest` endpoint receives data every 2-3 minutes from every active agent:
   - Minimal validation (schema check only, detailed validation is async)
   - Batch INSERT via `COPY` or `unnest()` for raw buffer
   - Return **202 Accepted** immediately, process asynchronously
   - Rate limit per device (not per user)
2. **Device JWT ≠ User JWT.** Agent JWT contains `device_id` + `tenant_id` but NO user permissions. The `type: "agent"` claim distinguishes them. See [[security/auth-architecture|Auth Architecture]].
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

### Agent-Facing (Device JWT auth)

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/register` | Tenant API key | Register new device, receive device JWT |
| POST | `/api/v1/agent/heartbeat` | Device JWT | Update `last_heartbeat_at`, report health, receive pending commands |
| GET | `/api/v1/agent/policy` | Device JWT | Fetch current monitoring policy (includes app allowlist) |
| POST | `/api/v1/agent/ingest` | Device JWT | Submit activity data batch (202 Accepted) |
| POST | `/api/v1/agent/login` | Device JWT + employee credentials | Link employee to device |
| POST | `/api/v1/agent/logout` | Device JWT | Unlink employee from device |
| GET | `/api/v1/agent/commands` | Device JWT | Fetch pending commands (fallback if SignalR disconnected) |
| POST | `/api/v1/agent/commands/{id}/ack` | Device JWT | Acknowledge command receipt |
| POST | `/api/v1/agent/commands/{id}/complete` | Device JWT | Report command completion with result |

### Manager-Facing (User JWT auth, requires `agent:command` permission)

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agents/{agentId}/capture-screenshot` | User JWT | Request remote screenshot from agent |
| POST | `/api/v1/agents/{agentId}/capture-photo` | User JWT | Request remote photo verification from agent |

### SignalR Hub — `/hubs/agent-commands`

**Connection:** Agent connects after employee login using Device JWT. Maintains persistent connection for real-time command push.

**Server → Agent methods:**

| Method | Payload | Purpose |
|:-------|:--------|:--------|
| `ExecuteCommand` | `{ commandId, type, payload }` | Push any command to agent |
| `StartMonitoring` | `{ sessionId }` | Employee clocked in — begin data collection |
| `StopMonitoring` | `{ reason }` | Employee clocked out — stop data collection |
| `PauseMonitoring` | `{ reason }` | Break started — pause data collection (NO data captured) |
| `ResumeMonitoring` | `{ sessionId }` | Break ended — resume data collection |
| `RefreshPolicy` | `{ }` | Policy changed — agent should re-fetch |

**Agent → Server methods:**

| Method | Payload | Purpose |
|:-------|:--------|:--------|
| `CommandAcknowledged` | `{ commandId }` | Agent received the command |
| `CommandCompleted` | `{ commandId, resultJson }` | Agent completed the command (e.g., screenshot URL) |
| `CommandFailed` | `{ commandId, error }` | Agent failed to execute command |

**Fallback:** If SignalR connection drops, agent polls `GET /api/v1/agent/commands` during each heartbeat cycle. Commands are idempotent — delivering twice is safe.

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
        "duration_seconds": 45,
        "app_category_type": "browser"
      }
    },
    {
      "type": "document_usage",
      "data": {
        "application_name": "Microsoft Excel",
        "document_category": "spreadsheet",
        "duration_seconds": 1800
      }
    },
    {
      "type": "communication_usage",
      "data": {
        "application_name": "Microsoft Outlook",
        "active_seconds": 3600,
        "send_event_count": 12
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
| `ExpirePendingCommandsJob` | Every 1 min | High | Mark `pending` commands past `expires_at` as `expired` |
| `CleanupRevokedAgentsJob` | Daily 3:00 AM | Low | Remove health logs for revoked agents older than 30 days |
| `CleanupCompletedCommandsJob` | Daily 3:00 AM | Low | Remove completed/expired commands older than 7 days |

---

## Important Notes

- **This is the ONLY ingestion endpoint for agent data.** All agent data flows through `/api/v1/agent/ingest`.
- **Rate limiting:** Per device, not per user. Default: 30 requests/minute/device.
- **Data routing:** The ingestion handler routes different `type` values to different modules: `activity_snapshot` → `activity_raw_buffer`, `device_session` → `device_sessions`, `verification_photo` → [[modules/identity-verification/overview|Identity Verification]].
- **Agent does NOT have HR permissions.** It cannot read employee profiles, leave data, or any HR information.

## Features (Server-Side)

- [[modules/agent-gateway/agent-registration/overview|Agent Registration]] — Device registration and employee linking
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]] — Heartbeat tracking and offline agent detection
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]] — Monitoring policy computation and push to agents (includes app allowlist)
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]] — High-throughput batch activity data ingestion (202 Accepted)
- [[modules/agent-gateway/remote-commands/overview|Remote Commands]] — Bidirectional SignalR command channel for server→agent push (capture requests, monitoring lifecycle, policy refresh)
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]] — Listens to workforce-presence events, sends start/stop/pause/resume commands to agent

## WorkPulse Agent Docs

- [[modules/agent-gateway/agent-overview|Agent Overview]] — Start here: architecture, data flow, macOS Phase 2 plan
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Full API contract (6 endpoints, payloads, error handling)
- [[modules/agent-gateway/data-collection|Data Collection]] — 7 collectors with Win32 P/Invoke code samples
- [[modules/agent-gateway/browser-extension|Browser Extension]] — Optional Chrome/Edge/Firefox extension for domain tracking (Phase 2)
- [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] — Named Pipes protocol between Service and TrayApp
- [[modules/agent-gateway/sqlite-buffer|Sqlite Buffer]] — Local SQLite buffer schema, offline resilience
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — Detection strategy, service recovery, reporting
- [[modules/identity-verification/photo-capture|Photo Capture]] — Camera capture flow for identity verification
- [[modules/agent-gateway/tray-app-ui|Tray App Ui]] — MAUI tray app UI states, windows, notifications
- [[modules/agent-gateway/agent-installer|Agent Installer]] — MSIX packaging (Windows Phase 1), macOS .pkg (Phase 2)
- [[modules/agent-gateway/mock-mode|Mock Mode]] — Development without backend (MockGatewayClient)

---

## Related

- [[security/auth-architecture|Auth Architecture]] — Device JWT (separate from user JWT), `type: "agent"` claim
- [[infrastructure/multi-tenancy|Multi Tenancy]] — All agents scoped to tenant via `tenant_id`
- [[backend/messaging/event-catalog|Event Catalog]] — `AgentRegistered`, `AgentHeartbeatLost`, `AgentRevoked`
- [[backend/messaging/error-handling|Error Handling]] — Rate limiting per device, async ingestion with minimal validation
- [[security/data-classification|Data Classification]] — RESTRICTED data (screenshots, photos)
- [[security/compliance|Compliance]] — GDPR monitoring consent, privacy modes
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task file (Agent Gateway section)

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/identity-verification/overview|Identity Verification]], [[modules/auth/overview|Auth]], [[AI_CONTEXT/tech-stack|Tech Stack]]

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.

### App Blocking
Phase 1 logs and alerts on non-allowed app usage but does NOT block applications. Phase 2 will add the ability for the agent to actively prevent non-allowed applications from running (process termination or launch interception). This requires careful implementation to avoid blocking system-critical processes and needs a robust override/emergency-stop mechanism.

### Silent Capture
Phase 1 requires mandatory employee notification before any screenshot or photo capture (GDPR requirement). Phase 2 may add a "silent capture" mode for jurisdictions where this is legally permitted, triggered only for critical exception alerts with explicit legal review. This feature will be gated by tenant jurisdiction configuration and require legal compliance sign-off.

### Agent Auto-Update Push
Phase 1 auto-update is agent-initiated (agent checks for updates on startup/heartbeat). Phase 2 will add server-pushed update commands, forcing agents to update within a specified window. This is needed for critical security patches.
