# Performance Budget

## Core Web Vitals Targets

| Metric | Target | Threshold | Measurement |
|:-------|:-------|:----------|:------------|
| **LCP** (Largest Contentful Paint) | ≤1.5s | ≤2.5s | Dashboard page load |
| **FID** (First Input Delay) | ≤50ms | ≤100ms | First interaction response |
| **INP** (Interaction to Next Paint) | ≤100ms | ≤200ms | Any interaction |
| **CLS** (Cumulative Layout Shift) | ≤0.05 | ≤0.1 | No layout shifts after skeleton |
| **TTFB** (Time to First Byte) | ≤200ms | ≤500ms | Server response time |
| **FCP** (First Contentful Paint) | ≤1.0s | ≤1.5s | First visible content |

## Bundle Size Budget

| Chunk | Budget (gzipped) | Alert At | Action |
|:------|:-----------------|:---------|:-------|
| Framework (React + Vite runtime) | ≤90KB | >95KB | Audit imports, check for duplicates |
| Shared UI (shadcn + shared components) | ≤40KB | >45KB | Review composed components |
| Per-route chunk (largest) | ≤60KB | >70KB | Split heavy components, lazy load |
| Charts (Recharts + Tremor) | ≤80KB | >90KB | Ensure charts are lazy loaded |
| SignalR client | ≤20KB | >25KB | Only loaded on real-time pages |
| Total initial JS (critical path) | ≤200KB | >220KB | Audit everything |
| Total initial CSS | ≤30KB | >35KB | Purge unused Tailwind |

## Page Load Budgets

| Page | Target Load Time | Max JS | Notes |
|:-----|:----------------|:-------|:------|
| Login | ≤1.0s | ≤80KB | Minimal JS and fast client render |
| Dashboard Overview | ≤1.5s | ≤180KB | App shell + lazy dashboard cards |
| Employee List | ≤1.2s | ≤150KB | App shell + client table |
| Employee Detail | ≤1.5s | ≤160KB | Client header + tabs |
| Workforce Live | ≤2.0s | ≤250KB | Charts + SignalR (heavier) |
| Leave Calendar | ≤1.5s | ≤170KB | Calendar component |
| Settings | ≤1.0s | ≤100KB | Mostly static |

## Enforcement

### CI Checks

```yaml
# In CI pipeline
- name: Bundle size check
  run: |
    npm run build
    npx vite-bundle-visualizer
    # Fail if any chunk exceeds budget
    node scripts/check-bundle-budget.js
```

### Lighthouse CI

```yaml
- name: Lighthouse CI
  run: |
    npx lhci autorun
  # Asserts:
  # - Performance score ≥ 90
  # - LCP ≤ 2.5s
  # - CLS ≤ 0.1
  # - Total blocking time ≤ 300ms
```

### Import Cost Awareness

Use `eslint-plugin-import` to flag heavy imports:

```json
{
  "rules": {
    "no-restricted-imports": ["error", {
      "paths": [
        { "name": "lodash", "message": "Import specific functions: lodash/debounce" },
        { "name": "date-fns", "message": "Import specific functions: date-fns/format" },
        { "name": "recharts", "message": "Use dynamic import for chart components" }
      ]
    }]
  }
}
```

## Optimization Techniques

### Image Optimization
- Use native responsive images or an app-level image component; do not use `next/image`
- Avatar images: 64x64 and 128x128 variants generated server-side
- Max upload size for profile photos: 5MB (resized server-side)

### Font Optimization
- Outfit, Geist, and JetBrains Mono loaded via CSS/font assets with preconnect/preload as needed
- `font-display: swap` for fastest text render

### CSS Optimization
- Tailwind CSS purge removes unused classes (typically 95%+ reduction)
- No CSS-in-JS runtime (Tailwind is build-time only)

### Prefetch Strategy
- React Router/TanStack Query prefetch: on hover or viewport intent for high-value links
- TanStack Query prefetch: on hover for table rows → detail pages
- Next page prefetch: prefetch page N+1 when viewing page N

## Related

- Code Splitting — dynamic imports and lazy loading
- [[frontend/performance/monitoring|Monitoring]] — runtime performance monitoring
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — CSR, Suspense, and route-level lazy loading
- [[backend/module-boundaries|Module Boundaries]] — bundle composition
