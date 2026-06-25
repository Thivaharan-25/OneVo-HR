# Authorization (Hybrid Permission Control in Frontend)

## Permission Model

Permissions flow from the backend session as **effective permissions** - already resolved from the tenant's active modules, included feature keys, runtime feature flags, user's roles, individual overrides, and backend authorization policies. The frontend uses them for **UI gating only** - the API enforces authorization server-side. Frontend authorization is a UX concern: don't show things the user can't access.

The `AuthService` in `@onevo/shared` exposes signals for all permission checks. Components never decode JWT claims directly.

### Permission Format

```
{resource}:{action}
{resource}:{action}:{scope}
```

Examples:
```
employees:read            - view employee list (filtered by backend employee visibility)
employees:write           - create or edit employees
time_off:approve             - approve Time Off requests
payroll:read              - view payroll data
monitoring:view            - view monitoring intelligence
monitoring:alerts:read    - view Phase 1 monitoring alerts
monitoring:alerts:resolve - resolve Phase 1 monitoring alerts
monitoring:configure      - change monitoring settings
settings:read             - view tenant settings
```

Full Exception Engine permissions such as `exceptions:manage` are Phase 2 and must not drive Phase 1 navigation or route guards.

## Gating Levels

### Level 1: Route Guard (Module/Feature + Permission)

Functional guards in `app.routes.ts` combine active module, included/runtime-enabled feature key, and permission checks:

```typescript
// Route with permission guard
{
  path: 'monitoring',
  canActivate: [authGuard, permissionGuard('monitoring:view')],
  loadComponent: () => import('./features/monitoring/live-dashboard.component')
    .then(m => m.LiveDashboardComponent),
}

// Route with feature + permission guard
{
  path: 'work/projects',
  canActivate: [authGuard, featureGuard('work_management.projects'), permissionGuard('projects:read')],
  loadComponent: () => import('./features/work/projects/project-list.component')
    .then(m => m.ProjectListComponent),
}
```

### Level 2: Nav Rail Items

Sections and items hidden when the user lacks the module or permission:

```typescript
// shell/nav-rail.component.ts
export class NavRailComponent {
  private auth = inject(AuthService);

  navItems = computed(() => NAV_CONFIG
    .filter(item => {
      if (item.feature && !this.auth.hasFeature(item.feature)()) return false;
      if (item.permission && !this.auth.hasPermission(item.permission)()) return false;
      return true;
    })
  );
}
```

### Level 3: Page Sections

Within a page, gate tabs or sections using the `*hasPermission` structural directive:

```html
<!-- employee-detail.component.html -->
<mat-tab-group>
  <mat-tab label="Overview">...</mat-tab>
  <mat-tab label="Employment">...</mat-tab>
  <ng-container *hasPermission="'payroll:read'">
    <mat-tab label="Compensation">
      <app-compensation-section [employeeId]="employeeId()" />
    </mat-tab>
  </ng-container>
</mat-tab-group>
```

Or with new control flow and a permission signal:

```html
@if (auth.hasPermission('payroll:read')()) {
  <mat-tab label="Compensation">
    <app-compensation-section />
  </mat-tab>
}
```

### Level 4: Component Actions (Buttons, Links)

```html
<!-- Only show Approve button if user has time_off:approve -->
<button *hasPermission="'time_off:approve'"
        mat-raised-button color="primary"
        (click)="approve()">
  Approve
</button>
```

### Level 5: Field-Level

Sensitive fields masked or hidden:

```html
<!-- payroll:read gates salary display -->
@if (auth.hasPermission('payroll:read')()) {
  <span class="font-mono">{{ employee.salary | currency }}</span>
} @else {
  <span class="text-muted">Restricted</span>
}
```

## `HasPermissionDirective` (from `@onevo/shared`)

Structural directive for template-level gating. Supports single permission, multiple permissions (any-of), and `fallback` template:

```typescript
// shared/src/lib/auth/has-permission.directive.ts
@Directive({
  selector: '[hasPermission]',
  standalone: true,
})
export class HasPermissionDirective {
  private auth = inject(AuthService);
  private vcr = inject(ViewContainerRef);
  private tmpl = inject(TemplateRef);

  @Input() set hasPermission(permission: string | string[]) {
    const permissions = Array.isArray(permission) ? permission : [permission];
    const granted = computed(() => permissions.some(p => this.auth.hasPermission(p)()));

    effect(() => {
      this.vcr.clear();
      if (granted()) this.vcr.createEmbeddedView(this.tmpl);
    });
  }
}
```

Usage:

```html
<!-- Single permission -->
<button *hasPermission="'employees:write'" mat-button>Edit</button>

<!-- Any-of (array) -->
<div *hasPermission="['employees:write', 'employees:delete']">
  Admin actions
</div>
```

## `AuthService` Permission API

```typescript
// shared/src/lib/auth/auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private _permissions = signal<string[]>([]);
  private _activeModules = signal<string[]>([]);
  private _activeFeatures = signal<string[]>([]);
  private _capabilities = signal<Record<string, boolean>>({});

  // Permission check - returns a computed signal (reactive)
  hasPermission(code: string): Signal<boolean> {
    return computed(() => this._permissions().includes(code));
  }

  hasAnyPermission(...codes: string[]): Signal<boolean> {
    return computed(() => codes.some(c => this._permissions().includes(c)));
  }

  hasAllPermissions(...codes: string[]): Signal<boolean> {
    return computed(() => codes.every(c => this._permissions().includes(c)));
  }

  // Module check
  hasModule(moduleKey: string): Signal<boolean> {
    return computed(() => this._activeModules().includes(moduleKey));
  }

  // Commercially included and runtime-enabled feature check
  hasFeature(featureKey: string): Signal<boolean> {
    return computed(() => this._activeFeatures().includes(featureKey));
  }

  hasCapability(key: string): Signal<boolean> {
    return computed(() => this._capabilities()[key] === true);
  }
}
```

## Data Access (Management Coverage)

The **API handles employee visibility server-side through management coverage** - it only returns data the user can see. The frontend adapts the UI based on returned capabilities but never filters data client-side:

```typescript
// Adjust filter UI based on returned capabilities
export class EmployeeListComponent {
  private auth = inject(AuthService);

  // Show broad filters only when the API/session capabilities allow them.
  showAllDepartments = this.auth.hasCapability('employees.filter.allDepartments');
}
```

## No Hardcoded Role Names


```typescript
// [wrong] Wrong - never check role name
if (auth.user()?.role === 'HR Manager') { ... }

// [ok] Correct - check the permission signal
if (auth.hasPermission('employees:write')()) { ... }

// [ok] Correct - check module access
if (auth.hasModule('time_off')()) { ... }
if (auth.hasFeature('time_off.requests')()) { ... }
```

## Related

- [[frontend/cross-cutting/authentication|Authentication]] - auth flow, session management
- [[frontend/architecture/routing|Routing]] - functional route guards
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] - nav rail gating
- [[frontend/design-system/patterns/table-patterns|Table Patterns]] - column-level gating
