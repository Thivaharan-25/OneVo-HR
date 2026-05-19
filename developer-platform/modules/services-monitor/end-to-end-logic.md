# Services Monitor End-to-End Logic

## Inspect Service

1. Operator opens System Operations -> Services Monitor.
2. Frontend calls `GET /admin/v1/operations/services`.
3. Operator opens a service detail.
4. Frontend calls `GET /admin/v1/operations/services/{serviceKey}`.
5. Backend returns status, recent errors, latency, and safe dependency metadata.

## Optional Service Action

1. Operator selects a supported action such as retry health probe.
2. Backend verifies `platform.health.manage`.
3. Backend queues or executes the action through a safe service interface.
4. Backend writes an audit event.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/operations/services` | Service list | `platform.health.read` |
| GET | `/admin/v1/operations/services/{serviceKey}` | Service detail | `platform.health.read` |
| POST | `/admin/v1/operations/services/{serviceKey}/actions/{action}` | Safe service action | `platform.health.manage` |

## Rules

- Raw logs are not returned in Phase 1; expose summarized, redacted diagnostics only.
- Unsupported service actions return `404` or validation failure, not ad hoc command execution.
- Service keys, dependencies, criticality, and approved actions come from the Platform Health registry.
- Display names are labels only. The route identifier is always `service_key`.
