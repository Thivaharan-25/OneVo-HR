# Authorization (Hybrid Permission Control)

**Module:** Auth & Security
**Feature:** Authorization

---

## Purpose

Hybrid permission control combining **custom roles** (as convenience templates) with **per-employee permission overrides** and **hierarchy-scoped access**. This is NOT role-based access control — roles are just a way to bulk-assign permissions. The real access model is:

1. **Super Admin grants access** to any feature/module for any role OR individual employee
2. **Effective permissions** = role permissions + individual overrides (overrides win)
3. **Hierarchy scoping** — a user can only see/manage employees directly below them in the org hierarchy

## How It Works

```
Super Admin
  ├── Creates custom roles (templates with permission sets)
  ├── Assigns roles to employees
  ├── Grants feature/module access to ANY role or ANY individual employee
  └── Grants per-employee permission overrides (add or revoke specific permissions)

When Employee X accesses a feature:
  1. Resolve effective permissions = role permissions ∪ individual grants − individual revocations
  2. Check if the required permission exists in effective permissions
  3. Scope data to hierarchy — only show records for employees below X in the reporting chain
```

## Database Tables

### `roles`

Custom roles created by Super Admin. These are templates, not the access control mechanism.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Custom name — Super Admin defines these, never hardcoded |
| `description` | `varchar(255)` | |
| `is_system` | `boolean` | Only `Super Admin` is system; rest are custom |
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

Permissions assigned to a role (template). When a role is assigned to a user, they get these permissions as a baseline.

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK → roles |
| `permission_id` | `uuid` | FK → permissions |
| PK: `(role_id, permission_id)` | | |

### `user_roles`

Which role an employee is assigned to. An employee can have one or more roles.

| Column | Type | Notes |
|:-------|:-----|:------|
| `user_id` | `uuid` | FK → users |
| `role_id` | `uuid` | FK → roles |
| `assigned_at` | `timestamptz` | |
| `assigned_by` | `uuid` | FK → users (who granted this) |
| PK: `(user_id, role_id)` | | |

### `user_permission_overrides`

**Per-employee permission overrides.** Super Admin can grant or revoke individual permissions for a specific employee, independent of their role. Overrides always win over role permissions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `permission_id` | `uuid` | FK → permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `reason` | `varchar(255)` | Why this override exists |
| `granted_by` | `uuid` | FK → users (Super Admin who set this) |
| `created_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, user_id, permission_id)` | | One override per permission per user |

### `feature_access_grants`

**Module/feature-level access grants.** Super Admin can enable or disable entire feature modules for a role or an individual employee. If a feature is not granted, none of its permissions are effective even if the user has them.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `grantee_type` | `varchar(10)` | `role` or `employee` |
| `grantee_id` | `uuid` | FK → roles.id OR users.id depending on grantee_type |
| `module` | `varchar(50)` | Module code: `leave`, `payroll`, `performance`, etc. |
| `is_enabled` | `boolean` | true = access granted |
| `granted_by` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module)` | | One grant per module per grantee |

## Effective Permission Resolution

```
EffectivePermissions(userId) =
  1. Get all role_permissions from user's assigned roles
  2. Add all user_permission_overrides where grant_type = 'grant'
  3. Remove all user_permission_overrides where grant_type = 'revoke'
  4. Filter out permissions whose module is NOT in feature_access_grants for this user
     (check both employee-level grants and role-level grants)
  5. Return final permission set
```

## Hierarchy Scoping

Every data query is scoped to the employee's position in the org hierarchy:

- An employee with `leave:approve` can only approve leave for **employees reporting to them** (direct or indirect via the reporting chain in `employees.reports_to_id`)
- A department head can see all employees in their department and sub-departments
- **Super Admin** bypasses hierarchy scoping entirely
- The hierarchy is resolved from `employees.reports_to_id` — a recursive CTE walks the tree

### Implementation — `HierarchyFilter`

`IHierarchyScopeService.GetFilterAsync()` (Auth module public interface) returns a `HierarchyFilter` value object. Pass it to repository methods — **never materialize a list of IDs**.

| User type | Filter returned | SQL mechanism |
|:----------|:----------------|:--------------|
| Super Admin | `HierarchyFilter.All` | No additional filter — skip CTE entirely |
| Manager (has `employees:read-team`) | `HierarchyFilter.SubordinatesOf(managerId)` | Recursive CTE in one query |
| Employee | `HierarchyFilter.OwnOnly(employeeId)` | `WHERE id = @employeeId` |

The CTE includes the manager themselves + all employees below in the reporting chain — one DB round-trip, no `WHERE IN (...)` list regardless of org size.

Supporting index: `idx_employees_reports_to_id ON employees(reports_to_id, tenant_id) WHERE is_deleted = false`

See [[backend/shared-kernel|Shared Kernel]] for `HierarchyFilter` definition and `BaseRepository.ApplyHierarchyFilter()`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create custom role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| DELETE | `/api/v1/roles/{id}` | `roles:manage` | Delete custom role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Set role permissions |
| POST | `/api/v1/users/{id}/roles` | `roles:manage` | Assign role to employee |
| DELETE | `/api/v1/users/{id}/roles/{roleId}` | `roles:manage` | Remove role from employee |
| GET | `/api/v1/users/{id}/permissions` | `roles:manage` | Get employee's effective permissions |
| POST | `/api/v1/users/{id}/permission-overrides` | `roles:manage` | Grant/revoke individual permission for employee |
| DELETE | `/api/v1/users/{id}/permission-overrides/{permId}` | `roles:manage` | Remove override |
| GET | `/api/v1/feature-access` | `roles:manage` | List all feature access grants |
| POST | `/api/v1/feature-access` | `roles:manage` | Grant feature access to role or employee |
| DELETE | `/api/v1/feature-access/{id}` | `roles:manage` | Revoke feature access |

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[modules/org-structure/job-hierarchy/end-to-end-logic|Job Hierarchy]] — provides the reporting chain for hierarchy scoping
