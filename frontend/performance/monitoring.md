# Performance Monitoring

## Runtime Monitoring

### Web Vitals Collection

Uses the `web-vitals` npm package — not any Next.js or React-specific API.

```typescript
// shared/src/lib/performance/web-vitals.service.ts
import { Injectable } from '@angular/core';
import { inject } from '@angular/core';
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';
import { AnalyticsService } from '../analytics/analytics.service';

@Injectable({ providedIn: 'root' })
export class WebVitalsService {
  private analytics = inject(AnalyticsService);

  init() {
    const report = (metric: { name: string; value: number; rating: string }) => {
      this.analytics.track('web_vital', {
        name: metric.name,      // CLS, INP, FCP, LCP, TTFB
        value: metric.value,
        rating: metric.rating,  // 'good' | 'needs-improvement' | 'poor'
        page: location.pathname,
      });

      if (metric.rating === 'poor') {
        // Alert on poor vitals in production
        console.warn(`Poor Web Vital: ${metric.name}`, metric);
      }
    };

    onCLS(report);
    onINP(report);
    onLCP(report);
    onFCP(report);
    onTTFB(report);
  }
}
```

Initialize in `APP_INITIALIZER`:

```typescript
// app.config.ts
{
  provide: APP_INITIALIZER,
  useFactory: () => {
    const vitals = inject(WebVitalsService);
    return () => vitals.init();
  },
  multi: true,
}
```

### API Latency Tracking

Track slow HTTP calls via an Angular `HttpInterceptorFn`:

```typescript
// shared/src/lib/api/interceptors/timing.interceptor.ts
export const timingInterceptor: HttpInterceptorFn = (req, next) => {
  const start = performance.now();

  return next(req).pipe(
    tap(() => {
      const duration = performance.now() - start;
      if (duration > 3000) {
        console.warn('Slow API call', { url: req.url, durationMs: Math.round(duration) });
        // Send to analytics / Sentry
      }
    }),
  );
};
```

### Component Render Tracking

For critical paths, use the `performance` API in Angular lifecycle hooks:

```typescript
// Tracks initial render time of a heavy component
export class LiveDashboardComponent implements AfterViewInit {
  private readonly startTime = performance.now();

  ngAfterViewInit() {
    const renderTime = performance.now() - this.startTime;
    if (renderTime > 100) {
      console.warn('Slow render: LiveDashboardComponent', { renderTimeMs: Math.round(renderTime) });
    }
  }
}
```

## Dashboards & Alerts

### Key Metrics

| Metric | Source | Alert Threshold |
|:-------|:-------|:----------------|
| p75 LCP | Web Vitals | >2.5s |
| p75 INP | Web Vitals | >200ms |
| p95 API latency | Timing interceptor | >3s |
| JS error rate | Sentry Angular SDK | >1% of sessions |
| Bundle size (initial) | Angular CLI CI | >240KB gzipped |
| Lighthouse score | Lighthouse CI | <85 |

### Performance Regression Detection

CI runs Lighthouse on every PR:

```yaml
assertions:
  categories:performance:
    - error
  largest-contentful-paint:
    - warn: 2500
    - error: 4000
  total-blocking-time:
    - warn: 300
    - error: 600
  cumulative-layout-shift:
    - warn: 0.1
    - error: 0.25
```

## Performance Debugging

### Angular DevTools

- Install the [Angular DevTools](https://angular.dev/tools/devtools) browser extension
- **Component Tree tab** — inspect component hierarchy, input/output signals, change detection state
- **Profiler tab** — record change detection cycles, identify components with excessive re-renders
- **Signals tab** — inspect reactive signal values and their dependencies

### Angular CLI Bundle Analysis

```bash
# Generate bundle stats JSON
ng build employee-app --stats-json

# View with webpack-bundle-analyzer (works with Angular CLI esbuild output via esbuild-bundle-analyzer)
npx esbuild-bundle-analyzer dist/employee-app/stats.json
```

This opens an interactive treemap showing chunk composition and why packages are included.

### Change Detection Profiling

Enable `NgZone` instrumentation in development to find unexpected change detection triggers:

```typescript
// main.ts (development only)
bootstrapApplication(AppComponent, {
  ...appConfig,
  providers: [
    ...appConfig.providers,
    { provide: NgZone, useClass: NgZone, useFactory: () => new NgZone({ enableLongStackTrace: true }) },
  ],
});
```

> This is a CSR-only SPA. There is no SSR hydration step. Any references to server-side rendering or hydration debugging do not apply here.

## Related

- [[frontend/performance/budget|Budget]] — performance targets and bundle budgets
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — lazy loading and `@defer`
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry Angular SDK
- [[frontend/cross-cutting/analytics|Analytics]] — product analytics
