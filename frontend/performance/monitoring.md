# Performance Monitoring

## Runtime Monitoring

### Web Vitals Collection

```tsx
// app/layout.tsx
import { useReportWebVitals } from 'next/web-vitals';

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    // Send to analytics
    analytics.track('web_vital', {
      name: metric.name,     // CLS, FID, FCP, LCP, TTFB, INP
      value: metric.value,
      rating: metric.rating, // 'good', 'needs-improvement', 'poor'
      navigationType: metric.navigationType,
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
  });

  return null;
}
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

### Next.js Built-in
- `next build --profile` for production profiling
- `NEXT_PUBLIC_DEBUG=true` for verbose hydration logging

### Bundle Analysis
```bash
# Generate bundle visualization
ANALYZE=true next build
# Opens interactive treemap showing chunk composition
```

## Related

- [[frontend/performance/budget|Budget]] — performance targets
- Code Splitting — optimization strategy
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry integration
- [[frontend/cross-cutting/analytics|Analytics]] — product analytics
