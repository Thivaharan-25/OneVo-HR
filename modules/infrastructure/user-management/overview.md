# User Management

**Module:** Infrastructure  
**Feature:** User Management

---

## Purpose

Authentication identity management. Users are linked 1:1 to employees (HR identity) via `user_id` on the employees table.

## Database Tables

### `users`
Key columns: `tenant_id`, `email` (UNIQUE per tenant), `password_hash` (bcrypt), `is_active`, `email_verified`, `last_login_at`.

## Key Business Rules

1. Users ≠ Employees. `users` = login identity, `employees` = HR identity in Core HR.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/users` | `users:read` | List users |
| POST | `/api/v1/users` | `users:manage` | Create user |
| PUT | `/api/v1/users/{id}` | `users:manage` | Update user |

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]]
