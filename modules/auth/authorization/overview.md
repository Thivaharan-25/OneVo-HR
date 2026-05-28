# Authorization (Hybrid Permission Control)

**Module:** Auth & Security
**Feature:** Authorization

---

## Purpose

Authorization combines tenant commercial availability, runtime feature flags, tenant roles, per-user permission overrides, and hierarchy-scoped data access.

This is not simple RBAC. Roles are convenience bundles. They never override tenant commercial boundaries.

## Access Decision Order

Every protected tenant-facing action must pass these checks in this order:

1. Tenant has an active module entitlement in `tenant_module_entitlements`.
2. If the action maps to a feature key, the tenant's current subscription/custom contract includes that key in `tenant_subscriptions.selected_feature_keys`.
3. If the feature has a runtime flag, Feature Flag Manager evaluates it as enabled for this tenant.
4. The user has the required effective permission from roles and/or valid user permission overrides.
5. Employee-data access is inside the user's resolved hierarchy/access-policy scope.

If any check fails, the API returns `403 Forbidden`.

Tenant Super Admin can receive all permissions inside enabled tenant modules, but cannot access disabled, unpurchased, or commercially excluded module features.

## Core Tables

### `roles`

Custom tenant roles created by Tenant Super Admin or delegated permission admins.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK to tenants |
| `name` | `varchar(100)` | Custom name; never hardcoded |
| `description` | `varchar(255)` | |
| `is_system` | `boolean` | Seeded roles only; role names are not authorization rules |
| `created_at` | `timestamptz` | |

### `permissions`

Global permission definitions. Permissions belong to exactly one module through Module Catalog ownership.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `code` | `varchar(120)` | e.g. `employees:read`, `leave:approve` |
| `description` | `varchar(255)` | |
| `module` | `varchar(80)` | Owning module key |
| `feature_key` | `varchar(120)` | Nullable; set only when a permission is tied to a commercial feature key |

### `role_permissions`

Permission assignments for a role. These are filtered by module entitlement and feature availability at resolution time.

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK to roles |
| `permission_id` | `uuid` | FK to permissions |
| `access_policy` | `varchar(50)` | `self`, `direct_reports`, `reporting_tree`, `department`, `department_tree`, `org_unit_tree`, or `organization` |

### `user_permission_overrides`

Per-user grants or revocations. Overrides cannot grant access outside the tenant's active modules and included feature keys.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK to tenants |
| `user_id` | `uuid` | FK to users |
| `permission_id` | `uuid` | FK to permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `access_policy` | `varchar(50)` | Optional policy override |
| `reason` | `varchar(255)` | Audit reason |
| `valid_from` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable |

### `feature_access_grants`

Optional role/employee feature visibility grants inside the tenant's already-commercially-included boundary.

This table is not a billing table and not the source of truth for what the tenant bought. It cannot enable a module or feature that is missing from `tenant_module_entitlements` or `tenant_subscriptions.selected_feature_keys`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK to tenants |
| `grantee_type` | `varchar(10)` | `role` or `employee` |
| `grantee_id` | `uuid` | Role ID or user ID |
| `module` | `varchar(80)` | Module key |
| `feature_key` | `varchar(120)` | Nullable feature key |
| `is_enabled` | `boolean` | User-level allow/deny inside the commercial boundary |
| `granted_by` | `uuid` | FK to users; admin or delegated permission manager who made the change |
| `valid_from` | `timestamptz` | Nullable; defaults to active immediately |
| `expires_at` | `timestamptz` | Nullable; used for temporary role/employee feature visibility |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module, feature_key)` | | |

`grantee_id` is resolved based on `grantee_type`: when `grantee_type = role`, it points to `roles.id`; when `grantee_type = employee`, it points to `users.id`. Employee-data hierarchy scope is still resolved separately through the logged-in user's `employees.user_id` mapping and `employee_hierarchy`.

## Effective Permission Resolution

```text
EffectivePermissions(userId, tenantId):
  1. Resolve tenant active modules from tenant_module_entitlements.
  2. Resolve tenant included feature keys from current tenant_subscriptions.selected_feature_keys.
  3. Resolve enabled runtime feature flags for included feature keys.
  4. Start with universal permissions.
  5. Add permissions from active user roles.
  6. Add valid user_permission_overrides where grant_type = grant.
  7. Remove valid user_permission_overrides where grant_type = revoke.
  8. Keep only permissions whose module is active for the tenant.
  9. For permissions with feature_key, keep only if the feature is commercially included and runtime-enabled.
 10. Apply feature_access_grants only as an additional role/employee visibility filter inside that boundary.
 11. Return final permission codes.
```

## Access Policy Scoping

Employee-data queries are scoped by the effective `access_policy` for the permission. The frontend never sends employee ID lists.

| Policy | Meaning |
|:-------|:--------|
| `self` | Current employee only |
| `direct_reports` | Direct reports only |
| `reporting_tree` | Full reporting subtree |
| `department` | Current employee's department |
| `department_tree` | Department subtree |
| `org_unit_tree` | Org unit subtree |
| `organization` | All active employees in tenant |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create custom role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Set role permissions within active module/feature boundary |
| POST | `/api/v1/users/{id}/roles` | `roles:manage` | Assign role to employee |
| GET | `/api/v1/users/{id}/permissions` | `roles:manage` | Get effective permissions |
| POST | `/api/v1/users/{id}/permission-overrides` | `roles:manage` | Grant/revoke individual permission inside active module/feature boundary |
| GET | `/api/v1/feature-access` | `roles:manage` | List role/employee feature visibility grants |
| POST | `/api/v1/feature-access` | `roles:manage` | Grant role/employee visibility inside commercial boundary |
| DELETE | `/api/v1/feature-access/{id}` | `roles:manage` | Revoke role/employee visibility grant |

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]]
- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]]
