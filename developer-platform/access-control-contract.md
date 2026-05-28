# Developer Platform Access Control Contract

## Purpose

This file is the canonical permission and rendering contract for the OneVo Developer Platform. Backend controllers, Angular route guards, sidebar filtering, component action rendering, tests, and module docs must follow this contract.

Developer Platform access is permission-based. Role names are never authorization rules.

## Core Model

- Platform accounts are stored in `dev_platform_accounts`.
- Platform roles are stored in `dev_platform_roles`.
- Permissions are stored in `dev_platform_permissions`.
- Role permission grants are stored in `dev_platform_role_permissions`.
- Account role assignments are stored in `dev_platform_account_roles`.
- A platform account may have multiple active roles.
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
| Module Catalog Manager | Product module catalog, integration catalog, role templates, and configuration templates |
| Operations Engineer | Platform health, services monitor, devices, infrastructure, background jobs, and agent versions |
| Read-Only Viewer | Dashboard and broad read-only visibility without mutation permissions |

Seeded role names are convenience presets. If a seeded role is edited, its current permission set is the source of truth.

## Recoverable Admin Guard

The backend must reject any role, role-permission, account-role, account-status, or session-revocation change that would leave the platform with zero active recoverable admins.

A recoverable admin is an active platform account whose effective permissions include both:

- `platform.accounts.manage`
- `platform.roles.manage`

Additional guard rules:

- `Platform Super Admin` cannot be deleted.
- If system roles are editable, edits to `Platform Super Admin` must not remove either `platform.accounts.manage` or `platform.roles.manage` unless another active account still remains recoverable after the change.
- Deactivating an account, removing a role from an account, archiving a role, or replacing role permissions must run the same recoverable-admin check.
- The check must evaluate effective permissions after the proposed change, not before it.

If the guard blocks a request, return:

```json
{
  "code": "recoverable_admin_required",
  "message": "At least one active platform account must retain platform account and role management permissions."
}
```

## Route Visibility

| UI Area | Route | Required Permission | Without Permission |
|---|---|---|---|
| Dashboard | `/` | `platform.dashboard.view` or any platform permission | Direct URL shows 403 if account has no platform permissions |
| Tenants | `/platform/tenants` | `platform.tenants.read` | Hide nav item; direct URL shows 403 |
| Subscriptions | `/platform/subscriptions` | `platform.subscriptions.read` | Hide nav item; direct URL shows 403 |
| Platform Users | `/platform/platform-users` | `platform.accounts.read` | Hide nav item; direct URL shows 403 |
| Platform Roles | `/platform/platform-roles` | `platform.roles.read` | Hide nav item; direct URL shows 403 |
| Global Policies | `/platform/global-policies` | `platform.policies.read` | Hide nav item; direct URL shows 403 |
| Module Catalog | `/platform/module-catalog` | `platform.module_catalog.read` | Hide nav item; direct URL shows 403 |
| Role Templates | `/platform/role-templates` | `platform.role_templates.read` | Hide nav item; direct URL shows 403 |
| Feature Flags | `/platform/feature-flags` | `platform.feature_flags.read` | Hide nav item; direct URL shows 403 |
| Platform Health | `/operations/platform-health` | `platform.health.read` | Hide nav item; direct URL shows 403 |
| Services Monitor | `/operations/services` | `platform.health.read` | Hide nav item; direct URL shows 403 |
| Device Management | `/operations/devices` | `platform.health.read` | Hide nav item; direct URL shows 403 |
| Infrastructure | `/operations/infrastructure` | `platform.health.read` | Hide nav item; direct URL shows 403 |
| Background Jobs | `/operations/background-jobs` | `platform.health.read` | Hide nav item; direct URL shows 403 |
| Agent Versions | `/operations/agent-versions` | `platform.agent_versions.read` | Hide nav item; direct URL shows 403 |
| Security Center | `/security/security-center` | `platform.security.read` | Hide nav item; direct URL shows 403 |
| Audit Logs | `/security/audit-logs` | `platform.audit.read` | Hide nav item; direct URL shows 403 |
| Compliance Center | `/security/compliance` | `platform.compliance.read` | Hide nav item; direct URL shows 403 |
| Data Retention | `/security/data-retention` | `platform.compliance.read` | Hide nav item; direct URL shows 403 |
| Platform Analytics | `/analytics/platform` | `platform.reports.read` | Hide nav item; direct URL shows 403 |
| Reports | `/analytics/reports` | `platform.reports.read` | Hide nav item; direct URL shows 403 |
| System Settings | `/settings/system` | `platform.system_config.read` | Hide nav item; direct URL shows 403 |
| App Catalog | `/settings/app-catalog` | `platform.app_catalog.read` | Hide nav item; direct URL shows 403 |
| API Keys | `/settings/api-keys` | Phase 2 permission contract | Hidden in Phase 1 |

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
