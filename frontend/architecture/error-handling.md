# Error Handling Architecture

## Error Handling Hierarchy

Errors are caught at the narrowest possible scope to avoid blowing up the entire page when one section fails.

```
Root Application
+-- Global ErrorHandler (app.config.ts -> provideErrorHandler)
|   +-- Catches: unhandled exceptions, provider failures
|       Action: Log to error monitoring, show full-page error with "Reload app" button
|
+-- Dashboard Layout route error (dashboard.routes.ts -> error component)
|   +-- Catches: layout-level failures (auth provider, sidebar data)
|       Action: Error within dashboard chrome, sidebar still works
|
+-- Section error (people.routes.ts -> error component)
|   +-- Catches: section-wide failures (People API down)
|       Action: Error card within content area, nav still works
|
+-- Page error (employees.routes.ts -> error component)
|   +-- Catches: page-specific failures (employee list fetch failed)
|       Action: Error state with retry button, breadcrumbs visible
|
+-- Component error (try/catch in services, signal error state)
    +-- Catches: individual widget failures (chart crash, malformed data)
        Action: Inline error card, rest of page unaffected
```

## Error Types

| Type | Source | Handling |
|:-----|:-------|:---------|
| `AuthError` | 401 from API, expired token | Redirect to `/login?redirect={current}`, clear auth store |
| `ForbiddenError` | 403 from API | Show inline "no permission" state, log to analytics |
| `NotFoundError` | 404 from API | Navigate to not-found route via `Router.navigate(['/not-found'])` |
| `ValidationError` | 400 from API (RFC 7807) | Map to form field errors via `errors` map |
| `ApiError` | 500, 502, 503 from API | Toast notification + retry button |
| `NetworkError` | Fetch failed, timeout | "Connection lost" banner + auto-retry with backoff |
| `RenderError` | Angular component crash | Global `ErrorHandler` catches, shows fallback UI |
| `ChunkLoadError` | Lazy route import failed | Auto-retry import, then show "update available" prompt |

## API Error Flow

```
API Response (non-2xx)
    |
    v
HttpClient interceptor (error.interceptor.ts)
    |
    +-- 401 -> AuthError -> refresh token attempt
    |   +-- Refresh succeeds -> retry original request
    |   +-- Refresh fails -> redirect to /login
    |
    +-- 403 -> ForbiddenError -> throw (component handles)
    |
    +-- 404 -> NotFoundError -> throw (page navigates to not-found)
    |
    +-- 400 -> ValidationError -> throw (form maps to field errors)
    |
    +-- 429 -> RateLimitError -> auto-retry after Retry-After header
    |
    +-- 5xx -> ApiError -> throw (error component catches)
              |
              v
         HttpClient retry with RxJS
              |
              +-- retry 1 -> wait 1s
              +-- retry 2 -> wait 2s
              +-- retry 3 -> wait 4s
              +-- give up -> error state in component
```

## Network Resilience

### Offline Detection

```typescript
// shared/components/network-status-banner.component.ts
@Component({
  selector: 'app-network-status-banner',
  standalone: true,
  imports: [MatIconModule],
  template: `
    @if (!isOnline()) {
      <div class="sticky top-0 z-50 flex items-center gap-2 bg-yellow-100 px-4 py-2 text-sm text-yellow-800">
        <mat-icon>wifi_off</mat-icon>
        You're offline. Changes will sync when connection is restored.
      </div>
    }
    @if (justReconnected()) {
      <div class="sticky top-0 z-50 flex items-center gap-2 bg-green-100 px-4 py-2 text-sm text-green-800">
        <mat-icon>wifi</mat-icon>
        Back online. Syncing data...
      </div>
    }
  `,
})
export class NetworkStatusBannerComponent {
  private readonly isOnline = signal(navigator.onLine);
  private readonly justReconnected = signal(false);

  constructor() {
    window.addEventListener('online', () => {
      this.isOnline.set(true);
      this.justReconnected.set(true);
      setTimeout(() => this.justReconnected.set(false), 3000);
    });
    window.addEventListener('offline', () => this.isOnline.set(false));
  }
}
```

### Stale Data Indicator

When a service is refreshing data in the background:

```typescript
// Example: employee-list.component.ts
@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [DataTableComponent],
  template: `
    @if (isRefreshing()) {
      <div class="animate-pulse text-xs text-slate-500">Refreshing...</div>
    }
    <app-data-table [data]="employees()" />
  `,
})
export class EmployeeListComponent {
  private readonly employeeService = inject(EmployeeService);

  readonly employees = this.employeeService.employees;
  readonly isRefreshing = this.employeeService.isRefreshing;
}
```

## Error UI Components

### Page-Level Error State

Angular page-level error components receive a display-safe message and emit retry/navigation actions. Error capture goes through the selected error monitoring adapter once the provider is chosen.

```typescript
@Component({
  selector: 'app-page-error',
  standalone: true,
  template: `
    <section class="flex flex-col items-center justify-center py-20">
      <mat-icon class="mb-4 text-red-600">error</mat-icon>
      <h2 class="text-lg font-semibold">Something went wrong</h2>
      <p class="mt-1 max-w-md text-center text-sm text-slate-600">
        {{ message }}
      </p>
      <button mat-flat-button class="mt-6" (click)="retry.emit()">Try again</button>
    </section>
  `,
  imports: [MatIconModule, MatButtonModule],
})
export class PageErrorComponent {
  @Input() message = 'An unexpected error occurred.';
  @Output() retry = new EventEmitter<void>();
}
```

### Inline Error State

```typescript
@Component({
  selector: 'app-inline-error',
  standalone: true,
  template: `
    <div class="flex items-center gap-2 rounded border border-red-200 bg-red-50 p-4">
      <mat-icon class="text-red-600">error_outline</mat-icon>
      <span class="text-sm">{{ message }}</span>
      @if (retryable) {
        <button mat-button (click)="retry.emit()">Retry</button>
      }
    </div>
  `,
  imports: [MatIconModule, MatButtonModule],
})
export class InlineErrorComponent {
  @Input() message = '';
  @Input() retryable = false;
  @Output() retry = new EventEmitter<void>();
}
```

### Toast Notifications

```typescript
// shared/services/error-toast.service.ts
@Injectable({ providedIn: 'root' })
export class ErrorToastService {
  private readonly snackBar = inject(MatSnackBar);

  showError(error: ApiError): void {
    const severity = error.status >= 500 ? 'critical' : 'warning';
    const panelClass = severity === 'critical' ? 'snackbar-error' : 'snackbar-warning';
    const duration = severity === 'critical' ? 0 : 5000;

    const ref = this.snackBar.open(
      error.detail ?? error.title,
      error.retryable ? 'Retry' : 'Dismiss',
      { duration, panelClass }
    );

    if (error.retryable) {
      ref.onAction().subscribe(() => error.retry());
    }
  }
}
```

## Chunk Load Error Recovery

When a lazy-loaded route fails to load (deploy during user session):

```typescript
// app/app.routes.ts - wrap loadComponent with error recovery
function safeLoadComponent(importFn: () => Promise<any>) {
  return () =>
    importFn().catch((error) => {
      if (error?.name === 'ChunkLoadError' || error?.message?.includes('Loading chunk')) {
        const snackBar = inject(MatSnackBar);
        const ref = snackBar.open(
          'A new version is available. Please refresh.',
          'Refresh',
          { duration: 0 }
        );
        ref.onAction().subscribe(() => window.location.reload());
      }
      throw error;
    });
}

// Usage in routes
{
  path: 'monitoring/analytics',
  loadComponent: safeLoadComponent(() =>
    import('./monitoring/analytics/monitoring-analytics.component').then(m => m.MonitoringAnalyticsComponent)
  ),
}
```

## Related

- [[frontend/architecture/routing|Routing]] - error routes in route tree
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] - error tracking integration (provider not yet selected)
- [[frontend/cross-cutting/authentication|Authentication]] - auth error flows
- [[frontend/data-layer/api-integration|Api Integration]] - API error types
