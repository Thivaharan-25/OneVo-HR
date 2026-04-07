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

- [[infrastructure|Infrastructure Module]]
- [[file-management]]
- [[reference-data]]
- [[tenant-management]]
- [[authentication]]
- [[authorization]]
- [[audit-logging]]
- [[multi-tenancy]]
- [[migration-patterns]]
- [[WEEK1-infrastructure-setup]]
