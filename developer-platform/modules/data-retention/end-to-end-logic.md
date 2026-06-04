# Data Retention End-to-End Logic

## Update Retention Policy

1. Operator opens Security & Compliance -> Data Retention.
2. Frontend calls `GET /admin/v1/retention-policies`.
3. Operator creates or edits a policy.
4. Backend verifies `platform.retention.manage`.
5. Backend validates category, duration, action, and tenant/global scope.
6. Backend saves policy and audits the change.

## Sweep Execution

1. Scheduled retention sweep runs in the backend scheduler. Phase 1 surfaces only read-only sweep health/status through Platform Health; standalone Background Jobs operations are Phase 2.
2. Sweep reads active policies.
3. Sweep skips records covered by legal holds.
4. Sweep deletes or anonymizes records according to policy.
5. Sweep writes run summary and failures.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/retention-policies` | List policies | `platform.retention.read` |
| POST | `/admin/v1/retention-policies` | Create policy | `platform.retention.manage` |
| PATCH | `/admin/v1/retention-policies/{id}` | Update policy | `platform.retention.manage` |
| GET | `/admin/v1/retention-policies/{id}/impact` | Preview impact | `platform.retention.read` |

## Rules

- Shortening retention on existing data requires impact preview and audit reason.
- Legal hold protection cannot be bypassed by policy update.
