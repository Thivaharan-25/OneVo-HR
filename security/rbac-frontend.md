# Frontend RBAC Patterns

## Permission Source

Permissions come from backend session endpoints such as `/api/v1/auth/session` or `/api/v1/auth/refresh`. The customer web frontend does not decode JWTs.

```json
{
  "employeeId": "uuid",
  "displayTitle": "Engineering Manager",
  "modules": ["core-hr", "time_off", "monitoring"],
  "capabilities": [
    { "permission": "employees:read",  "coverage": "management_coverage", "source": "role" },
    { "permission": "time_off:approve",   "coverage": "management_coverage", "source": "role" },
    { "permission": "monitoring:view",  "policy": null,             "source": "role" },
    { "permission": "monitoring:alerts:read", "policy": null,      "source": "role" }
  ],
  "navigation": [
    "my-dashboard", "my-time_off", "my-attendance",
  ]
}
```

This comes from `GET /api/v1/me/app-context` on session start. `capabilities` replaces the flat permission array; each entry carries the permission code and its resolved assignment scope. `navigation` is computed by the backend and rendered by Angular exactly as returned. `AuthService` caches capabilities and navigation signals and refreshes them when the session is refreshed.

## `*hasPermission` Structural Directive

The primary way to gate UI by permission in Angular templates:

```html
<!-- Single permission -->
<app-monitoring-dashboard *hasPermission="'monitoring:view'" />

<!-- Any of multiple permissions (array) -->
<app-monitoring-settings *hasPermission="['monitoring:configure', 'monitoring:view-settings']" />

<!-- With fallback template -->
<div *hasPermission="'payroll:read'; else forbidden">
  <app-payroll-page />
</div>
<ng-template #forbidden><app-forbidden-inline /></ng-template>

<!-- Render nothing when denied (default) -->
<button *hasPermission="'monitoring:alerts:resolve'" mat-button (click)="resolveAlert()">
  Configure Rules
</button>
```

## Signal-Based Checks in Components

For conditional logic within component code:

```typescript
export class WorkforceSectionComponent {
  private auth = inject(AuthService);

  canViewWorkforce = this.auth.hasPermission('monitoring:view');
  canConfigureMonitoring = this.auth.hasPermission('monitoring:configure');
}
```

```html
@if (canViewWorkforce()) {
  <app-monitoring-dashboard />
}

@if (canConfigureMonitoring()) {
  <app-monitoring-settings />
}
```

For conditional data fetching, drive the `resource()` request with a permission signal:

```typescript
monitoringResource = resource({
  request: () => this.canViewWorkforce() ? {} : null,
  loader: ({ request }) => request
    ? firstValueFrom(this.monitoringService.getLiveStatus())
    : Promise.resolve(null),
});
```

## Nav Rail Gating

Nav rail items are filtered by `AuthService` signals:

```typescript
// shell/nav-rail.component.ts
export class NavRailComponent {
  private auth = inject(AuthService);

  navItems = computed(() => NAV_CONFIG.filter(item => {
    if (item.feature && !this.auth.hasFeature(item.feature)()) return false;
    if (item.permission && !this.auth.hasPermission(item.permission)()) return false;
    return true;
  }));
}
```

Nav configuration:

```typescript
export const NAV_CONFIG: NavItem[] = [
  { label: 'Home',       icon: 'home',          path: '/home' },
  { label: 'People',     icon: 'group',          path: '/employees',  permission: 'employees:read' },
  { label: 'Time Off',      icon: 'calendar_month', path: '/time-off',      permission: 'time_off:read' },
  { label: 'Monitoring',  icon: 'dashboard',      path: '/monitoring',  permission: 'monitoring:view', feature: 'monitoring' },
  { label: 'Monitoring Alerts', icon: 'warning', path: '/monitoring/alerts', permission: 'monitoring:alerts:read', feature: 'monitoring' },
  { label: 'Org',        icon: 'account_tree',   path: '/org',        permission: 'org:read' },
  { label: 'Admin',      icon: 'shield',         path: '/admin',      permission: 'users:manage' },
  { label: 'Settings',   icon: 'settings',       path: '/settings',   permission: 'settings:read' },
];
```

Items where the user lacks permission are **hidden entirely** (not greyed out).

## Management-Coverage-Driven Data Access

The frontend does not enforce employee-data filtering. The backend resolves employee visibility from Org Structure management coverage and filters queries accordingly. The frontend adapts the UI based on what `capabilities` the backend returned in `app-context`:

| Effective capability | What the frontend shows |
|:---------------------|:------------------------|
| `employees:read` + management coverage | Employee views for covered positions/departments/company |
| `employees:read` without management coverage | Own profile only where self-service applies |
| `time_off:approve` + management coverage | Approvals inbox |
| `analytics:view` (no policy) | Analytics section |

```typescript
// Derive UI flags from capabilities, not role names
const empRead = capabilities().find(c => c.permission === 'employees:read');
showManagedEmployeeFilters = empRead?.coverage === 'management_coverage';
showCompanyWideFilter = empRead?.coverage === 'management_coverage' && empRead?.coverageLevel === 'company';
```

## Monitoring Config Gating

Monitoring UI is gated by both RBAC permission AND monitoring configuration:

```typescript
// monitoring-section.component.ts
export class WorkforceSectionComponent {
  private auth = inject(AuthService);
  private configService = inject(MonitoringConfigService);

  hasPermission = this.auth.hasPermission('monitoring:view');

  configResource = resource({
    request: () => this.hasPermission() ? {} : null,
    loader: () => firstValueFrom(this.configService.getMonitoringConfig()),
  });

  showDashboard = computed(() =>
    this.hasPermission() && this.configResource.value()?.activityMonitoring === true
  );

  showDisabledBanner = computed(() =>
    this.hasPermission() && this.configResource.value()?.activityMonitoring === false
  );
}
```

```html
@if (showDashboard()) {
  <app-monitoring-dashboard />
} @else if (showDisabledBanner()) {
  <app-monitoring-disabled-banner />
}
```

## Permission Reference

### HR Management
| Permission | Grants |
|:-----------|:-------|
| `employees:read` | View employees covered by management coverage; own profile remains self-service where supported |
| `employees:write` | Create, edit employees |
| `time_off:read` | View Time Off records covered by management coverage |
| `time_off:approve` | Approve/reject Time Off assigned through management coverage |
| `time_off:manage` | Configure Time Off policies |
| `payroll:read` | View payroll runs |
| `payroll:run` | Execute payroll calculation |
| `payroll:approve` | Approve payroll for payment |

### Monitoring
| Permission | Grants |
|:-----------|:-------|
| `monitoring:view` | Live dashboard, employee activity |
| `monitoring:manage` | Modify presence records |
| `monitoring:alerts:read` | View exception/monitoring alerts |
| `monitoring:alerts:resolve` | Acknowledge/dismiss alerts |
| `monitoring:alerts:read` | View Phase 1 monitoring alerts |
| `monitoring:alerts:resolve` | Resolve Phase 1 monitoring alerts |
| `exceptions:manage` | Phase 2: configure Exception Engine rules and escalation chains |
| `monitoring:configure` | Edit monitoring feature toggles |
| `monitoring:view-settings` | View monitoring settings (read-only) |
| `analytics:view` | View reports and analytics |
| `analytics:export` | Export reports |
| `verification:view` | View verification logs |
| `verification:configure` | Configure verification policies |
| `agent:manage` | Manage registered agents |
| `agent:view-health` | View agent health status |

## No Hardcoded Role Names

```typescript
// [wrong] Wrong - never check role name
if (user.role === 'HR Manager') { ... }

// [ok] Correct - check the permission signal
if (auth.hasPermission('employees:write')()) { ... }
```

## Related

- [[frontend/cross-cutting/authorization|Authorization]] - full permission system
- [[security/auth-flow|Auth Flow]] - session and token architecture
- [[frontend/architecture/app-structure|App Structure]] - customer-app + dev-console monorepo
