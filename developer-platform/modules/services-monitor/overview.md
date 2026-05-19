# Services Monitor

## Purpose

Services Monitor provides detailed operational visibility for individual ONEVO services and platform components - the next level of detail after Platform Health identifies an issue. It shows recent error summaries, latency trends, and allows execution of a pre-approved set of safe service actions.

## Data / Systems Read and Written

| Source | Role |
|---|---|
| Platform Health registry | Registered service/component list, environment, criticality, expected dependencies, and approved actions |
| Health check results | Current and historical status per service |
| Observability / log readers | Error summaries and latency indicators (redacted) |
| Agent command pipeline | Write approved service actions |
| Audit log | Write every service action executed |

## Capabilities

- List all monitored ONEVO services and components with current status
- View per-service detail: uptime %, latency p95, error rate, recent error summary (redacted - no secrets or PII)
- Execute approved safe service actions (e.g., flush cache, restart queue worker) - only pre-registered actions are callable; URL-guessing cannot invoke arbitrary actions
- View recent action history per service

## Navigation

| Route | Permission |
|---|---|
| `/operations/services` | `platform.health.read` |
| Service actions | `platform.health.manage` |

## Key Rules

- Only explicitly registered approved actions can be executed - unknown action names return 400
- Error summaries redact all secrets, connection strings, PII, and internal file paths
- Every executed service action is audit-logged with service name, action name, actor, and timestamp
- Unknown service names return 404 - not a 500
- Service detail routes use the Platform Health `service_key`. Display names are labels only and must not be used as identifiers.
- Services Monitor must not define a second service registry. It reads services, dependencies, criticality, and approved actions from the Platform Health registry.

## Related

- [[developer-platform/modules/services-monitor/end-to-end-logic|Services Monitor End-to-End Logic]]
- [[developer-platform/modules/platform-health/overview|Platform Health]] - high-level health overview
- [[developer-platform/modules/platform-health/health-registry|Platform Health Registry and Rules]] - registry schema shared with Services Monitor
- [[developer-platform/modules/background-jobs/overview|Background Jobs]] - job-level observability
