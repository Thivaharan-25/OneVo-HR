# Heartbeat Monitoring

**Module:** Agent Gateway
**Feature:** Heartbeat Monitoring

---

## Purpose

Agents send heartbeats every 60 seconds. If no heartbeat for 5+ minutes, fires `AgentHeartbeatLost` event. Also collects health data (CPU, memory, errors, tamper detection).

## Database Tables

### `agent_health_logs`

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

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AgentHeartbeatLost` | No heartbeat for 5+ minutes | [[modules/exception-engine/overview\|Exception Engine]] (flag offline agent) |

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `DetectOfflineAgentsJob` | Every 5 min | High | Find agents with stale heartbeat |
| `CleanupRevokedAgentsJob` | Daily 3:00 AM | Low | Remove health logs for revoked agents older than 30 days |

## API Endpoints

| Method | Route | Auth | Description |
|:-------|:------|:-----|:------------|
| POST | `/api/v1/agent/heartbeat` | Device JWT | Update heartbeat, report health |
