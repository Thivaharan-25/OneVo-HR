# API Integration

## API Client

The ApiClient is a thin class that runs every request through an ordered interceptor pipeline. Uses `import.meta.env.VITE_API_URL` — **not** `process.env.NEXT_PUBLIC_API_URL` (that is a Next.js prefix; this project uses Vite).

```typescript
// lib/api/client.ts
import { authInterceptor } from './interceptors/auth.interceptor';
import { tenantInterceptor } from './interceptors/tenant.interceptor';
import { correlationInterceptor } from './interceptors/correlation.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';

class ApiClient {
  private baseUrl = import.meta.env.VITE_API_URL;

  async fetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    let request = new Request(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // httpOnly refresh token cookie
    });

    // Request interceptors (order matters)
    request = await authInterceptor.onRequest(request);
    request = await tenantInterceptor.onRequest(request);
    request = await correlationInterceptor.onRequest(request);

    const response = await fetch(request);

    // Response interceptor handles 401/403/429/5xx
    return errorInterceptor.onResponse<T>(response, () => this.fetch(path, options));
  }
}

export const apiClient = new ApiClient();
```

---

## Interceptors

Four interceptors, each with a single responsibility. Located in `lib/api/interceptors/`.

```typescript
// lib/api/interceptors/auth.interceptor.ts
import { tokenManager } from '@/lib/security/token-manager';
import { refreshAccessToken } from '@/lib/api/endpoints/auth';

export const authInterceptor = {
  async onRequest(request: Request): Promise<Request> {
    // Proactive refresh — don't wait for a 401 failure
    if (tokenManager.isExpiringSoon()) {
      await refreshAccessToken();
    }
    const token = tokenManager.get();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};
```

```typescript
// lib/api/interceptors/tenant.interceptor.ts
import { useAuthStore } from '@/stores/use-auth-store';

export const tenantInterceptor = {
  onRequest(request: Request): Request {
    const entityId = useAuthStore.getState().activeEntityId;
    if (entityId) {
      request.headers.set('X-Entity-Id', entityId);
    }
    return request;
  },
};
```

```typescript
// lib/api/interceptors/correlation.interceptor.ts
export const correlationInterceptor = {
  onRequest(request: Request): Request {
    request.headers.set('X-Correlation-Id', crypto.randomUUID());
    return request;
  },
};
```

```typescript
// lib/api/interceptors/error.interceptor.ts
import { tokenManager } from '@/lib/security/token-manager';
import { ApiError, AuthError } from '@/lib/api/errors';
import { toast } from 'sonner';

export const errorInterceptor = {
  async onResponse<T>(response: Response, retry: () => Promise<T>): Promise<T> {
    if (response.ok) return response.json();

    switch (response.status) {
      case 401:
        tokenManager.clear();
        window.location.href = '/login';
        throw new AuthError('Session expired');

      case 403:
        window.location.href = '/403';
        throw new ApiError({ status: 403, title: 'Forbidden', detail: 'Access denied' });

      case 429: {
        const retryAfter = Number(response.headers.get('Retry-After') ?? 5);
        await new Promise(r => setTimeout(r, retryAfter * 1000));
        return retry();
      }

      default: {
        const problem = await response.json();
        toast.error(problem.detail ?? problem.title ?? 'An error occurred');
        throw new ApiError(problem);
      }
    }
  },
};
```

---

## Token Security

Access tokens are stored **in-memory only** — never in `localStorage` or `sessionStorage`. This prevents XSS from stealing tokens. Refresh tokens live in an `httpOnly` cookie set by the backend — JavaScript cannot read them.

```typescript
// lib/security/token-manager.ts
let _accessToken: string | null = null;
let _expiresAt: number | null = null;

export const tokenManager = {
  set(token: string, expirySeconds: number): void {
    _accessToken = token;
    _expiresAt = Date.now() + expirySeconds * 1000;
  },
  get(): string | null {
    return _accessToken;
  },
  isExpiringSoon(): boolean {
    return _expiresAt !== null && Date.now() > _expiresAt - 60_000;
  },
  clear(): void {
    _accessToken = null;
    _expiresAt = null;
  },
};
```

---

## Endpoint Organization

One file per module under `lib/api/endpoints/`. Each exports a typed object that calls `apiClient.fetch`.

```typescript
// lib/api/endpoints/employees.ts
import { apiClient } from '@/lib/api/client';
import type { Employee, EmployeeFilters, CreateEmployeeDto } from '@/types/core-hr';
import type { PagedResult } from '@/lib/api/errors';
import { toParams } from '@/lib/utils/to-params';

export const employeesApi = {
  list: (filters: EmployeeFilters) =>
    apiClient.fetch<PagedResult<Employee>>(`/api/v1/employees?${toParams(filters)}`),

  get: (id: string) =>
    apiClient.fetch<Employee>(`/api/v1/employees/${id}`),

  create: (data: CreateEmployeeDto) =>
    apiClient.fetch<Employee>('/api/v1/employees', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Partial<CreateEmployeeDto>) =>
    apiClient.fetch<Employee>(`/api/v1/employees/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};
```

```typescript
// lib/api/index.ts — single composed api object used everywhere
import { authApi }          from './endpoints/auth';
import { employeesApi }     from './endpoints/employees';
import { leaveApi }         from './endpoints/leave';
import { orgApi }           from './endpoints/org';
import { workforceApi }     from './endpoints/workforce';
import { calendarApi }      from './endpoints/calendar';
import { notificationsApi } from './endpoints/notifications';
import { settingsApi }      from './endpoints/settings';
import { adminApi }         from './endpoints/admin';
import { agentsApi }        from './endpoints/agents';
import { identityApi }      from './endpoints/identity';
import { projectsApi }      from './endpoints/wms/projects';
import { tasksApi }         from './endpoints/wms/tasks';
import { plannerApi }       from './endpoints/wms/planner';
import { goalsApi }         from './endpoints/wms/goals';
import { docsApi }          from './endpoints/wms/docs';
import { timeApi }          from './endpoints/wms/time';
import { chatApi }          from './endpoints/wms/chat';

export const api = {
  auth:          authApi,
  employees:     employeesApi,
  leave:         leaveApi,
  org:           orgApi,
  workforce:     workforceApi,
  calendar:      calendarApi,
  notifications: notificationsApi,
  settings:      settingsApi,
  admin:         adminApi,
  agents:        agentsApi,
  identity:      identityApi,
  wms: {
    projects: projectsApi,
    tasks:    tasksApi,
    planner:  plannerApi,
    goals:    goalsApi,
    docs:     docsApi,
    time:     timeApi,
    chat:     chatApi,
  },
};
```

---

## Error Types

```typescript
// lib/api/errors.ts
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

export class ApiError extends Error {
  constructor(public problem: ProblemDetails) {
    super(problem.detail ?? problem.title);
  }
}

export class AuthError extends Error {}
```

---

## Pagination

Cursor-based only — never offset pagination.

```typescript
export function useEmployeesInfinite(filters: EmployeeFilters) {
  return useInfiniteQuery({
    queryKey: ['employees', 'infinite', filters],
    queryFn: ({ pageParam }) =>
      api.employees.list({ ...filters, cursor: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: undefined as string | undefined,
  });
}
```

---

## Global Query Config

```typescript
// App.tsx — TanStack Query client config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error instanceof AuthError) return false;
        return failureCount < 3;
      },
    },
  },
});
```

---

## Related

- [[backend/api-conventions|Api Conventions]] — backend API conventions
- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/data-layer/state-management|State Management]] — state management patterns
- [[frontend/coding-standards|Frontend Coding Standards]] — coding standards
