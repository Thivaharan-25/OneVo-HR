# Platform Health Contract Validation

## Purpose

Use this artifact before the Platform Health endpoint and real readers are fully built. It validates whether the registry model, fake reader outputs, status mapping, redaction rules, and overall health calculation are coherent.

This is not runtime evidence. Passing these contract tests proves the model is implementable; it does not prove the live platform is healthy.

## Minimum Registry Fixture

The fixture must be enough to test critical services, medium services, dependencies, missing evidence, planned readers, redaction, and score calculation.

```json
{
  "environment": "local",
  "services": [
    {
      "service_key": "auth_service",
      "display_name": "Auth Service",
      "owner_module": "Auth & Security",
      "environment": "all",
      "criticality": "critical",
      "phase": "phase_1",
      "status_weight": 5,
      "health_endpoint": "reader:auth_health_reader",
      "expected_dependencies": ["postgresql", "jwt_signing_key"],
      "freshness_sla_seconds": 120,
      "timeout_ms": 2000,
      "safe_actions": [],
      "redaction_policy": "platform_health_default",
      "checks": [
        {
          "check_key": "login_flow",
          "check_type": "auth_probe",
          "evidence_source": "test_output:LoginTests.ValidCredentialsCreatesSession",
          "expected_result": "last_result = pass and failure_count_5m <= 3",
          "degraded_when": "failure_count_5m > 3 and failure_count_5m <= 10",
          "down_when": "last_result = fail and failure_count_5m > 10",
          "unknown_when": "missing reader, stale evidence, timeout, permission denied, or redaction failed",
          "redacted_fields": ["email", "password", "cookie", "refresh_token", "access_token"],
          "evidence_returned": ["last_result", "failure_count_5m", "checked_at"]
        },
        {
          "check_key": "token_validation",
          "check_type": "auth_probe",
          "evidence_source": "reader:token_validation_reader",
          "expected_result": "configured = true and minimum_length_met = true and validation_result = pass",
          "degraded_when": "validation_result = pass and failure_count_5m > 0",
          "down_when": "configured = false or validation_result = fail",
          "unknown_when": "missing reader, stale evidence, timeout, permission denied, or redaction failed",
          "redacted_fields": ["jwt", "signing_key", "cookie", "raw_exception"],
          "evidence_returned": ["configured", "minimum_length_met", "validation_result", "failure_count_5m", "checked_at"]
        },
        {
          "check_key": "module_filtered_permissions",
          "check_type": "authorization_probe",
          "evidence_source": "planned_reader:module_filtered_permission_reader",
          "expected_result": "module_filter_applied = true",
          "degraded_when": "not applicable until reader exists",
          "down_when": "not applicable until reader exists",
          "unknown_when": "planned reader has no implementation",
          "redacted_fields": ["employee_id", "tenant_user_id", "raw_permission_payload"],
          "evidence_returned": ["reader_error_code", "checked_at"]
        }
      ]
    },
    {
      "service_key": "data_service",
      "display_name": "Data Service",
      "owner_module": "Shared Platform / Database",
      "environment": "all",
      "criticality": "critical",
      "phase": "phase_1",
      "status_weight": 5,
      "health_endpoint": "reader:database_health_reader",
      "expected_dependencies": ["postgresql"],
      "freshness_sla_seconds": 120,
      "timeout_ms": 2000,
      "safe_actions": [],
      "redaction_policy": "platform_health_default",
      "checks": [
        {
          "check_key": "db_connection",
          "check_type": "db_probe",
          "evidence_source": "reader:database_connection_reader",
          "expected_result": "can_connect = true and latency_ms <= 100",
          "degraded_when": "can_connect = true and latency_ms > 100 and latency_ms <= 500",
          "down_when": "can_connect = false",
          "unknown_when": "missing reader, stale evidence, timeout, permission denied, or redaction failed",
          "redacted_fields": ["connection_string", "host_ip", "username", "password", "raw_exception"],
          "evidence_returned": ["can_connect", "latency_ms", "checked_at"]
        },
        {
          "check_key": "db_migration_state",
          "check_type": "migration_probe",
          "evidence_source": "reader:ef_migration_reader",
          "expected_result": "pending_migration_count = 0",
          "degraded_when": "pending_migration_count > 0",
          "down_when": "__EFMigrationsHistory unavailable or required tables missing",
          "unknown_when": "missing reader, stale evidence, timeout, permission denied, or redaction failed",
          "redacted_fields": ["connection_string", "raw_sql", "raw_exception"],
          "evidence_returned": ["latest_migration_id", "pending_migration_count", "required_table_sample_passed", "checked_at"]
        }
      ]
    },
    {
      "service_key": "frontend_console",
      "display_name": "Developer Platform Frontend",
      "owner_module": "Developer Platform Frontend",
      "environment": "all",
      "criticality": "medium",
      "phase": "phase_1",
      "status_weight": 2,
      "health_endpoint": "reader:frontend_health_reader",
      "expected_dependencies": ["api_gateway"],
      "freshness_sla_seconds": 300,
      "timeout_ms": 2000,
      "safe_actions": [],
      "redaction_policy": "platform_health_default",
      "checks": [
        {
          "check_key": "cookie_auth_model",
          "check_type": "frontend_probe",
          "evidence_source": "test_output:FrontendAuthCookieModeSmoke",
          "expected_result": "credentials_include = true and browser_token_storage_found = false",
          "degraded_when": "credentials_include = true and browser_token_storage_found = true",
          "down_when": "session_check_failed = true",
          "unknown_when": "missing reader, stale evidence, timeout, permission denied, or redaction failed",
          "redacted_fields": ["cookie", "jwt", "refresh_token", "access_token"],
          "evidence_returned": ["credentials_include", "browser_token_storage_found", "session_check_result", "checked_at"]
        },
        {
          "check_key": "session_refresh_check",
          "check_type": "frontend_probe",
          "evidence_source": "planned_reader:frontend_session_refresh_reader",
          "expected_result": "refresh_result = pass",
          "degraded_when": "not applicable until reader exists",
          "down_when": "not applicable until reader exists",
          "unknown_when": "planned reader has no implementation",
          "redacted_fields": ["cookie", "jwt", "refresh_token", "access_token"],
          "evidence_returned": ["reader_error_code", "checked_at"]
        }
      ]
    }
  ],
  "dependencies": [
    {
      "dependency_key": "postgresql",
      "display_name": "PostgreSQL",
      "type": "database",
      "environment": "all",
      "criticality": "critical",
      "owner_module": "Shared Platform / Database",
      "evidence_source": "reader:database_connection_reader",
      "freshness_sla_seconds": 120,
      "timeout_ms": 2000,
      "redacted_fields": ["connection_string", "host_ip", "username", "password", "raw_exception"],
      "evidence_returned": ["can_connect", "latency_ms", "pool_usage_pct", "checked_at"]
    },
    {
      "dependency_key": "jwt_signing_key",
      "display_name": "JWT Signing Key",
      "type": "secret",
      "environment": "all",
      "criticality": "critical",
      "owner_module": "Auth & Security",
      "evidence_source": "options_validator:JwtOptions",
      "freshness_sla_seconds": 300,
      "timeout_ms": 500,
      "redacted_fields": ["signing_key", "raw_env_value"],
      "evidence_returned": ["configured", "minimum_length_met", "checked_at"]
    },
    {
      "dependency_key": "api_gateway",
      "display_name": "API Gateway",
      "type": "internal_component",
      "environment": "all",
      "criticality": "critical",
      "owner_module": "Backend API",
      "evidence_source": "reader:api_route_reader",
      "freshness_sla_seconds": 120,
      "timeout_ms": 2000,
      "redacted_fields": ["cookie", "jwt", "raw_response", "raw_exception"],
      "evidence_returned": ["route_map_available", "representative_probe_passed", "checked_at"]
    }
  ]
}
```

## Fake Reader Output Fixtures

These reader outputs let status mapping be tested before real readers exist.

| Fixture | Reader Output | Expected Check Status |
|---|---|---|
| `healthy_auth_token` | `configured = true`, `minimum_length_met = true`, `validation_result = pass`, fresh `checked_at`, `redaction_applied = true` | `healthy` |
| `degraded_login_failures` | `last_result = pass`, `failure_count_5m = 6`, fresh `checked_at`, `redaction_applied = true` | `degraded` |
| `down_db_connection` | `can_connect = false`, fresh `checked_at`, `redaction_applied = true` | `down` |
| `unknown_stale_migration` | `pending_migration_count = 0`, `checked_at` older than `freshness_sla_seconds`, `redaction_applied = true` | `unknown` |
| `unknown_timeout` | no evidence, `reader_error_code = reader_timeout` | `unknown` |
| `unknown_planned_reader` | no evidence, `reader_error_code = reader_not_implemented` | `unknown` |
| `unknown_unredacted_output` | evidence contains `connection_string` or `jwt`, `redaction_applied = false` | `unknown` |
| `degraded_frontend_token_storage` | `credentials_include = true`, `browser_token_storage_found = true`, fresh `checked_at`, `redaction_applied = true` | `degraded` |

## Contract Test Cases

These tests should run against the registry fixture and fake reader outputs before endpoint integration tests exist.

| Test Key | Setup | Expected Result |
|---|---|---|
| `PH-CONTRACT-001` | Registry contains unique service keys and dependency keys | Validation passes |
| `PH-CONTRACT-002` | Duplicate `service_key` exists | Validation fails with safe configuration error |
| `PH-CONTRACT-003` | `expected_dependencies` references a missing dependency key | Validation fails with safe configuration error |
| `PH-CONTRACT-004` | Service has empty `checks` | Validation fails |
| `PH-CONTRACT-005` | Service has invalid `criticality` | Validation fails |
| `PH-CONTRACT-006` | Check has missing `expected_result`, `degraded_when`, `down_when`, or `unknown_when` | Validation fails |
| `PH-CONTRACT-007` | Planned reader exists with `planned_reader:` evidence source | Validation passes, check maps to `unknown` |
| `PH-CONTRACT-008` | Reader evidence is stale | Check maps to `unknown`, not `healthy` |
| `PH-CONTRACT-009` | Reader times out | Check maps to `unknown`; full health response still returns if safe payload can be built |
| `PH-CONTRACT-010` | Reader output is not redacted | Unsafe evidence is discarded and check maps to `unknown` |
| `PH-CONTRACT-011` | Critical service has one `down` required check | Service status maps to `down`; overall status maps to `down` |
| `PH-CONTRACT-012` | Critical service has one `unknown` required check and no `down` checks | Overall status cannot be better than `degraded` |
| `PH-CONTRACT-013` | Two equal-weight services: one `healthy`, one `unknown` | `overall_health_pct = 50`; `unknown_check_count > 0` |
| `PH-CONTRACT-014` | All enabled services are `unknown` | `overall_health_pct = 0`; `overall_status = unknown` |
| `PH-CONTRACT-015` | Services Monitor receives service keys from Platform Health registry | It uses the same `service_key`, dependency keys, criticality, and approved actions |

## Score Calculation Examples

### Mixed Critical And Medium Services

Fixture weights:

- `auth_service = 5`
- `data_service = 5`
- `frontend_console = 2`

Reader statuses:

- `auth_service = healthy`
- `data_service = degraded`
- `frontend_console = unknown`

Calculation:

```text
weighted_score = (5 * 1.0) + (5 * 0.5) + (2 * 0.0)
total_weight = 12
overall_health_pct = 62.5
overall_status = degraded
```

### Critical Down Override

Reader statuses:

- `auth_service = healthy`
- `data_service = down`
- `frontend_console = healthy`

Calculation:

```text
weighted_score = (5 * 1.0) + (5 * 0.0) + (2 * 1.0)
total_weight = 12
overall_health_pct = 58.33
overall_status = down
```

`overall_status` is `down` because a critical service is down, regardless of percentage.

## Redaction Assertions

Contract tests must reject any returned evidence containing:

- connection strings
- raw SQL
- raw JWTs
- cookies
- refresh tokens
- API keys
- signing keys
- raw environment variable values
- internal IP addresses
- stack traces
- raw exception payloads
- employee, tenant user, or customer PII

If redaction cannot produce safe summarized evidence, the check status must be `unknown`.

## Required Implementation Order

1. Registry validator against the fixture.
2. Status mapper using fake reader outputs.
3. Redaction guard using unsafe fake output.
4. Overall health calculator using weighted fixture services.
5. Endpoint integration tests after the API route exists.
6. Real reader tests one reader at a time.

Do not mark Platform Health complete from contract tests alone. Contract tests only prove the model and status logic before full implementation.
