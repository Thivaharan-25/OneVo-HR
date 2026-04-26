# Exception Rules

**Module:** Exception Engine  
**Feature:** Exception Rules

---

## Purpose

Configurable anomaly detection rules with JSON-based thresholds. Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`, `non_allowed_app`, `presence_without_activity`, `heartbeat_gap`.

> **`non_allowed_app`** — fires when an employee accumulates time in an app where `application_usage.is_allowed = false` beyond the `violation_threshold_minutes` in `threshold_json`. Apps with `is_allowed = null` (pending review) are never evaluated. See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] for the full allowlist resolution flow.

## Database Tables

### `exception_rules`
Key columns: `rule_name`, `rule_type`, `threshold_json`, `severity` (`info`, `warning`, `critical`), `applies_to` (`all`, `department`, `team`, `employee`), `applies_to_id`.

Threshold JSON must be validated against known schema before evaluation. Invalid JSON = skip rule + log warning.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/rules` | `exceptions:manage` | List rules |
| POST | `/api/v1/exceptions/rules` | `exceptions:manage` | Create rule |
| PUT | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Update rule |
| DELETE | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Deactivate rule |

## Related

- [[modules/exception-engine/overview|Exception Engine Module]]
- [[frontend/architecture/overview|Alert Generation]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[frontend/architecture/overview|Escalation Chains]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
