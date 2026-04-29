# Rendering Strategy

> This app is a **Vite SPA — all rendering is Client-Side Rendering (CSR)**. There are no Server Components, no SSR, no `'use client'` directives, no streaming. All data fetching happens in the browser via TanStack Query. Loading states use React Suspense boundaries and TanStack Query `isLoading` flags.

## Why CSR

- The app is behind authentication — SEO is not a concern
- Vite SPA is simpler to host (static files + CDN), with no server runtime required
- TanStack Query handles all the complexity of caching, background refetch, and stale-while-revalidate

## Loading State Strategy

| Level | Mechanism | When to Use |
|:------|:----------|:------------|
| Route transition | React Suspense around lazy-loaded page components | Heavy pages loaded with `React.lazy()` |
| Section | `<Suspense fallback={<Skeleton />}>` inside page | Independent data sections |
| Component | TanStack Query `isLoading` | Inline skeleton within a component |
| Action | Mutation `isPending` | Button spinner / disabled state |

## Page Rendering Pattern

All pages follow the same pattern — a thin page component that imports feature components:

```tsx
// src/pages/dashboard/people/employees/EmployeesPage.tsx
import { Suspense } from 'react';
import { PageHeader } from '@/components/shared/page-header';
import { EmployeeList } from '@/components/hr/employee-list';
import { TableSkeleton } from '@/components/shared/table-skeleton';
import { PermissionGate } from '@/components/shared/permission-gate';

export function EmployeesPage() {
  return (
    <>
      <PageHeader
        title="Employees"
        actions={[
          <PermissionGate key="add" permission="employees:write">
            <AddEmployeeButton />
          </PermissionGate>
        ]}
      />
      <Suspense fallback={<TableSkeleton rows={10} columns={6} />}>
        <EmployeeList />
      </Suspense>
    </>
  );
}
```

## Dashboard Home Pattern

Multiple independent data sections each have their own Suspense boundary — they load in parallel, not sequentially:

```tsx
// src/pages/dashboard/HomePage.tsx
export function HomePage() {
  return (
    <>
      <PageHeader title="Overview" />
      <div className="grid grid-cols-4 gap-4">
        <Suspense fallback={<StatCardSkeleton />}>
          <EmployeeCountCard />
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <ActiveWorkforceCard />
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <PendingLeaveCard />
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <OpenExceptionsCard />
        </Suspense>
      </div>
      <Suspense fallback={<ChartSkeleton height={300} />}>
        <WorkforceTrendChart />
      </Suspense>
    </>
  );
}
```

## Lazy Loading Heavy Pages

Routes with heavy components (charts, kanban boards, org charts) are lazy-loaded to reduce initial bundle:

```tsx
// src/router.tsx
import { lazy, Suspense } from 'react';
import { PageSkeleton } from '@/components/shared/page-skeleton';

const ProjectBoardPage   = lazy(() => import('@/pages/dashboard/workforce/projects/ProjectBoardPage'));
const ProjectRoadmapPage = lazy(() => import('@/pages/dashboard/workforce/projects/ProjectRoadmapPage'));
const OrgPage            = lazy(() => import('@/pages/dashboard/org/OrgPage'));
const WorkforceAnalyticsPage = lazy(() => import('@/pages/dashboard/workforce/WorkforceAnalyticsPage'));
const ChatPage           = lazy(() => import('@/pages/dashboard/workforce/ChatPage'));

// Wrap lazy routes in Suspense in the route config:
{
  path: '/workforce/projects/:id/board',
  element: (
    <Suspense fallback={<PageSkeleton />}>
      <ProjectBoardPage />
    </Suspense>
  ),
}
```

## Lazy Loading Heavy Components

Within a page, heavy components that aren't needed immediately:

```tsx
import { lazy, Suspense } from 'react';

const OrgChart       = lazy(() => import('@/components/org/org-chart'));
const ActivityHeatmap = lazy(() => import('@/components/workforce/activity-heatmap'));
const KanbanBoard    = lazy(() => import('@/components/wms/kanban-board'));

// Usage with skeleton fallback:
<Suspense fallback={<ChartSkeleton height={600} />}>
  <OrgChart data={orgData} />
</Suspense>
```

**Apply `React.lazy()` to:** org charts, kanban boards, roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets, and any component that pulls in a library >50KB (Recharts, react-dnd, etc.).

> **Do NOT use `next/dynamic()`** — that is a Next.js API. In Vite use `React.lazy()` + `<Suspense>`.

## Error Handling

```tsx
// Wrap feature sections in error boundaries — NOT full-page boundaries for every route
import { SectionErrorBoundary } from '@/components/shared/section-error-boundary';

<SectionErrorBoundary section="employees">
  <Suspense fallback={<TableSkeleton rows={10} />}>
    <EmployeeList />
  </Suspense>
</SectionErrorBoundary>
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — route tree and page file structure
- [[frontend/architecture/overview|Overview]] — architecture principles
- [[frontend/architecture/module-boundaries|Module Boundaries]] — code splitting strategy
