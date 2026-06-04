# Platform Health

## Purpose

Platform Health shows the current operational state of all ONEVO services in one view. It is the first screen operators check when investigating an incident or responding to a dashboard alert about service degradation.

## Data / Systems Read

| Source | Role |
|---|---|
| Health registry | Canonical monitored services, dependencies, criticality, checks, thresholds, and evidence requirements |
| Health check results | Per-service status, latency p95/p99, error rate, dependency probe results, and stale/unknown states |
| Background job store | Job queue health |
| SignalR hub telemetry | Real-time connection health |
| Infrastructure metrics | CPU, memory, storage |
| Agent Gateway | Agent command pipeline health |
| Observability readers | Redacted log, metric, trace, and alert availability |
| Configuration validators | Redacted options, secret presence/length, and environment validation results |

## Monitored Services

| Service | Healthy Threshold |
|---|---|
| API Gateway | Latency p99 < 500ms, error rate < 0.1% |
| Auth Service | Success rate > 99.9% |
| Data Service | DB error rate < 0.01% |
| Sync Service (SignalR) | Drop rate < 1% in window |
| Reporting Engine | Job failure rate < 1% |
| AI Insights Engine | Error rate < 2%, p95 < 3s |

## Capabilities

- Overall health percentage with weighted per-service breakdown
- Per-service: status badge (Healthy / Degraded / Down / Unknown), uptime %, latency, error rate
- Dependency health: database, external services, payment gateways, email provider
- Link to Services Monitor for deeper investigation of a specific service
- Show read-only background job and dependency health summaries; standalone Background Jobs and Infrastructure Operations screens are Phase 2

## Navigation

| Route | Permission |
|---|---|
| `/operations/platform-health` | `platform.health.read` |

## Key Rules

- This module is read-only in Phase 1
- Response must not contain connection strings, API keys, or internal infrastructure secrets
- A single failing service does not fail the whole health response; each service is shown independently
- Health check reader timeout shows `status = "unknown"` rather than blocking the page
- Services, dependencies, thresholds, criticality, and required evidence must come from the health registry contract, not hardcoded UI logic
- `overall_health_pct` is computed from all enabled registry services; `unknown` is counted as failed evidence and is not excluded from the denominator
- Documentation-only claims are not health evidence. A check is healthy only when a runtime reader, captured test result, or validator output proves it.
- The UI must show unknown checks and missing readers clearly enough for operators to distinguish "not implemented" from "healthy".

## Related

- [[developer-platform/modules/platform-health/end-to-end-logic|Platform Health End-to-End Logic]]
- [[developer-platform/modules/platform-health/health-registry|Platform Health Registry and Rules]]
- [[developer-platform/modules/platform-health/contract-validation|Platform Health Contract Validation]]
- [[developer-platform/modules/services-monitor/overview|Services Monitor]] - detailed per-service metrics
- [[developer-platform/modules/background-jobs/overview|Background Jobs]] - Phase 2 standalone job operations; Phase 1 shows summary health only
- [[developer-platform/modules/dashboard/overview|Dashboard]] - platform health widget (summary)
