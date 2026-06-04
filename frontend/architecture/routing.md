# Routing Architecture

> This app uses **Angular Router** with typed routes defined in `app.routes.ts`. There is no file-based routing, no middleware.ts, no parallel routes, and no intercepting routes. All route guards are functional (`CanActivateFn`).

## Route Groups

| Group | Shell Component | Auth Required |
|:------|:----------------|:--------------|
| Auth | `AuthLayoutComponent` — centered card, no nav | No |
| App | App-specific shell — nav rail + topbar + `<router-outlet>` | Yes |

All three apps (`setup-control-app`, `operations-lifecycle-app`, and `dev-console`) follow the same routing pattern. Guards and permission checks are shared from `@onevo/shared`; Developer Platform routes use platform-admin auth and `/admin/v1/*`.

## Functional Guards

```typescript
// projects/shared/src/lib/auth/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;

  return router.createUrlTree(['/login'], {
    queryParams: { redirect: state.url },
  });
};
```

```typescript
// projects/shared/src/lib/auth/permission.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const permissionGuard = (permission: string): CanActivateFn =>
  () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (auth.hasPermission(permission)()) return true;
    return router.createUrlTree(['/403']);
  };
```

## Route Config Pattern (`app.routes.ts`)

All routes defined in a single file per app. Heavy routes use `loadComponent` for lazy loading.

### Operations / Lifecycle App

```typescript
// projects/operations-lifecycle-app/src/app/app.routes.ts
import { Routes } from '@angular/router';
import { authGuard, permissionGuard } from '@onevo/shared';

export const routes: Routes = [
  // Auth — public
  {
    path: '',
    loadComponent: () =>
      import('./features/auth/auth-layout.component').then(m => m.AuthLayoutComponent),
    children: [
      { path: 'login',           loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent) },
      { path: 'forgot-password', loadComponent: () => import('./features/auth/forgot-password/forgot-password.component').then(m => m.ForgotPasswordComponent) },
      { path: 'reset-password',  loadComponent: () => import('./features/auth/reset-password/reset-password.component').then(m => m.ResetPasswordComponent) },
      { path: 'mfa',             loadComponent: () => import('./features/auth/mfa/mfa.component').then(m => m.MfaComponent) },
    ],
  },

  // Authenticated — operations shell
  {
    path: '',
    loadComponent: () =>
      import('./shell/operations-shell.component').then(m => m.OperationsShellComponent),
    canActivate: [authGuard],
    children: [
      { path: '',       redirectTo: 'home', pathMatch: 'full' },
      { path: 'home',   loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent) },
      {
        path: 'leave',
        canActivate: [permissionGuard('leave:create')],
        loadComponent: () => import('./features/leave/leave-overview.component').then(m => m.LeaveOverviewComponent),
      },
      {
        path: 'attendance',
        canActivate: [permissionGuard('attendance:read-own')],
        loadChildren: () => import('./features/attendance/attendance.routes').then(m => m.attendanceRoutes),
      },
      { path: 'profile',       loadComponent: () => import('./features/profile/my-profile.component').then(m => m.MyProfileComponent) },
      { path: 'calendar',      loadComponent: () => import('./features/calendar/my-calendar.component').then(m => m.MyCalendarComponent) },
      { path: 'my-work',       loadComponent: () => import('./features/my-work/my-work.component').then(m => m.MyWorkComponent) },
      { path: 'notifications', loadComponent: () => import('./features/notifications/inbox.component').then(m => m.InboxComponent) },
      { path: 'chat',          loadComponent: () => import('./features/chat/chat.component').then(m => m.ChatComponent) },
    ],
  },

  { path: '403', loadComponent: () => import('./features/errors/forbidden.component').then(m => m.ForbiddenComponent) },
  { path: '**',  loadComponent: () => import('./features/errors/not-found.component').then(m => m.NotFoundComponent) },
];
```

### Setup / Control App (key routes)

```typescript
// projects/setup-control-app/src/app/app.routes.ts (excerpt)
export const routes: Routes = [
  // Auth — same pattern as operations-lifecycle-app
  { path: '', loadComponent: () => import('./features/auth/auth-layout.component') /* ... */ },

  // Authenticated — setup shell
  {
    path: '',
    loadComponent: () => import('./shell/setup-control-shell.component').then(m => m.SetupControlShellComponent),
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'setup', pathMatch: 'full' },
      { path: 'setup/legal-entities', canActivate: [permissionGuard('org:manage')], loadChildren: () => import('./features/legal-entities/legal-entities.routes').then(m => m.legalEntityRoutes) },
      { path: 'setup/departments', canActivate: [permissionGuard('org:manage')], loadChildren: () => import('./features/departments/departments.routes').then(m => m.departmentRoutes) },
      { path: 'setup/positions', canActivate: [permissionGuard('org:manage')], loadChildren: () => import('./features/positions/positions.routes').then(m => m.positionRoutes) },
      { path: 'setup/roles', canActivate: [permissionGuard('roles:manage')], loadChildren: () => import('./features/roles/roles.routes').then(m => m.roleRoutes) },
      { path: 'setup/import', canActivate: [permissionGuard('data-import:write')], loadChildren: () => import('./features/import/import.routes').then(m => m.importRoutes) },
      { path: 'setup/add-ons', canActivate: [permissionGuard('billing:request')], loadChildren: () => import('./features/add-ons/add-ons.routes').then(m => m.addOnRoutes) },
    ],
  },

  { path: '403', loadComponent: () => import('./features/errors/forbidden.component').then(m => m.ForbiddenComponent) },
  { path: '**',  loadComponent: () => import('./features/errors/not-found.component').then(m => m.NotFoundComponent) },
];
```

## Permission Gating

### Layer 1: Route Guard (functional)

Applied in `app.routes.ts` via `canActivate: [permissionGuard('resource:action')]`. Redirects to `/403`.

### Layer 2: `*hasPermission` Structural Directive (template-level)

Fine-grained UI hiding within pages — does NOT replace route guards:

```html
<!-- Only show "Approve" button if user has leave:approve -->
<button *hasPermission="'leave:approve'" mat-button (click)="approve()">
  Approve
</button>

<!-- Render different content based on permission -->
<ng-container *hasPermission="'payroll:read'; else restricted">
  <app-salary-display [amount]="employee.salary" />
</ng-container>
<ng-template #restricted>
  <app-restricted-field label="Salary" />
</ng-template>
```

### Layer 3: Feature / Tenant Module Gates

WorkSync routes only render when the tenant has the module enabled:

```typescript
// In app.routes.ts — canActivate with combined guard
{
  path: 'worksync/projects',
  canActivate: [authGuard, permissionGuard('projects:read'), featureGuard('wms:projects')],
  loadComponent: () => import('./features/worksync/projects/project-list.component')
    .then(m => m.ProjectListComponent),
},
```

```typescript
// projects/shared/src/lib/auth/feature.guard.ts
// `feature` is a commercial feature key that has already passed runtime flag evaluation
// in the backend session metadata, e.g. `work_management.projects`.
export const featureGuard = (feature: string): CanActivateFn =>
  () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    if (auth.hasFeature(feature)()) return true;
    return router.createUrlTree(['/403']);
  };
```

## Edit Panels and Slide-Overs

Angular Router does not use parallel routes. Edit panels open via component-level signal state:

```typescript
// employee-detail.component.ts
editSection = signal<string | null>(null);
```

```html
<!-- employee-detail.component.html -->
<app-employee-detail-sections (edit)="editSection.set($event)" />

@if (editSection()) {
  <app-slide-over-panel (close)="editSection.set(null)">
    <app-edit-employee-section [section]="editSection()!" />
  </app-slide-over-panel>
}
```

For bookmarkable modals, use query params:

```typescript
// employee-list.component.ts
private router = inject(Router);
private route = inject(ActivatedRoute);

showCreate = toSignal(
  this.route.queryParamMap.pipe(map(p => p.get('action') === 'new')),
  { initialValue: false }
);

openCreate() {
  this.router.navigate([], { queryParams: { action: 'new' }, queryParamsHandling: 'merge' });
}
closeCreate() {
  this.router.navigate([], { queryParams: { action: null }, queryParamsHandling: 'merge' });
}
```

## Breadcrumb Generation

Derived from `ActivatedRoute` data — attach `title` / `breadcrumb` data to route definitions:

```typescript
// In route config
{
  path: 'employees',
  data: { breadcrumb: 'Employees' },
  loadComponent: () => import('./features/employees/employee-list.component')
    .then(m => m.EmployeeListComponent),
}
```

```typescript
// projects/shared/src/lib/ui/breadcrumb/breadcrumb.service.ts
@Injectable({ providedIn: 'root' })
export class BreadcrumbService {
  private router = inject(Router);
  private activatedRoute = inject(ActivatedRoute);

  breadcrumbs = toSignal(
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd),
      map(() => this.buildBreadcrumbs(this.activatedRoute.root)),
    ),
    { initialValue: [] }
  );

  private buildBreadcrumbs(route: ActivatedRoute, url = '', crumbs: Breadcrumb[] = []): Breadcrumb[] {
    const routeUrl = route.snapshot.url.map(s => s.path).join('/');
    const fullUrl = routeUrl ? `${url}/${routeUrl}` : url;
    const label = route.snapshot.data['breadcrumb'];
    if (label) crumbs.push({ label, url: fullUrl });
    return route.firstChild ? this.buildBreadcrumbs(route.firstChild, fullUrl, crumbs) : crumbs;
  }
}
```

## Navigation Active State

```typescript
// In shell component
private router = inject(Router);

activePillar = toSignal(
  this.router.events.pipe(
    filter(e => e instanceof NavigationEnd),
    map(() => this.router.url.split('/')[1]),
  ),
  { initialValue: '' }
);
```

Or use Angular Router's built-in `routerLinkActive` directive in templates:

```html
<a routerLink="/employees" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: false }">
  <mat-icon>people</mat-icon>
</a>
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — full feature file tree
- [[frontend/cross-cutting/authorization|Authorization]] — permission system details
- [[frontend/data-layer/state-management|State Management]] — Angular Signals
