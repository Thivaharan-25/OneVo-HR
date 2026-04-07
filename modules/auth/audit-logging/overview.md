# Audit Logging

**Module:** Auth & Security
**Feature:** Audit Logging

---

## Purpose

Append-only audit trail for all significant actions. Partitioned by month via `pg_partman`. Never deleted (compliance requirement).

## Database Tables

### `audit_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users (nullable for system actions) |
| `action` | `varchar(100)` | e.g., `employee.created`, `leave.approved` |
| `resource_type` | `varchar(50)` | e.g., `Employee`, `LeaveRequest` |
| `resource_id` | `uuid` | |
| `old_values_json` | `jsonb` | Previous state |
| `new_values_json` | `jsonb` | New state |
| `ip_address` | `varchar(45)` | |
| `correlation_id` | `uuid` | Request correlation |
| `created_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/audit-logs` | `settings:admin` | Query audit logs |

## Related

- [[auth|Auth Module]]
- [[authentication]]
- [[authorization]]
- [[session-management]]
- [[mfa]]
- [[gdpr-consent]]
- [[auth-architecture]]
- [[compliance]]
- [[data-classification]]
- [[logging-standards]]
- [[migration-patterns]]
- [[WEEK1-auth-security]]
