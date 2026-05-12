# Contract: Agent Gateway (Fleet Health + Install + Version)

**Backend owner:** DEV4 Tasks 1, 3, 7, 8  
**Consumers:** DEV6 Task 4 (fleet health), DEV8 Task 5 (install flow), DEV5 Tasks 6-7 (version manager via admin-api.md)  
**Canonical source:** `ONEVO.Application/Features/AgentGateway/` and `ONEVO.Application/Features/DevPlatform/`

---

## GET `/api/v1/agent/fleet` (admin/manager only, cursor paginated)

```ts
interface AgentFleetItemDto {
  agent_id: string
  device_name: string
  employee_id: string
  employee_name: string
  state: "online" | "degraded" | "offline" | "failed"
  agent_version: string
  os_version: string
  last_heartbeat_at: string
  policy_state: "current" | "pending" | "error"
}
```

## GET `/api/v1/agent/fleet/{agentId}`

```ts
interface AgentDetailDto {
  agent_id: string
  device_name: string
  employee_id: string
  registered_at: string
  current_session: { session_id: string; started_at: string } | null
  policy: { version: number; applied_at: string }
  health_logs: Array<{ state: string; recorded_at: string; detail: string | null }>
}
```

## POST `/api/v1/agent/ingest`

Auth: Device JWT only. Tenant ownership is resolved from token claims, not from the JSON payload.

```ts
interface AgentDeviceClaims {
  type: "agent"
  tenant_id: string
  agent_id: string
  device_id: string
}

interface AgentIngestPayload {
  device_id?: string       // validation hint; must match JWT claim when present
  employee_id?: string     // validation hint; must match active agent_sessions row
  timestamp: string
  batch: AgentIngestItem[]
}

type AgentIngestItem =
  | ActivitySnapshotItem
  | AppUsageItem
  | DeviceSessionItem
  | WorkLocationEvidenceItem
  | MeetingItem

interface ActivitySnapshotItem {
  type: "activity_snapshot"
  data: {
    keyboard_events_count: number
    mouse_events_count: number
    active_seconds: number
    idle_seconds: number
    foreground_process_name?: string
    captured_at: string
  }
}

interface AppUsageItem {
  type: "app_usage"
  data: {
    process_name: string          // required, authoritative app identity
    application_name?: string     // display metadata only
    publisher?: string | null
    executable_path_hash?: string | null
    window_title_hash?: string | null
    duration_seconds: number
    captured_at: string
  }
}

interface DeviceSessionItem {
  type: "device_session"
  data: Record<string, unknown>
}

interface WorkLocationEvidenceItem {
  type: "work_location_evidence"
  data: Record<string, unknown>
}

interface MeetingItem {
  type: "meeting"
  data: Record<string, unknown>
}
```

Server rules:

- `tenant_id`, `agent_id`, and trusted `device_id` come from Device JWT claims.
- Client-sent `tenant_id` is ignored or rejected.
- `employee_id` comes from the active `agent_sessions` row for the device.
- App allowlist/blocklist matching uses `process_name`; `application_name` is never authoritative.

## POST `/api/v1/ide/agent-install/request`

```ts
// response
interface AgentInstallJobDto {
  job_id: string
  download_url: string
  sha256_hash: string         // extension must verify before running installer
  expires_at: string
}
```

## GET `/api/v1/ide/agent-install/status/{jobId}`

```ts
interface AgentInstallStatusDto {
  job_id: string
  status: "pending" | "downloading" | "installing" | "installed" | "failed"
  error: string | null
}
```

## Notes

- Device credential (`type: "agent"` JWT claim) is completely separate from user JWT - never reuse
- `sha256_hash` must be verified by the extension client before running the downloaded installer
- Agent fleet API is scoped to the requesting user's tenant; cross-tenant fleet view is admin-only via `/admin/v1/*`
- Agent version release and ring management DTOs live in `admin-api.md` (served by `ONEVO.Api` `/admin/v1/*`)

