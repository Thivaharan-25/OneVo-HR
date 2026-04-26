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

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[code-standards/logging-standards|Logging Standards]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
