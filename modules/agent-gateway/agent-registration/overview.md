# Agent Registration

**Module:** Agent Gateway
**Feature:** Agent Registration

---

## Purpose

Handles desktop agent registration and employee linking. New devices register using a tenant API key and receive a device JWT. When an employee logs in via the MAUI tray app, the device is linked to their profile.

## Database Tables

### `registered_agents`

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

## Key Business Rules

1. Device JWT contains `device_id` + `tenant_id` + `type: "agent"` claim — NO user permissions.
2. Employee linking: device registers with `employee_id = null`, set on employee login.
3. Agent does NOT have HR permissions.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AgentRegistered` | New device registered | [[modules/configuration/overview|Configuration]] (push initial policy) |
| `AgentRevoked` | Admin revokes agent access | Agent receives 401 on next request |

## API Endpoints

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/register` | Tenant API key | Register new device, receive device JWT |
| POST | `/api/v1/agent/login` | Device JWT + employee credentials | Link employee to device |
| POST | `/api/v1/agent/logout` | Device JWT | Unlink employee from device |

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
