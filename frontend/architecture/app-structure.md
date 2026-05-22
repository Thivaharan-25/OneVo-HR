# Frontend App Structure

> **Stack:** Angular 21 standalone components, two-app monorepo workspace. No NgModules, no SSR, no file-based routing. All routes are defined in `app.routes.ts`. Feature components live in `features/`. Loading states use Angular's `@defer` or `resource.isLoading()` signals.

> **Two apps, one backend:** `employee-app` (`app.{tenant}.onevo.com`) for employee self-service; `management-app` (`manage.{tenant}.onevo.com`) for HR/Admin/Manager/Executive workflows. Both consume the same `/api/v1/*` backend and share a `shared` Angular library.

## Monorepo Workspace Structure

```
onevo-frontend/                        ← Angular workspace root
├── angular.json                       ← Workspace config (defines all three projects)
├── tsconfig.json                      ← Root TypeScript config
├── package.json                       ← Shared dependencies
│
├── projects/
│   ├── employee-app/                  ← Employee self-service SPA
│   ├── management-app/                ← HR / Admin / Manager / Executive SPA
│   └── shared/                        ← Angular library (shared across both apps)
│
└── e2e/                               ← Playwright E2E tests (cross-app)
```

---

## Shared Library (`projects/shared/`)

Built once with `ng build shared`. Both apps import from `@onevo/shared`.

```
projects/shared/src/lib/
├── auth/
│   ├── auth.service.ts               # AuthService: session state signals, login/logout
│   ├── auth.guard.ts                 # Functional CanActivateFn — redirects to /login
│   ├── permission.guard.ts           # Functional CanActivateFn — redirects to /403
│   ├── auth.interceptor.ts           # HttpInterceptorFn: session cookie + refresh
│   ├── has-permission.directive.ts   # *hasPermission="'resource:action'" structural directive
│   └── models/
│       └── session.model.ts          # Session, UserProfile, TenantInfo
│
├── api/
│   ├── base-api.service.ts           # Base class with HttpClient + error normalisation
│   ├── interceptors/
│   │   ├── tenant.interceptor.ts     # Injects X-Tenant-Id from AuthService
│   │   ├── correlation.interceptor.ts# Injects X-Correlation-Id (crypto.randomUUID)
│   │   └── error.interceptor.ts     # RFC 7807 → MatSnackBar toast on 4xx/5xx
│   └── endpoints/
│       ├── employees.service.ts
│       ├── leave.service.ts
│       ├── attendance.service.ts
│       ├── workforce.service.ts
│       ├── notifications.service.ts
│       ├── calendar.service.ts
│       ├── settings.service.ts
│       ├── agents.service.ts
│       ├── identity.service.ts
│       └── worksync/
│           ├── projects.service.ts
│           ├── tasks.service.ts
│           ├── goals.service.ts
│           ├── docs.service.ts
│           ├── time.service.ts
│           └── chat.service.ts
│
├── realtime/
│   └── signalr.service.ts            # HubConnectionBuilder; exposes typed observables per channel
│
├── ui/
│   ├── shell/
│   │   ├── shell-layout.component.ts # Root shell: nav rail + topbar + router-outlet
│   │   ├── nav-rail.component.ts     # Icon rail (52px floating dark card)
│   │   ├── topbar.component.ts       # 40px topbar with context switcher
│   │   └── context-switcher.component.ts # Switches between employee-app and management-app
│   ├── data-display/
│   │   ├── data-table.component.ts   # MatTable wrapper with sorting/pagination/export
│   │   ├── stat-card.component.ts    # KPI card
│   │   └── empty-state.component.ts
│   └── feedback/
│       ├── loading-bar.component.ts
│       └── error-state.component.ts
│
├── models/
│   ├── employee.model.ts
│   ├── leave.model.ts
│   ├── attendance.model.ts
│   ├── workforce.model.ts
│   ├── notification.model.ts
│   └── pagination.model.ts
│
└── utils/
    ├── format-date.ts                # date-fns wrappers
    ├── to-params.ts                  # Object → HttpParams
    └── validators.ts                 # Custom Angular Validators
```

---

## Employee App (`projects/employee-app/`)

### Authorization Model

**Hybrid permissions — not traditional fixed-role RBAC:**
1. **Custom roles** — tenants create roles with custom names and assign granular permissions
2. **Per-employee overrides** — individual employees can be granted/revoked specific access independent of their role

**Never hardcode role names.** Always check permission keys (e.g., `leave:read`, `attendance:read-own`).

```typescript
// AuthService.hasPermission() checks BOTH role permissions AND employee-level overrides
private authService = inject(AuthService);

canViewTeam = this.authService.hasPermission('leave:read');      // signal<boolean>
canRequestLeave = this.authService.hasPermission('leave:create');
```

### Directory Structure

```
projects/employee-app/src/
├── main.ts                            # bootstrapApplication(AppComponent, appConfig)
├── app/
│   ├── app.component.ts               # Root component (router-outlet only)
│   ├── app.config.ts                  # provideRouter, provideHttpClient, provideAnimations,
│   │                                  # withInterceptors([authInterceptor, tenantInterceptor, ...])
│   ├── app.routes.ts                  # ALL employee-app routes defined here
│   │
│   ├── shell/
│   │   └── employee-shell.component.ts # Shell with employee nav rail + topbar
│   │
│   └── features/
│       │
│       │── ── AUTH (public, no nav) ────
│       │
│       ├── auth/
│       │   ├── login/
│       │   │   └── login.component.ts
│       │   ├── forgot-password/
│       │   │   └── forgot-password.component.ts
│       │   ├── reset-password/
│       │   │   └── reset-password.component.ts
│       │   └── mfa/
│       │       └── mfa.component.ts
│       │
│       │── ── DASHBOARD (authenticated) ────
│       │
│       ├── home/
│       │   └── home.component.ts      # Employee landing: my tasks, upcoming leave, status
│       │
│       ├── my-work/
│       │   ├── my-work.component.ts   # Tasks assigned to me across all projects
│       │   └── my-space.component.ts  # Personal workspace / My Space
│       │
│       ├── leave/
│       │   ├── leave-overview.component.ts   # My leave requests + balance cards
│       │   ├── leave-request.component.ts    # Submit new leave request
│       │   └── leave-calendar.component.ts   # My leave calendar view
│       │
│       ├── attendance/
│       │   ├── my-attendance.component.ts    # My attendance records
│       │   └── my-shifts.component.ts        # My shift schedule
│       │
│       ├── profile/
│       │   ├── my-profile.component.ts       # Personal profile, dependents, documents
│       │   └── my-skills.component.ts        # My skill profile + validation requests
│       │
│       ├── calendar/
│       │   └── my-calendar.component.ts      # Personal calendar (leave, shifts, events)
│       │
│       ├── notifications/
│       │   ├── inbox.component.ts            # Notification inbox
│       │   └── preferences.component.ts     # Notification preferences
│       │
│       ├── chat/                             # WorkSync chat (Package 2)
│       │   └── chat.component.ts
│       │
│       └── errors/
│           ├── not-found.component.ts        # 404
│           ├── forbidden.component.ts        # 403
│           └── error.component.ts            # Global error fallback
└── environments/
    ├── environment.ts
    └── environment.prod.ts
```

### Route Config Pattern (`app.routes.ts`)

```typescript
// projects/employee-app/src/app/app.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from '@onevo/shared';
import { permissionGuard } from '@onevo/shared';

export const routes: Routes = [
  // Auth routes (public)
  {
    path: '',
    loadComponent: () => import('./features/auth/auth-layout.component'),
    children: [
      { path: 'login', loadComponent: () => import('./features/auth/login/login.component') },
      { path: 'forgot-password', loadComponent: () => import('./features/auth/forgot-password/forgot-password.component') },
      { path: 'reset-password', loadComponent: () => import('./features/auth/reset-password/reset-password.component') },
      { path: 'mfa', loadComponent: () => import('./features/auth/mfa/mfa.component') },
    ],
  },
  // Authenticated routes
  {
    path: '',
    loadComponent: () => import('./shell/employee-shell.component'),
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      { path: 'home', loadComponent: () => import('./features/home/home.component') },
      {
        path: 'leave',
        canActivate: [permissionGuard('leave:create')],
        loadComponent: () => import('./features/leave/leave-overview.component'),
      },
      {
        path: 'attendance',
        canActivate: [permissionGuard('attendance:read-own')],
        loadComponent: () => import('./features/attendance/my-attendance.component'),
      },
      { path: 'profile', loadComponent: () => import('./features/profile/my-profile.component') },
      { path: 'calendar', loadComponent: () => import('./features/calendar/my-calendar.component') },
      { path: 'chat', loadComponent: () => import('./features/chat/chat.component') },
      { path: 'notifications', loadComponent: () => import('./features/notifications/inbox.component') },
    ],
  },
  { path: '403', loadComponent: () => import('./features/errors/forbidden.component') },
  { path: '**', loadComponent: () => import('./features/errors/not-found.component') },
];
```

---

## Management App (`projects/management-app/`)

### Directory Structure

```
projects/management-app/src/
├── main.ts
├── app/
│   ├── app.component.ts
│   ├── app.config.ts
│   ├── app.routes.ts                  # ALL management-app routes
│   │
│   ├── shell/
│   │   └── management-shell.component.ts # Shell with management nav rail + topbar
│   │
│   └── features/
│       │
│       ├── auth/                      # Same auth pages (shared login endpoint)
│       │
│       ├── home/
│       │   └── dashboard.component.ts # Management dashboard: pending approvals, alerts
│       │
│       │── ── HR MANAGEMENT ────
│       │
│       ├── employees/
│       │   ├── employee-list.component.ts     # Directory (MatTable + search + filters)
│       │   ├── employee-new.component.ts      # Create employee — multi-step wizard
│       │   └── employee-detail.component.ts   # Detail — sections + slide-over edit panel
│       │
│       ├── leave/
│       │   ├── leave-management.component.ts  # All leave requests (approve/reject)
│       │   ├── leave-calendar.component.ts    # Team leave calendar
│       │   ├── leave-balances.component.ts    # Per-type balance overview
│       │   └── leave-policies.component.ts    # Policy CRUD
│       │
│       ├── attendance/
│       │   ├── attendance-overview.component.ts  # Team attendance records
│       │   ├── attendance-corrections.component.ts
│       │   ├── shifts.component.ts               # Shift schedule management
│       │   └── overtime.component.ts             # Overtime approvals
│       │
│       │── ── WORKFORCE INTELLIGENCE ────
│       │
│       ├── workforce/
│       │   ├── live-dashboard.component.ts    # Live presence card grid
│       │   ├── employee-activity.component.ts # /workforce/:id — activity detail
│       │   └── analytics.component.ts         # Productivity scores + capacity analytics
│       │
│       ├── exceptions/
│       │   ├── exception-dashboard.component.ts  # Exception alerts + escalations
│       │   └── exception-rules.component.ts      # Rule configuration
│       │
│       ├── identity-verification/
│       │   └── verification-review.component.ts  # Photo verification review queue
│       │
│       │── ── WORKSYNC OVERSIGHT ────
│       │
│       ├── worksync/
│       │   ├── projects/
│       │   │   ├── project-list.component.ts
│       │   │   ├── project-detail.component.ts
│       │   │   ├── project-board.component.ts
│       │   │   └── project-roadmap.component.ts
│       │   ├── goals/
│       │   │   ├── goals-overview.component.ts
│       │   │   └── goal-detail.component.ts
│       │   ├── time/
│       │   │   └── time-reports.component.ts
│       │   └── chat/
│       │       └── chat.component.ts
│       │
│       │── ── ORG STRUCTURE ────
│       │
│       ├── org/
│       │   ├── org-chart.component.ts
│       │   ├── departments.component.ts
│       │   ├── teams.component.ts
│       │   ├── job-families.component.ts
│       │   └── legal-entities.component.ts
│       │
│       │── ── CALENDAR & PLANNING ────
│       │
│       ├── calendar/
│       │   └── calendar.component.ts          # Unified calendar (leave, holidays, reviews)
│       │
│       │── ── ADMIN ────
│       │
│       ├── admin/
│       │   ├── users.component.ts             # User management + role assignment
│       │   ├── roles.component.ts             # Role + permission management
│       │   ├── audit.component.ts             # Audit log viewer
│       │   ├── agents/
│       │   │   ├── agents-list.component.ts   # Desktop agent fleet
│       │   │   └── agent-detail.component.ts
│       │   ├── devices.component.ts           # Hardware terminals
│       │   └── compliance.component.ts        # GDPR / data governance
│       │
│       │── ── SETTINGS ────
│       │
│       ├── settings/
│       │   ├── general.component.ts           # Tenant settings
│       │   ├── monitoring.component.ts        # Monitoring toggles + feature flags
│       │   ├── notifications.component.ts     # Org-level notification channel config
│       │   ├── integrations.component.ts      # SSO, LMS, payroll providers
│       │   ├── branding.component.ts          # Logo, colours, domain
│       │   ├── billing.component.ts           # Subscription & plan
│       │   └── alerts.component.ts            # Alert rule configuration
│       │
│       ├── notifications/
│       │   └── inbox.component.ts
│       │
│       └── errors/
│           ├── not-found.component.ts
│           ├── forbidden.component.ts
│           └── error.component.ts
└── environments/
    ├── environment.ts
    └── environment.prod.ts
```

## Angular Bootstrap Pattern (`app.config.ts`)

```typescript
// projects/{app}/src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import {
  authInterceptor,
  tenantInterceptor,
  correlationInterceptor,
  errorInterceptor,
} from '@onevo/shared';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(
      withInterceptors([authInterceptor, tenantInterceptor, correlationInterceptor, errorInterceptor])
    ),
    provideAnimationsAsync(),
  ],
};
```

## Standalone Component Pattern

```typescript
// projects/management-app/src/app/features/employees/employee-list.component.ts
@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatButtonModule,
    HasPermissionDirective,   // from @onevo/shared
    RouterLink,
  ],
  templateUrl: './employee-list.component.html',
})
export class EmployeeListComponent {
  private employeeService = inject(EmployeeService);

  filters = signal<EmployeeFilters>({ page: 0, pageSize: 25 });

  employeesResource = resource({
    request: () => this.filters(),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });
}
```

```html
<!-- employee-list.component.html -->
@if (employeesResource.isLoading()) {
  <mat-progress-bar mode="indeterminate" />
}

@if (employeesResource.hasValue()) {
  <mat-table [dataSource]="employeesResource.value()!.items">
    <!-- column definitions -->
  </mat-table>
}

@if (employeesResource.error()) {
  <app-error-state [error]="employeesResource.error()" />
}
```

## Module → Route Mapping

| # | Backend Module | Employee App | Management App |
|---|---|---|---|
| 1 | auth | `/login`, `/mfa`, `/reset-password` | Same auth pages |
| 2 | core-hr | My profile (`/profile`) | Employee directory + detail (`/employees`) |
| 3 | leave | My leave (`/leave`) | Leave management (`/leave`) |
| 4 | attendance | My attendance (`/attendance`) | Attendance overview + corrections |
| 5 | workforce-presence | My shifts (`/attendance/shifts`) | Shift management + live dashboard |
| 6 | activity-monitoring | — | Workforce live + employee activity detail |
| 7 | productivity-analytics | — | Workforce analytics |
| 8 | exception-engine | — | Exception dashboard + rule config |
| 9 | identity-verification | — | Verification review queue |
| 10 | notifications | Inbox (`/notifications`) | Inbox + org config |
| 11 | calendar | My calendar (`/calendar`) | Unified calendar |
| 12 | org-structure | — | Departments, teams, org chart |
| 13 | work-management (WMS) | My work (`/my-work`), chat | Projects, goals, docs, time, chat |
| 14 | configuration | — | Settings + monitoring toggles |
| 15 | auth (admin) | — | Users, roles, audit, compliance |
| 16 | agent-gateway | — | Agent fleet + device management |

## Layout System

### Shell Layout

Responsive behaviour is centralised in shared shell primitives from `@onevo/shared`:

```
shared/src/lib/ui/shell/
├── shell-layout.component.ts   # Responsive wrapper: topbar + nav rail + router-outlet
├── nav-rail.component.ts       # 52px floating dark card (icon rail)
├── topbar.component.ts         # 40px topbar with context switcher for dual-role users
└── context-switcher.component.ts # App switcher (employee ↔ management)
```

- **Nav Rail:** 52px floating dark card (`#17181F`, radius 12px). Permission-gated; collapses on mobile.
- **Topbar:** 40px height, floating card (radius 10px). Includes context switcher visible only to users with management permissions.
- **Floating-cards layout:** Every element is a separate rounded card with `8px` body padding and `6px` gaps.

## Page Count

| App | Section | Pages |
|-----|---------|-------|
| employee-app | Auth | 4 |
| employee-app | Home, My Work, Leave, Attendance, Profile, Calendar, Chat, Notifications | ~12 |
| management-app | Auth | 4 (shared login endpoint) |
| management-app | Dashboard, Employees, Leave, Attendance, Workforce, Exceptions, WorkSync | ~35 |
| management-app | Org, Calendar, Admin, Settings, Notifications | ~20 |
| **Total** | | **~75** |

## Related

- [[frontend/architecture/routing|Routing]] — typed routes, functional guards, breadcrumbs
- [[frontend/architecture/module-boundaries|Module Boundaries]] — code splitting, import rules
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — lazy loading, deferred views
- [[frontend/cross-cutting/authorization|Authorization]] — permission system details
- [[frontend/data-layer/state-management|State Management]] — Angular Signals
