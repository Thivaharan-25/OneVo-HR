# Authorization (Hybrid Permission Control)

**Module:** Auth & Security
**Feature:** Authorization

---

## Purpose

Authorization combines tenant commercial availability, runtime feature flags, tenant roles, per-user permission overrides, and hierarchy-scoped data access.

This is not simple RBAC. Roles are convenience bundles. They never override tenant commercial boundaries.

Roles & Permissions has two separate role surfaces:

- **Security Roles**: tenant/module authority such as HR Admin, Project Admin, Payroll Admin, System Admin, or Tenant Owner. These use `roles`, `role_permissions`, and `user_roles`.
- **Team Roles**: scoped team/workspace authority such as Admin / Lead, Member, and Viewer / Reviewer. These use `team_roles`, `team_role_permissions`, and `team_member_roles`.

Tenant security roles are separate from explicit stored team roles, WorkSync workspace membership, and WorkSync project membership. Positions may define access templates, but templates only generate scoped grants after confirmation or approval; the position template itself is not an active grant.

## Access Decision Order

Every protected tenant-facing action must pass these checks in this order:

1. Tenant has an active module entitlement in `tenant_module_entitlements`.
2. If the action maps to a feature key, the tenant's current subscription/custom contract includes that key in `tenant_subscriptions.selected_feature_keys`.
3. If the feature has a runtime flag, Tenant Runtime Overrides evaluates it as enabled for this tenant.
4. The user has the required effective permission from roles and/or valid user permission overrides.
5. Employee-data access is inside the user's resolved hierarchy/access-policy scope.

If any check fails, the API returns `403 Forbidden`.

Tenant Super Admin can receive all permissions inside enabled tenant modules, but cannot access disabled, unpurchased, or commercially excluded module features.

Module Catalog defines possible modules and feature keys; it does not grant tenant access. Tenant-facing access is based on the tenant subscription snapshot and active module entitlements. Runtime flags and RBAC are evaluated only after the commercial snapshot says the tenant has the module/feature.

Tenant commercial state is split by level: module access is materialized in `tenant_module_entitlements`; feature commercial inclusion is stored in `tenant_subscriptions.selected_feature_keys`; runtime availability is controlled by `tenant_module_entitlements.runtime_override` and feature flag evaluation.

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

Security role permissions must not be used as the only check for WorkSync access. Workspace-scoped actions require active workspace membership. Project-scoped actions require active `project_members` access. When access is inherited through explicit team sync, the applicable team role permission must also pass.

Team role permission assignment must use a team-scoped permission catalog only. The backend must reject tenant security, HR admin, payroll, billing, project visibility, system settings, and security role management permissions in `team_role_permissions`.

### `user_roles`

Security role assignment with explicit scope. Scope belongs here so the same role can be assigned at different boundaries.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK to tenants |
| `user_id` | `uuid` | FK to users |
| `role_id` | `uuid` | FK to roles |
| `scope_type` | `varchar(30)` | `Organization`, `Department`, `DepartmentTree`, `Team`, `Own`, `DirectReports`, or `ReportingTree` |
| `scope_id` | `uuid` | Nullable boundary id. Required for `Department`, `DepartmentTree`, and `Team`; null for `Organization`, `Own`, `DirectReports`, and `ReportingTree` |
| `source_type` | `varchar(30)` | `Manual`, `PositionTemplate`, or `EmployeeOverride` |
| `source_position_id` | `uuid` | Nullable source position for generated grants |
| `source_position_access_template_id` | `uuid` | Nullable source position access template |
| `effective_from` | `timestamptz` | Nullable |
| `effective_to` | `timestamptz` | Nullable |
| `status` | `varchar(20)` | `Active`, `Scheduled`, `PendingApproval`, `Expired`, or `Revoked` |
| `assigned_at` | `timestamptz` | |
| `assigned_by` | `uuid` | FK to users |
| `approved_by` | `uuid` | Nullable FK to users; approver for generated or requested grants |
| `expires_at` | `timestamptz` | Deprecated compatibility alias; use `effective_to` for time-bound role grants |

**Uniqueness rule:** Role assignments must use `NULLS NOT DISTINCT` or an equivalent normalized/partial unique index for `(tenant_id, user_id, role_id, scope_type, scope_id)` so null `scope_id` values cannot create duplicate grants.

### `user_permission_overrides`

Per-user grants or revocations. Overrides cannot grant access outside the tenant's active modules and included feature keys.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK to tenants |
| `user_id` | `uuid` | FK to users |
| `permission_id` | `uuid` | FK to permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `scope_type` | `varchar(30)` | Optional scope for this individual override |
| `scope_id` | `uuid` | Nullable boundary id for scoped overrides |
| `reason` | `varchar(255)` | Audit reason |
| `valid_from` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable |

### `feature_access_grants`

Optional role/employee feature visibility grants inside the tenant's already-commercially-included boundary.

This table is not a billing table and not the source of truth for what the tenant bought. It cannot enable a module or feature that is missing from `tenant_module_entitlements` or `tenant_subscriptions.selected_feature_keys`.

Example: if a tenant has the `work_management` module but `work_management.ai_sprint_planning` is not present in `tenant_subscriptions.selected_feature_keys`, a Tenant Admin cannot grant that feature through `feature_access_grants`. The tenant subscription must first be updated through an audited commercial path.

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

Employee-data queries are scoped by the effective active `user_roles.scope_type` and `scope_id` for the role assignment. Position access templates only generate `user_roles` rows or access approval requests; templates are not active grants by themselves. The frontend never sends employee ID lists.

| Policy | Meaning |
|:-------|:--------|
| `Own` | Current employee only |
| `DirectReports` | Direct reports only |
| `ReportingTree` | Direct and indirect reports |
| `Department` | Employees in the assigned department boundary |
| `DepartmentTree` | Employees in the assigned department and child departments |
| `Team` | Employees in the assigned team boundary |
| `Organization` | All active employees in tenant |

Scope validation rules:

- `Department` and `DepartmentTree` scope require `scope_id` pointing to an active department in the same tenant.
- `Team` scope requires `scope_id` pointing to an active team in the same tenant.
- `Organization`, `Own`, `DirectReports`, and `ReportingTree` require `scope_id = null`.
- A permission check must verify both that the user has the permission and that the target record is inside the resolved scope.

### Position-Generated Access Approval

When onboarding, transfer, promotion, or position assignment generates access from a position template:

1. If the template does not require approval, create or schedule the `user_roles` grant.
2. If the template requires approval and the actor has `roles:manage` or `access:approve`, show the grant diff and create/schedule the grant after confirmation.
3. If the template requires approval and the actor lacks access authority, create an `access_grant_requests` record and keep the grant inactive.
4. Route approval by target position department: scoped access approvers covering that department, then tenant-wide access approvers, then Tenant Admin. If multiple match, notify all and first approval wins.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create custom role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Set role permissions within active module/feature boundary |
| GET | `/api/v1/team-roles` | `roles:manage` | List standard team roles and their scoped permission sets |
| PUT | `/api/v1/team-roles/{id}/permissions` | `roles:manage` | Set team-role permissions from team-scoped catalog only |
| GET | `/api/v1/permissions/team-catalog` | `roles:manage` | List permissions eligible for team roles |
| POST | `/api/v1/users/{id}/roles` | `roles:manage` | Assign role to employee |
| GET | `/api/v1/users/{id}/permissions` | `roles:manage` | Get effective permissions |
| POST | `/api/v1/users/{id}/permission-overrides` | `roles:manage` | Grant/revoke individual permission inside active module/feature boundary |
| GET | `/api/v1/access-grant-requests` | `access:approve` OR `roles:manage` | List pending generated access grants in the approver's scope |
| POST | `/api/v1/access-grant-requests/{id}/decision` | `access:approve` OR `roles:manage` | Approve, reject, narrow, or expire a generated position-template access grant |
| GET | `/api/v1/feature-access` | `roles:manage` | List role/employee feature visibility grants |
| POST | `/api/v1/feature-access` | `roles:manage` | Grant role/employee visibility inside commercial boundary |
| DELETE | `/api/v1/feature-access/{id}` | `roles:manage` | Revoke role/employee visibility grant |

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]]
- [[developer-platform/modules/feature-flag-manager/overview|Tenant Runtime Overrides]]
