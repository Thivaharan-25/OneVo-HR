# Infrastructure Operations End-to-End Logic

## Load Infrastructure View

1. Operator opens System Operations -> Infrastructure.
2. Frontend calls `GET /admin/v1/operations/infrastructure`.
3. Backend verifies `platform.infrastructure.read`.
4. Backend aggregates safe infrastructure metrics.
5. Frontend renders capacity, dependency, and region status.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/operations/infrastructure` | Infrastructure summary | `platform.infrastructure.read` |
| GET | `/admin/v1/operations/infrastructure/dependencies` | Dependency detail | `platform.infrastructure.read` |

## Rules

- Metrics are summarized; no raw provider credentials or internal host secrets.
- If a provider API is unavailable, show stale/degraded state with timestamp.
