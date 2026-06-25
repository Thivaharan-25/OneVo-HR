# Rendering Strategy

> This app is an **Angular 21 CSR SPA - all rendering is Client-Side Rendering**. There are no Server Components, no SSR, no streaming. All data fetching happens in the browser via Angular `HttpClient` with `toSignal()` / `resource()` for signal-integrated async data. Loading states use Angular `@defer` blocks, `@if` control flow, and signal-based flags.

## Why CSR

- The app is behind authentication - SEO is not a concern
- Angular CLI builds static files deployable to any CDN, with no server runtime required
- Angular signals and `resource()` handle reactive state, caching, and loading/error states natively

## Loading State Strategy

| Level | Mechanism | When to Use |
|:------|:----------|:------------|
| Route transition | Angular Router `loadComponent` / `loadChildren` with route-level loading indicator | Heavy feature modules loaded on demand |
| Section | `@defer` with `@placeholder` and `@loading` blocks | Independent data sections within a page |
| Component | Signal-based `loading()` flag from service or `resource()` | Inline skeleton within a component |
| Action | `submitting` signal on form/button | Button spinner / disabled state |

## Page Rendering Pattern

All pages follow the same pattern - a standalone component that composes feature components:

```typescript
// pages/people/employees/employees-page.component.ts
@Component({
  selector: 'app-employees-page',
  standalone: true,
  imports: [PageHeaderComponent, EmployeeListComponent, HasPermissionDirective],
  template: `
    <app-page-header title="Employees">
      <button mat-flat-button *hasPermission="'employees:write'" routerLink="add">
        Add Employee
      </button>
    </app-page-header>

    @defer {
      <app-employee-list />
    } @placeholder {
      <app-table-skeleton [rows]="10" [columns]="6" />
    }
  `,
})
export class EmployeesPageComponent {}
```

## Dashboard Home Pattern

Multiple independent data sections each use their own `@defer` block - they load in parallel, not sequentially:

```typescript
// pages/dashboard/home-page.component.ts
@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [
    PageHeaderComponent, EmployeeCountCardComponent,
    ActiveMonitoringCardComponent, PendingLeaveCardComponent,
    OpenExceptionsCardComponent, MonitoringTrendChartComponent,
    StatCardSkeletonComponent, ChartSkeletonComponent,
  ],
  template: `
    <app-page-header title="Overview" />
    <div class="grid grid-cols-4 gap-4">
      @defer {
        <app-employee-count-card />
      } @placeholder { <app-stat-card-skeleton /> }

      @defer {
        <app-active-monitoring-card />
      } @placeholder { <app-stat-card-skeleton /> }

      @defer {
        <app-pending-leave-card />
      } @placeholder { <app-stat-card-skeleton /> }

      @defer {
        <app-open-exceptions-card />
      } @placeholder { <app-stat-card-skeleton /> }
    </div>

    @defer {
      <app-monitoring-trend-chart />
    } @placeholder { <app-chart-skeleton [height]="300" /> }
  `,
})
export class HomePageComponent {}
```

## Lazy Loading Heavy Pages

Routes with heavy components (charts, kanban boards, org charts) are lazy-loaded via Angular Router:

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'work/projects/:id/items',
    loadComponent: () =>
      import('./pages/work/projects/project-board-page.component')
        .then(m => m.ProjectBoardPageComponent),
  },
  {
    path: 'org',
    loadComponent: () =>
      import('./pages/org/org-page.component')
        .then(m => m.OrgPageComponent),
  },
  {
    path: 'monitoring/analytics',
    loadComponent: () =>
      import('./pages/monitoring/monitoring-analytics-page.component')
        .then(m => m.MonitoringAnalyticsPageComponent),
  },
];
```

## Lazy Loading Heavy Components

Within a page, heavy components that aren't needed immediately use `@defer`:

```typescript
@Component({
  selector: 'app-monitoring-detail',
  standalone: true,
  imports: [ActivityHeatmapComponent, OrgChartComponent, KanbanBoardComponent],
  template: `
    @defer (on viewport) {
      <app-activity-heatmap [data]="activityData()" />
    } @placeholder {
      <app-chart-skeleton [height]="400" />
    }
  `,
})
export class MonitoringDetailComponent {
  activityData = input.required<ActivityData[]>();
}
```

**Apply `@defer` or `loadComponent` to:** org charts, work item boards, Phase 2 roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets, and any component that pulls in a library >50KB (ng2-charts, Angular CDK drag-drop, etc.).

## Error Handling

```typescript
// Wrap feature sections in error-handling components - NOT full-page boundaries for every route
@Component({
  selector: 'app-employees-section',
  standalone: true,
  imports: [EmployeeListComponent, SectionErrorComponent],
  template: `
    @if (error()) {
      <app-section-error section="employees" (retry)="reload()" />
    } @else {
      <app-employee-list />
    }
  `,
})
export class EmployeesSectionComponent {
  private employeeService = inject(EmployeeService);
  error = this.employeeService.error;
  reload() { this.employeeService.refresh(); }
}
```

## Customer App Route State

Phase 1 uses one merged `customer-app`, so there is no cross-app route memory or customer-facing app switcher. Normal Angular Router state remains inside `customer-app`.

```
Entity context: EntityContextService.activeEntityId()
Route state: Angular Router query params for filters, tabs, and pagination
Cleared: on logout where persisted by feature code
```

Legal-entity context is handled by [[frontend/design-system/patterns/app-entity-switcher|Entity Context Pattern]]. Filters, pagination, and form drafts should stay feature-owned and should not introduce app-switcher state.

## Library-Level Splitting

Heavy libraries should only load with the components that need them:

| Library | Size | Loaded With |
|:--------|:-----|:------------|
| ng2-charts / Chart.js | ~200KB | Chart components only |
| date-fns | ~70KB | Calendar/date picker pages only |
| @microsoft/signalr | ~50KB | Monitoring live + exceptions pages |
| Angular Reactive Forms + Zod | ~40KB | Form-heavy pages only |

## Bundle Composition Target

| Chunk | Max Size (gzipped) | Contents |
|:------|:-------------------|:---------|
| Framework | <=80KB | Angular core, Router runtime |
| Shared UI | <=40KB | Angular Material primitives, shared components |
| Per-route | <=60KB | Route-specific components + services |
| Charts | <=80KB | ng2-charts / Chart.js (loaded on demand) |
| Real-time | <=20KB | SignalR client (loaded on demand) |

## Feature-Gated Modules

Some modules and module features are gated by tenant subscription. Module sections use active module keys; feature screens use active feature keys that already include commercial inclusion and runtime flag evaluation.

```typescript
// app.routes.ts - feature-gated route
{
  path: 'work/projects',
  canActivate: [hasPermissionGuard('projects:read')],
  loadComponent: () =>
    import('./pages/work/projects/projects-page.component')
      .then(m => m.ProjectsPageComponent),
  data: { requiredFeature: 'work_management.projects' },
}
```

Components also check at render time:

```typescript
@Component({
  selector: 'app-monitoring-section',
  standalone: true,
  imports: [LiveDashboardComponent, UpgradeBannerComponent],
  template: `
    @if (authService.hasFeature('monitoring')) {
      <app-live-dashboard />
    } @else {
      <app-upgrade-banner module="Monitoring" />
    }
  `,
})
export class MonitoringSectionComponent {
  protected authService = inject(AuthService);
}
```

## Related

- [[frontend/architecture/app-structure|App Structure]] - route tree and page file structure
- [[frontend/architecture/overview|Overview]] - architecture principles
- [[frontend/architecture/module-boundaries|Module Boundaries]] - code splitting strategy
