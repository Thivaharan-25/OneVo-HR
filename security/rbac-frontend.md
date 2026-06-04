# Frontend RBAC Patterns

## Permission Source

Permissions come from backend session endpoints such as `/api/v1/auth/session` or `/api/v1/auth/refresh`. The customer web frontend does not decode JWTs.

```json
{
  "employeeId": "uuid",
  "displayTitle": "Engineering Manager",
  "modules": ["core-hr", "leave", "workforceIntelligence"],
  "capabilities": [
    { "permission": "employees:read",  "policy": "reporting_tree", "source": "role" },
    { "permission": "leave:approve",   "policy": "direct_reports", "source": "role" },
    { "permission": "workforce:view",  "policy": null,             "source": "role" },
    { "permission": "monitoring:alerts:read", "policy": null,      "source": "role" }
  ],
  "navigation": [
    "my-dashboard", "my-leave", "my-attendance",
    "team-dashboard", "team-leave", "team-leave-approvals", "team-attendance"
  ]
}
```

This comes from `GET /api/v1/me/app-context` on session start. `capabilities` replaces the flat permission array; each entry carries the permission code and its resolved assignment scope. `navigation` is computed by the backend and rendered by Angular exactly as returned. `AuthService` caches capabilities and navigation signals and refreshes them when the session is refreshed.

## `*hasPermission` Structural Directive

The primary way to gate UI by permission in Angular templates:

```html
<!-- Single permission -->
<app-workforce-dashboard *hasPermission="'workforce:view'" />

<!-- Any of multiple permissions (array) -->
<app-monitoring-settings *hasPermission="['monitoring:configure', 'monitoring:view-settings']" />

<!-- With fallback template -->
<div *hasPermission="'payroll:read'; else forbidden">
  <app-payroll-page />
</div>
<ng-template #forbidden><app-forbidden-inline /></ng-template>

<!-- Render nothing when denied (default) -->
<button *hasPermission="'exceptions:manage'" mat-button (click)="configureRules()">
  Configure Rules
</button>
```

## Signal-Based Checks in Components

For conditional logic within component code:

```typescript
export class WorkforceSectionComponent {
  private auth = inject(AuthService);

  canViewWorkforce = this.auth.hasPermission('workforce:view');
  canConfigureMonitoring = this.auth.hasPermission('monitoring:configure');
}
```

```html
@if (canViewWorkforce()) {
  <app-workforce-dashboard />
}

@if (canConfigureMonitoring()) {
  <app-monitoring-settings />
}
```

For conditional data fetching, drive the `resource()` request with a permission signal:

```typescript
workforceResource = resource({
  request: () => this.canViewWorkforce() ? {} : null,
  loader: ({ request }) => request
    ? firstValueFrom(this.workforceService.getLiveStatus())
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
  { label: 'Leave',      icon: 'calendar_month', path: '/leave',      permission: 'leave:read' },
  { label: 'Workforce',  icon: 'dashboard',      path: '/workforce',  permission: 'workforce:view', feature: 'workforceIntelligence' },
  { label: 'Exceptions', icon: 'warning',        path: '/exceptions', permission: 'exceptions:view', feature: 'workforceIntelligence' },
  { label: 'Org',        icon: 'account_tree',   path: '/org',        permission: 'org:read' },
  { label: 'Admin',      icon: 'shield',         path: '/admin',      permission: 'users:manage' },
  { label: 'Settings',   icon: 'settings',       path: '/settings',   permission: 'settings:read' },
];
```

Items where the user lacks permission are **hidden entirely** (not greyed out).

## Access-Policy-Driven Data Scoping

The frontend does not enforce data scoping. The backend resolves the assignment scope for each permission from `user_roles` and `user_permission_overrides`, then filters queries accordingly. The frontend adapts the UI based on what `capabilities` the backend returned in `app-context`:

| Effective capability | What the frontend shows |
|:---------------------|:------------------------|
| `employees:read` + `self` | Own profile only |
| `employees:read` + `direct_reports` / `reporting_tree` | Team/subordinate views |
| `employees:read` + `organization` | All-employee views |
| `leave:approve` + any policy | Approvals inbox |
| `analytics:view` (no policy) | Analytics section |

```typescript
// Derive UI flags from capabilities, not role names
const empRead = capabilities().find(c => c.permission === 'employees:read');
showTeamFilter = empRead?.policy === 'direct_reports' || empRead?.policy === 'reporting_tree';
showOrgFilter  = empRead?.policy === 'organization';
```

## Monitoring Config Gating

Workforce Intelligence UI is gated by both RBAC permission AND monitoring configuration:

```typescript
// workforce-section.component.ts
export class WorkforceSectionComponent {
  private auth = inject(AuthService);
  private configService = inject(MonitoringConfigService);

  hasPermission = this.auth.hasPermission('workforce:view');

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
  <app-workforce-dashboard />
} @else if (showDisabledBanner()) {
  <app-monitoring-disabled-banner />
}
```

## Permission Reference

### HR Management
| Permission | Grants |
|:-----------|:-------|
| `employees:read` | View employees — scope determined by access policy on role (`self` / `direct_reports` / `reporting_tree` / `organization`) |
| `employees:write` | Create, edit employees |
| `leave:read` | View leave records — scope determined by access policy |
| `leave:approve` | Approve/reject leave — scope determined by access policy |
| `leave:manage` | Configure leave policies |
| `payroll:read` | View payroll runs |
| `payroll:run` | Execute payroll calculation |
| `payroll:approve` | Approve payroll for payment |

### Workforce Intelligence
| Permission | Grants |
|:-----------|:-------|
| `workforce:view` | Live dashboard, employee activity |
| `workforce:manage` | Modify presence records |
| `monitoring:alerts:read` | View exception/monitoring alerts |
| `monitoring:alerts:resolve` | Acknowledge/dismiss alerts |
| `exceptions:manage` | Configure rules, escalation chains |
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
// ❌ Wrong — never check role name
if (user.role === 'HR Manager') { ... }

// ✅ Correct — check the permission signal
if (auth.hasPermission('employees:write')()) { ... }
```

## Related

- [[frontend/cross-cutting/authorization|Authorization]] — full permission system
- [[security/auth-flow|Auth Flow]] — session and token architecture
- [[frontend/architecture/app-structure|App Structure]] — three-app monorepo
