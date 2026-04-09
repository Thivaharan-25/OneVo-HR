# Rendering Strategy

## Decision Matrix

Every route has an explicit rendering decision. Default is **RSC (Server Component)** — opt into client rendering only when required.

### When to Use Server Components (RSC)
- Static content (settings pages, policy displays, documentation)
- Initial data fetch for list/detail pages (SSR the first paint)
- SEO-sensitive pages (login, public-facing)
- Layouts, navigation shells, breadcrumbs

### When to Use Client Components (`'use client'`)
- Forms with interactive validation
- Real-time data (SignalR subscriptions)
- Client state (modals, sidebar, filters with immediate feedback)
- Charts and data visualizations (Recharts/Tremor require DOM)
- Drag-and-drop interactions
- Search with debounced input

## Route-Level Rendering Map

| Route | Rendering | Rationale |
|:------|:----------|:----------|
| `(auth)/login` | SSR | Fast first paint, SEO, minimal JS |
| `(auth)/forgot-password` | SSR | Static form, server action for submit |
| `(auth)/mfa` | Client | Interactive OTP input, timer |
| `(dashboard)/overview` | Hybrid | SSR shell + client KPI cards (real-time) |
| `(dashboard)/people/employees` | Hybrid | SSR table shell + client pagination/filters |
| `(dashboard)/people/employees/[id]` | Hybrid | SSR profile header + client tabs |
| `(dashboard)/people/employees/new` | Client | Multi-step form wizard |
| `(dashboard)/people/leave` | Hybrid | SSR list + client status filters |
| `(dashboard)/people/leave/calendar` | Client | Interactive calendar component |
| `(dashboard)/people/performance` | Hybrid | SSR list + client review workflow |
| `(dashboard)/people/payroll` | Hybrid | SSR runs list + client calculations |
| `(dashboard)/workforce/live` | Client | Full real-time dashboard (SignalR) |
| `(dashboard)/workforce/activity/[id]` | Client | Real-time activity data, charts |
| `(dashboard)/workforce/reports` | Hybrid | SSR report list + client chart rendering |
| `(dashboard)/workforce/exceptions` | Client | Real-time alerts, acknowledge actions |
| `(dashboard)/org/*` | SSR | Mostly static org data, infrequent changes |
| `(dashboard)/settings/*` | SSR | Configuration forms (server actions) |
| `(employee)/*` | Hybrid | SSR shell + client interactive widgets |

## Hybrid Pattern

Most pages use the **Hybrid** pattern — an RSC shell that streams in client islands:

```tsx
// app/(dashboard)/people/employees/page.tsx  — Server Component (no 'use client')
import { Suspense } from 'react';
import { PageHeader } from '@/components/shared/page-header';
import { EmployeeList } from '@/components/hr/employee-list'; // 'use client'
import { TableSkeleton } from '@/components/shared/table-skeleton';

export default function EmployeesPage() {
  return (
    <>
      <PageHeader
        title="Employees"
        actions={[{ label: 'Add Employee', href: '/people/employees/new', permission: 'employees:create' }]}
      />
      <Suspense fallback={<TableSkeleton rows={10} columns={6} />}>
        <EmployeeList />  {/* Client component with TanStack Query */}
      </Suspense>
    </>
  );
}
```

## Streaming SSR

Use Next.js streaming for pages with multiple independent data sources:

```tsx
// app/(dashboard)/overview/page.tsx
export default function OverviewPage() {
  return (
    <>
      <PageHeader title="Overview" />
      <div className="grid grid-cols-4 gap-4">
        <Suspense fallback={<StatCardSkeleton />}>
          <EmployeeCountCard />    {/* Independent fetch */}
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <ActiveWorkforceCard />  {/* Independent fetch */}
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <PendingLeaveCard />     {/* Independent fetch */}
        </Suspense>
        <Suspense fallback={<StatCardSkeleton />}>
          <OpenExceptionsCard />   {/* Independent fetch */}
        </Suspense>
      </div>
      <Suspense fallback={<ChartSkeleton height={300} />}>
        <WorkforceTrendChart />
      </Suspense>
    </>
  );
}
```

## Loading States

| Level | Component | Behavior |
|:------|:----------|:---------|
| Route | `loading.tsx` | Full-page skeleton shown during navigation |
| Section | `<Suspense>` | Per-section skeleton while streaming |
| Component | TanStack Query `isLoading` | Inline skeleton within client components |
| Action | Mutation `isPending` | Button spinner / disabled state |

Every route group has a `loading.tsx`:
```
app/(dashboard)/
├── loading.tsx              # Dashboard-wide loading (sidebar stays, content skeleton)
├── hr/
│   ├── loading.tsx          # HR section loading
│   └── employees/
│       └── loading.tsx      # Employee-specific loading
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — route tree
- [[frontend/architecture/overview|Overview]] — architecture principles
- [[backend/module-boundaries|Module Boundaries]] — code splitting
