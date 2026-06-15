# App Structure

## Canonical Navigation

The Developer Platform frontend is an Angular 21 application with a flat Super Admin sidebar. This navigation is separate from the tenant-facing ONEVO app navigation.

| Sidebar Item | Route |
|---|---|
| Dashboard | `/` |
| Tenant Management | `/platform/tenants` |
| Subscription Plans | `/platform/subscription-plans` |
| Module Catalog | `/platform/module-catalog` |
| Demo Profiles | `/platform/demo-profiles` |
| Requests Center | `/platform/requests` |
| Customer Support | `/platform/support` |
| Platform Users | `/platform/platform-users` |
| Platform Roles | `/platform/platform-roles` |
| Template Management | `/platform/templates` |
| Security Center | `/security/security-center` |
| Audit Console | `/security/audit-console` |
| Compliance Center | `/security/compliance` |
| Reports / Analytics | `/reports-analytics` |
| System Config | `/settings/system` |
| Operations | `/operations` |
| App Catalog | `/settings/app-catalog` |

Permission categories are shown inside the Platform Roles permission matrix only; they are not a separate sidebar item.

Route visibility is controlled by platform permissions from Platform Roles. Do not use tenant roles or ONEVO product module entitlements to show Developer Platform routes. The canonical permission and rendering rules are defined in `developer-platform/access-control-contract.md`.

## Canonical Angular Route Tree

```text
src/app/
|-- app.config.ts
|-- app.routes.ts
|-- app.component.ts
|-- core/
|   |-- auth/
|   |   |-- auth.guard.ts
|   |   |-- permission.guard.ts
|   |   |-- auth.service.ts
|   |   `-- permission.service.ts
|   |-- http/
|   |   |-- admin-api.interceptor.ts
|   |   `-- admin-api.service.ts
|   `-- models/
|       `-- platform-auth.models.ts
|-- layout/
|   |-- console-shell.component.ts
|   |-- sidebar-rail.component.ts
|   |-- sidebar-panel.component.ts
|   `-- topbar.component.ts
|-- pages/
|   |-- login/
|   |-- mfa/
|   |-- forbidden/
|   |-- dashboard/
|   |-- platform/
|   |   |-- tenants/
|   |   |-- subscription-plans/
|   |   |-- demo-profiles/
|   |   |-- requests/
|   |   |-- support/
|   |   |-- platform-users/
|   |   |-- platform-roles/
|   |   |-- templates/
|   |   |-- module-catalog/
|   |   `-- tenant-runtime-overrides/  # Tenant Detail tab, not a sidebar route
|   |-- operations/
|   |   |-- index/
|   |   |-- platform-health/
|   |   `-- background-jobs/   # Phase 2
|   |-- security/
|   |   |-- security-center/
|   |   |-- audit-console/
|   |   `-- compliance/
|   |-- reports-analytics/
|   `-- settings/
|       |-- system/
|       `-- app-catalog/
`-- shared/
    |-- components/
    |   |-- status-badge/
    |   |-- confirm-action-dialog/
    |   `-- empty-state/
    `-- directives/
        `-- has-permission.directive.ts
```

## Route Guard Structure

### Public Routes

`/login` is public. It accepts email/password and creates only a pending MFA challenge when primary login succeeds. `/mfa` verifies the second factor and only then creates the platform-admin session. Optional Google OAuth account setup for invited managers must also finish with MFA before a session is issued.

### Authenticated Console Routes

All console routes are children of the `ConsoleShellComponent` layout and use Angular route guards:

- `authGuard` verifies that a platform-admin session exists.
- `permissionGuard` verifies the route's required platform permission.
- Missing route permission renders `/forbidden`.
- Sidebar items for missing route permissions are hidden.

Example route metadata:

```ts
{
  path: 'platform/tenants',
  loadComponent: () => import('./pages/platform/tenants/tenant-list.component')
    .then(m => m.TenantListComponent),
  canActivate: [authGuard, permissionGuard],
  data: { requiredPermission: 'platform.tenants.read' }
}
```

## Core Services

- `auth.service.ts` manages email/password login, pending MFA challenge state, optional OAuth setup callbacks, current account state, session expiry, and logout.
- `permission.service.ts` exposes `hasPermission`, `hasAnyPermission`, `hasAllPermissions`, `canViewRoute`, and action filtering helpers.
- `admin-api.service.ts` is the typed API client for `/admin/v1/*`.
- `admin-api.interceptor.ts` attaches credentials, handles 401 logout, and maps 403 responses to the forbidden page or inline permission errors where appropriate.

## Component Rules

Components must not check role names. They must use `PermissionService` or a shared `hasPermission` directive.

- Read permission present and manage permission absent: render the page read-only.
- Missing action permission: hide the action.
- Disabled controls are for invalid state only.
- Dangerous actions require a confirmation dialog and audit reason when the module requires one.

## Phase 2 Note

The `/settings/api-keys`, `/operations/devices`, `/operations/infrastructure`, `/operations/background-jobs`, and `/operations/agent-versions` routes are Phase 2. Keep them hidden in Phase 1 unless the Phase 2 permission contract is implemented.

