# API Integration

## Angular HttpClient Services

API calls use Angular's `HttpClient` wrapped in typed services under `shared/src/lib/api/endpoints/`. Components never call `HttpClient` directly - they inject the service.

Customer web API calls use a BFF-style HttpOnly cookie session. The browser frontend does not attach tenant JWTs directly to `/api/v1/*` requests - the cookie carries the session.

```typescript
// shared/src/lib/api/endpoints/employees.service.ts
@Injectable({ providedIn: 'root' })
export class EmployeeApiService {
  private http = inject(HttpClient);
  private baseUrl = inject(API_BASE_URL); // InjectionToken from environment

  list(filters: EmployeeFilters): Observable<PagedResult<Employee>> {
    const params = toHttpParams(filters);
    return this.http.get<PagedResult<Employee>>('/api/v1/employees', { params });
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

---

## Functional Interceptors

Interceptors are registered in `app.config.ts` via `withInterceptors([...])`. All are functional (`HttpInterceptorFn`).

```typescript
// shared/src/lib/api/interceptors/auth.interceptor.ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Cookie-based session - no Authorization header for customer web.
  // withCredentials ensures cookies are sent cross-origin to the API.
  return next(req.clone({ withCredentials: true }));
};
```

```typescript
// shared/src/lib/api/interceptors/tenant.interceptor.ts
export const tenantInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const tenantId = auth.user()?.tenantId;

  if (tenantId) {
    return next(req.clone({ setHeaders: { 'X-Tenant-Id': tenantId } }));
  }
  return next(req);
};
```

```typescript
// shared/src/lib/api/interceptors/correlation.interceptor.ts
export const correlationInterceptor: HttpInterceptorFn = (req, next) =>
  next(req.clone({ setHeaders: { 'X-Correlation-Id': crypto.randomUUID() } }));
```

```typescript
// shared/src/lib/api/interceptors/error.interceptor.ts
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);
  const router = inject(Router);
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      switch (err.status) {
        case 401:
          auth.clear();
          router.navigate(['/login']);
          break;
        case 403:
          router.navigate(['/403']);
          break;
        case 429: {
          const retryAfter = Number(err.headers.get('Retry-After') ?? 5);
          return timer(retryAfter * 1000).pipe(switchMap(() => next(req)));
        }
        default: {
          const problem = err.error as ProblemDetails;
          snackBar.open(problem?.detail ?? problem?.title ?? 'An error occurred', 'Dismiss', { duration: 5000 });
        }
      }
      return throwError(() => err);
    }),
  );
};
```

---

## Session Security

Customer web sessions are stored only in HttpOnly Secure SameSite cookies set by the backend. Browser JavaScript cannot read those cookies and must not store tenant JWTs in memory, `localStorage`, or `sessionStorage`.

```typescript
// shared/src/lib/auth/auth.service.ts (session refresh)
refreshSession(): Observable<SessionDto> {
  return this.http.post<SessionDto>('/api/v1/auth/refresh', {}).pipe(
    tap(session => {
      this.setSession(session.user, session.permissions, session.activeModules, session.activeFeatures);
    }),
  );
}
```

Non-browser clients (IDE extension, WorkPulse Agent, platform-admin server) use Bearer tokens per their own contracts.

---

## Environment Configuration

```typescript
// projects/customer-app/src/environments/environment.ts
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:5000',
  signalRUrl: 'http://localhost:5000/hubs',
};
```

```typescript
// projects/customer-app/src/app/app.config.ts
import { environment } from '../environments/environment';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([authInterceptor, tenantInterceptor, correlationInterceptor, errorInterceptor])),
    { provide: API_BASE_URL, useValue: environment.apiBaseUrl },
  ],
};
```

---

## Error Types

```typescript
// shared/src/lib/api/models/problem-details.model.ts
export interface ProblemDetails {
  type?: string;
  title: string;
  status: number;
  detail: string;
  errors?: Record<string, string[]>;
}

export interface PagedResult<T> {
  items: T[];
  nextCursor: string | null;
  hasMore: boolean;
}
```

---

## Pagination

Cursor-based only; never offset pagination for high-volume tenant data.

```typescript
// In a component using resource() with cursor pagination
export class EmployeeListComponent {
  private employeeService = inject(EmployeeApiService);

  filters = signal<EmployeeFilters>({ pageSize: 25, cursor: null });

  employeesResource = resource({
    request: () => this.filters(),
    loader: ({ request }) => firstValueFrom(this.employeeService.list(request)),
  });

  loadNextPage() {
    const cursor = this.employeesResource.value()?.nextCursor;
    if (cursor) {
      this.filters.update(f => ({ ...f, cursor }));
    }
  }
}
```

---

## Helper: `toHttpParams`

```typescript
// shared/src/lib/utils/to-params.ts
import { HttpParams } from '@angular/common/http';

export function toHttpParams(obj: Record<string, unknown>): HttpParams {
  let params = new HttpParams();
  for (const [key, value] of Object.entries(obj)) {
    if (value !== null && value !== undefined && value !== '') {
      params = params.set(key, String(value));
    }
  }
  return params;
}
```

---

## Related

- [[backend/api-conventions|API Conventions]] - backend API contract
- [[frontend/architecture/app-structure|App Structure]] - workspace structure
- [[frontend/data-layer/state-management|State Management]] - Angular Signals + resource()
- [[frontend/coding-standards|Coding Standards]] - Angular conventions
