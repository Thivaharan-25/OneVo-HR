# Frontend Development Rules

## 1. File & Component Conventions

### Naming
| Element | Convention | Example |
|:--------|:-----------|:--------|
| Files (components) | `kebab-case.tsx` | `employee-list.tsx`, `live-dashboard.tsx` |
| Files (utilities) | `kebab-case.ts` | `use-employees.ts`, `format-date.ts` |
| Components | `PascalCase` | `EmployeeList`, `LiveDashboard` |
| Hooks | `useCamelCase` | `useEmployees`, `useSignalR` |
| Stores (Zustand) | `useCamelCaseStore` | `useSidebarStore`, `useFilterStore` |
| Types/Interfaces | `PascalCase` | `Employee`, `LeaveRequest`, `ActivitySnapshot` |
| API query keys | `['resource', params]` | `['employees', { page: 1 }]` |
| Route segments | `kebab-case` | `/workforce/live`, `/hr/employees` |

### Directory Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/             # Auth layout group
│   ├── (dashboard)/        # Dashboard layout group
│   └── layout.tsx          # Root layout
├── components/
│   ├── ui/                 # shadcn/ui primitives (Button, Dialog, etc.)
│   ├── shared/             # Shared composed components (DataTable, PageHeader)
│   ├── hr/                 # Pillar 1 components
│   ├── workforce/          # Pillar 2 components
│   └── layout/             # Sidebar, Topbar, Breadcrumbs
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities, API client, constants
│   ├── api/                # API client + endpoint definitions
│   ├── signalr/            # SignalR connection manager
│   └── utils/              # Formatting, validation helpers
├── stores/                 # Zustand stores
├── types/                  # TypeScript types (mirroring backend DTOs)
└── styles/                 # Global CSS, Tailwind config
```

## 2. Component Patterns

### Server vs Client Components
- **Default to Client Components** — most dashboard pages need interactivity
- **Use Server Components for:** Static pages, initial data fetch, layout wrappers
- **"use client" directive** at the top of interactive components

### Permission Gating

```tsx
// Always gate features by permission
<PermissionGate permission="workforce:view">
  <WorkforceDashboard />
</PermissionGate>

// For conditional rendering within a component
const { hasPermission } = useAuth();
if (!hasPermission('exceptions:manage')) return null;
```

### Data Fetching (TanStack Query)

```tsx
// Standard pattern for data fetching
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
    staleTime: 30_000, // 30 seconds
  });
}

// Mutation with optimistic update
export function useApproveLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.leave.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
    },
  });
}
```

### Form Pattern

```tsx
const schema = z.object({
  firstName: z.string().min(1).max(100),
  email: z.string().email(),
});

type FormData = z.infer<typeof schema>;

export function CreateEmployeeForm() {
  const form = useForm<FormData>({ resolver: zodResolver(schema) });
  const mutation = useCreateEmployee();
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(data => mutation.mutate(data))}>
        {/* fields */}
      </form>
    </Form>
  );
}
```

## 3. API Integration Rules

- **All API calls go through the typed API client** — never raw `fetch()`
- **Use TanStack Query for ALL data fetching** — no `useEffect` + `useState` for API calls
- **Handle loading, error, empty states** for every data-fetching component
- **Pagination via nuqs** — page/cursor in URL params
- **Error display:** RFC 7807 Problem Details → user-friendly error toast

## 4. Real-time Rules

- **SignalR for:** workforce-live, exception-alerts, notifications, agent-status
- **Polling fallback:** 30s polling if SignalR connection fails
- **Reconnection:** Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- **Stale data indicator:** Show "Last updated X seconds ago" on live dashboards

## 5. Styling Rules

- **Tailwind utilities first** — avoid custom CSS unless absolutely necessary
- **shadcn/ui for all base components** — don't build custom buttons, dialogs, etc.
- **CSS Custom Properties for theming** — light/dark mode, tenant brand colors
- **Responsive:** Desktop-first, but all pages must be usable on tablet (≥768px)
- **No inline styles** — use Tailwind classes or CSS modules

## 6. Testing Rules

- **Vitest for hooks and utilities** — pure logic tests
- **React Testing Library for components** — test behavior, not implementation
- **Playwright for critical E2E flows** — login, leave request, exception management
- **MSW for API mocking** — realistic API responses in tests
- **No snapshot tests** — they break on every UI change

## 7. Security Rules

- **Never store JWT in localStorage** — access token in memory, refresh in HttpOnly cookie
- **Sanitize all user-generated content** before rendering (XSS prevention)
- **RBAC check on every route** — redirect to 403 if unauthorized
- **No sensitive data in URL params** — employee IDs are OK, PII is not
- **CSP headers** configured in Next.js middleware
