# Performance Budget

## Core Web Vitals Targets

| Metric | Target | Threshold | Measurement |
|:-------|:-------|:----------|:------------|
| **LCP** (Largest Contentful Paint) | ≤1.5s | ≤2.5s | Dashboard page load |
| **INP** (Interaction to Next Paint) | ≤100ms | ≤200ms | Any interaction |
| **CLS** (Cumulative Layout Shift) | ≤0.05 | ≤0.1 | No layout shifts after skeleton |
| **TTFB** (Time to First Byte) | ≤200ms | ≤500ms | Server response time |
| **FCP** (First Contentful Paint) | ≤1.0s | ≤1.5s | First visible content |

## Bundle Size Budget

Angular CLI (esbuild) produces separate named chunks per lazy route. Budgets are enforced in `angular.json`.

| Chunk | Budget (gzipped) | Alert At | Action |
|:------|:-----------------|:---------|:-------|
| Framework (Angular runtime + common) | ≤120KB | >130KB | Audit barrel imports, check for duplicate providers |
| Shared library (`@onevo/shared`) initial | ≤50KB | >60KB | Review what is eagerly imported |
| Angular Material (initial) | ≤40KB | >50KB | Import only used Material modules |
| Per-route chunk (largest) | ≤60KB | >70KB | Split heavy components, use `@defer` |
| Charts (ng2-charts + Chart.js) | ≤80KB | >90KB | Always lazy-load chart components |
| SignalR client | ≤20KB | >25KB | Only loaded on real-time pages |
| Total initial JS (critical path) | ≤220KB | >240KB | Audit everything |
| Total initial CSS (Tailwind purged) | ≤30KB | >35KB | Check Tailwind content paths |

### Enforcing in `angular.json`

```json
{
  "budgets": [
    { "type": "initial", "maximumWarning": "220kb", "maximumError": "280kb" },
    { "type": "anyComponentStyle", "maximumWarning": "4kb", "maximumError": "8kb" },
    { "type": "anyScript", "maximumWarning": "60kb", "maximumError": "80kb" }
  ]
}
```

## Page Load Budgets

| Page | Target Load Time | Notes |
|:-----|:----------------|:------|
| Login | ≤1.0s | Minimal Angular shell, no charts |
| Home (employee) | ≤1.5s | App shell + lazy dashboard cards |
| Home (management dashboard) | ≤1.5s | App shell + pending actions widget |
| Employee List | ≤1.2s | MatTable + lazy data |
| Employee Detail | ≤1.5s | MatTabGroup + lazy section data |
| Workforce Live | ≤2.0s | Charts + SignalR (heavier) |
| Leave Calendar | ≤1.5s | Calendar component (lazy) |
| Settings | ≤1.0s | Mostly static form |

## Responsive Performance Budget

| Concern | Requirement |
|:--------|:------------|
| Mobile initial JS | Keep critical mobile shell and first page under the same initial budget; `@defer` charts, heavy tables, non-visible panels |
| Dashboard cards | Render primary action cards first; defer lower-priority analytics until visible |
| Navigation drawers | Drawer open/close must avoid layout shift; do not mount heavy page content in drawer |
| Data tables | Mobile card/list views reuse loaded data; avoid loading desktop-only column renderers when hidden |
| Avatars / images | Use responsive image sizes and reserve dimensions (width/height attributes) to avoid CLS |
| Touch interactions | Keep INP within target for filters, drawer navigation, row actions, and form submission |

Rules:
- Do not load chart libraries on mobile until the chart section is visible or explicitly opened.
- Do not render hidden desktop panels on mobile/tablet if they contain expensive data or charts.
- Use skeleton dimensions that match final mobile and desktop layouts to avoid CLS.

## Optimization Techniques

### Lazy Loading (Angular Router)

Every feature route must use `loadComponent` or `loadChildren`:

```typescript
// ✅ Correct — lazy loaded
{ path: 'workforce', loadComponent: () => import('./features/workforce/live-dashboard.component').then(m => m.LiveDashboardComponent) }

// ❌ Wrong — eager import kills initial bundle
import { LiveDashboardComponent } from './features/workforce/live-dashboard.component';
{ path: 'workforce', component: LiveDashboardComponent }
```

### `@defer` for Heavy In-Page Components

```html
<!-- Org chart only loads when the tab becomes visible -->
@defer (on viewport) {
  <app-org-chart [data]="orgData()" />
} @placeholder {
  <app-chart-skeleton height="400" />
}

<!-- Kanban board deferred until project board tab is active -->
@defer (when boardTabActive()) {
  <app-kanban-board [projectId]="projectId()" />
} @loading (minimum 300ms) {
  <app-board-skeleton />
}
```

Apply `@defer` to: org charts, kanban boards, roadmap timelines, activity heatmaps, rich text editors, and any chart component.

### `OnPush` Change Detection

Use `ChangeDetectionStrategy.OnPush` on all display components that receive data via `@Input()` or signals:

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  // ...
})
export class EmployeeCardComponent {
  employee = input.required<Employee>();
}
```

### Font Optimization

- Load fonts via `@font-face` in global CSS with `font-display: swap`
- Use `<link rel="preconnect">` and `<link rel="preload">` for above-the-fold fonts

### CSS Optimization

- Tailwind CSS v4 purges unused classes at build time (typically 95%+ reduction)
- Per-component SCSS is tree-shaken by Angular CLI — no runtime CSS-in-JS overhead

### Import Cost Awareness

```json
// .eslintrc — flag heavy barrel imports
{
  "rules": {
    "no-restricted-imports": ["error", {
      "paths": [
        { "name": "chart.js", "message": "Import only needed Chart.js modules" },
        { "name": "date-fns", "message": "Import specific functions: date-fns/format" }
      ]
    }]
  }
}
```

## Enforcement

### CI — Angular Budget Check

Angular CLI fails the build when budgets are exceeded:

```bash
ng build employee-app --configuration=production
# Fails if any budget from angular.json is exceeded
```

### Lighthouse CI

```yaml
- name: Lighthouse CI
  run: npx lhci autorun
  # Asserts:
  # - Performance score ≥ 90
  # - LCP ≤ 2.5s
  # - CLS ≤ 0.1
  # - Total blocking time ≤ 300ms
```

## Related

- [[frontend/performance/monitoring|Performance Monitoring]] — runtime Web Vitals tracking
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — lazy loading, @defer, OnPush
- [[frontend/architecture/module-boundaries|Module Boundaries]] — bundle composition
