# API Integration

## API Client

```typescript
// lib/api/client.ts
import { getAccessToken, refreshToken } from '@/lib/auth';

class ApiClient {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL;

  async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const token = getAccessToken();
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        'X-Correlation-Id': crypto.randomUUID(),
        ...options?.headers,
      },
      credentials: 'include', // Include refresh token cookie
    });

    if (response.status === 401) {
      // Try refresh
      const refreshed = await refreshToken();
      if (refreshed) return this.fetch<T>(path, options);
      throw new AuthError('Session expired');
    }

    if (!response.ok) {
      const problem = await response.json() as ProblemDetails;
      throw new ApiError(problem);
    }

    return response.json();
  }
}

export const api = new ApiClient();
```

## Endpoint Organization

```typescript
// lib/api/endpoints/employees.ts
export const employeesApi = {
  list: (filters: EmployeeFilters) =>
    api.fetch<PagedResult<Employee>>(`/api/v1/employees?${toParams(filters)}`),
  
  get: (id: string) =>
    api.fetch<Employee>(`/api/v1/employees/${id}`),
  
  create: (data: CreateEmployeeDto) =>
    api.fetch<Employee>('/api/v1/employees', { method: 'POST', body: JSON.stringify(data) }),
};

// lib/api/endpoints/workforce.ts
export const workforceApi = {
  liveStatus: () =>
    api.fetch<WorkforceStatus>('/api/v1/workforce/presence/live'),
  
  activitySummary: (employeeId: string, date: string) =>
    api.fetch<ActivityDailySummary>(`/api/v1/activity/summary/${employeeId}?date=${date}`),
  
  exceptions: (filters: ExceptionFilters) =>
    api.fetch<PagedResult<ExceptionAlert>>(`/api/v1/exceptions/alerts?${toParams(filters)}`),
};
```

## Error Handling

```typescript
// RFC 7807 Problem Details
interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  errors?: Record<string, string[]>; // Validation errors
}

// Global error handler in TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error instanceof AuthError) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      onError: (error) => {
        if (error instanceof ApiError) {
          toast.error(error.problem.detail || error.problem.title);
        }
      },
    },
  },
});
```

## Pagination

```typescript
// Cursor-based pagination
interface PagedResult<T> {
  items: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

// Usage with TanStack Query infinite query
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

## Related

- [[backend/api-conventions|Api Conventions]] — backend API conventions
- [[security/auth-flow|Auth Flow]] — authentication flow
- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/data-layer/state-management|State Management]] — state management patterns
- [[frontend/coding-standards|Frontend Coding Standards]] — coding standards
