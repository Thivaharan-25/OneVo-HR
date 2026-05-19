# Device Management

## Purpose

Device Management provides cross-tenant visibility into all registered ONEVO desktop agent devices and their current state. It allows operators to investigate device issues and queue approved support commands — without exposing any employee activity content.

## Data / Systems Read and Written

| Source | Role |
|---|---|
| Agent Gateway device registry | Read device state, agent version, ring, last heartbeat |
| Tenant registry | Read tenant context for each device |
| Agent command pipeline | Write approved support commands |
| Audit log | Write every command queued |

## Capabilities

- List all registered devices across all tenants with: device name, tenant, OS, agent version (with up-to-date / outdated / unsupported badge), connection status (Online / Idle / Offline), assigned user, last heartbeat, deployment ring
- Filter by: tenant, status, agent version, deployment ring
- View per-device detail: version history, recent commands, last check-in
- Queue approved agent commands: `UPDATE_AGENT`, `COLLECT_DIAGNOSTIC`, `RESTART_SERVICE` — only pre-approved command types accepted
- All commands are audit-logged with device, tenant, command type, operator, and reason

## Navigation

| Route | Permission |
|---|---|
| `/operations/devices` | `platform.health.read` |
| Queue commands | `platform.health.manage` |

## Key Rules

- Device views must not expose captured employee activity data — no application usage logs, screenshot data, keystroke counts, or session content
- Only pre-registered approved command types can be queued — URL-guessing cannot invoke arbitrary commands
- Every queued command is audit-logged
- Cross-tenant data is never mixed: viewing device from Tenant A never returns data from Tenant B

## Related

- [[developer-platform/modules/device-management/end-to-end-logic|Device Management End-to-End Logic]]
- [[developer-platform/modules/agent-version-manager/overview|Agent Version Manager]] — version catalog and ring assignments
- [[modules/agent-gateway/overview|Agent Gateway]] — agent command infrastructure
