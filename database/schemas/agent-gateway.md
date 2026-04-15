# Agent Gateway — Schema

**Module:** [[modules/agent-gateway/overview|Agent Gateway]]
**Phase:** Phase 1
**Tables:** 5

---

## `agent_commands`

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

**Foreign Keys:** `agent_id` → [[#`registered_agents`|registered_agents]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `requested_by` → [[database/schemas/infrastructure#`users`|users]]

---

## `agent_health_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `reported_at` | `timestamptz` |  |
| `cpu_usage` | `decimal(5,2)` | Agent process CPU% |
| `memory_mb` | `int` | Agent process memory |
| `errors_json` | `jsonb` | Recent errors array |
| `tamper_detected` | `boolean` | Service stopped/modified |

**Foreign Keys:** `agent_id` → [[#`registered_agents`|registered_agents]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `agent_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `policy_json` | `jsonb` | See policy schema below |
| `last_synced_at` | `timestamptz` | When agent last fetched this policy |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `agent_id` → [[#`registered_agents`|registered_agents]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `registered_agents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees (nullable — set at employee login) |
| `device_id` | `uuid` | Unique device identifier (generated at install) |
| `device_name` | `varchar(100)` | Computer hostname |
| `os_version` | `varchar(50)` | e.g., "Windows 11 23H2" |
| `agent_version` | `varchar(20)` | e.g., "1.0.0" |
| `registered_at` | `timestamptz` |  |
| `last_heartbeat_at` | `timestamptz` | Updated every 60s |
| `status` | `varchar(20)` | `active`, `inactive`, `revoked` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `agent_sessions`

Tracks which employee is currently logged in on each device. Used by the ingest endpoint to validate `employee_id` in the payload.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `device_id` | `uuid` | FK → registered_agents.device_id |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees — the currently logged-in employee |
| `is_active` | `boolean` | Only one active session per device at a time |
| `created_at` | `timestamptz` | When employee logged in via tray app |
| `ended_at` | `timestamptz` | Nullable — set on logout or next login |

UNIQUE partial index: `(device_id) WHERE is_active = true` — enforces one active session per device.

**Flow:** Employee login via tray app → Service calls `POST /api/v1/agent/session/login` → previous session deactivated, new row inserted. Ingest endpoint looks up `agent_sessions` by `device_id` from Device JWT to resolve and validate the `employee_id` in the payload.

**Foreign Keys:** `device_id` → [[#`registered_agents`|registered_agents]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/data-collection|Data Collection]] — employee-device binding flow
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]