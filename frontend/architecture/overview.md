# Frontend Architecture Overview

## Tech Stack

| Layer | Technology | Version | Rationale |
|:------|:-----------|:--------|:----------|
| Build Tool | Vite | 8.x | Fast HMR, ESM-native, no SSR complexity |
| UI Library | React | 19.x | Component model, Suspense, concurrent features |
| Routing | React Router | v7 | SPA routing, nested layouts, `<Outlet />` |
| Language | TypeScript | 5.x | Type safety across API boundary, refactoring confidence |
| Styling | Tailwind CSS | 4.x | Utility-first, design token mapping, tree-shaking |
| Components | shadcn/ui + Radix | Latest | Accessible primitives, full customization, no lock-in |
| Server State | TanStack Query | v5 | Cache management, background sync, optimistic updates |
| Client State | Zustand | 4.x | Lightweight, no boilerplate, middleware for persistence |
| URL State | React Router `useSearchParams` | v7 | Built-in, no extra dependency, shareable filter states |
| Real-time | SignalR (@microsoft/signalr) | Latest | .NET ecosystem alignment, auto-reconnect, hub protocol |
| Charts | Recharts | Latest | Composable charts, works in CSR |
| Forms | React Hook Form + Zod | Latest | Performance (uncontrolled), schema-first validation |
| Testing | Vitest + RTL + Playwright + MSW | Latest | Fast unit tests, behavior-driven component tests, real E2E |

## Architecture Principles

### 1. Client-Side Rendering (CSR) Throughout
This is a Vite SPA â€” there are no Server Components, no SSR, no `'use client'` directives. All rendering happens in the browser. Data fetching is handled by TanStack Query. Loading states use React Suspense boundaries. This is intentional â€” the app is behind authentication and SEO is not a concern.

### 2. Module Isolation
Each product domain (Core HR, Workforce Intelligence, Payroll, etc.) owns its own:
- Route group under `app/(dashboard)/`
- Feature components under `components/{module}/`
- API hooks under `hooks/{module}/`
- Types under `types/{module}.ts`

Cross-module imports go through `components/shared/` or `hooks/shared/` â€” never directly between modules.

### 3. Data Ownership Is Clear
- **Server state** (TanStack Query): anything that came from the API
- **Client state** (Zustand): ephemeral UI state (sidebar, modals, preferences)
- **URL state** (React Router `useSearchParams`): anything the user should be able to bookmark or share
- **Never duplicate** server state into client state

### 4. Permission-Driven Rendering
Every route, sidebar section, button, and data column respects RBAC. Permissions flow from backend session metadata -> AuthStore -> `<PermissionGate>` wrappers and `useHasPermission()` hooks. The UI never shows actions the user can't perform.

### 5. Real-Time as an Overlay
SignalR pushes are **cache invalidation signals**, not primary data sources. When a push arrives, TanStack Query refetches â€” the API remains the source of truth. This keeps the data layer testable and avoids split-brain state.

### 6. Tenant Isolation at Every Layer
- API requests include `X-Tenant-Id` header (set by ApiClient from auth context)
- TanStack Query keys include `tenantId` to prevent cross-tenant cache pollution
- Theming tokens are tenant-configurable (logo, primary color, accent)
- Feature flags are tenant-scoped

## High-Level Data Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Browser                                                         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ React Server â”‚   â”‚ Client       â”‚   â”‚ SignalR              â”‚ â”‚
â”‚  â”‚ Components   â”‚   â”‚ Components   â”‚   â”‚ WebSocket            â”‚ â”‚
â”‚  â”‚ (SSR data)   â”‚   â”‚ (interactive)â”‚   â”‚ (push notifications) â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚         â”‚                  â”‚                       â”‚             â”‚
â”‚         â”‚           â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”               â”‚             â”‚
â”‚         â”‚           â”‚ TanStack     â”‚â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜             â”‚
â”‚         â”‚           â”‚ Query Cache  â”‚  invalidate on push         â”‚
â”‚         â”‚           â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜                             â”‚
â”‚         â”‚                  â”‚                                     â”‚
â”‚         â”‚           â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”                             â”‚
â”‚         â”‚           â”‚ ApiClient    â”‚                             â”‚
â”‚         â”‚           â”‚ (interceptorsâ”‚                             â”‚
â”‚         â”‚           â”‚  auth, retry)â”‚                             â”‚
â”‚         â”‚           â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜                             â”‚
â”‚         â”‚                  â”‚                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â”‚                  â”‚
          â–¼                  â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  .NET 9 current API Gateway (per-tenant)â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ Core HR  â”‚ â”‚ Workforceâ”‚ â”‚ Payroll â”‚ â”‚
â”‚  â”‚ Service  â”‚ â”‚ Service  â”‚ â”‚ Service â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Deployment Architecture

| Concern | Strategy |
|:--------|:---------|
| Hosting | Azure Static Web Apps or any static host (Vite outputs `dist/`) |
| CDN | Azure CDN for static assets |
| Environment Config | `VITE_*` env vars per environment â€” accessed via `import.meta.env.VITE_*` |
| Preview Deployments | Per-PR preview URLs via Azure Static Web Apps staging slots |
| Static Assets | Immutable hashing, `Cache-Control: max-age=31536000, immutable` |
| API Proxy | Configure nginx or Azure CDN to proxy `/api/v1/**` to backend (avoids CORS) |
| Security Headers | Set via nginx or CDN rules in production â€” see `frontend/cross-cutting/security.md` |

## Related

- [[frontend/architecture/app-structure|App Structure]] â€” route tree and layout hierarchy
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] â€” SSR vs CSR decision matrix
- [[backend/module-boundaries|Module Boundaries]] â€” code splitting and isolation rules
- [[frontend/architecture/routing|Routing]] â€” route guards, middleware, parallel routes
- [[backend/messaging/error-handling|Error Handling]] â€” error boundary hierarchy


