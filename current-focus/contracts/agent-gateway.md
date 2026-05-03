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
- Agent version release and ring management DTOs live in `admin-api.md` (served by `ONEVO.Admin.Api`)

