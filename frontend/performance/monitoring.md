# Performance Monitoring

## Runtime Monitoring

### Web Vitals Collection

Uses the `web-vitals` npm package directly — **not** `next/web-vitals` (that is Next.js-only).

```tsx
// lib/web-vitals.ts
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

export function initWebVitals() {
  const report = (metric: { name: string; value: number; rating: string; navigationType?: string }) => {
    // Send to analytics
    analytics.track('web_vital', {
      name: metric.name,     // CLS, INP, FCP, LCP, TTFB
      value: metric.value,
      rating: metric.rating, // 'good' | 'needs-improvement' | 'poor'
      page: window.location.pathname,
    });

    // Alert on poor vitals in production
    if (metric.rating === 'poor') {
      Sentry.captureMessage(`Poor Web Vital: ${metric.name}`, {
        level: 'warning',
        tags: { vital: metric.name, rating: metric.rating },
        extra: { value: metric.value, page: window.location.pathname },
      });
    }
  };

  onCLS(report);
  onINP(report);
  onLCP(report);
  onFCP(report);
  onTTFB(report);
}

// src/main.tsx — call after mount
initWebVitals();
```

### API Latency Tracking

```tsx
// Track slow API calls
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      meta: {
        onSettled: (data: unknown, error: unknown, query: Query) => {
          const duration = query.state.dataUpdatedAt - query.state.fetchMeta?.startTime;
          if (duration > 3000) {
            // Flag slow queries
            Sentry.captureMessage('Slow API query', {
              level: 'warning',
              extra: {
                queryKey: query.queryKey,
                duration,
                page: window.location.pathname,
              },
            });
          }
        },
      },
    },
  },
});
```

### Component Render Tracking

For critical paths, track render performance:

```tsx
// hooks/use-render-performance.ts
export function useRenderPerformance(componentName: string) {
  const startTime = useRef(performance.now());

  useEffect(() => {
    const renderTime = performance.now() - startTime.current;
    if (renderTime > 100) { // >100ms is slow
      analytics.track('slow_render', {
        component: componentName,
        renderTimeMs: Math.round(renderTime),
        page: window.location.pathname,
      });
    }
  }, []);
}

// Usage in heavy components
function LiveDashboard() {
  useRenderPerformance('LiveDashboard');
  // ...
}
```

## Dashboards & Alerts

### Key Metrics Dashboard

| Metric | Source | Alert Threshold |
|:-------|:-------|:----------------|
| p75 LCP | Web Vitals | >2.5s |
| p75 INP | Web Vitals | >200ms |
| p95 API latency | ApiClient timing | >3s |
| JS error rate | Sentry | >1% of sessions |
| Bundle size (main) | CI | >220KB gzipped |
| Lighthouse score | Lighthouse CI | <85 |

### Performance Regression Detection

CI runs Lighthouse on every PR against the base branch:

```yaml
assertions:
  categories:performance:
    - error            # Fail PR if perf score drops below threshold
  largest-contentful-paint:
    - warn: 2500       # Warn if LCP > 2.5s
    - error: 4000      # Fail if LCP > 4s
  total-blocking-time:
    - warn: 300
    - error: 600
  cumulative-layout-shift:
    - warn: 0.1
    - error: 0.25
```

## Performance Debugging

### React DevTools Profiler
- Identify unnecessary re-renders
- Find slow component trees
- Measure render duration per commit

### Vite Bundle Analysis

```bash
# Install visualizer plugin (dev dependency)
npm install -D rollup-plugin-visualizer

# vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true, gzipSize: true, brotliSize: true }),
  ],
});

# Run build — opens interactive treemap showing chunk composition
npm run build
```

### React DevTools Profiler
- Identify unnecessary re-renders
- Find slow component trees
- Measure render duration per commit

> **No hydration debugging** — this is a CSR-only SPA. There is no SSR hydration step. If you see `NEXT_PUBLIC_DEBUG` or `next build --profile` referenced anywhere, those are Next.js concepts that do not apply here.

## Related

- [[frontend/performance/budget|Budget]] — performance targets
- Code Splitting — optimization strategy
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry integration
- [[frontend/cross-cutting/analytics|Analytics]] — product analytics
