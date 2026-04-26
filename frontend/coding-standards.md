# Frontend Coding Standards

## Project Structure

```
src/
├── app/                    # Next.js App Router (pages + layouts only)
├── components/
│   ├── ui/                 # shadcn/ui primitives (auto-generated, don't edit)
│   ├── shared/             # Reusable composed components (DataTable, PageHeader, etc.)
│   ├── hr/                 # Pillar 1 feature components
│   ├── workforce/          # Pillar 2 feature components
│   └── layout/             # Sidebar, Topbar, Breadcrumbs
├── hooks/                  # Custom React hooks (one hook per file)
├── lib/
│   ├── api/                # API client + endpoint definitions
│   ├── signalr/            # SignalR connection manager
│   └── utils/              # Formatting, validation helpers
├── stores/                 # Zustand stores (one store per file)
├── types/                  # TypeScript interfaces (mirror backend DTOs)
└── styles/                 # Global CSS, Tailwind config
```

## File Organization Rules

1. **Page files (`app/`)** should be thin — import components, pass data down
2. **Feature components** follow a three-tier promotion path:
   - Route-exclusive → colocated in `app/(dashboard)/.../components/`
   - Module-shared (2+ pages in same module) → promoted to `components/{module}/` (delete colocated copy)
   - Cross-module → promoted to `components/shared/` (delete module copy)
3. **One component per file** (except small private helpers used only in that file)
4. **One hook per file** in `hooks/` — named `use-{resource}.ts`
5. **One store per file** in `stores/` — named `use-{name}-store.ts`
6. **Types** mirroring a backend DTO go in `types/{module}.ts`
7. **Route-local types** (form schemas, column defs, local UI state) go in `_types.ts` colocated in the route folder — never API response shapes there

## Component Template

```tsx
'use client';

import { useState } from 'react';
import { useEmployees } from '@/hooks/use-employees';
import { DataTable } from '@/components/shared/data-table';
import { PermissionGate } from '@/components/shared/permission-gate';

interface EmployeeListProps {
  departmentId?: string;
}

export function EmployeeList({ departmentId }: EmployeeListProps) {
  const [search, setSearch] = useQueryState('search', { defaultValue: '' });
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
// 1. React/Next.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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

- **Lazy load** heavy components (charts, data tables) with `next/dynamic` (not `React.lazy` — App Router requires `next/dynamic` for proper SSR control)
- **Paginate** all lists — never load unbounded data
- **Debounce** search inputs (300ms)
- **Prefetch** on hover for navigation links (Next.js handles this)
- **Image optimization** via Next.js `Image` component

## Related

- [[frontend/architecture/app-structure|App Structure]]
- [[frontend/design-system/components/component-catalog|Component Catalog]]
- [[AI_CONTEXT/rules|Rules]]
