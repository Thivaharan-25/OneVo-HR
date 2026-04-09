# State Management

## Three Types of State

| Type | Technology | Examples |
|:-----|:-----------|:--------|
| Server State | TanStack Query v5 | Employees, leave requests, activity data |
| Client State | Zustand | Sidebar open/closed, filter preferences, theme |
| URL State | nuqs | Page number, search query, date range, filters |

## TanStack Query Patterns

### Query Key Convention

```typescript
// [resource, ...params]
['employees']                          // all employees
['employees', { page: 1, dept: 'eng' }]  // filtered list
['employee', employeeId]              // single employee
['activity-summary', employeeId, date] // activity data
['exception-alerts', { status: 'new' }] // filtered alerts
```

### Stale Time by Data Type

| Data Type | Stale Time | Rationale |
|:----------|:-----------|:----------|
| Static data (countries, departments) | 5 min | Rarely changes |
| Employee list | 30s | Moderate change |
| Leave requests | 30s | Active workflow |
| Activity summaries | 60s | Aggregated data |
| Live workforce status | 0 (SignalR) | Real-time |
| Exception alerts | 0 (SignalR) | Real-time |

### Standard Hook Pattern

```typescript
// hooks/use-employees.ts
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData, // Smooth pagination
  });
}
```

## Zustand Stores

### Sidebar Store

```typescript
interface SidebarStore {
  isOpen: boolean;
  toggle: () => void;
  activeSection: string | null;
  setActiveSection: (section: string) => void;
}
```

### Filter Store

```typescript
// Persisted to localStorage
interface FilterStore {
  workforce: {
    department: string | null;
    dateRange: [Date, Date];
    status: string[];
  };
  setWorkforceFilters: (filters: Partial<WorkforceFilters>) => void;
  resetFilters: () => void;
}
```

### Auth Store

```typescript
interface AuthStore {
  user: User | null;
  permissions: string[];
  hasPermission: (permission: string) => boolean;
  setUser: (user: User, permissions: string[]) => void;
  clear: () => void;
}
```

## URL State (nuqs)

```typescript
// Used for: pagination, search, filters that should be shareable/bookmarkable
const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
const [search, setSearch] = useQueryState('q', parseAsString);
const [dateFrom, setDateFrom] = useQueryState('from', parseAsIsoDateTime);
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/data-layer/api-integration|API Integration]] — API integration patterns
- [[backend/real-time|Real-Time Architecture]] — real-time data via SignalR
- [[frontend/coding-standards|Frontend Coding Standards]] — coding conventions
