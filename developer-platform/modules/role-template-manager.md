# Role Template Manager

## Purpose

The Role Template Manager lets ONEVO operators define starter role configurations during tenant provisioning. It is part of the internal Developer Platform at `console.onevo.io`; customers do not access this tool directly.

Role templates are not runtime permissions by themselves. A template is a reusable operator-managed blueprint. When applied to a tenant, it materializes into normal tenant-scoped `roles` and `role_permissions` records owned by the Auth module.

Operators do not need to create a new template for every tenant. They use the reusable global template library for common patterns, and create tenant-specific roles directly during provisioning when a role is unique to one customer. Both paths must use the same module-filtered permission catalog.

## Core Rule

Role templates must always be filtered by the tenant's enabled modules.

If a tenant has only Employee Management and Leave enabled, the Developer Platform role-template UI must show only:

- universal safe permissions
- permissions from enabled employee/core HR modules
- permissions from enabled leave modules

It must not show permissions for Payroll, Workforce Intelligence, WorkSync, Agent Gateway, Identity Verification, or any module the tenant has not bought, trialed, or been granted.

The same rule applies later inside the tenant app: tenant owners can create and edit roles, but only from permissions exposed by their enabled modules.

## Data Ownership

| Data | Owner | Notes |
|---|---|---|
| `permissions` | Auth | Global permission catalog, each permission has a module key. |
| `roles` | Auth | Tenant-scoped materialized roles. |
| `role_permissions` | Auth | Tenant role permission mapping. |
| `role_templates` | Auth or DevPlatform facade | Operator-managed template definitions. Must store module coverage and permission codes/IDs. |
| tenant module entitlements | SharedPlatform / InfrastructureModule | Determines which permissions can be shown or assigned. |

Admin controllers must call module interfaces. They must not query tables directly.

Roles do not require job levels. A basic role is a tenant-scoped permission container and can be created without departments, job families, reporting lines, or hierarchy records. Job levels and hierarchy become relevant only for scoped permissions, workflow approver resolution, escalation rules, or organisation-aware access policies.

## Required Capabilities

### Global Template Library

Operators can create templates such as:

- Tenant Owner
- HR Admin
- Leave Manager
- Employee
- Workforce Supervisor
- WorkSync Project Manager

Each template stores:

- name
- description
- intended modules
- permission set
- whether it is a ONEVO default template
- version
- active/inactive status

Templates may be system/default templates or operator-created reusable templates. System templates can be cloned but should not be edited in place except by `super_admin`. Operator-created templates can be edited while preserving version history.

### Tenant Filtered Permission Catalog

For a selected tenant, the backend exposes a permission catalog filtered by active modules:

```http
GET /admin/v1/tenants/{tenantId}/permissions/catalog
```

The response includes only assignable permissions for that tenant, grouped by module. Disabled/unpurchased module permissions are excluded.

### Apply Template to Tenant

Operators can apply a template to a tenant:

```http
POST /admin/v1/tenants/{tenantId}/role-templates/{templateId}/apply
```

The backend validates every permission in the template against the tenant's enabled modules before creating the tenant role. Permissions outside the tenant entitlement boundary are rejected or skipped with an explicit validation result; they must never be silently granted.

Applying a template creates or updates normal tenant-scoped roles. Re-applying the same template must be idempotent or require an explicit duplicate-name override. The system must not silently create duplicate roles with confusing names.

### Tenant-Specific Role Creation During Provisioning

During provisioning, operators can create roles that belong only to the selected tenant:

```http
GET /admin/v1/tenants/{tenantId}/roles
POST /admin/v1/tenants/{tenantId}/roles
PUT /admin/v1/tenants/{tenantId}/roles/{roleId}/permissions
```

Use this when a sales or onboarding agreement requires a unique role that should not be saved as a global template. These roles are still normal tenant-scoped Auth roles, and every permission must be validated against the same tenant permission catalog returned by:

```http
GET /admin/v1/tenants/{tenantId}/permissions/catalog
```

The first tenant owner/admin invite must assign one of the materialized tenant roles. The selected role must include the minimum owner/admin permission set required by product.

### Tenant Owner Role Management

After activation, tenant owners use tenant-facing role APIs:

```http
GET /api/v1/roles
POST /api/v1/roles
PUT /api/v1/roles/{id}
PUT /api/v1/roles/{id}/permissions
```

Those APIs use the same module-filtered permission catalog. Tenant owners cannot assign permissions for modules ONEVO has not enabled for their tenant.

## Provisioning Flow Integration

The provisioning wizard uses Role Template Manager after module selection and before owner invite:

1. Tenant details are saved.
2. Plan/commercial model is selected.
3. Modules are selected.
4. Permission catalog is resolved from selected modules.
5. Operator applies reusable templates, creates a new reusable template, or creates tenant-specific roles.
6. First tenant owner invite is sent and assigned to a valid tenant owner/admin role.
7. Tenant activates only after the role/permission step is complete.

## Validation Rules

- A template cannot contain unknown permission codes.
- A template cannot assign permissions from modules not enabled for the selected tenant.
- Applying the same template twice must be idempotent or require an explicit duplicate-name override.
- System templates can be cloned but not edited in place unless the operator has `super_admin`.
- Tenant-specific roles created during provisioning follow the same permission validation as template-applied roles.
- First owner/admin invite cannot be sent unless at least one valid tenant owner/admin role exists.
- Any template apply/update writes an audit log with tenant, operator, role name, template version, added permissions, and removed permissions.
- Permission version counters are incremented for affected users when a materialized role changes.

## Related

- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]]
- [[developer-platform/modules/tenant-console/overview|Tenant Console]]
- [[modules/auth/overview|Auth & Security]]
- [[Userflow/Auth-Access/role-creation|Role Creation]]
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- [[database/schemas/auth|Auth Schema]]
- [[database/schemas/shared-platform|Shared Platform Schema]]
