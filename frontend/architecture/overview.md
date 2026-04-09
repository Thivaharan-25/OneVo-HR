# Frontend Architecture Overview

## Tech Stack

| Layer | Technology | Version | Rationale |
|:------|:-----------|:--------|:----------|
| Framework | Next.js (App Router) | 14.x | SSR/SSG flexibility, file-based routing, RSC support |
| UI Library | React | 18.x | Component model, ecosystem, RSC compatibility |
| Language | TypeScript | 5.x | Type safety across API boundary, refactoring confidence |
| Styling | Tailwind CSS | 3.x | Utility-first, design token mapping, tree-shaking |
| Components | shadcn/ui + Radix | Latest | Accessible primitives, full customization, no lock-in |
| Server State | TanStack Query | v5 | Cache management, background sync, optimistic updates |
| Client State | Zustand | 4.x | Lightweight, no boilerplate, middleware for persistence |
| URL State | nuqs | Latest | Type-safe URL params, shareable filter states |
| Real-time | SignalR (@microsoft/signalr) | Latest | .NET ecosystem alignment, auto-reconnect, hub protocol |
| Charts | Recharts + Tremor | Latest | Composable charts + dashboard-ready KPI blocks |
| Forms | React Hook Form + Zod | Latest | Performance (uncontrolled), schema-first validation |
| Testing | Vitest + RTL + Playwright + MSW | Latest | Fast unit tests, behavior-driven component tests, real E2E |

## Architecture Principles

### 1. Server-First, Client When Needed
Default to React Server Components for data fetching and static content. Use `'use client'` only when interactivity requires it (forms, real-time, client state). This minimizes JS shipped to the browser.

### 2. Module Isolation
Each product domain (Core HR, Workforce Intelligence, Payroll, etc.) owns its own:
- Route group under `app/(dashboard)/`
- Feature components under `components/{module}/`
- API hooks under `hooks/{module}/`
- Types under `types/{module}.ts`

Cross-module imports go through `components/shared/` or `hooks/shared/` — never directly between modules.

### 3. Data Ownership Is Clear
- **Server state** (TanStack Query): anything that came from the API
- **Client state** (Zustand): ephemeral UI state (sidebar, modals, preferences)
- **URL state** (nuqs): anything the user should be able to bookmark or share
- **Never duplicate** server state into client state

### 4. Permission-Driven Rendering
Every route, sidebar section, button, and data column respects RBAC. Permissions flow from JWT claims → AuthStore → `<PermissionGate>` wrappers and `useHasPermission()` hooks. The UI never shows actions the user can't perform.

### 5. Real-Time as an Overlay
SignalR pushes are **cache invalidation signals**, not primary data sources. When a push arrives, TanStack Query refetches — the API remains the source of truth. This keeps the data layer testable and avoids split-brain state.

### 6. Tenant Isolation at Every Layer
- API requests include `X-Tenant-Id` header (set by ApiClient from auth context)
- TanStack Query keys include `tenantId` to prevent cross-tenant cache pollution
- Theming tokens are tenant-configurable (logo, primary color, accent)
- Feature flags are tenant-scoped

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │ React Server │   │ Client       │   │ SignalR              │ │
│  │ Components   │   │ Components   │   │ WebSocket            │ │
│  │ (SSR data)   │   │ (interactive)│   │ (push notifications) │ │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘ │
│         │                  │                       │             │
│         │           ┌──────▼───────┐               │             │
│         │           │ TanStack     │◄──────────────┘             │
│         │           │ Query Cache  │  invalidate on push         │
│         │           └──────┬───────┘                             │
│         │                  │                                     │
│         │           ┌──────▼───────┐                             │
│         │           │ ApiClient    │                             │
│         │           │ (interceptors│                             │
│         │           │  auth, retry)│                             │
│         │           └──────┬───────┘                             │
│         │                  │                                     │
└─────────┼──────────────────┼─────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────────────────────────────┐
│  .NET 9 API Gateway (per-tenant)        │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Core HR  │ │ Workforce│ │ Payroll │ │
│  │ Service  │ │ Service  │ │ Service │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
```

## Deployment Architecture

| Concern | Strategy |
|:--------|:---------|
| Hosting | Vercel (Next.js native) or Azure Static Web Apps + Azure Functions |
| CDN | Vercel Edge / Azure CDN for static assets |
| Environment Config | `NEXT_PUBLIC_*` env vars per environment (dev/staging/prod) |
| Preview Deployments | Per-PR preview URLs via Vercel or Azure |
| Static Assets | Immutable hashing, `Cache-Control: max-age=31536000, immutable` |
| API Proxy | Next.js rewrites to avoid CORS (`/api/v1/** → backend`) |

## Related

- [[frontend/architecture/app-structure|App Structure]] — route tree and layout hierarchy
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR vs CSR decision matrix
- [[backend/module-boundaries|Module Boundaries]] — code splitting and isolation rules
- [[frontend/architecture/routing|Routing]] — route guards, middleware, parallel routes
- [[backend/messaging/error-handling|Error Handling]] — error boundary hierarchy
