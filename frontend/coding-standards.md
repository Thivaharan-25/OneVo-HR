# Frontend Coding Standards

## Project Structure

This project runs on **Vite + React 19 + React Router v7**. It is not a Next.js app. There is no `app/` directory with file-based routing — routes are defined in `src/router.tsx`.

```
src/
├── main.tsx                # Entry point — mounts App into #root
├── App.tsx                 # Provider stack + RouterProvider
├── router.tsx              # React Router v7 full route config (all routes defined here)
│
├── pages/                  # Page components — thin, import features, pass data down
│   ├── auth/               # AuthLayout + Login, ForgotPassword, ResetPassword, Mfa
│   ├── dashboard/          # DashboardLayout + all authenticated pages (mirrors route tree)
│   └── errors/             # NotFoundPage, ErrorPage, ForbiddenPage
│
├── components/
│   ├── ui/                 # shadcn/ui primitives (auto-generated, never edit)
│   ├── shared/             # Cross-module: DataTable, PageHeader, StatusBadge, PermissionGate,
│   │                       #   EmptyState, TableSkeleton, ErrorState, Avatar
│   ├── layout/             # Shell: NavRail, ExpansionPanel, Topbar, EntitySwitcher, Breadcrumb
│   ├── hr/                 # Core HR feature components
│   ├── leave/              # Leave management components
│   ├── workforce/          # Workforce Intelligence (presence, activity, identity verification)
│   ├── exceptions/         # Exception Engine components
│   ├── org/                # Org Structure components
│   ├── calendar/           # Calendar, schedule, attendance components
│   ├── admin/              # Admin panel components
│   ├── settings/           # Settings components
│   ├── wms/                # WMS components (projects, tasks, planner, goals, docs, time, chat)
│   ├── performance/        # Phase 2
│   ├── payroll/            # Phase 2
│   ├── grievance/          # Phase 2
│   └── expense/            # Phase 2
│
├── hooks/
│   ├── hr/                 # use-employees, use-leave, use-org
│   ├── workforce/          # use-presence, use-activity, use-exceptions
│   ├── wms/                # use-projects, use-tasks, use-goals, use-docs, use-time, use-chat
│   ├── admin/              # use-agents, use-audit
│   └── shared/             # use-debounce, use-permissions
│
├── lib/
│   ├── api/
│   │   ├── client.ts       # ApiClient class — runs requests through interceptor pipeline
│   │   ├── index.ts        # Composed api object (api.employees, api.wms.projects, etc.)
│   │   ├── errors.ts       # ApiError, AuthError, ProblemDetails, PagedResult
│   │   └── interceptors/
│   │       ├── auth.interceptor.ts        # Attach Bearer token, proactive refresh
│   │       ├── tenant.interceptor.ts      # Attach X-Entity-Id header
│   │       ├── correlation.interceptor.ts # X-Correlation-Id per request
│   │       └── error.interceptor.ts       # 401/403/429/5xx global handling
│   ├── security/
│   │   ├── token-manager.ts   # In-memory access token (never localStorage)
│   │   ├── idle-timeout.ts    # Auto logout after N minutes inactivity
│   │   ├── sanitizer.ts       # DOMPurify wrapper — use before rendering any user HTML
│   │   └── permission-guard.tsx # Route-level guard (redirects, not just hides)
│   ├── signalr/
│   │   └── client.ts          # SignalR connection manager
│   └── utils/
│       ├── cn.ts              # shadcn/ui class merger
│       ├── format-date.ts     # Date formatting helpers
│       └── to-params.ts       # URLSearchParams builder for query strings
│
├── stores/                 # Zustand stores — one store per file, named use-*-store.ts
│   ├── use-auth-store.ts
│   ├── use-sidebar-store.ts
│   ├── use-filter-store.ts
│   └── use-theme-store.ts
│
├── types/                  # TypeScript interfaces mirroring backend DTOs
│   ├── auth.ts
│   ├── core-hr.ts
│   ├── org.ts
│   ├── workforce.ts
│   ├── notifications.ts
│   ├── settings.ts
│   ├── admin.ts
│   └── wms/
│       ├── projects.ts
│       ├── tasks.ts
│       ├── goals.ts
│       └── chat.ts
│
└── styles/
    ├── globals.css         # Tailwind directives + resets
    └── tokens.css          # CSS custom properties (color tokens, spacing, typography)
```

## File Organization Rules

1. **Page files (`pages/`)** should be thin — import components, pass data down
2. **Feature components** follow a three-tier promotion path:
   - Route-exclusive → colocated near the route page under `pages/.../components/`
   - Module-shared (2+ pages in same module) → promoted to `components/{module}/` (delete colocated copy)
   - Cross-module → promoted to `components/shared/` (delete module copy)
3. **One component per file** (except small private helpers used only in that file)
4. **One hook per file** in `hooks/{module}/` — named `use-{resource}.ts` (e.g., `hooks/hr/use-employees.ts`, `hooks/wms/use-projects.ts`)
5. **One store per file** in `stores/` — named `use-{name}-store.ts`
6. **Types** mirroring a backend DTO go in `types/{module}.ts`
7. **Route-local types** (form schemas, column defs, local UI state) go in `_types.ts` colocated in the route folder — never API response shapes there

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

- **API errors:** Handled globally by ApiClient error interceptor → toast notification
- **Component errors:** Use React Error Boundaries around feature sections
- **Permission errors:** Redirect to 403 page via PermissionGate fallback
- **Network errors:** Show retry button, not just error message

## Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML (`<nav>`, `<main>`, `<aside>`, `<table>`)
- Color is never the only indicator — use icons + text alongside color
- shadcn/ui components handle most a11y patterns (focus traps, ARIA)

## Performance

- **Lazy load** heavy components (charts, kanban boards, org charts) with `React.lazy()` + `<Suspense>` — never `next/dynamic()` (that is a Next.js API)
- **Paginate** all lists — never load unbounded data
- **Debounce** search inputs (300ms)
- **Prefetch** on hover for navigation links with TanStack Query or route-level lazy imports
- **Image optimization** via responsive image markup or the project image component; do not use Next.js `Image`

## Related

- [[frontend/architecture/app-structure|App Structure]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
- [[AI_CONTEXT/rules|Rules]]
