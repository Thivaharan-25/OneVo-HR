# Module Boundaries & Code Splitting

## Module Map

Each product domain is a **frontend module** — an isolated vertical slice with its own routes, components, hooks, and types.

| Module | Route Prefix | Component Dir | Lazy Loaded |
|:-------|:-------------|:--------------|:------------|
| Core HR | `/people/employees`, `/people/documents`, `/people/skills` | `components/hr/` | No (core) |
| Leave | `/people/leave` | `components/leave/` | Yes |
| Performance | `/people/performance` | `components/performance/` | Yes |
| Payroll | `/people/payroll` | `components/payroll/` | Yes |
| Grievance | `/people/grievance` | `components/grievance/` | Yes |
| Expense | `/people/expense` | `components/expense/` | Yes |
| Workforce Live | `/workforce/live` | `components/workforce/` | Yes |
| Activity Monitoring | `/workforce/activity` | `components/workforce/` | Yes (heavy charts) |
| Exception Engine | `/workforce/exceptions` | `components/exceptions/` | Yes |
| Identity Verification | `/workforce/verification` | `components/verification/` | Yes |
| Org Structure | `/org/*` | `components/org/` | Yes |
| Settings | `/settings/*` | `components/settings/` | Yes |
| Employee Self-Service | `/my-*` | `components/self-service/` | No (separate entry) |

## Import Rules

```
✅ Allowed imports:
  components/hr/employee-list → components/shared/data-table     (module → shared)
  components/hr/employee-list → hooks/hr/use-employees           (module → own hooks)
  components/hr/employee-list → types/core-hr                    (module → own types)
  components/shared/stat-card → components/ui/card               (shared → primitives)

❌ Forbidden imports:
  components/hr/employee-list → components/workforce/live-dashboard  (module → module)
  components/payroll/run-detail → hooks/hr/use-employees             (module → other module's hooks)
  components/ui/button → components/shared/stat-card                 (primitive → composed)
```

**If two modules need the same logic**, extract it to `shared/` or `hooks/shared/`.

## Dependency Graph

```
┌──────────────────────────────────────────────────────┐
│                    app/ (routes)                      │
│  Imports feature components per route                 │
└────────────────────────┬─────────────────────────────┘
                         │
         ┌───────────────┼───────────────────┐
         ▼               ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ components/  │ │ components/  │ │ components/      │
│ hr/          │ │ workforce/   │ │ payroll/         │
│ (Core HR)    │ │ (Workforce)  │ │ (Payroll)        │
└──────┬───────┘ └──────┬───────┘ └──────┬───────────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌──────────────────┐
              │ components/      │
              │ shared/          │
              │ (DataTable, etc) │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │ components/ui/   │
              │ (shadcn/ui)      │
              └──────────────────┘
```

## Code Splitting Strategy

### Route-Level Splitting (Automatic)
Next.js App Router automatically code-splits per route segment. Each `page.tsx` and `layout.tsx` is a separate chunk.

### Component-Level Splitting (Manual)
Heavy components that aren't needed on first render:

```tsx
// Lazy load chart-heavy components
const ActivityHeatmap = dynamic(
  () => import('@/components/workforce/activity-heatmap'),
  { loading: () => <ChartSkeleton height={400} />, ssr: false }
);

const OrgChart = dynamic(
  () => import('@/components/org/org-chart'),
  { loading: () => <ChartSkeleton height={600} />, ssr: false }
);

const PayrollCalculator = dynamic(
  () => import('@/components/payroll/payroll-calculator'),
  { loading: () => <TableSkeleton rows={20} /> }
);

// Lazy load dialog content (not needed until user clicks)
const EmployeeCreateDialog = dynamic(
  () => import('@/components/hr/employee-create-dialog')
);
```

### Library-Level Splitting
Heavy libraries should only load with the components that need them:

| Library | Size | Loaded With |
|:--------|:-----|:------------|
| Recharts | ~200KB | Chart components only |
| date-fns | ~70KB | Calendar/date picker pages only |
| @microsoft/signalr | ~50KB | Workforce live + exceptions pages |
| react-hook-form + zod | ~40KB | Form-heavy pages only |

### Bundle Composition Target

| Chunk | Max Size (gzipped) | Contents |
|:------|:-------------------|:---------|
| Framework | ≤90KB | React, Next.js runtime |
| Shared UI | ≤40KB | shadcn/ui primitives, shared components |
| Per-route | ≤60KB | Route-specific components + hooks |
| Charts | ≤80KB | Recharts + Tremor (loaded on demand) |
| Real-time | ≤20KB | SignalR client (loaded on demand) |

## Feature-Gated Modules

Some modules are gated by tenant subscription:

```tsx
// middleware.ts — redirect if module not enabled
export function middleware(request: NextRequest) {
  const tenant = getTenantFromRequest(request);

  if (request.nextUrl.pathname.startsWith('/workforce') && !tenant.features.workforceIntelligence) {
    return NextResponse.redirect(new URL('/people/employees', request.url));
  }

  if (request.nextUrl.pathname.startsWith('/people/payroll') && !tenant.features.payroll) {
    return NextResponse.redirect(new URL('/people/employees', request.url));
  }
}
```

Components also check at render time:
```tsx
<FeatureGate feature="workforceIntelligence" fallback={<UpgradeBanner module="Workforce Intelligence" />}>
  <LiveDashboard />
</FeatureGate>
```

## Related

- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR/CSR per route
- [[frontend/architecture/app-structure|App Structure]] — route tree
- [[frontend/architecture/app-structure|Code Splitting]] — detailed splitting strategy
- [[frontend/cross-cutting/feature-flags|Feature Flags]] — feature flag system
