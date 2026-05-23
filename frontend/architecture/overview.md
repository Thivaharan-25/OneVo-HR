# Frontend Architecture Overview

## Tech Stack

| Layer | Technology | Version | Rationale |
|:------|:-----------|:--------|:----------|
| Framework | Angular | 21.x | Standalone components, signals, typed routes, official enterprise support |
| Build Tool | Angular CLI (esbuild) | 21.x | Fast builds, differential loading, `ng build` / `ng serve` |
| Language | TypeScript | 5.x | Type safety across API boundary, refactoring confidence |
| Styling | Tailwind CSS | 4.x | Utility-first, design token mapping, tree-shaking |
| Components | Angular Material | 21.x | Accessible Material Design primitives, Angular CDK, full customisation |
| Reactive State | Angular Signals | Built-in | `signal()`, `computed()`, `effect()` — no NgRx in Phase 1 |
| URL State | Angular Router `queryParams` | Built-in | Built-in, no extra dependency, shareable filter states |
| HTTP | Angular `HttpClient` | Built-in | `resource()` + `toSignal()` for signal integration, functional interceptors |
| Real-time | SignalR (@microsoft/signalr) | Latest | .NET ecosystem alignment, auto-reconnect, hub protocol |
| Charts | ng2-charts (Chart.js) | Latest | Composable charts, tree-shakeable, CSR-compatible |
| Forms | Angular Reactive Forms + Zod | Built-in + Latest | Type-safe form groups, schema-first cross-field validation |
| Testing | Jest + Angular Testing Library + Playwright + MSW | Latest | Fast unit tests, behaviour-driven component tests, real E2E |

## Two-App Monorepo

ONEVO has two separate Angular apps in one Angular workspace:

| App | URL | Persona | Bundle goal |
|:----|:----|:--------|:------------|
| `employee-app` | `app.{tenant}.onevo.com` | Employee self-service | Lean — only employee features, fast load |
| `management-app` | `manage.{tenant}.onevo.com` | HR / Admin / Manager / Executive | Full — analytics, monitoring, configuration |

A `shared` Angular library is built once and imported by both apps. It contains auth, API services, SignalR, design system components, and shared models.

Dual-role users (e.g. team leads) see a context-switcher in the header. Both apps share the same JWT session cookie (same parent domain) — switching apps requires no re-login.

## Architecture Principles

### 1. Client-Side Rendering (CSR) Throughout
Both apps are Angular CSR SPAs — there is no SSR, no universal rendering. All rendering happens in the browser. Data fetching uses Angular `HttpClient` with signals. Loading states use `@if (resource.isLoading())` or `<mat-progress-bar>`. This is intentional — the app is behind authentication and SEO is not a concern.

### 2. Standalone Components Only
Every `@Component`, `@Directive`, and `@Pipe` must be `standalone: true`. No NgModules. Feature isolation is achieved through directory structure and import boundaries, not module declarations.

### 3. Signals as the Reactive Model
- **Reactive state** (`signal()` / `computed()` / `effect()`): all component and service state
- **URL state** (Angular Router `queryParams`): anything the user should be able to bookmark or share
- **Never duplicate** server state into a separate signal — derive it from `resource()` or `toSignal()`
- **No RxJS `BehaviorSubject`** for UI state — signals replace it entirely

### 4. Permission-Driven Rendering
Every route guard, sidebar section, button, and data column respects RBAC. Permissions flow from backend session metadata → `AuthService` → `*hasPermission` structural directive and `authService.hasPermission()`. The UI never shows actions the user cannot perform.

### 5. Real-Time as a Cache Invalidation Signal
SignalR pushes are **invalidation signals**, not primary data sources. When a push arrives, the relevant `resource()` is reloaded — the API remains the source of truth. This keeps the data layer testable and avoids split-brain state.

### 6. Tenant Isolation at Every Layer
- API requests include `X-Tenant-Id` header (set by `TenantInterceptor` from auth state)
- Signal resource keys include `tenantId` to prevent cross-tenant data leakage
- Theming tokens are tenant-configurable (logo, primary colour, accent)
- Feature flags are tenant-scoped

## High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Browser (Angular 21 CSR SPA)                                │
│                                                              │
│  ┌──────────────────────┐   ┌──────────────────────────┐    │
│  │  Angular Components  │   │  SignalR WebSocket        │    │
│  │  (standalone, CSR)   │   │  (push notifications)    │    │
│  └──────────┬───────────┘   └──────────────┬───────────┘    │
│             │                              │                 │
│             │               resource.reload() on push        │
│             │                              │                 │
│  ┌──────────▼───────────────────────────── ▼──────────────┐  │
│  │  resource() / toSignal()  ←  HttpClient services       │  │
│  │  (signals-based async data layer)                      │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │  Functional HttpInterceptors (auth, tenant, retry)   │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────┐
│  .NET 10 API (single ONEVO.Api host)      │
│  /api/v1/*  (customer)                   │
│  /hubs/*    (SignalR)                    │
└──────────────────────────────────────────┘
```

## Deployment Architecture

| Concern | Strategy |
|:--------|:---------|
| Hosting | Azure Static Web Apps (or equivalent static host — Angular CLI outputs `dist/`) |
| CDN | Azure CDN for static assets |
| Environment Config | `environment.ts` / `environment.prod.ts` per environment — accessed via Angular's environment injection |
| Preview Deployments | Per-PR preview URLs via Azure Static Web Apps staging slots |
| Static Assets | Immutable hashing, `Cache-Control: max-age=31536000, immutable` |
| API Proxy | Configure nginx or Azure CDN to proxy `/api/v1/**` to backend (avoids CORS) |
| Security Headers | Set via nginx or CDN rules in production — see `frontend/cross-cutting/security.md` |
| Build commands | `ng build employee-app` / `ng build management-app` (separate dist outputs per app) |

## Related

- [[frontend/architecture/app-structure|App Structure]] — monorepo workspace, route trees, and Angular bootstrap
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — lazy loading, deferred views
- [[frontend/architecture/module-boundaries|Module Boundaries]] — code splitting and isolation rules
- [[frontend/architecture/routing|Routing]] — typed routes, functional guards, breadcrumbs
- [[frontend/architecture/error-handling|Error Handling]] — Angular ErrorHandler, error pages
