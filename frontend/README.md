# Frontend Architecture

**Angular 21** | TypeScript | Angular Material | Tailwind CSS v4 | Angular Signals | Angular Router | Reactive Forms + Zod | SignalR | Two-app monorepo

Two customer-facing apps: `employee-app` (`app.{tenant}.onevo.com`) and `management-app` (`manage.{tenant}.onevo.com`), sharing a `shared` Angular library.

---

## Architecture

Core architectural decisions and system design:

- [[frontend/architecture/overview|Overview]] — tech stack, principles, data flow, deployment
- [[frontend/architecture/app-structure|App Structure]] — monorepo workspace, route trees, layout system, Angular bootstrap
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — CSR throughout, lazy routes via `loadComponent`/`loadChildren`
- [[frontend/architecture/module-boundaries|Module Boundaries]] — code splitting, import rules, feature-gated modules, bundle targets
- [[frontend/architecture/routing|Routing]] — Angular Router typed routes, functional guards, breadcrumbs
- [[frontend/architecture/error-handling|Error Handling]] — Angular ErrorHandler, HTTP error interceptor, error pages

## Design System

Visual language, components, and interaction patterns:

### Foundations
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand, semantic, status, severity (light + dark)
- [[frontend/design-system/foundations/typography|Typography]] — font scale, monospace for data, responsive type
- [[frontend/design-system/foundations/spacing|Spacing]] — 4px base, layout spacing, component internal spacing
- [[frontend/design-system/foundations/elevation|Elevation]] — shadow scale, z-index layers, flat-by-default
- [[frontend/design-system/foundations/motion|Motion]] — Angular Animations duration scale, easing, reduced-motion
- [[frontend/design-system/foundations/iconography|Iconography]] — Material Symbols, size scale, domain icon map

### Components & Patterns
- [[frontend/design-system/components/component-catalog|Component Catalog]] — Angular Material primitives + composed components
- [[frontend/design-system/patterns/layout-patterns|Layouts]] — dashboard, list, detail page types
- [[frontend/design-system/patterns/form-patterns|Forms]] — Angular Reactive Forms + Zod, multi-step wizard, inline edit, filters
- [[frontend/design-system/patterns/table-patterns|Tables]] — MatTable, column types, sorting, pagination, bulk actions, export
- [[frontend/design-system/patterns/navigation-patterns|Navigation]] — nav rail states, topbar, Quick Search, breadcrumbs, tabs
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — ng2-charts (Chart.js), chart types per page

### Theming
- [[frontend/design-system/theming/dark-mode|Dark Mode]] — system + user preference, Angular Material color scheme
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — CSS custom property tokens, logo injection, contrast safety

## Data Layer

How the frontend fetches, caches, and syncs data:

- [[frontend/data-layer/state-management|State Management]] — Angular Signals (reactive state) + Angular Router queryParams (URL state)
- [[frontend/data-layer/api-integration|API Integration]] — typed Angular HttpClient services, functional interceptors, error handling, pagination
- [[frontend/data-layer/real-time|Real-Time (SignalR)]] — connection lifecycle, hub channels, event handlers, reconnection
- [[frontend/data-layer/caching-strategy|Caching]] — `resource()` cache, signal memoisation, prefetching, tenant scoping
- [[frontend/data-layer/file-handling|File Handling]] — upload (presigned URLs), download, preview, validation

## Cross-Cutting Concerns

Enterprise-grade concerns that touch every page:

- [[frontend/cross-cutting/authentication|Authentication]] — BFF-style HttpOnly cookie sessions, session refresh, multi-tab sync
- [[frontend/cross-cutting/authorization|Authorization (RBAC)]] — 5 levels of gating (route → sidebar → page → action → field)
- [[frontend/cross-cutting/i18n|Internationalization]] — Angular i18n, `$localize`, locale files
- [[frontend/cross-cutting/security|Security]] — CSP, Angular DomSanitizer, CSRF, sensitive data handling
- [[frontend/cross-cutting/analytics|Product Analytics]] — event taxonomy, funnel tracking, privacy-first
- [[frontend/cross-cutting/error-monitoring|Error Monitoring]] — Sentry Angular SDK, PII scrubbing, alert rules
- [[frontend/cross-cutting/feature-flags|Feature Flags]] — tenant features (plan-gated) + release flags (gradual rollout)

## Performance

Concrete targets and enforcement:

- [[frontend/performance/budget|Performance Budget]] — Web Vitals targets, bundle size limits, page load budgets
- [[frontend/performance/monitoring|Performance Monitoring]] — runtime Web Vitals, API latency, render tracking, CI regression

## Quality

- [[frontend/coding-standards|Coding Standards]] — file organisation, Angular component patterns, import order, a11y rules
- [[frontend/testing/strategy|Testing Strategy]] — Jest + Angular Testing Library + Playwright + MSW, coverage targets

## Related

- [[backend/README|Backend]] — .NET 10 / C# 14 API architecture
- [[security/README|Security]] — platform security model
- [[infrastructure/README|Infrastructure]] — deployment, cloud architecture
- [[Userflow/README|User Flows]] — end-to-end feature flows
