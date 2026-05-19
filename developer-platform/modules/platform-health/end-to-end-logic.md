# Platform Health End-to-End Logic

## Load Health Dashboard

1. Operator opens System Operations -> Platform Health.
2. Frontend calls `GET /admin/v1/operations/platform-health`.
3. Backend verifies `platform.health.read`.
4. Backend loads the Platform Health registry.
5. Backend validates registry shape: unique service keys, valid dependency references, valid check definitions, and safe action allowlists.
6. Backend calls registered health readers with per-reader timeout and freshness limits.
7. Backend normalizes reader results and applies redaction before returning evidence.
8. Backend maps check evidence to `healthy`, `degraded`, `down`, or `unknown`.
9. Backend calculates weighted `overall_health_pct` from all enabled registry services; `unknown` counts as failed evidence.
10. Frontend renders service status, uptime, dependency state, degraded/down components, and unknown/missing evidence.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/operations/platform-health` | Overall platform health | `platform.health.read` |
| GET | `/admin/v1/operations/platform-health/dependencies` | Dependency-level health | `platform.health.read` |

## Failure Handling

- Health readers must time out quickly.
- Unknown health state must render as degraded, not healthy.
- Secrets and raw exception payloads must be redacted.
- Missing, stale, or timed-out evidence maps to `status = "unknown"`.
- A single failed reader must not fail the whole endpoint when the API can still return a redacted status payload.
- A registry validation failure is a platform configuration error. The API may return a safe 500 for invalid registry shape, but it must not silently drop invalid services.
- Reader output that is not redacted is discarded and maps to `unknown`.

## Registry Rules

- Services, dependencies, criticality, expected evidence, thresholds, and approved actions come from [[developer-platform/modules/platform-health/health-registry|Platform Health Registry and Rules]].
- The UI must not hardcode pass/fail rules that are absent from the registry.
- `PlatformHealthCheckJob` uses the same registry and status mapping as the read endpoints.
- Services Monitor must use the same `service_key`, dependency keys, and approved action keys. It can show more detail, but it must not define a second service registry.
