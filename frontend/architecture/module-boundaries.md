# Module Boundaries & Code Splitting

## Module Map

Each product domain is a **frontend module** - an isolated vertical slice with its own routes, components, services, and types.

### HR & Platform Modules

| Module | Route(s) | Component Dir | Lazy Loaded |
|:-------|:---------|:--------------|:------------|
| Core HR | `/people/employees` | `components/hr/` | No (core) |
| Time Off | `/time-off` | `components/time_off/` | Yes |
| Performance | Employee detail `#performance` section | `components/performance/` | Yes (Phase 2) |
| Payroll | Employee detail `#pay-benefits` section | `components/payroll/` | Yes (Phase 2) |
| Grievance | Employee detail `#grievance` section | `components/grievance/` | Yes (Phase 2) |
| Expense | Employee detail `#expense` section | `components/expense/` | Yes (Phase 2) |
| Time & Attendance | `/time-attendance` | `components/monitoring/` | Yes |
| Monitoring | `/monitoring`, `/monitoring/employees/[employeeId]` | `components/monitoring/` | Yes (heavy charts) |
| Identity Verification | `/monitoring` (online status dot on cards) | `components/monitoring/` | Yes |
| Monitoring Alerts | `/monitoring/alerts` | `components/exceptions/` | Yes; full Exception Engine is Phase 2 |
| Org Structure | `/org/*` | `components/org/` | Yes |
| Settings | `/settings/*` | `components/settings/` | Yes |

### WMS Modules

> Work is a **distinct product domain** from Monitoring and Time & Attendance. Components live in `components/wms/` or `components/work/` - never in `components/monitoring/`. Routes use the `/work` prefix.

| Module | Route(s) | Component Dir | Lazy Loaded |
|:-------|:---------|:--------------|:------------|
| Projects | `/work/projects` | `components/wms/` | Yes |
| Work Items | `/work/items`, `/work/projects/[id]/items` | `components/wms/` | Yes |
| Planning | `/work/planner`, `/work/projects/[id]/sprints`, `/work/projects/[id]/roadmap` | `components/wms/` | Phase 2 only |
| OKR / Goals | `/work/goals` | `components/wms/` | Phase 2 only |
| Documents | `/work/documents` | `components/wms/` | Yes |
| Worklogs | `/work/worklogs` | `components/wms/` | Yes |
| Resource / Capacity | `/work/analytics` (capacity section) | `components/wms/` | Phase 2 unless required for project access |
| Chat | `/chat` | `components/wms/` | Phase 2 |

## Import Rules

```
[ok] Allowed imports:
  components/hr/employee-list -> components/shared/data-table     (module -> shared)
  components/hr/employee-list -> services/hr/employee.service     (module -> own services)
  components/hr/employee-list -> types/core-hr                    (module -> own types)
  components/shared/stat-card -> shared library components        (shared -> primitives)

[wrong] Forbidden imports:
  components/hr/employee-list -> components/monitoring/live-dashboard  (module -> module)
  components/payroll/run-detail -> services/hr/employee.service        (module -> other module's services)
  shared library primitive -> components/shared/stat-card              (primitive -> composed)
  components/wms/kanban-board -> components/monitoring/presence-card   (wms -> monitoring-intelligence)
  components/monitoring/presence-card -> components/wms/task-card      (monitoring-intelligence -> wms)
```

**If two modules need the same logic**, extract it to `shared/` or `services/shared/`.

## Dependency Graph

```
+---------------------------------------------------------------------+
|                       app.routes.ts (routes)                        |
|  Imports feature components per route via loadComponent             |
+--------------------------------+------------------------------------+
                                 |
      +----------+---------------+---------------+----------+
      v          v               v               v          v
+----------+ +----------+ +--------------+ +---------+ +----------+
|components| |components| | components/  | |compnts/ | |components|
|  /hr/    | |/monitoring| |    /wms/     | |  /org/  | |  /time_off/ |
| (Core HR)| | (WI)     | |   (WMS)     | |  etc.   | |  etc.    |
+----+-----+ +----+-----+ +------+-------+ +----+----+ +----+-----+
     |             |              |               |            |
     +-------------+--------------+---------------+------------+
                                  |
                        +---------v----------+
                        |  components/shared/ |
                        |  (DataTable, etc.)  |
                        +---------+-----------+
                                  v
                        +----------------------+
                        | shared library       |
                        | (Angular Material)   |
                        +----------------------+
```

No horizontal arrows exist between module boxes - that is the rule the linter enforces.

## Code Splitting Strategy

### Route-Level Splitting (Angular Router)

Angular Router lazy-loads feature routes via `loadComponent` and `loadChildren`:

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'work/projects/:id/board',
    loadComponent: () => import('./pages/work/projects/project-board.component')
      .then(m => m.ProjectBoardComponent),
    canActivate: [authGuard],
  },
  {
    path: 'org',
    loadChildren: () => import('./pages/org/org.routes')
      .then(m => m.ORG_ROUTES),
  },
  {
    path: 'monitoring/analytics',
    loadComponent: () => import('./pages/monitoring/monitoring-analytics.component')
      .then(m => m.MonitoringAnalyticsComponent),
  },
];
```

### Component-Level Splitting (Angular `@defer`)

Heavy components that aren't needed on first render use `@defer`:

```typescript
// Inside a page template
@defer (on viewport) {
  <app-activity-heatmap [data]="activityData()" />
} @placeholder {
  <app-chart-skeleton [height]="400" />
}

@defer (on viewport) {
  <app-org-chart [data]="orgData()" />
} @placeholder {
  <app-chart-skeleton [height]="600" />
}

@defer (on viewport) {
  <app-kanban-board [projectId]="projectId()" />
} @placeholder {
  <app-page-skeleton />
}
```

**Apply `@defer` to:** org charts, work item boards, Phase 2 roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets, and any component that pulls in a library >50KB.

### Library-Level Splitting

Heavy libraries should only load with the components that need them:

| Library | Size | Loaded With |
|:--------|:-----|:------------|
| Chart library | ~200KB | Chart components only (via `@defer`) |
| date-fns | ~70KB | Calendar/date picker pages only |
| @microsoft/signalr | ~50KB | Monitoring live + exceptions pages |
| Angular Reactive Forms + Zod | ~40KB | Form-heavy pages only |

### Bundle Composition Target

| Chunk | Max Size (gzipped) | Contents |
|:------|:-------------------|:---------|
| Framework | <=80KB | Angular core, Router runtime |
| Shared UI | <=40KB | Angular Material primitives, shared components |
| Per-route | <=60KB | Route-specific components + services |
| Charts | <=80KB | Chart library (loaded on demand via `@defer`) |
| Real-time | <=20KB | SignalR client (loaded on demand) |

## Feature-Gated Modules

Some modules and module features are gated by tenant subscription. Module sections use active module keys; feature screens use active feature keys that already include commercial inclusion and runtime flag evaluation.

```typescript
// app.routes.ts - feature-gated route
{
  path: 'work/projects',
  loadComponent: () => import('./pages/work/projects/projects.component')
    .then(m => m.ProjectsComponent),
  canActivate: [authGuard, featureGuard('work_management.projects')],
}
```

Components also check at render time using the `*hasPermission` structural directive or feature service:

```typescript
// In template
<ng-container *hasPermission="'projects:read'">
  <app-live-dashboard />
</ng-container>

// Feature gating in template
@if (featureService.isEnabled('monitoring')) {
  <app-live-dashboard />
} @else {
  <app-upgrade-banner module="Monitoring" />
}
```

## Boundary Enforcement

Use `eslint-plugin-boundaries` to enforce the import rules above in CI. This is the only way to catch violations of the three-tier promotion rule automatically - "never keep both copies" cannot be reviewed manually at scale.

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
      { "type": "monitoring",   "pattern": "components/monitoring/*" },
      { "type": "wms",         "pattern": "components/wms/*" },
      { "type": "org",         "pattern": "components/org/*" },
      { "type": "time_off",       "pattern": "components/time_off/*" },
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
        { "from": "monitoring",  "allow": ["monitoring", "shared", "ui"] },
        { "from": "wms",        "allow": ["wms", "shared", "ui"] },
        { "from": "org",        "allow": ["org", "shared", "ui"] },
        { "from": "time_off",      "allow": ["time_off", "shared", "ui"] },
        { "from": "exceptions", "allow": ["exceptions", "shared", "ui"] },
        { "from": "settings",   "allow": ["settings", "shared", "ui"] }
      ]
    }]
  }
}
```

When a component needs to cross boundaries, that is the signal to promote it to `components/shared/` - not to relax the rule.

## Related

- [[frontend/architecture/rendering-strategy|Rendering Strategy]] - CSR rendering approach
- [[frontend/architecture/app-structure|App Structure]] - route tree and page file structure
- [[frontend/architecture/app-structure|Code Splitting]] - detailed splitting strategy
- [[frontend/cross-cutting/feature-flags|Feature Flags]] - feature flag system
