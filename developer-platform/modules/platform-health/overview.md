# Platform Health

## Purpose

Platform Health shows the current operational state of ONEVO inside the Operations area. It is the first operational screen operators check when investigating an incident or responding to a dashboard alert about service degradation.

## Data / Systems Read

| Source | Role |
|---|---|
| Health registry | Canonical monitored services, dependencies, criticality, checks, thresholds, evidence requirements, and approved safe service actions |
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
- Per-service status rows with status badge (Healthy / Degraded / Down / Unknown), uptime %, latency, error rate, redacted evidence, and approved safe service actions
- Dependency health: database, external services, payment gateways, email provider, storage, DNS/CDN, and cloud provider checks when available
- Read-only background job summary: worker heartbeat, failed job count, queue depth, last critical job run, and next scheduled run
- Configuration checks: required options, redacted environment validation, and secret presence/length validation
- Security checks: CORS policy, security headers, HTTPS middleware/order evidence, and rate-limit rule read result when available
- Recent events: degraded service, failed check, recovery, alert creation, alert acknowledgement, and approved operator action
- Standalone Background Jobs, Infrastructure Operations, Device Management, and Agent Versions screens are Phase 2

## Navigation

| Route | Permission |
|---|---|
| `/operations/platform-health` | `platform.health.read` |
| Safe service actions on the Platform Health screen | `platform.health.manage` |

## Key Rules

- Health visibility is read-only in Phase 1; approved safe service actions require `platform.health.manage`
- Response must not contain connection strings, API keys, or internal infrastructure secrets
- A single failing service does not fail the whole health response; each service is shown independently
- Health check reader timeout shows `status = "unknown"` rather than blocking the page
- Services, dependencies, thresholds, criticality, required evidence, and approved action keys must come from the health registry contract, not hardcoded UI logic
- `overall_health_pct` is computed from all enabled registry services; `unknown` is counted as failed evidence and is not excluded from the denominator
- Documentation-only claims are not health evidence. A check is healthy only when a runtime reader, captured test result, or validator output proves it.
- The UI must show unknown checks and missing readers clearly enough for operators to distinguish "not implemented" from "healthy".

## Related

- [[developer-platform/modules/platform-health/end-to-end-logic|Platform Health End-to-End Logic]]
- [[developer-platform/modules/platform-health/health-registry|Platform Health Registry and Rules]]
- [[developer-platform/modules/platform-health/contract-validation|Platform Health Contract Validation]]
- [[developer-platform/modules/background-jobs/overview|Background Jobs]] - Phase 2 standalone job operations; Phase 1 shows summary health only
- [[developer-platform/modules/dashboard/overview|Dashboard]] - platform health widget (summary)
