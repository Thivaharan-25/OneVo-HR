# Audit Console

## Purpose

The Audit Console provides a read-only, cross-tenant view of every action recorded in the ONEVO audit log — by tenant users, platform admins, and automated system processes. It is the primary tool for compliance investigation, security review, and support escalation where a full history of what happened is required.

Access to the Audit Console is itself audit-logged — the operator's identity and query parameters are recorded every time the screen is used.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `audit_log` | Read-only — no writes, no deletions ever permitted through this module |

## Capabilities

### Cross-Tenant Log Viewer
- Query audit events across all tenants in a single interface
- 9 concurrent filters: date range (required), tenant, actor type, actor name, action category, action code, resource type, result (success/failed), IP address, and free-text search
- Table shows: timestamp, actor (name + type badge), action (human-readable + machine code), resource, tenant, IP, result
- Expand any row inline for full detail: previous state, new state, request ID, user agent, session ID, metadata — sensitive fields redacted to `[REDACTED]`

### Tenant-Scoped View
- Access tenant-specific audit trail directly from Tenant Detail → Activity Log tab
- Same filters, same columns, pre-filtered to the selected tenant

### Export
- Export filtered results as CSV or JSON
- CSV: flattened columns including all metadata fields
- JSON: includes `previous_state` and `new_state` snapshots (with sensitive fields redacted)
- Synchronous download for < 10,000 rows; async email delivery for 10,000–100,000 rows; blocked above 100,000 rows
- Every export is audit-logged with the operator, format, filters applied, and row count

## Action Code Catalog

Every audit entry has a machine-readable `action_code` in the format `{entity}.{action}`, e.g.:
- `tenant.activated`, `tenant.suspended`, `tenant.impersonated`
- `subscription.assigned`, `invoice.paid`, `payment.failed`
- `feature_flag.default_changed`, `module.runtime_disabled`
- `role_template.applied`, `tenant.role.permissions_updated`
- `alert.resolved`, `session.revoked`, `audit_log.queried`

See [[developer-platform/modules/audit-console/end-to-end-logic|Audit Console End-to-End Logic]] for the full action code catalog.

## Retention Rules

| Data Category | Hot Storage (queryable) | After Expiry |
|---|---|---|
| Standard events | 2 years | Cold storage (available on engineering request) |
| Security-category events | 5 years | Cold storage |
| Billing events | 7 years | Cold storage |

Audit records are append-only within their retention period. They are never modified or deleted via any API or admin interface.

## Navigation

| Route | Permission |
|---|---|
| `/security/audit-logs` | `platform.audit.read` |
| Export | `platform.audit.export` |

## Key Rules

- Date range (`from` and `to`) is required — unbounded queries are blocked
- Maximum query window: 90 days in a single request (use export for wider ranges)
- This module is strictly read-only — no write, update, or delete operations exist
- Audit records are never deleted within their retention period (legal obligation)
- Every query is itself audit-logged

## Related

- [[developer-platform/modules/audit-console/end-to-end-logic|Audit Console End-to-End Logic]]
- [[developer-platform/modules/security-center/overview|Security Center]] — alert management
- [[developer-platform/modules/compliance-center/overview|Compliance Center]] — legal holds and compliance exports
