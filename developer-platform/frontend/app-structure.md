# App Structure

## Canonical Navigation

The Developer Platform frontend is an Angular 21 application. It uses a sidebar icon rail with a secondary panel for grouped modules. This navigation is separate from the tenant-facing ONEVO app navigation.

| Rail Area | Default Route | Has Panel | Panel Items |
|---|---|---:|---|
| Dashboard | `/` | No | None |
| Platform Management | `/platform/tenants` | Yes | Tenants, Subscriptions, Platform Users, Platform Roles, Global Policies, Module Catalog, Templates, Feature Flags |
| System Operations | `/operations/platform-health` | Yes | Platform Health, Services Monitor; Device Management, Infrastructure, Background Jobs, and Agent Versions are Phase 2 |
| Security & Compliance | `/security/security-center` | Yes | Security Center, Audit Logs, Compliance Center, Data Retention |
| Analytics & Reports | `/analytics/platform` | Yes | Platform Analytics, Reports |
| Settings | `/settings/system` | Yes | System Settings, App Catalog, API Keys *(Phase 2)* |

Route visibility is controlled by platform permissions from Platform Access. Do not use tenant roles or ONEVO product module entitlements to show Developer Platform routes. The canonical permission and rendering rules are defined in `developer-platform/access-control-contract.md`.

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
|   |-- forbidden/
|   |-- dashboard/
|   |-- platform/
|   |   |-- tenants/
|   |   |-- subscriptions/
|   |   |-- platform-users/
|   |   |-- platform-roles/
|   |   |-- global-policies/
|   |   |-- module-catalog/
|   |   |-- templates/
|   |   `-- feature-flags/
|   |-- operations/
|   |   |-- platform-health/
|   |   |-- services/
|   |   |-- devices/          # Phase 2
|   |   |-- infrastructure/   # Phase 2
|   |   |-- background-jobs/   # Phase 2
|   |   `-- agent-versions/   # Phase 2
|   |-- security/
|   |   |-- security-center/
|   |   |-- audit-logs/
|   |   |-- compliance/
|   |   `-- data-retention/
|   |-- analytics/
|   |   |-- platform/
|   |   `-- reports/
|   `-- settings/
|       |-- system/
|       |-- app-catalog/
|       `-- api-keys/
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

`/login` is public. It initiates Google OAuth and exchanges the Google token for a platform-admin session.

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

- `auth.service.ts` manages Google OAuth callback handling, current account state, session expiry, and logout.
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

