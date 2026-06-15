# Developer Platform Access Control Contract

## Purpose

This file is the canonical permission and rendering contract for the OneVo Developer Platform. Backend controllers, Angular route guards, sidebar filtering, component action rendering, tests, and module docs must follow this contract.

Developer Platform access is permission-based. Role names are never authorization rules.

## Core Model

- Platform users are stored in `platform_users`.
- Platform roles are stored in `platform_roles`.
- Permissions are stored in the platform permission catalog.
- Role permission grants are stored in `platform_role_permissions`.
- Platform user role assignments are stored in `platform_user_roles`.
- Platform user sessions are stored in `platform_user_sessions`.
- Platform auth events are stored in `platform_auth_events`.
- A platform user may have multiple active roles.
- Effective permissions are the union of permissions from all active roles assigned to the account.
- Custom roles are unlimited.
- Seeded system roles are default presets. They are editable by accounts with `platform.roles.manage`, but they cannot be deleted.
- Authorization checks use permission codes only. Do not check role names in backend or frontend code.

## Seeded System Roles

| Seed Role | Initial Permission Scope |
|---|---|
| Platform Super Admin | All platform permissions |
| Tenant Operations Manager | Tenant lifecycle, provisioning, activation, tenant role materialization, and tenant read/manage actions; no impersonation unless explicitly granted |
| Billing Manager | Subscription plans, invoices, payment gateways, billing reports, and commercial read/manage actions |
| Security Auditor | Security, audit, compliance, and retention read-only permissions |
| Module Catalog Manager | Product module catalog, integration catalog, and template management |
| Operations Engineer | Platform health, services monitor, tenant runtime overrides, and system configuration review |
| Read-Only Viewer | Dashboard and broad read-only visibility without mutation permissions |

Seeded role names are convenience presets. If a seeded role is edited, its current permission set is the source of truth.

## Recoverable Admin Guard

The backend must reject any role, role-permission, user-role, user-status, or session-revocation change that would leave the platform with zero active recoverable admins.

A recoverable admin is an active platform user whose effective permissions include both:

- `platform.accounts.manage`
- `platform.roles.manage`

Additional guard rules:

- `Platform Super Admin` cannot be deleted.
- If system roles are editable, edits to `Platform Super Admin` must not remove either `platform.accounts.manage` or `platform.roles.manage` unless another active account still remains recoverable after the change.
- Deactivating a platform user, removing a role from a user, archiving a role, or replacing role permissions must run the same recoverable-admin check.
- The check must evaluate effective permissions after the proposed change, not before it.

If the guard blocks a request, return:

```json
{
  "code": "recoverable_admin_required",
  "message": "At least one active platform user must retain platform user and role management permissions."
}
```

## Route Visibility

| UI Area | Route | Required Permission | Without Permission |
|---|---|---|---|
| Dashboard | `/` | `platform.dashboard.view` or any platform permission | Direct URL shows 403 if account has no platform permissions |
| Tenant Management | `/platform/tenants` | `platform.tenants.read` | Hide nav item; direct URL shows 403 |
| Subscription Plans | `/platform/subscription-plans` | `platform.subscriptions.read` | Hide nav item; direct URL shows 403 |
| Module Catalog | `/platform/module-catalog` | `platform.module_catalog.read` | Hide nav item; direct URL shows 403 |
| Demo Profiles | `/platform/demo-profiles` | `platform.demo_profiles.read` | Hide nav item; direct URL shows 403 |
| Requests Center | `/platform/requests` | `platform.requests.read` | Hide nav item; direct URL shows 403 |
| Customer Support | `/platform/support` | `platform.support.read` | Hide nav item; direct URL shows 403 |
| Platform Users | `/platform/platform-users` | `platform.accounts.read` | Hide nav item; direct URL shows 403 |
| Platform Roles | `/platform/platform-roles` | `platform.roles.read` | Hide nav item; direct URL shows 403 |
| Template Management | `/platform/templates` | `platform.templates.read` | Hide nav item; direct URL shows 403 |
| Security Center | `/security/security-center` | `platform.security.read` | Hide nav item; direct URL shows 403 |
| Audit Console | `/security/audit-console` | `platform.audit.read` | Hide nav item; direct URL shows 403 |
| Compliance Center | `/security/compliance` | `platform.compliance.read` | Hide nav item; direct URL shows 403 |
| Reports / Analytics | `/reports-analytics` | `platform.reports.read` | Hide nav item; direct URL shows 403 |
| System Config | `/settings/system` | `platform.system_config.read` | Hide nav item; direct URL shows 403 |
| Operations | `/operations` | `platform.operations.read` | Hide nav item; direct URL shows 403 |
| Operations service sections/actions | `/operations` service rows/actions | Read: `platform.operations.read`; actions: `platform.operations.manage` | Hide action controls when manage permission is missing |
| App Catalog | `/settings/app-catalog` | `platform.app_catalog.read` | Hide nav item; direct URL shows 403 |

## Angular Rendering Rules

- Sidebar items are hidden when the user lacks the route permission.
- Direct navigation to a protected route without permission renders the Angular 403 page.
- Pages with read permission but without manage permission render in read-only mode.
- Actions requiring missing permissions are hidden.
- Disabled controls are used for invalid state only, not missing permission.
- Dangerous actions require permission, confirmation, and audit reason where the module specifies one.
- Frontend route filtering is a user experience layer only. Backend authorization remains the security boundary.

## Angular Permission Helpers

The frontend should expose one permission service used by route guards, sidebar filtering, tabs, and action menus:

```ts
hasPermission(code: string): boolean
hasAnyPermission(codes: string[]): boolean
hasAllPermissions(codes: string[]): boolean
canViewRoute(route: string): boolean
filterVisibleActions<T extends { requiredPermission?: string }>(actions: T[]): T[]
```

Do not duplicate permission logic inside individual components.

## Standard 403 Response

Backend permission failures should use:

```json
{
  "code": "permission_denied",
  "message": "You do not have permission to perform this action.",
  "required_permission": "platform.tenants.manage"
}
```

Tenant JWTs presented to `/admin/v1/*` return 401. Platform-admin JWTs missing a required permission return 403.

## Permission Categories

Platform Roles must expose these categories in the permission matrix. These are not sidebar items.

- Tenant Management permissions
- Tenant Runtime Override permissions are part of Tenant Management permissions
- Subscription permissions
- Module Catalog permissions
- Demo Profile permissions
- Requests permissions
- Support permissions
- Platform Account permissions
- Platform Role permissions
- Template Management permissions
- Operations permissions
- Security permissions
- Audit permissions
- Compliance permissions
- Report / Analytics permissions
- System Config permissions
- Runtime Flag Definition permissions are part of System Config permissions
- App Catalog permissions

Minimum canonical permission keys:

```text
platform.tenants.read
platform.tenants.manage
platform.subscriptions.read
platform.subscriptions.manage
platform.module_catalog.read
platform.module_catalog.manage
platform.demo_profiles.read
platform.demo_profiles.manage
platform.requests.read
platform.requests.manage
platform.support.read
platform.support.manage
platform.accounts.read
platform.accounts.manage
platform.roles.read
platform.roles.manage
platform.templates.read
platform.templates.manage
platform.runtime_flags.read
platform.runtime_flags.manage
platform.tenants.feature_overrides.read
platform.tenants.feature_overrides.manage
platform.security.read
platform.security.manage
platform.audit.read
platform.compliance.read
platform.reports.read
platform.system_config.read
platform.system_config.manage
platform.operations.read
platform.operations.manage
platform.app_catalog.read
platform.app_catalog.manage
```

