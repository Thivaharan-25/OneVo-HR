# Caching Strategy

## Angular `resource()` Cache Rules

Angular's `resource()` API caches the last value per request signal. For more granular control, use explicit reload triggers or service-level signals.

### Refresh Strategy by Data Category

| Category | Strategy | Rationale |
|:---------|:---------|:----------|
| Reference data (countries, departments) | `toSignal` — fetched once on init | Rarely changes |
| Entity lists (employees, leave requests) | `resource()` — reload on filter signal change | Moderate churn |
| Entity detail (employee profile) | `resource()` — reload on route param change | On-demand |
| Aggregated data (activity summaries) | `resource()` + 60 s interval `effect()` | Periodic refresh |
| Live / real-time data | SignalR push → `resource.reload()` | Push-driven |
| User session / permissions | `AuthService` signals — set once on login | Session-scoped |
| Search results | `resource()` with debounced search signal | On-type |

### Request Signal as Cache Key

The `resource()` request signal acts as the cache key — it re-runs the loader whenever the signal value changes.

```typescript
// Only fetches when filters() actually changes (deep equality by Angular)
employeesResource = resource({
  request: () => this.filters(),     // signal — acts as cache key
  loader: ({ request }) =>
    firstValueFrom(this.employeeService.list(request)),
});
```

---

## Optimistic Updates

Use for high-confidence actions where the outcome is predictable and the user expects instant feedback.

### When to Use

| Action | Optimistic | Rationale |
|:-------|:-----------|:----------|
| Acknowledge alert | Yes | Binary toggle, almost never fails |
| Approve/reject leave | Yes | Clear outcome |
| Update a single employee field | Yes | Simple field patch |
| Create employee | No | Complex validation, server-side checks |
| Run payroll | No | Long-running, needs server confirmation |
| Delete entity | No | Destructive — confirm first |

### Implementation Pattern

```typescript
// exception-list.component.ts
export class ExceptionListComponent {
  private exceptionService = inject(ExceptionApiService);

  alertsResource = resource({
    loader: () => firstValueFrom(this.exceptionService.getAlerts()),
  });

  acknowledge(alertId: string) {
    // Optimistic: update local signal immediately
    const current = this.alertsResource.value();
    if (current) {
      const optimistic = {
        ...current,
        items: current.items.map(a =>
          a.id === alertId ? { ...a, status: 'acknowledged' } : a
        ),
      };
      // Patch the resource value signal directly (Angular resource supports this)
      this.alertsResource.set(optimistic);
    }

    // Server call — reload on completion to reconcile
    this.exceptionService.acknowledge(alertId).subscribe({
      next: () => this.alertsResource.reload(),
      error: () => this.alertsResource.reload(), // revert via reload
    });
  }
}
```

---

## Prefetching

### Hover Prefetch via Route Preloading

Angular Router supports preloading strategies. Use `PreloadAllModules` for management-app heavy routes, or a custom strategy for employee-app:

```typescript
// app.config.ts
provideRouter(routes, withPreloading(PreloadAllModules))
```

### Manual Prefetch on Hover

For data prefetching (not just code), trigger an Angular service call and cache the result in a signal on the service:

```typescript
// employee-list.component.ts
prefetchEmployee(id: string) {
  // Kick off a background fetch — the service caches the result
  this.employeeService.get(id).subscribe();
}
```

```html
<tr (mouseenter)="prefetchEmployee(employee.id)" (click)="navigate(employee.id)">
```

---

## What Is and Is Not Persisted

Only non-sensitive UI-preference data persists across sessions:

| Data | Persisted | Storage |
|:-----|:----------|:--------|
| Sidebar state | Yes | Angular service signal + `localStorage` effect |
| Theme preference | Yes | `ThemeService` signal + `localStorage` effect |
| Table column preferences | Yes | Service signal + `localStorage` effect |
| Filter preferences | No — in URL `queryParams` | Bookmarkable via URL |
| `resource()` data | No | Memory only (security) |
| Auth session | HttpOnly cookie only | Browser cookie |

### Why Server Data Is Never Persisted to localStorage

- **Multi-tenant:** risk of cross-tenant data on shared devices
- **Staleness:** employee/financial data must always be fresh from the API
- **Security:** sensitive data (salaries, performance reviews) must not be in localStorage

---

## Tenant-Scoped Data

All `resource()` requests implicitly scope to the current tenant via the `TenantInterceptor` (adds `X-Tenant-Id` header) and the URL path (tenant resolved from subdomain on the server). No client-side tenant scoping of cache keys is required — the interceptor ensures every HTTP call carries the correct tenant context.

When a user switches apps (employee ↔ management), the components remount and `resource()` instances re-initialize fresh. No stale cross-context data.

---

## SignalR as Cache Invalidation

When a SignalR push arrives, call `resource.reload()` to trigger a fresh fetch:

```typescript
// workforce-live.component.ts — live data driven by SignalR
ngOnInit() {
  this.signalR.on('workforce-live', 'PresenceChanged', () => {
    this.presenceResource.reload();
  });

  // High-frequency updates: set directly instead of reload to avoid thundering herd
  this.signalR.on('workforce-live', 'WorkforceStatusUpdate', (snapshot) => {
    this.presenceResource.set(snapshot);
  });
}
```

**Rule:** Use `reload()` for low-frequency events (employee created, leave approved). Use `resource.set()` for high-frequency live data (workforce presence updates).

---

## Related

- [[frontend/data-layer/state-management|State Management]] — Angular Signals + resource() patterns
- [[frontend/data-layer/real-time|Real-Time Architecture]] — SignalR cache invalidation
- [[frontend/data-layer/api-integration|API Integration]] — HttpClient services
- [[frontend/architecture/overview|Overview]] — data ownership principle
