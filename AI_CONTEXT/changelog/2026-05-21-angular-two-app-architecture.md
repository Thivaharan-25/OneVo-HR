# 2026-05-21: Angular 21 Frontend Architecture Decision

## Summary

Historical note: this older entry recorded a three-app Angular workspace. It has since been superseded by the current **customer-app + dev-console Angular workspace** decision.

## What Changed

### Architecture Decision
- **Three Angular apps** instead of one unified SPA:
  - Legacy config app for tenant/company setup, legal entities, departments, positions, roles/permissions, policies, imports, and add-on requests
  - Legacy operations app for daily employee, manager, HR, monitoring, and WorkSync operations
  - `dev-console` for ONEVO internal Developer Platform workflows
  - `shared` Angular library built once and imported by all apps

### Framework Change
| Before | After |
|:-------|:------|
| Vite + React 19 | Angular 21 (standalone components) |
| React Router v7 | Angular Router (typed routes, functional guards) |
| TanStack Query v5 | Angular `resource()` + `toSignal()` |
| Zustand | Angular Signals (`signal()`, `computed()`, `effect()`) |
| shadcn/ui (Radix) | Angular Material 21 |
| Lucide React | Material Symbols |
| Recharts + Tremor | ng2-charts (Chart.js) |
| React Hook Form + Zod | Angular Reactive Forms + Zod |
| Framer Motion | Angular Animations |
| Vitest + RTL | Jest + Angular Testing Library |
| React component pattern | Standalone components, `inject()`, `@if`/`@for` |

### Why Separate Apps
1. **Different work modes** - setup/configuration work is separated from daily operational work
2. **Security** - internal Developer Platform code is not in customer app bundles
3. **Bundle performance** - setup, operations, and platform routes build as separate outputs
4. **Angular monorepo** - shared library eliminates duplication (auth, API services, design system)
5. **Interconnection** - customer apps share the same backend, BFF cookie session, and SignalR hubs; automation/real-time is backend-driven and unaffected by app count

### Cross-App Users
Context-switcher in the topbar lets authorized users switch between Setup / Control and Operations / Lifecycle. Customer apps use the same BFF cookie session; Developer Platform uses separate platform-admin auth.

## Files Updated

**Core context (authoritative - AI reads these first):**
- `AI_CONTEXT/tech-stack.md` - Section 3 Frontend fully rewritten
- `AI_CONTEXT/project-context.md` - Section 10 Frontend fully rewritten
- `AI_CONTEXT/rules.md` - Section 10 Frontend rules fully rewritten
- `CLAUDE.md` - Frontend sections updated

**Frontend directory (full rewrite):**
- `frontend/README.md`
- `frontend/architecture/overview.md`, `app-structure.md`, `routing.md`
- `frontend/data-layer/state-management.md`, `api-integration.md`, `caching-strategy.md`, `real-time.md`
- `frontend/coding-standards.md`
- `frontend/cross-cutting/authentication.md`, `authorization.md`, `feature-flags.md`, `security.md`
- `frontend/testing/strategy.md`
- `frontend/performance/budget.md`, `monitoring.md`
- `frontend/design-system/README.md`, `foundations/iconography.md`

**Scattered references:**
- `README.md`, `ADE-START-HERE.md`, `backend/README.md`, `backend/api-conventions.md`
- `backend/real-time.md`, `security/rbac-frontend.md`, `security/auth-flow.md`
- `AI_CONTEXT/known-issues.md`, `current-focus/README.md`, `current-focus/DEV5.md`
- `developer-platform/frontend/overview.md`

## Unchanged
- Desktop agent (WorkPulse Agent): Windows Service + .NET MAUI tray app - confirmed correct as documented
- Developer Platform console: remains a separate Angular app at `console.onevo.io` (was Next.js, now Angular)
- Backend (.NET 10), database (PostgreSQL), SignalR hub channels - unchanged
