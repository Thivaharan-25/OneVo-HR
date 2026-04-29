# Caching Strategy

## TanStack Query Cache Rules

### Stale Time by Data Category

| Category | Stale Time | GC Time | Examples |
|:---------|:-----------|:--------|:---------|
| Reference data | 5 min | 30 min | Countries, currencies, departments, job families |
| Entity lists | 30s | 5 min | Employee list, leave requests, payroll runs |
| Entity detail | 60s | 10 min | Employee profile, review cycle detail |
| Aggregated data | 60s | 5 min | Activity summaries, report data |
| Live/real-time | 0s (SignalR) | 30s | Workforce live status, exception alerts |
| User session | Infinity | Infinity | Current user permissions, tenant config |
| Search results | 0s | 60s | Command palette, employee search |

### Query Key Structure

Hierarchical keys for targeted invalidation:

```typescript
// Convention: [domain, resource, ...params]
['employees']                                    // All employee queries
['employees', 'list', { page: 1, dept: 'eng' }] // Filtered list
['employees', 'detail', employeeId]              // Single employee
['employees', 'detail', employeeId, 'documents'] // Employee's documents

['leave', 'requests', { status: 'pending' }]    // Filtered leave list
['leave', 'balances', employeeId]                // Employee leave balance
['leave', 'calendar', { month: '2026-04' }]     // Calendar view

['workforce', 'live']                            // Live dashboard data
['workforce', 'activity', employeeId, date]      // Daily activity
['workforce', 'reports', reportType, dateRange]  // Report data

['exceptions', 'alerts', filters]                // Exception list
['exceptions', 'alert', alertId]                 // Single alert

['tenant', 'config']                             // Tenant settings
['tenant', 'features']                           // Feature flags
```

### Invalidation Patterns

```typescript
// Invalidate all employee queries (list + details)
queryClient.invalidateQueries({ queryKey: ['employees'] });

// Invalidate only the employee list (not individual details)
queryClient.invalidateQueries({ queryKey: ['employees', 'list'] });

// Invalidate a specific employee
queryClient.invalidateQueries({ queryKey: ['employees', 'detail', employeeId] });

// Invalidate everything for a domain
queryClient.invalidateQueries({ queryKey: ['leave'] });
```

## Optimistic Updates

Used for actions where the outcome is highly predictable and the user expects instant feedback.

### When to Use Optimistic Updates

| Action | Optimistic | Rationale |
|:-------|:-----------|:----------|
| Toggle status (acknowledge alert) | Yes | Binary toggle, almost never fails |
| Approve/reject leave | Yes | Clear outcome, undo available |
| Update employee field | Yes | Simple field change |
| Create employee | No | Complex validation, may fail server-side |
| Run payroll calculation | No | Long-running, needs server confirmation |
| Delete entity | No | Destructive, confirm first |

### Implementation Pattern

```typescript
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => api.exceptions.acknowledge(alertId),

    // Optimistic update
    onMutate: async (alertId) => {
      // Cancel in-flight fetches
      await queryClient.cancelQueries({ queryKey: ['exceptions', 'alerts'] });

      // Snapshot previous value for rollback
      const previousAlerts = queryClient.getQueryData(['exceptions', 'alerts']);

      // Optimistically update
      queryClient.setQueryData(['exceptions', 'alerts'], (old: AlertsResponse) => ({
        ...old,
        items: old.items.map(alert =>
          alert.id === alertId ? { ...alert, status: 'acknowledged' } : alert
        ),
      }));

      return { previousAlerts };
    },

    // Rollback on error
    onError: (err, alertId, context) => {
      queryClient.setQueryData(['exceptions', 'alerts'], context?.previousAlerts);
      toast.error('Failed to acknowledge alert');
    },

    // Refetch on settle (success or error) to ensure consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['exceptions', 'alerts'] });
    },
  });
}
```

## Prefetching

### Hover Prefetch

Prefetch data when user hovers over a navigation link:

```tsx
function EmployeeRow({ employee }: { employee: Employee }) {
  const queryClient = useQueryClient();

  return (
    <TableRow
      onMouseEnter={() => {
        queryClient.prefetchQuery({
          queryKey: ['employees', 'detail', employee.id],
          queryFn: () => api.employees.get(employee.id),
          staleTime: 30_000,
        });
      }}
      onClick={() => router.push(`/people/employees/${employee.id}`)}
    >
      ...
    </TableRow>
  );
}
```

### Route Prefetch

React Router does not automatically prefetch route data. Use TanStack Query for programmatic prefetch:

```tsx
// Prefetch next page of results
useEffect(() => {
  if (data?.hasMore) {
    queryClient.prefetchQuery({
      queryKey: ['employees', 'list', { ...filters, page: page + 1 }],
      queryFn: () => api.employees.list({ ...filters, page: page + 1 }),
    });
  }
}, [data, page]);
```

## Cache Persistence

### What's Persisted

Only non-sensitive, UI-preference data persists to localStorage:

| Data | Persisted | Storage |
|:-----|:----------|:--------|
| Sidebar state | Yes | Zustand + localStorage |
| Theme preference | Yes | Zustand/theme store + localStorage |
| Table column preferences | Yes | Zustand + localStorage |
| Filter preferences | Yes | Zustand + localStorage |
| TanStack Query cache | No | Memory only (security) |
| Auth tokens | HttpOnly cookie (refresh) / memory (access) | Cookie + memory |

### Why Not Persist Query Cache

Server data is **never** persisted to localStorage because:
- Multi-tenant: risk of cross-tenant data leakage on shared devices
- Stale data: employee/financial data must always be fresh
- Security: sensitive data (salaries, performance reviews) shouldn't be in localStorage

## Tenant-Scoped Cache

All query keys implicitly scope to the current tenant (set in the QueryClient default context):

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryKeyHashFn: (queryKey) => {
        // Prepend tenant ID to all cache keys
        return JSON.stringify([tenantId, ...queryKey]);
      },
    },
  },
});
```

This prevents cache pollution when a user switches tenants.

## Related

- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand patterns
- [[backend/real-time|Real-Time Architecture]] — SignalR cache invalidation
- [[frontend/data-layer/api-integration|Api Integration]] — API client
- [[frontend/architecture/overview|Overview]] — data ownership principle
