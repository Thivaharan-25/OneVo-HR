# State Management

## Three Types of State

| Type | Technology | Examples |
|:-----|:-----------|:--------|
| Server State | TanStack Query v5 | Employees, leave requests, activity data |
| Client State | Zustand | Sidebar open/closed, filter preferences, theme |
| URL State | React Router `useSearchParams` | Page number, search query, date range, filters |

> **Note:** `nuqs` is a Next.js-only library and must NOT be used here. This project runs on Vite + React Router v7. All URL state uses React Router's built-in `useSearchParams`.

---

## TanStack Query Patterns

### Query Key Convention

```typescript
// [resource, ...params]
['employees']                            // all employees
['employees', { page: 1, dept: 'eng' }] // filtered list
['employee', employeeId]                 // single employee
['activity-summary', employeeId, date]  // activity data
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
// hooks/hr/use-employees.ts
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData, // smooth pagination
  });
}
```

---

## Zustand Stores

### Auth Store

```typescript
// stores/use-auth-store.ts
interface AuthStore {
  user: User | null;
  activeEntityId: string | null;
  permissions: string[];
  hasPermission: (permission: string) => boolean;
  setUser: (user: User, entityId: string, permissions: string[]) => void;
  clear: () => void;
}
```

### Sidebar Store

```typescript
// stores/use-sidebar-store.ts
interface SidebarStore {
  isExpanded: boolean;
  activePillar: string | null;
  toggle: () => void;
  setActivePillar: (pillar: string | null) => void;
}
```

### Filter Store

```typescript
// stores/use-filter-store.ts — persisted to localStorage
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

### Theme Store

```typescript
// stores/use-theme-store.ts — persisted to localStorage
interface ThemeStore {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}
```

---

## URL State (React Router useSearchParams)

Use for any state that should be bookmarkable or shareable: pagination, search, filters, date ranges.

```typescript
import { useSearchParams } from 'react-router-dom';

function EmployeesPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read
  const page   = Number(searchParams.get('page') ?? '1');
  const search = searchParams.get('q') ?? '';
  const dept   = searchParams.get('dept') ?? '';

  // Write — always spread prev to preserve other params
  const setPage = (p: number) =>
    setSearchParams(prev => { prev.set('page', String(p)); return prev; });

  const setSearch = (q: string) =>
    setSearchParams(prev => { prev.set('q', q); prev.delete('page'); return prev; });

  const setDept = (d: string) =>
    setSearchParams(prev => { prev.set('dept', d); prev.delete('page'); return prev; });
}
```

**When to use URL state vs Zustand:**

| Scenario | Use |
|---|---|
| Filter that should survive page refresh or be shareable | `useSearchParams` |
| UI-only state (sidebar open, modal open) | Zustand |
| User preference persisted across sessions | Zustand (with `persist` middleware) |

---

## Related

- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/data-layer/api-integration|API Integration]] — API integration patterns
- [[frontend/data-layer/real-time|Real-Time Architecture]] — real-time data via SignalR
- [[frontend/coding-standards|Frontend Coding Standards]] — coding conventions
