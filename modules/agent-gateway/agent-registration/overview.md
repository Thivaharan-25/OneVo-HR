# Agent Registration

**Module:** Agent Gateway
**Feature:** Agent Registration

---

## Purpose

Handles login-based Windows agent enrollment and employee-device linking. In Phase 1, the default flow is:

```
Install WorkPulse Agent
-> Tray app opens sign-in
-> User signs in
-> Backend resolves tenant and employee
-> Device is enrolled
-> Internal device credential is stored locally
-> Policy is fetched
-> Monitoring starts only when Time & Attendance lifecycle allows it
```

Employees never enter an API key, tenant key, tenant ID, or server URL. The device credential is issued by the backend after authenticated enrollment and is stored by the agent using DPAPI / Windows Credential Manager. The user does not see or handle the credential.

## Database Tables

### `registered_agents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, resolved from authenticated user |
| `employee_id` | `uuid` | FK -> employees, set after successful tray sign-in |
| `device_id` | `uuid` | Unique device identifier generated on install |
| `device_name` | `varchar(100)` | Computer hostname |
| `os_version` | `varchar(50)` | e.g., "Windows 11 23H2" |
| `agent_version` | `varchar(20)` | e.g., "1.0.0" |
| `registered_at` | `timestamptz` | First successful enrollment |
| `last_heartbeat_at` | `timestamptz` | Updated every 60s |
| `status` | `varchar(20)` | `active`, `inactive`, `revoked` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Indexes:** `(tenant_id, device_id)` UNIQUE, `(tenant_id, status)`, `(tenant_id, employee_id)`

### `agent_sessions`

Tracks the currently logged-in employee on an enrolled device.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `device_id` | `uuid` | FK -> registered_agents.device_id |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `is_active` | `boolean` | Only one active session per device |
| `created_at` | `timestamptz` | Login/enrollment completion time |
| `ended_at` | `timestamptz` | Set on logout or next login |

**Index:** UNIQUE `(device_id) WHERE is_active = true`

## Key Business Rules

1. Login-based enrollment is the default Phase 1 source of truth. Tenant-key registration is legacy/admin-only and must not be used as the employee install flow.
2. `enroll/start` creates a short-lived enrollment challenge for the TrayApp/system-browser sign-in.
3. `enroll/complete` validates the authenticated user, resolves `tenant_id` and `employee_id`, creates or updates `registered_agents`, creates the active `agent_sessions` row, and returns the internal device credential.
4. Device credential contains `device_id`, `tenant_id`, and `type: "agent"` claims. It contains no HR permissions and is not a user JWT.
5. Agent does not have HR permissions. It can only call Agent Gateway endpoints with the device credential.
6. Data ingestion is rejected unless the payload employee matches the active `agent_sessions` record for the device.
7. Monitoring starts only after login/enrollment, policy fetch, consent gate, and Time & Attendance lifecycle permit collection.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AgentRegistered` | New device is enrolled | [[modules/configuration/overview\|Configuration]] (push initial policy) |
| `AgentSessionStarted` | Employee is linked to an enrolled device | [[modules/agent-gateway/monitoring-lifecycle/overview\|Monitoring Lifecycle]] |
| `AgentRevoked` | Admin revokes agent access | Agent receives 401 on next request |

## API Endpoints

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/enroll/start` | User sign-in challenge | Start login-based device enrollment |
| POST | `/api/v1/agent/enroll/complete` | Authenticated user + challenge | Enroll device, create/link session, return internal device credential |
| POST | `/api/v1/agent/login` | Device credential + user auth/session | Resume or refresh employee-device session |
| POST | `/api/v1/agent/logout` | Device credential | End active employee-device session |

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/agent-gateway/agent-installer|Agent Installer]]
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]
- [[modules/auth/overview|Auth]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
