# Frontend Coding Standards

## Project Structure

Two Angular 21 standalone-component apps in one Angular workspace monorepo. No NgModules, no SSR, no file-based routing. All routes defined in `app.routes.ts`. See [[frontend/architecture/app-structure|App Structure]] for the full workspace layout.

```
projects/shared/src/lib/        ← shared library (auth, api, realtime, ui, models, utils)
projects/employee-app/src/app/
├── app.routes.ts               ← all employee-app routes
├── app.config.ts               ← ApplicationConfig (providers)
├── shell/                      ← nav rail + topbar
└── features/                   ← feature components (standalone, lazy-loaded)

projects/management-app/src/app/
├── app.routes.ts               ← all management-app routes
├── app.config.ts
├── shell/
└── features/
```

## File Organization Rules

1. **Feature components are standalone** — `standalone: true` on every `@Component`, `@Directive`, `@Pipe`
2. **One component per file** (except small private helpers only used in that file)
3. **Colocate first, promote when shared:**
   - Used by only one route → colocated in `features/{domain}/{page}/`
   - Used by 2+ pages in the same domain → promoted to `features/{domain}/components/` (delete colocated copy)
   - Used across both apps → promoted to `shared/src/lib/ui/` (delete app-level copy — never keep both)
4. **API services** live in `shared/src/lib/api/endpoints/` — one service per backend module
5. **Models** mirroring backend DTOs live in `shared/src/lib/models/` — one file per module

## Naming Conventions

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Component files | `kebab-case.component.ts` | `employee-list.component.ts` |
| Component template | `kebab-case.component.html` | `employee-list.component.html` |
| Component styles | `kebab-case.component.scss` | `employee-list.component.scss` |
| Service files | `kebab-case.service.ts` | `employee-api.service.ts` |
| Guard files | `kebab-case.guard.ts` | `auth.guard.ts` |
| Pipe files | `kebab-case.pipe.ts` | `format-date.pipe.ts` |
| Store service files | `kebab-case.store.ts` | `sidebar.store.ts` |
| Component classes | `PascalCaseComponent` | `EmployeeListComponent` |
| Service classes | `PascalCaseService` | `EmployeeApiService` |
| Guard functions | `camelCaseGuard` | `authGuard`, `permissionGuard` |
| Pipe classes | `PascalCasePipe` | `FormatDatePipe` |
| Types / interfaces | `PascalCase` | `Employee`, `LeaveRequest` |
| Route segments | `kebab-case` | `/workforce/live`, `/hr/employees` |

## Angular 21 Mandatory Patterns

### Standalone Components Only

```typescript
@Component({
  selector: 'app-employee-list',
  standalone: true,                          // ← always
  imports: [MatTableModule, RouterLink, HasPermissionDirective],
  templateUrl: './employee-list.component.html',
  styleUrl: './employee-list.component.scss',
})
export class EmployeeListComponent { }
```

### inject() — Never Constructor Injection

```typescript
// ✅ Correct
export class EmployeeListComponent {
  private employeeService = inject(EmployeeApiService);
  private router = inject(Router);
}

// ❌ Wrong
export class EmployeeListComponent {
  constructor(
    private employeeService: EmployeeApiService,
    private router: Router,
  ) {}
}
```

### New Control Flow — Never Legacy Structural Directives

```html
<!-- ✅ Correct -->
@if (employeesResource.isLoading()) {
  <mat-progress-bar mode="indeterminate" />
}
@for (employee of employees(); track employee.id) {
  <app-employee-row [employee]="employee" />
}
@switch (status()) {
  @case ('active') { <mat-chip color="primary">Active</mat-chip> }
  @case ('inactive') { <mat-chip>Inactive</mat-chip> }
}

<!-- ❌ Wrong -->
<mat-progress-bar *ngIf="loading" />
<app-employee-row *ngFor="let e of employees" [employee]="e" />
```

### Signals — Never BehaviorSubject for State

```typescript
// ✅ Correct
export class SidebarService {
  isExpanded = signal(true);
  toggle() { this.isExpanded.update(v => !v); }
}

// ❌ Wrong
export class SidebarService {
  isExpanded$ = new BehaviorSubject(true);
  toggle() { this.isExpanded$.next(!this.isExpanded$.value); }
}
```

### resource() for Async Data

```typescript
// ✅ Correct — resource() driven by a filter signal
export class EmployeeListComponent {
  private employeeService = inject(EmployeeApiService);

  filters = signal<EmployeeFilters>({ page: 0, pageSize: 25 });

  employeesResource = resource({
    request: () => this.filters(),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });
}
```

```html
<!-- Template reads synchronously from signals -->
@if (employeesResource.isLoading()) { <mat-progress-bar /> }
@if (employeesResource.hasValue()) {
  <mat-table [dataSource]="employeesResource.value()!.items" />
}
@if (employeesResource.error()) {
  <app-error-state [error]="employeesResource.error()" />
}
```

### Functional Guards — Never Class-Based

```typescript
// ✅ Correct — functional guard
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isAuthenticated() ? true : router.createUrlTree(['/login']);
};

// ❌ Wrong — class-based guard (Angular 21 deprecated)
@Injectable()
export class AuthGuard implements CanActivate {
  canActivate() { ... }
}
```

### Functional Interceptors — Never Class-Based

```typescript
// ✅ Correct
export const correlationInterceptor: HttpInterceptorFn = (req, next) =>
  next(req.clone({ setHeaders: { 'X-Correlation-Id': crypto.randomUUID() } }));

// ❌ Wrong
@Injectable()
export class CorrelationInterceptor implements HttpInterceptor {
  intercept(req, next) { ... }
}
```

## Component Template

```typescript
// features/employees/employee-list.component.ts
@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatInputModule,
    HasPermissionDirective,
    RouterLink,
    EmployeeRowComponent,
  ],
  templateUrl: './employee-list.component.html',
})
export class EmployeeListComponent {
  private employeeService = inject(EmployeeApiService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // URL state → signals
  private queryParams = toSignal(this.route.queryParamMap, { requireSync: true });
  search = computed(() => this.queryParams().get('q') ?? '');
  page   = computed(() => Number(this.queryParams().get('page') ?? '0'));

  // Async data driven by URL state
  employeesResource = resource({
    request: () => ({ search: this.search(), page: this.page() }),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });

  setSearch(q: string) {
    this.router.navigate([], {
      queryParams: { q: q || null, page: null },
      queryParamsHandling: 'merge',
    });
  }
}
```

## Service Template

```typescript
// shared/src/lib/api/endpoints/employees.service.ts
@Injectable({ providedIn: 'root' })
export class EmployeeApiService {
  private http = inject(HttpClient);

  list(filters: EmployeeFilters): Observable<PagedResult<Employee>> {
    return this.http.get<PagedResult<Employee>>('/api/v1/employees', {
      params: toHttpParams(filters as Record<string, unknown>),
    });
  }

  get(id: string): Observable<Employee> {
    return this.http.get<Employee>(`/api/v1/employees/${id}`);
  }

  create(data: CreateEmployeeDto): Observable<Employee> {
    return this.http.post<Employee>('/api/v1/employees', data);
  }

  update(id: string, data: Partial<CreateEmployeeDto>): Observable<Employee> {
    return this.http.patch<Employee>(`/api/v1/employees/${id}`, data);
  }
}
```

## Import Order

```typescript
// 1. Angular core + platform
import { Component, inject, signal, computed } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

// 2. Angular Material
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';

// 3. Third-party libraries
import { firstValueFrom } from 'rxjs';
import { z } from 'zod';

// 4. Shared library imports
import { HasPermissionDirective, EmployeeApiService } from '@onevo/shared';

// 5. Same-app shared components
import { DataTableComponent } from '../../shared/data-table/data-table.component';

// 6. Local feature components
import { EmployeeRowComponent } from './employee-row/employee-row.component';

// 7. Types / models
import type { Employee, EmployeeFilters } from '@onevo/shared';
```

## Error Handling

- **HTTP errors:** handled globally by `errorInterceptor` → `MatSnackBar` toast
- **Component errors:** use Angular's `ErrorHandler` + error state template block
- **Permission errors:** functional guard redirects to `/403`; `*hasPermission` directive hides elements
- **Network errors:** show retry button, not just error message

## Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML (`<nav>`, `<main>`, `<aside>`, `<table>`)
- Angular Material components handle most a11y patterns (focus traps, ARIA roles)
- Colour is never the only indicator — use icons + text alongside colour

## Performance

- **Lazy load** all heavy feature routes via `loadComponent` / `loadChildren` — never eager-import route components in `app.routes.ts`
- **`@defer`** for heavy in-page components (org charts, kanban boards, activity heatmaps)
- **Paginate** all lists — never load unbounded data
- **Debounce** search inputs (300 ms) before updating filter signal
- **`OnPush` change detection** on pure display components when rendering large lists

```typescript
// For high-frequency update components — use OnPush
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  // ...
})
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — workspace structure
- [[frontend/design-system/components/component-catalog|Component Catalog]] — Angular Material + shared components
- [[AI_CONTEXT/rules|Rules]] — Angular 21 mandatory patterns (authoritative)
