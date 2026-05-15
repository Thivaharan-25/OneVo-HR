# Frontend Architecture

**Vite + React 19 + React Router v7** | TypeScript | TanStack Query | Zustand | shadcn/ui | Tailwind CSS v4 | SignalR | Outfit + Geist | Violet Electric

---

## Architecture

Core architectural decisions and system design:

- [[frontend/architecture/overview|Overview]] â€” tech stack, principles, data flow, deployment
- [[frontend/architecture/app-structure|App Structure]] â€” route tree, layout system, provider stack
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] â€” CSR throughout, Suspense boundaries, React.lazy for heavy routes/components
- [[backend/module-boundaries|Module Boundaries]] â€” code splitting, import rules, feature-gated modules, bundle targets
- [[frontend/architecture/routing|Routing]] â€” React Router v7 route config, ProtectedRoute guard, edit panels via state, breadcrumbs
- [[backend/messaging/error-handling|Error Handling]] â€” error boundary hierarchy, error types, network resilience, chunk recovery

## Design System

Visual language, components, and interaction patterns:

### Foundations
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] â€” brand, semantic, status, severity (light + dark)
- [[frontend/design-system/foundations/typography|Typography]] â€” Outfit + Geist font scale, monospace for data, responsive type
- [[frontend/design-system/foundations/spacing|Spacing]] â€” 4px base, layout spacing, component internal spacing
- [[frontend/design-system/foundations/elevation|Elevation]] â€” shadow scale, z-index layers, flat-by-default
- [[frontend/design-system/foundations/motion|Motion]] â€” duration scale, easing, keyframes, reduced-motion
- [[frontend/design-system/foundations/iconography|Iconography]] â€” Lucide React, size scale, domain icon map

### Components & Patterns
- [[frontend/design-system/components/component-catalog|Component Catalog]] â€” shadcn/ui primitives + composed components
- [[frontend/design-system/patterns/layout-patterns|Layouts]] â€” dashboard, list, detail, dashboard page types
- [[frontend/design-system/patterns/form-patterns|Forms]] â€” React Hook Form + Zod, multi-step wizard, inline edit, filters
- [[frontend/design-system/patterns/table-patterns|Tables]] â€” DataTable, column types, sorting, pagination, bulk actions, export
- [[frontend/design-system/patterns/navigation-patterns|Navigation]] â€” sidebar states, topbar, Quick Search, breadcrumbs, tabs
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] â€” Recharts + Tremor, chart types per page

### Theming
- [[frontend/design-system/theming/dark-mode|Dark Mode]] â€” system + user preference, token mapping
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] â€” customizable tokens, logo injection, contrast safety

## Data Layer

How the frontend fetches, caches, and syncs data:

- [[frontend/data-layer/state-management|State Management]] â€” TanStack Query (server) + Zustand (client) + React Router useSearchParams (URL)
- [[frontend/data-layer/api-integration|API Integration]] â€” ApiClient, endpoint organization, error handling, pagination
- [[backend/real-time|Real-Time (SignalR)]] â€” connection lifecycle, hub channels, event handlers, reconnection
- [[frontend/data-layer/caching-strategy|Caching]] â€” stale times, query keys, optimistic updates, prefetching, tenant scoping
- [[frontend/data-layer/file-handling|File Handling]] â€” upload (presigned URLs), download, preview, validation

## Cross-Cutting Concerns

Enterprise-grade concerns that touch every page:

- [[frontend/cross-cutting/authentication|Authentication]] - BFF-style HttpOnly cookie sessions, session refresh, multi-tab sync
- [[frontend/cross-cutting/authorization|Authorization (RBAC)]] â€” 5 levels of gating (route â†’ sidebar â†’ page â†’ action â†’ field)
- [[frontend/cross-cutting/i18n|Internationalization]] â€” i18next, ICU MessageFormat, locale resolution
- [[frontend/cross-cutting/security|Security]] â€” CSP, XSS prevention, CSRF, sensitive data handling, open redirect
- [[frontend/cross-cutting/analytics|Product Analytics]] â€” event taxonomy, funnel tracking, privacy-first
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] â€” Sentry integration, PII scrubbing, alert rules
- [[frontend/cross-cutting/feature-flags|Feature Flags]] â€” tenant features (plan-gated) + release flags (gradual rollout)

## Performance

Concrete targets and enforcement:

- [[frontend/performance/budget|Performance Budget]] â€” Web Vitals targets, bundle size limits, page load budgets
- [[frontend/performance/monitoring|Performance Monitoring]] â€” runtime Web Vitals, API latency, render tracking, CI regression

## Quality

- [[frontend/coding-standards|Coding Standards]] â€” file organization, component patterns, import order, a11y rules
- [[frontend/testing/strategy|Testing Strategy]] â€” Vitest + RTL + Playwright + MSW, coverage targets

## Related

- [[backend/README|Backend]] â€” .NET 9 current / .NET 10 target API architecture
- [[security/README|Security]] â€” platform security model
- [[infrastructure/README|Infrastructure]] â€” deployment, cloud architecture
- [[Userflow/README|User Flows]] â€” end-to-end feature flows
