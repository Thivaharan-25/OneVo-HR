# Authorization (RBAC)

**Module:** Auth & Security
**Feature:** Authorization

---

## Purpose

Role-Based Access Control with 90+ permissions across both pillars.

## Database Tables

### `roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "HR Manager", "CEO", "Employee" |
| `description` | `varchar(255)` | |
| `is_system` | `boolean` | System roles can't be deleted |
| `created_at` | `timestamptz` | |

### `permissions`

Global permission definitions — NOT tenant-scoped.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `code` | `varchar(50)` | e.g., `employees:read`, `workforce:view` |
| `description` | `varchar(255)` | |
| `module` | `varchar(50)` | Which module this permission belongs to |

### `role_permissions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK → roles |
| `permission_id` | `uuid` | FK → permissions |

### `user_roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `user_id` | `uuid` | FK → users |
| `role_id` | `uuid` | FK → roles |
| `assigned_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Assign permissions |

## Related

- [[auth|Auth Module]]
- [[authentication]]
- [[session-management]]
- [[mfa]]
- [[audit-logging]]
- [[gdpr-consent]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[shared-kernel]]
- [[logging-standards]]
- [[WEEK1-auth-security]]
