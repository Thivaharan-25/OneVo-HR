# Exception Rules

**Module:** Exception Engine  
**Feature:** Exception Rules

---

## Purpose

Configurable anomaly detection rules with JSON-based thresholds. Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`.

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

- [[exception-engine|Exception Engine Module]]
- [[exception-engine/alert-generation/overview|Alert Generation]]
- [[exception-engine/evaluation-engine/overview|Evaluation Engine]]
- [[exception-engine/escalation-chains/overview|Escalation Chains]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-exception-engine]]
