# Module Boundaries & Code Splitting

## Module Map

Each product domain is a **frontend module** — an isolated vertical slice with its own routes, components, hooks, and types.

### HR & Platform Modules

| Module | Route(s) | Component Dir | Lazy Loaded |
|:-------|:---------|:--------------|:------------|
| Core HR | `/people/employees` | `components/hr/` | No (core) |
| Leave | `/people/leave` | `components/leave/` | Yes |
| Performance | Employee detail `#performance` section | `components/performance/` | Yes (Phase 2) |
| Payroll | Employee detail `#pay-benefits` section | `components/payroll/` | Yes (Phase 2) |
| Grievance | Employee detail `#grievance` section | `components/grievance/` | Yes (Phase 2) |
| Expense | Employee detail `#expense` section | `components/expense/` | Yes (Phase 2) |
| Workforce Presence | `/workforce` (presence cards) | `components/workforce/` | Yes |
| Activity Monitoring | `/workforce/[employeeId]` | `components/workforce/` | Yes (heavy charts) |
| Identity Verification | `/workforce` (online status dot on cards) | `components/workforce/` | Yes |
| Exception Engine | `/settings/alert-rules`, escalated cards on `/workforce` | `components/exceptions/` | Yes |
| Org Structure | `/org/*` | `components/org/` | Yes |
| Settings | `/settings/*` | `components/settings/` | Yes |

### WMS Modules

> WMS is a **distinct product domain** from Workforce Intelligence. Components live in `components/wms/` — never in `components/workforce/`. Routes share the `/workforce/` prefix for now but will split if WMS gets its own nav pillar.

| Module | Route(s) | Component Dir | Lazy Loaded |
|:-------|:---------|:--------------|:------------|
| Projects | `/workforce/projects` | `components/wms/` | Yes |
| Tasks | `/workforce/projects/[id]/board`, `/workforce/my-work` | `components/wms/` | Yes |
| Planning | `/workforce/planner`, `/workforce/projects/[id]/sprints`, `/workforce/projects/[id]/roadmap` | `components/wms/` | Yes |
| OKR | `/workforce/goals` | `components/wms/` | Yes |
| Docs / Wiki | `/workforce/docs` | `components/wms/` | Yes |
| Time | `/workforce/time` | `components/wms/` | Yes |
| Resource / Capacity | `/workforce/analytics` (capacity section) | `components/wms/` | Yes |
| Chat | `/chat` | `components/wms/` | Yes |

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
  components/wms/kanban-board → components/workforce/presence-card   (wms → workforce-intelligence)
  components/workforce/presence-card → components/wms/task-card      (workforce-intelligence → wms)
```

**If two modules need the same logic**, extract it to `shared/` or `hooks/shared/`.

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────┐
│                         app/ (routes)                                │
│  Imports feature components per route                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
      ┌──────────┬───────────────┼───────────────┬──────────┐
      ▼          ▼               ▼               ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────┐ ┌──────────┐
│components│ │components│ │ components/  │ │compnts/ │ │components│
│  /hr/    │ │/workforce│ │    /wms/     │ │  /org/  │ │  /leave/ │
│ (Core HR)│ │ (WI)     │ │   (WMS)     │ │  etc.   │ │  etc.    │
└────┬─────┘ └────┬─────┘ └──────┬───────┘ └────┬────┘ └────┬─────┘
     │             │              │               │            │
     └─────────────┴──────────────┴───────────────┴────────────┘
                                  │
                        ┌─────────▼──────────┐
                        │  components/shared/ │
                        │  (DataTable, etc.)  │
                        └─────────┬───────────┘
                                  ▼
                        ┌──────────────────────┐
                        │   components/ui/      │
                        │   (shadcn/ui)         │
                        └──────────────────────┘
```

No horizontal arrows exist between module boxes — that is the rule the linter enforces.

## Code Splitting Strategy

### Route-Level Splitting (Manual with React.lazy)
Vite does not auto-split per route. Heavy pages must be explicitly lazy-loaded in `router.tsx`:

```tsx
// src/router.tsx
import { lazy, Suspense } from 'react';

const ProjectBoardPage    = lazy(() => import('@/pages/dashboard/workforce/projects/ProjectBoardPage'));
const OrgPage             = lazy(() => import('@/pages/dashboard/org/OrgPage'));
const WorkforceAnalyticsPage = lazy(() => import('@/pages/dashboard/workforce/WorkforceAnalyticsPage'));

// Wrap in Suspense in the route definition:
{ path: '/workforce/projects/:id/board', element: (
  <Suspense fallback={<PageSkeleton />}><ProjectBoardPage /></Suspense>
)}
```

> **Do NOT use `next/dynamic()`** — that is a Next.js API. Always use `React.lazy()` + `<Suspense>`.

### Component-Level Splitting (Manual with React.lazy)
Heavy components that aren't needed on first render:

```tsx
import { lazy, Suspense } from 'react';

const ActivityHeatmap = lazy(() => import('@/components/workforce/activity-heatmap'));
const OrgChart        = lazy(() => import('@/components/org/org-chart'));
const KanbanBoard     = lazy(() => import('@/components/wms/kanban-board'));

// Usage:
<Suspense fallback={<ChartSkeleton height={400} />}>
  <ActivityHeatmap data={activityData} />
</Suspense>
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
| Framework | ≤80KB | React, React Router runtime |
| Shared UI | ≤40KB | shadcn/ui primitives, shared components |
| Per-route | ≤60KB | Route-specific components + hooks |
| Charts | ≤80KB | Recharts (loaded on demand) |
| Real-time | ≤20KB | SignalR client (loaded on demand) |

## Feature-Gated Modules

Some modules are gated by tenant subscription. Gating happens in the route config via `useAuthStore`:

```tsx
// src/router.tsx — feature-gated route
{ path: '/workforce/projects', element: (
  <ProtectedRoute permission="projects:read">
    {useAuthStore.getState().hasFeature('wms:projects')
      ? <ProjectsPage />
      : <Navigate to="/workforce" replace />
    }
  </ProtectedRoute>
)}
```

Components also check at render time:
```tsx
<FeatureGate feature="workforceIntelligence" fallback={<UpgradeBanner module="Workforce Intelligence" />}>
  <LiveDashboard />
</FeatureGate>
```

## Boundary Enforcement

Use `eslint-plugin-boundaries` to enforce the import rules above in CI. This is the only way to catch violations of the three-tier promotion rule automatically — "never keep both copies" cannot be reviewed manually at scale.

```bash
npm install -D eslint-plugin-boundaries
```

```json
// .eslintrc
{
  "plugins": ["boundaries"],
  "settings": {
    "boundaries/elements": [
      { "type": "ui",          "pattern": "components/ui/*" },
      { "type": "shared",      "pattern": "components/shared/*" },
      { "type": "hr",          "pattern": "components/hr/*" },
      { "type": "workforce",   "pattern": "components/workforce/*" },
      { "type": "wms",         "pattern": "components/wms/*" },
      { "type": "org",         "pattern": "components/org/*" },
      { "type": "leave",       "pattern": "components/leave/*" },
      { "type": "exceptions",  "pattern": "components/exceptions/*" },
      { "type": "settings",    "pattern": "components/settings/*" }
    ]
  },
  "rules": {
    "boundaries/element-types": ["error", {
      "default": "disallow",
      "rules": [
        { "from": "*",          "allow": ["ui", "shared"] },
        { "from": "shared",     "allow": ["ui"] },
        { "from": "hr",         "allow": ["hr", "shared", "ui"] },
        { "from": "workforce",  "allow": ["workforce", "shared", "ui"] },
        { "from": "wms",        "allow": ["wms", "shared", "ui"] },
        { "from": "org",        "allow": ["org", "shared", "ui"] },
        { "from": "leave",      "allow": ["leave", "shared", "ui"] },
        { "from": "exceptions", "allow": ["exceptions", "shared", "ui"] },
        { "from": "settings",   "allow": ["settings", "shared", "ui"] }
      ]
    }]
  }
}
```

When a component needs to cross boundaries, that is the signal to promote it to `components/shared/` — not to relax the rule.

## Related

- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR/CSR per route
- [[frontend/architecture/app-structure|App Structure]] — route tree
- [[frontend/architecture/app-structure|Code Splitting]] — detailed splitting strategy
- [[frontend/cross-cutting/feature-flags|Feature Flags]] — feature flag system
