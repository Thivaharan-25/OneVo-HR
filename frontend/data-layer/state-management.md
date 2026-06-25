# State Management

## Three Types of State

| Type | Technology | Examples |
|:-----|:-----------|:--------|
| Server / async state | Angular `resource()` + `toSignal()` | Employees, Time Off requests, activity data |
| Client / UI state | Angular Signals (`signal()`) | Sidebar open/closed, filter preferences, theme |
| URL state | Angular Router `queryParams` | Page number, search query, date range, filters |

No NgRx, no RxJS `BehaviorSubject` for component or service state in Phase 1. Angular 21 Signals cover all reactive state needs.

---

## Server State - `resource()` and `toSignal()`

### `resource()` for parameterised async data

Use when the request depends on a reactive signal (filters, pagination, IDs):

```typescript
// employee-list.component.ts
export class EmployeeListComponent {
  private employeeService = inject(EmployeeService);

  filters = signal<EmployeeFilters>({ page: 0, pageSize: 25, search: '' });

  employeesResource = resource({
    request: () => this.filters(),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });

  // Usage in template:
  // employeesResource.value()   - current data (undefined while loading)
  // employeesResource.isLoading() - boolean signal
  // employeesResource.error()   - error signal
  // employeesResource.reload()  - manual refresh
}
```

### `toSignal()` for simple one-shot streams

```typescript
// When you don't need parameterised requests or manual reload
departments = toSignal(this.orgService.getDepartments(), { initialValue: [] });
```

### Stale Time / Refresh Strategy

| Data Type | Refresh Strategy | Rationale |
|:----------|:----------------|:----------|
| Static data (countries, departments) | `toSignal` - fetched once on init | Rarely changes |
| Employee list | `resource()` - reload on filter change | Moderate change |
| Time Off requests | `resource()` - reload + SignalR invalidation | Active request workflow |
| Activity summaries | `resource()` - 60 s timer effect | Aggregated |
| Live monitoring status | SignalR push -> `resource.reload()` | Real-time |
| Exception alerts | SignalR push -> `resource.reload()` | Real-time |

### SignalR as a cache invalidation trigger

```typescript
// monitoring-live.component.ts
export class MonitoringLiveComponent implements OnInit {
  private signalR = inject(SignalRService);

  presenceResource = resource({
    loader: () => firstValueFrom(this.monitoringService.getLiveStatus()),
  });

  ngOnInit() {
    this.signalR.on('monitoring-live', 'PresenceChanged', () => {
      this.presenceResource.reload();
    });
  }
}
```

---

## Client State - Angular Signals

Use `signal()` for all ephemeral UI state. Keep signals in services when state is shared across components; keep them local to the component when they're not.

### Auth Service (shared, from `@onevo/shared`)

```typescript
// shared/src/lib/auth/auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private _user = signal<User | null>(null);
  private _permissions = signal<string[]>([]);
  private _activeModules = signal<string[]>([]);
  private _activeFeatures = signal<string[]>([]);

  user = this._user.asReadonly();
  isAuthenticated = computed(() => this._user() !== null);

  hasPermission(permission: string): Signal<boolean> {
    return computed(() => this._permissions().includes(permission));
  }

  hasModule(moduleKey: string): Signal<boolean> {
    return computed(() => this._activeModules().includes(moduleKey));
  }

  hasFeature(featureKey: string): Signal<boolean> {
    return computed(() => this._activeFeatures().includes(featureKey));
  }

  setSession(user: User, permissions: string[], modules: string[], features: string[]) {
    this._user.set(user);
    this._permissions.set(permissions);
    this._activeModules.set(modules);
    this._activeFeatures.set(features);
  }

  clear() {
    this._user.set(null);
    this._permissions.set([]);
    this._activeModules.set([]);
    this._activeFeatures.set([]);
  }
}
```

### Sidebar State (per-app service)

```typescript
// shell/sidebar.service.ts (in each app)
@Injectable({ providedIn: 'root' })
export class SidebarService {
  isExpanded = signal(true);
  activePillar = signal<string | null>(null);

  toggle() { this.isExpanded.update(v => !v); }
}
```

### Filter State (component-level signal)

Prefer keeping filter signals local to the component that owns them. Only lift to a service if two sibling components genuinely need to share them.

```typescript
// employee-list.component.ts
filters = signal<EmployeeFilters>({ page: 0, pageSize: 25, search: '', deptId: null });

setSearch(search: string) {
  this.filters.update(f => ({ ...f, search, page: 0 }));
}

setDept(deptId: string | null) {
  this.filters.update(f => ({ ...f, deptId, page: 0 }));
}
```

### Theme State (persisted to localStorage)

```typescript
// shared/src/lib/ui/theme/theme.service.ts
@Injectable({ providedIn: 'root' })
export class ThemeService {
  theme = signal<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark' | 'system') ?? 'system'
  );

  constructor() {
    effect(() => {
      localStorage.setItem('theme', this.theme());
      document.documentElement.setAttribute('data-theme', this.resolvedTheme());
    });
  }

  resolvedTheme = computed(() => {
    const t = this.theme();
    if (t !== 'system') return t;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  setTheme(theme: 'light' | 'dark' | 'system') { this.theme.set(theme); }
}
```

---

## URL State - Angular Router `queryParams`

Use for any state that should be bookmarkable or shareable: pagination, search, filters, date ranges.

```typescript
// employee-list.component.ts
export class EmployeeListComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // Read URL state as signals
  private queryParams = toSignal(this.route.queryParamMap, { requireSync: true });

  page   = computed(() => Number(this.queryParams().get('page') ?? '0'));
  search = computed(() => this.queryParams().get('q') ?? '');
  deptId = computed(() => this.queryParams().get('dept') ?? null);

  // Drive resource from URL state
  employeesResource = resource({
    request: () => ({ page: this.page(), search: this.search(), deptId: this.deptId() }),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });

  // Write URL state
  setSearch(q: string) {
    this.router.navigate([], {
      queryParams: { q: q || null, page: null },
      queryParamsHandling: 'merge',
    });
  }

  setPage(page: number) {
    this.router.navigate([], {
      queryParams: { page: page || null },
      queryParamsHandling: 'merge',
    });
  }
}
```

**When to use URL state vs signal:**

| Scenario | Use |
|---|---|
| Filter that should survive page refresh or be shareable | Router `queryParams` |
| UI-only state (sidebar open, drawer open) | Component or service signal |
| User preference persisted across sessions | Service signal + `localStorage` effect |

---

## Rules

- **No `BehaviorSubject` for UI state** - use `signal()` instead
- **No `async` pipe** for component state - use `resource()` or `toSignal()` and read synchronously
- **No duplicating server state** in a local signal - derive from the `resource` value directly
- **No NgRx** in Phase 1 - Angular Signals cover all needs
- **`effect()` for side effects only** (localStorage sync, DOM, analytics) - never for data transformation; use `computed()` for that

---

## Related

- [[frontend/architecture/app-structure|App Structure]] - frontend architecture
- [[frontend/data-layer/api-integration|API Integration]] - Angular HttpClient services
- [[frontend/data-layer/real-time|Real-Time Architecture]] - SignalR integration
- [[frontend/coding-standards|Coding Standards]] - Angular conventions
