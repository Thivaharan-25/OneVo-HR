# API Integration

## API Client

The ApiClient is a thin class that runs every request through an ordered interceptor pipeline. It uses `import.meta.env.VITE_API_URL`; this project uses Vite, not Next.js.

Customer web API calls use a BFF-style HttpOnly cookie session. The browser frontend does not attach tenant JWTs to normal `/api/v1/*` requests.

```typescript
// lib/api/client.ts
import { sessionInterceptor } from './interceptors/session.interceptor';
import { tenantInterceptor } from './interceptors/tenant.interceptor';
import { correlationInterceptor } from './interceptors/correlation.interceptor';
import { csrfInterceptor } from './interceptors/csrf.interceptor';
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
      credentials: 'include',
    });

    request = await sessionInterceptor.onRequest(request);
    request = tenantInterceptor.onRequest(request);
    request = csrfInterceptor.onRequest(request);
    request = correlationInterceptor.onRequest(request);

    const response = await fetch(request);

    return errorInterceptor.onResponse<T>(response, () => this.fetch(path, options));
  }
}

export const apiClient = new ApiClient();
```

---

## Interceptors

Interceptors are located in `lib/api/interceptors/`.

```typescript
// lib/api/interceptors/session.interceptor.ts
import { refreshSessionIfNeeded } from '@/lib/api/endpoints/auth';

export const sessionInterceptor = {
  async onRequest(request: Request): Promise<Request> {
    // Browser authentication is cookie-based. Do not attach
    // Authorization: Bearer for customer web calls.
    await refreshSessionIfNeeded();
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
// lib/api/interceptors/csrf.interceptor.ts
import { getCsrfToken } from '@/lib/security/csrf';

export const csrfInterceptor = {
  onRequest(request: Request): Request {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      request.headers.set('X-CSRF-Token', getCsrfToken());
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
import { useAuthStore } from '@/stores/use-auth-store';
import { ApiError, AuthError } from '@/lib/api/errors';
import { toast } from 'sonner';

export const errorInterceptor = {
  async onResponse<T>(response: Response, retry: () => Promise<T>): Promise<T> {
    if (response.ok) return response.json();

    switch (response.status) {
      case 401:
        useAuthStore.getState().clear();
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

## Session Security

Customer web sessions are stored only in HttpOnly Secure SameSite cookies set by the backend. Browser JavaScript cannot read those cookies and must not store tenant JWTs in memory, `localStorage`, or `sessionStorage`.

```typescript
// lib/api/endpoints/auth.ts
export async function refreshSession(): Promise<SessionDto | null> {
  const response = await apiClient.fetch<SessionDto>('/api/v1/auth/refresh', {
    method: 'POST',
  });

  useAuthStore.getState().setSession(
    response.user,
    response.permissions,
    response.active_modules,
  );

  return response;
}
```

Non-browser clients such as the IDE extension, desktop agent, and platform-admin server internals may still use Bearer tokens where their own contracts say so.

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

---

## Error Types

```typescript
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

Cursor-based only; never offset pagination for high-volume tenant data.

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

## Related

- [[backend/api-conventions|Api Conventions]] - backend API conventions
- [[frontend/architecture/app-structure|App Structure]] - frontend architecture
- [[frontend/data-layer/state-management|State Management]] - state management patterns
- [[frontend/coding-standards|Frontend Coding Standards]] - coding standards
