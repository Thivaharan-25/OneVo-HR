# Frontend Coding Standards

## Project Structure

This project runs on **Vite + React 19 + React Router v7**. It is not a Next.js app. There is no `app/` directory with file-based routing â€” routes are defined in `src/router.tsx`.

```
src/
â”œâ”€â”€ main.tsx                # Entry point â€” mounts App into #root
â”œâ”€â”€ App.tsx                 # Provider stack + RouterProvider
â”œâ”€â”€ router.tsx              # React Router v7 full route config (all routes defined here)
â”‚
â”œâ”€â”€ pages/                  # Page components â€” thin, import features, pass data down
â”‚   â”œâ”€â”€ auth/               # AuthLayout + Login, ForgotPassword, ResetPassword, Mfa
â”‚   â”œâ”€â”€ dashboard/          # DashboardLayout + all authenticated pages (mirrors route tree)
â”‚   â””â”€â”€ errors/             # NotFoundPage, ErrorPage, ForbiddenPage
â”‚
â”œâ”€â”€ components/
â”‚   â”œâ”€â”€ ui/                 # shadcn/ui primitives (auto-generated, never edit)
â”‚   â”œâ”€â”€ shared/             # Cross-module: DataTable, PageHeader, StatusBadge, PermissionGate,
â”‚   â”‚                       #   EmptyState, TableSkeleton, ErrorState, Avatar
â”‚   â”œâ”€â”€ layout/             # Shell: NavRail, ExpansionPanel, Topbar, EntitySwitcher, Breadcrumb
â”‚   â”œâ”€â”€ hr/                 # Core HR feature components
â”‚   â”œâ”€â”€ leave/              # Leave management components
â”‚   â”œâ”€â”€ workforce/          # Workforce Intelligence (presence, activity, identity verification)
â”‚   â”œâ”€â”€ exceptions/         # Exception Engine components
â”‚   â”œâ”€â”€ org/                # Org Structure components
â”‚   â”œâ”€â”€ calendar/           # Calendar, schedule, attendance components
â”‚   â”œâ”€â”€ admin/              # Admin panel components
â”‚   â”œâ”€â”€ settings/           # Settings components
â”‚   â”œâ”€â”€ wms/                # WMS components (projects, tasks, planner, goals, docs, time, chat)
â”‚   â”œâ”€â”€ performance/        # Phase 2
â”‚   â”œâ”€â”€ payroll/            # Phase 2
â”‚   â”œâ”€â”€ grievance/          # Phase 2
â”‚   â””â”€â”€ expense/            # Phase 2
â”‚
â”œâ”€â”€ hooks/
â”‚   â”œâ”€â”€ hr/                 # use-employees, use-leave, use-org
â”‚   â”œâ”€â”€ workforce/          # use-presence, use-activity, use-exceptions
â”‚   â”œâ”€â”€ wms/                # use-projects, use-tasks, use-goals, use-docs, use-time, use-chat
â”‚   â”œâ”€â”€ admin/              # use-agents, use-audit
â”‚   â””â”€â”€ shared/             # use-debounce, use-permissions
â”‚
â”œâ”€â”€ lib/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ client.ts       # ApiClient class â€” runs requests through interceptor pipeline
â”‚   â”‚   â”œâ”€â”€ index.ts        # Composed api object (api.employees, api.wms.projects, etc.)
â”‚   â”‚   â”œâ”€â”€ errors.ts       # ApiError, AuthError, ProblemDetails, PagedResult
â”‚   â”‚   â””â”€â”€ interceptors/
â”‚   â”‚       â”œâ”€â”€ session.interceptor.ts     # Cookie-backed session refresh
â”‚   â”‚       â”œâ”€â”€ tenant.interceptor.ts      # Attach X-Entity-Id header
â”‚   â”‚       â”œâ”€â”€ correlation.interceptor.ts # X-Correlation-Id per request
â”‚   â”‚       â””â”€â”€ error.interceptor.ts       # 401/403/429/5xx global handling
â”‚   â”œâ”€â”€ security/
â”‚   â”‚   â”œâ”€â”€ csrf.ts            # CSRF header helper for cookie-authenticated mutations
â”‚   â”‚   â”œâ”€â”€ idle-timeout.ts    # Auto logout after N minutes inactivity
â”‚   â”‚   â”œâ”€â”€ sanitizer.ts       # DOMPurify wrapper â€” use before rendering any user HTML
â”‚   â”‚   â””â”€â”€ permission-guard.tsx # Route-level guard (redirects, not just hides)
â”‚   â”œâ”€â”€ signalr/
â”‚   â”‚   â””â”€â”€ client.ts          # SignalR connection manager
â”‚   â””â”€â”€ utils/
â”‚       â”œâ”€â”€ cn.ts              # shadcn/ui class merger
â”‚       â”œâ”€â”€ format-date.ts     # Date formatting helpers
â”‚       â””â”€â”€ to-params.ts       # URLSearchParams builder for query strings
â”‚
â”œâ”€â”€ stores/                 # Zustand stores â€” one store per file, named use-*-store.ts
â”‚   â”œâ”€â”€ use-auth-store.ts
â”‚   â”œâ”€â”€ use-sidebar-store.ts
â”‚   â”œâ”€â”€ use-filter-store.ts
â”‚   â””â”€â”€ use-theme-store.ts
â”‚
â”œâ”€â”€ types/                  # TypeScript interfaces mirroring backend DTOs
â”‚   â”œâ”€â”€ auth.ts
â”‚   â”œâ”€â”€ core-hr.ts
â”‚   â”œâ”€â”€ org.ts
â”‚   â”œâ”€â”€ workforce.ts
â”‚   â”œâ”€â”€ notifications.ts
â”‚   â”œâ”€â”€ settings.ts
â”‚   â”œâ”€â”€ admin.ts
â”‚   â””â”€â”€ wms/
â”‚       â”œâ”€â”€ projects.ts
â”‚       â”œâ”€â”€ tasks.ts
â”‚       â”œâ”€â”€ goals.ts
â”‚       â””â”€â”€ chat.ts
â”‚
â””â”€â”€ styles/
    â”œâ”€â”€ globals.css         # Tailwind directives + resets
    â””â”€â”€ tokens.css          # CSS custom properties (color tokens, spacing, typography)
```

## File Organization Rules

1. **Page files (`pages/`)** should be thin â€” import components, pass data down
2. **Feature components** follow a three-tier promotion path:
   - Route-exclusive â†’ colocated near the route page under `pages/.../components/`
   - Module-shared (2+ pages in same module) â†’ promoted to `components/{module}/` (delete colocated copy)
   - Cross-module â†’ promoted to `components/shared/` (delete module copy)
3. **One component per file** (except small private helpers used only in that file)
4. **One hook per file** in `hooks/{module}/` â€” named `use-{resource}.ts` (e.g., `hooks/hr/use-employees.ts`, `hooks/wms/use-projects.ts`)
5. **One store per file** in `stores/` â€” named `use-{name}-store.ts`
6. **Types** mirroring a backend DTO go in `types/{module}.ts`
7. **Route-local types** (form schemas, column defs, local UI state) go in `_types.ts` colocated in the route folder â€” never API response shapes there

## Component Template

```tsx`r`nimport { useState } from 'react';
import { useEmployees } from '@/hooks/use-employees';
import { DataTable } from '@/components/shared/data-table';
import { PermissionGate } from '@/components/shared/permission-gate';

interface EmployeeListProps {
  departmentId?: string;
}

export function EmployeeList({ departmentId }: EmployeeListProps) {
  const [searchParams, setSearchParams] = useSearchParams();`r`n  const search = searchParams.get('search') ?? '';
  const { data, isLoading, error } = useEmployees({ departmentId, search });

  if (isLoading) return <TableSkeleton rows={10} />;
  if (error) return <ErrorState message="Failed to load employees" retry />;
  if (!data?.items.length) return <EmptyState title="No employees found" />;

  return (
    <DataTable
      data={data.items}
      columns={columns}
      pagination={data.pagination}
    />
  );
}
```

## API Hook Template

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { Employee, EmployeeFilters } from '@/types/core-hr';

export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
    staleTime: 30_000,
  });
}

export function useCreateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateEmployeeInput) => api.employees.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });
}
```

## Import Order

```tsx
// 1. React and routing
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// 2. Third-party libraries
import { useQuery } from '@tanstack/react-query';
import { z } from 'zod';

// 3. Internal shared components
import { Button } from '@/components/ui/button';
import { DataTable } from '@/components/shared/data-table';

// 4. Feature components (same pillar)
import { ActivityTimeline } from '@/components/workforce/activity-timeline';

// 5. Hooks, stores, utils
import { useEmployees } from '@/hooks/use-employees';
import { formatDate } from '@/lib/utils/format-date';

// 6. Types
import type { Employee } from '@/types/core-hr';
```

## Error Handling

- **API errors:** Handled globally by ApiClient error interceptor â†’ toast notification
- **Component errors:** Use React Error Boundaries around feature sections
- **Permission errors:** Redirect to 403 page via PermissionGate fallback
- **Network errors:** Show retry button, not just error message

## Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML (`<nav>`, `<main>`, `<aside>`, `<table>`)
- Color is never the only indicator â€” use icons + text alongside color
- shadcn/ui components handle most a11y patterns (focus traps, ARIA)

## Performance

- **Lazy load** heavy components (charts, kanban boards, org charts) with `React.lazy()` + `<Suspense>` â€” never `next/dynamic()` (that is a Next.js API)
- **Paginate** all lists â€” never load unbounded data
- **Debounce** search inputs (300ms)
- **Prefetch** on hover for navigation links with TanStack Query or route-level lazy imports
- **Image optimization** via responsive image markup or the project image component; do not use Next.js `Image`

## Related

- [[frontend/architecture/app-structure|App Structure]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
- [[AI_CONTEXT/rules|Rules]]

