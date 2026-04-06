# Operations Documentation: ONEVO

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [[monitoring]] | Dashboards, alerting rules, golden signals |
| [[observability]] | Distributed tracing, correlation IDs, Serilog |

## SLA Targets

| Metric | Target |
|:-------|:-------|
| Uptime | 99.9% |
| API Response (p95) | < 500ms |
| API Response (p99) | < 2s |
| RTO | 15 minutes |
| RPO | 1 minute |

## Observability Stack

- **Logging:** Serilog → OpenTelemetry → Grafana Loki
- **Metrics:** Prometheus → Grafana
- **Tracing:** OpenTelemetry → Grafana Tempo
- **Alerting:** Grafana alerting rules → PagerDuty/Slack

## Golden Signals

| Signal | What to Monitor |
|:-------|:---------------|
| Latency | API response time (p50, p95, p99) |
| Traffic | Requests per second by endpoint |
| Errors | 4xx/5xx rates, exception rates |
| Saturation | CPU, memory, DB connections, Redis connections |

## Related

- [[logging-standards]] — structured logging with Serilog
- [[ci-cd-pipeline]] — deployment monitoring
- [[performance]] — database query monitoring
- [[tech-stack]] — observability stack components
