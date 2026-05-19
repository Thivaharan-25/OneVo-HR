# Audit Console Userflow

## Actor

Auditor or security operator.

## Journey

1. Operator opens Security & Compliance -> Audit Logs.
2. Console loads audit filters.
3. Operator filters by tenant, user, action, resource, and date range.
4. Backend audits the audit query itself.
5. Operator exports results if permitted.

## APIs Used

- `GET /admin/v1/audit-logs`
- `POST /admin/v1/audit-logs/export`

## Rules

Audit Console is read-only. It cannot edit or delete audit records.
