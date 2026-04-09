# Policy Distribution

**Module:** Agent Gateway
**Feature:** Policy Distribution

---

## Purpose

Distributes monitoring policies to desktop agents. Policy is computed by merging tenant-level toggles with per-employee overrides.

## Database Tables

### `agent_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `agent_id` | `uuid` | FK → registered_agents |
| `tenant_id` | `uuid` | FK → tenants |
| `policy_json` | `jsonb` | See policy schema |
| `last_synced_at` | `timestamptz` | When agent last fetched |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

## Policy Merge Pattern

```csharp
var tenantPolicy = await _configService.GetMonitoringTogglesAsync(tenantId, ct);
var employeeOverride = await _configService.GetEmployeeOverrideAsync(employeeId, ct);
var effectivePolicy = tenantPolicy.MergeWith(employeeOverride); // Override wins
```

## API Endpoints

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| GET | `/api/v1/agent/policy` | Device JWT | Fetch current monitoring policy |

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[modules/agent-gateway/policy-distribution/end-to-end-logic|Policy Distribution — End-to-End Logic]]
- [[modules/agent-gateway/policy-distribution/testing|Policy Distribution — Testing]]
- [[frontend/architecture/overview|Heartbeat Monitoring]]
- [[frontend/architecture/overview|Data Ingestion]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
