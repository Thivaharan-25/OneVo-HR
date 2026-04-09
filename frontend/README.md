# Frontend Architecture

**Next.js 14 App Router** | React 18 | TypeScript | TanStack Query | Zustand | shadcn/ui | Tailwind CSS | SignalR | Outfit + Geist | Violet Electric

---

## Architecture

Core architectural decisions and system design:

- [[frontend/architecture/overview|Overview]] — tech stack, principles, data flow, deployment
- [[frontend/architecture/app-structure|App Structure]] — route tree, layout system, provider stack
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR vs CSR decision matrix per route, streaming, hybrid pattern
- [[backend/module-boundaries|Module Boundaries]] — code splitting, import rules, feature-gated modules, bundle targets
- [[frontend/architecture/routing|Routing]] — route guards (middleware → layout → component), parallel routes, breadcrumbs
- [[backend/messaging/error-handling|Error Handling]] — error boundary hierarchy, error types, network resilience, chunk recovery

## Design System

Visual language, components, and interaction patterns:

### Foundations
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand, semantic, status, severity (light + dark)
- [[frontend/design-system/foundations/typography|Typography]] — Inter font scale, monospace for data, responsive type
- [[frontend/design-system/foundations/spacing|Spacing]] — 4px base, layout spacing, component internal spacing
- [[frontend/design-system/foundations/elevation|Elevation]] — shadow scale, z-index layers, flat-by-default
- [[frontend/design-system/foundations/motion|Motion]] — duration scale, easing, keyframes, reduced-motion
- [[frontend/design-system/foundations/iconography|Iconography]] — Lucide React, size scale, domain icon map

### Components & Patterns
- [[frontend/design-system/components/component-catalog|Component Catalog]] — shadcn/ui primitives + composed components
- [[frontend/design-system/patterns/layout-patterns|Layouts]] — dashboard, list, detail, dashboard page types
- [[frontend/design-system/patterns/form-patterns|Forms]] — React Hook Form + Zod, multi-step wizard, inline edit, filters
- [[frontend/design-system/patterns/table-patterns|Tables]] — DataTable, column types, sorting, pagination, bulk actions, export
- [[frontend/design-system/patterns/navigation-patterns|Navigation]] — sidebar states, topbar, command palette, breadcrumbs, tabs
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — Recharts + Tremor, chart types per page

### Theming
- [[frontend/design-system/theming/dark-mode|Dark Mode]] — system + user preference, token mapping
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — customizable tokens, logo injection, contrast safety

## Data Layer

How the frontend fetches, caches, and syncs data:

- [[frontend/data-layer/state-management|State Management]] — TanStack Query (server) + Zustand (client) + nuqs (URL)
- [[frontend/data-layer/api-integration|API Integration]] — ApiClient, endpoint organization, error handling, pagination
- [[backend/real-time|Real-Time (SignalR)]] — connection lifecycle, hub channels, event handlers, reconnection
- [[frontend/data-layer/caching-strategy|Caching]] — stale times, query keys, optimistic updates, prefetching, tenant scoping
- [[frontend/data-layer/file-handling|File Handling]] — upload (presigned URLs), download, preview, validation

## Cross-Cutting Concerns

Enterprise-grade concerns that touch every page:

- [[frontend/cross-cutting/authentication|Authentication]] — login flow, token management (in-memory), silent refresh, multi-tab sync
- [[frontend/cross-cutting/authorization|Authorization (RBAC)]] — 5 levels of gating (route → sidebar → page → action → field)
- [[frontend/cross-cutting/i18n|Internationalization]] — next-intl, ICU MessageFormat, locale resolution
- [[frontend/cross-cutting/security|Security]] — CSP, XSS prevention, CSRF, sensitive data handling, open redirect
- [[frontend/cross-cutting/analytics|Product Analytics]] — event taxonomy, funnel tracking, privacy-first
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry integration, PII scrubbing, alert rules
- [[frontend/cross-cutting/feature-flags|Feature Flags]] — tenant features (plan-gated) + release flags (gradual rollout)

## Performance

Concrete targets and enforcement:

- [[frontend/performance/budget|Performance Budget]] — Web Vitals targets, bundle size limits, page load budgets
- [[frontend/performance/monitoring|Performance Monitoring]] — runtime Web Vitals, API latency, render tracking, CI regression

## Quality

- [[frontend/coding-standards|Coding Standards]] — file organization, component patterns, import order, a11y rules
- [[frontend/testing/strategy|Testing Strategy]] — Vitest + RTL + Playwright + MSW, coverage targets

## Related

- [[backend/README|Backend]] — .NET 9 API architecture
- [[security/README|Security]] — platform security model
- [[infrastructure/README|Infrastructure]] — deployment, cloud architecture
- [[Userflow/README|User Flows]] — end-to-end feature flows
