# Platform Health Registry and Rules

## Purpose

The Platform Health registry is the executable contract for `GET /admin/v1/operations/platform-health`, `GET /admin/v1/operations/platform-health/dependencies`, Platform Health service detail/action rows, and `PlatformHealthCheckJob`.

It turns scattered module, database, authentication, authorization, endpoint, configuration, infrastructure, background job, observability, frontend, and security docs into explicit checks with owners, evidence, thresholds, status mapping, and redaction rules.

## Registry Source

Phase 1 can store the registry in configuration or seed data. Later phases may move it into Dev Platform tables. The runtime shape must stay equivalent to this contract.

The registry is a contract, not evidence. A service can be registered before every reader exists, but missing readers must produce `unknown` check status and must be visible in the API response.

Before real readers are complete, validate the registry and status rules with [[developer-platform/modules/platform-health/contract-validation|Platform Health Contract Validation]]. Those contract tests prove the model and mapping rules only; they do not prove live platform health.

The registry does not replace:

- `backend/module-catalog.md` feature registry
- `module_catalog` commercial module table
- `tenant_module_entitlements` tenant module entitlement table
- existing ASP.NET `/health` and `/health/ready` liveness/readiness probes

Those sources can be read by checks, but they are not themselves a complete Platform Health registry.

## Service Registry Schema

Every monitored service/component must define these fields.

| Field | Required | Description |
|---|---:|---|
| `service_key` | Yes | Stable snake_case identifier returned by APIs and used by Platform Health service detail/action routes |
| `display_name` | Yes | Operator-facing service name |
| `owner_module` | Yes | Module or platform area that owns the service |
| `environment` | Yes | `local`, `dev`, `staging`, `production`, or `all` |
| `criticality` | Yes | `critical`, `high`, `medium`, `low` |
| `phase` | Yes | Product phase where the service is expected to exist |
| `status_weight` | Yes | Weight for `overall_health_pct`; critical services must have higher weight than low criticality services |
| `health_endpoint` | Conditional | Endpoint or reader name if the service exposes a direct probe |
| `expected_dependencies` | Yes | Dependency keys that must be evaluated with this service |
| `checks` | Yes | Ordered check definitions from this document |
| `freshness_sla_seconds` | Yes | Maximum accepted age of evidence before status becomes `unknown` |
| `timeout_ms` | Yes | Max duration for the service reader before status becomes `unknown` |
| `safe_actions` | Yes | Approved Platform Health service actions; empty list if no actions are permitted |
| `redaction_policy` | Yes | Must be `platform_health_default` unless a stricter named policy exists |

Rules:

- `service_key` values are stable API identifiers. Renaming a service key is a breaking API change.
- `environment = "all"` means the service is expected in every environment. Environment-specific services must not be evaluated outside their configured environment.
- `expected_dependencies` must reference dependency keys defined in the dependency registry. Unknown dependency keys make the service registry invalid at startup.
- `checks` must reference implemented reader names or explicitly documented planned readers. Planned readers return `unknown` until implemented.
- `safe_actions` must be allowlisted by service and action key. A UI route, URL parameter, or operator-supplied command must never create an action dynamically.

## Dependency Registry Schema

Every dependency referenced by a service must define these fields.

| Field | Required | Description |
|---|---:|---|
| `dependency_key` | Yes | Stable snake_case identifier used by services and dependency APIs |
| `display_name` | Yes | Operator-facing dependency name |
| `type` | Yes | `database`, `queue`, `cache`, `storage`, `email`, `payment`, `identity_provider`, `dns_cdn`, `observability`, `secret`, `external_api`, or `internal_component` |
| `environment` | Yes | `local`, `dev`, `staging`, `production`, or `all` |
| `criticality` | Yes | `critical`, `high`, `medium`, `low` |
| `owner_module` | Yes | Module or platform area responsible for the dependency relationship |
| `evidence_source` | Yes | Endpoint, query, metric, job store, options validator, or log reader that proves dependency state |
| `freshness_sla_seconds` | Yes | Maximum accepted age of dependency evidence |
| `timeout_ms` | Yes | Max duration before dependency status becomes `unknown` |
| `redacted_fields` | Yes | Fields that must never be returned |
| `evidence_returned` | Yes | Safe fields returned to operators |

Dependency rules:

- A critical dependency marked `down` forces dependent critical services to at least `degraded`; it forces `down` only when the service cannot operate without that dependency.
- Missing dependency evidence maps to `unknown`, not `healthy`.
- Dependency checks must not expose connection strings, host IPs, credentials, account identifiers, tenant/customer PII, or raw provider error payloads.

## Check Definition Schema

Each `checks[]` entry must define:

| Field | Required | Description |
|---|---:|---|
| `check_key` | Yes | Stable key unique within the service |
| `check_type` | Yes | `http_probe`, `db_probe`, `migration_probe`, `auth_probe`, `authorization_probe`, `route_probe`, `di_probe`, `config_probe`, `job_probe`, `queue_probe`, `observability_probe`, `security_probe`, or `frontend_probe` |
| `evidence_source` | Yes | Exact source read by the check: endpoint, query, log reader, options validator, job store, metric, or test output |
| `expected_result` | Yes | Pass condition expressed as a concrete threshold or required value |
| `degraded_when` | Yes | Condition that maps to `degraded` |
| `down_when` | Yes | Condition that maps to `down` |
| `unknown_when` | Yes | Timeout, stale evidence, missing reader, missing permission, or unavailable dependency condition |
| `redacted_fields` | Yes | Fields that must never be returned |
| `evidence_returned` | Yes | Safe fields returned to the API response for operator verification |

Check rules:

- A check definition without a real `evidence_source` is a planned check. Planned checks are valid for roadmap visibility but must return `unknown`.
- Evidence must include `checked_at` or an equivalent timestamp. Evidence older than `freshness_sla_seconds` maps to `unknown`.
- A reader failure before safe evidence is produced maps to `unknown`; a reader result that proves the target is unavailable maps to `down`.
- Any check that depends on production-only metrics must define a local/dev substitute or be environment-scoped away from local/dev.

## Health Reader Result Contract

Each reader must return a normalized result before the Platform Health API maps status.

```json
{
  "check_key": "db_migration_state",
  "status_hint": "healthy",
  "checked_at": "2026-05-17T00:00:00Z",
  "duration_ms": 38,
  "evidence": {
    "latest_migration_id": "20260515155230_AddGlobalEmailDirectory",
    "pending_migration_count": 0
  },
  "redaction_applied": true,
  "reader_error_code": null
}
```

Rules:

- `status_hint` is advisory. Final status is calculated from the registry thresholds.
- `redaction_applied = true` is required before evidence can be returned.
- `reader_error_code` may contain a stable internal code such as `reader_timeout` or `permission_denied`; it must not contain raw exception text.
- Raw SQL, raw HTTP responses, stack traces, connection details, request cookies, JWTs, and secrets are never reader evidence.

## Required Check Groups

These groups are required for Platform Health to be reliable. If a group is not implemented, its status is `unknown`; it must not be reported as healthy.

| Group | Required Evidence |
|---|---|
| Service registry | Registered service count, environment, owner module, criticality, expected dependencies, enabled phase |
| Database health | Live DB connection result, `__EFMigrationsHistory` latest row, applied vs pending migration count, required table existence sample, PgBouncer/pool usage if available, read/write probe result in non-production-safe form |
| Authentication health | Login flow integration result, refresh result, token generation/validation result, configured signing key presence/length result, recent auth failure count |
| Authorization and entitlement health | Permission catalog read result, role permission resolution result, tenant module entitlement read result, module-filtered permission catalog result when implemented |
| API endpoint health | Route map/OpenAPI availability, representative endpoint probe results, response contract validation result |
| Dependency injection health | Container boot result, missing service report, lifetime conflict report if the DI validator supports it |
| Configuration health | Required options validation result, redacted env/config validation result, fail-fast secret validation result outside dev |
| Infrastructure health | CPU, memory, storage, DB pool, queue depth, external provider status, detected-at timestamp for degraded dependencies |
| Background jobs | Worker heartbeat, failed job count, queue depth, last successful run per critical job, next scheduled run |
| Observability | Log reader availability, metrics reader availability, trace/correlation-id presence, alert write/read result |
| Frontend/client health | Build or smoke-test result, configured API base URL presence, credentials/cookie mode validation, session refresh check |
| Security health | CORS policy check, security header scan, secret scan result, HTTPS middleware/order evidence where available, rate limit rule read result |

## Status Mapping

| Status | Meaning |
|---|---|
| `healthy` | All required checks pass with fresh evidence |
| `degraded` | One or more checks breach degraded thresholds, but the service is still partially usable |
| `down` | Required check proves the service is unavailable or a critical dependency is unavailable |
| `unknown` | Evidence is missing, stale, timed out, inaccessible, or the reader failed before producing safe evidence |

Rules:

- `unknown` is never converted to `healthy`.
- A timed-out reader returns that service/check as `unknown`; it does not block the full response.
- Overall response remains HTTP 200 when at least the Platform Health API itself can return a redacted status payload.
- Critical service `down` status must create or update a Platform Health alert through `PlatformHealthCheckJob`.
- Degraded or down dependency entries must include `detected_at` when the source can provide it.

## Overall Health Calculation

`overall_health_pct` must be deterministic and must not hide missing evidence.

Rules:

- Calculate score from all registry services enabled for the current environment.
- Each service contributes its `status_weight`.
- Service score values are: `healthy = 1.0`, `degraded = 0.5`, `down = 0.0`, `unknown = 0.0`.
- `unknown` checks are also returned in `unknown_check_count`; they are not silently excluded from the denominator.
- If every enabled service is `unknown`, return `overall_health_pct = 0` and `overall_status = "unknown"`.
- If any critical service is `down`, `overall_status = "down"` regardless of percentage.
- If any critical service is `unknown`, `overall_status` cannot be better than `degraded`.
- The API may include `healthy_check_count`, `degraded_check_count`, `down_check_count`, and `unknown_check_count` to make the score auditable.

## Minimum API Response Contract

`GET /admin/v1/operations/platform-health` returns:

```json
{
  "overall_health_pct": 93.5,
  "overall_status": "healthy",
  "generated_at": "2026-05-17T00:00:00Z",
  "evidence_fresh_until": "2026-05-17T00:02:00Z",
  "healthy_check_count": 42,
  "degraded_check_count": 1,
  "down_check_count": 0,
  "unknown_check_count": 0,
  "services": [
    {
      "service_key": "auth_service",
      "display_name": "Auth Service",
      "environment": "production",
      "criticality": "critical",
      "status": "healthy",
      "latency_p95_ms": 120,
      "latency_p99_ms": 260,
      "error_rate_pct": 0.02,
      "last_checked_at": "2026-05-17T00:00:00Z",
      "checks": [
        {
          "check_key": "token_validation",
          "status": "healthy",
          "checked_at": "2026-05-17T00:00:00Z",
          "evidence": {
            "validated_at": "2026-05-17T00:00:00Z",
            "failure_count_5m": 0
          }
        }
      ],
      "dependencies": ["postgresql", "jwt_signing_key"],
      "links": {
        "service_detail": "/operations/platform-health/services/auth_service"
      }
    }
  ]
}
```

`GET /admin/v1/operations/platform-health/dependencies` returns dependency-level entries with `dependency_key`, `type`, `status`, `criticality`, `last_checked_at`, `detected_at` when degraded/down, and safe evidence fields only.

The Platform Health Service Health section must use the same service and dependency keys returned by these APIs. It may add historical summaries and approved actions, but it must not introduce service names, dependencies, status thresholds, or actions that are absent from the registry.

## Redaction Rules

Platform Health and its service detail/action sections must never return:

- connection strings
- API keys or signing keys
- raw JWTs, cookies, or refresh tokens
- internal IP addresses
- raw exception payloads
- stack traces
- employee, tenant user, or customer PII
- full environment variable dumps

Return boolean or summarized evidence instead, such as `configured = true`, `minimum_length_met = true`, `failure_count_5m = 2`, or `pending_migration_count = 0`.

## Phase 1 Minimum Registry Entries

These entries align with the current Platform Health docs and should exist before Platform Health is considered complete.

| Service Key | Owner Module | Criticality | Required Check Groups |
|---|---|---|---|
| `api_gateway` | Backend API | critical | API endpoint, DI, configuration, security, observability |
| `auth_service` | Auth & Security | critical | Authentication, authorization, database, configuration, security |
| `data_service` | Shared Platform / Database | critical | Database, migration, configuration, observability |
| `sync_service` | SignalR / Realtime | high | API endpoint, observability, infrastructure |
| `background_jobs` | Background Jobs | high | Background jobs, queue, database, observability |
| `agent_gateway` | Agent Gateway | high | API endpoint, authorization, queue, observability |
| `reporting_engine` | Reporting Engine | medium | Job, database read, API endpoint, observability |
| `ai_insights_engine` | Agentic AI / Insights | medium | API endpoint, entitlement, external dependency, observability |
| `frontend_console` | Developer Platform Frontend | medium | Frontend/client, configuration, authentication session |
| `external_dependencies` | Infrastructure Operations | high | Payment, email, storage, DNS/CDN, cloud provider checks |

## Phase 1 Minimum Reader Gates

Platform Health cannot be marked complete until these gates are satisfied.

| Gate | Required Proof |
|---|---|
| Registry validation | Startup validation rejects duplicate service keys, unknown dependency keys, invalid criticality, empty check lists, and unsafe action definitions |
| Database reader | Safe output for live connection, latest migration, pending migration count, table sample, and read/write probe |
| Auth reader | Safe output for login integration result, refresh result, token validation result, signing key presence/length, and recent failure count |
| Entitlement reader | Safe output for permission catalog, role permission resolution, tenant entitlement read, and module-filtered permission result or explicit `unknown` |
| API reader | Route/OpenAPI availability plus representative endpoint probes |
| DI/config reader | Container boot/options validation output with no secret values |
| Job/queue reader | Worker heartbeat, failed job count, queue depth, last success, and next scheduled run for critical jobs |
| Observability reader | Log, metric, trace/correlation, and alert write/read availability |
| Frontend reader | Build or smoke result, API URL configuration, cookie/credential mode, and session refresh behavior |
| Security reader | CORS policy, security headers, secret scan, HTTPS middleware/order evidence where available, and rate-limit rule read |

## Known Gaps To Track

- Module-filtered role permission assignment is deferred in current focus docs; entitlement health must report the related check as `unknown` or `degraded` until implemented, not healthy.
- Browser token storage must be checked against the documented BFF cookie model before frontend auth health can be marked healthy.
- Live production database, queue, logs, metrics, and traces cannot be inferred from documentation. They require runtime readers or captured test output.
- Current backend source may not yet expose the Platform Health endpoints or readers. Until code and test output prove those endpoints exist, this document is a target contract, not implementation evidence.
