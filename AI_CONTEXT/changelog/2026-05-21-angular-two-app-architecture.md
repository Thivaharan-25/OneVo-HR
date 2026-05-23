# 2026-05-21: Angular 21 Two-App Architecture Decision

## Summary

Replaced the entire frontend tech stack description and all documentation with **Angular 21** in a **two-app Angular workspace monorepo**, replacing the previously documented Vite + React 19 SPA.

## What Changed

### Architecture Decision
- **Two separate Angular apps** instead of one unified SPA:
  - `employee-app` at `app.{tenant}.onevo.com` — employee self-service
  - `management-app` at `manage.{tenant}.onevo.com` — HR / Admin / Manager / Executive workflows
  - `shared` Angular library built once and imported by both apps

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

### Why Two Apps
1. **Different personas** — employee UX is simple/fast; management UX is data-dense/analytical
2. **Security** — monitoring and policy configuration code is not in the employee app's bundle
3. **Bundle performance** — employee app is lean; management app carries heavy analytics libs
4. **Angular monorepo** — shared library eliminates duplication (auth, API services, design system)
5. **Interconnection** — both apps share the same backend, JWT session cookie, and SignalR hubs; automation/real-time is backend-driven and unaffected by app count

### Dual-Role Users
Context-switcher in the topbar lets users with both employee and management roles switch apps. Same session cookie works on both (same parent domain) — no re-login required.

## Files Updated

**Core context (authoritative — AI reads these first):**
- `AI_CONTEXT/tech-stack.md` — Section 3 Frontend fully rewritten
- `AI_CONTEXT/project-context.md` — Section 10 Frontend fully rewritten
- `AI_CONTEXT/rules.md` — Section 10 Frontend rules fully rewritten
- `CLAUDE.md` — Frontend sections updated

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
- Desktop agent (WorkPulse Agent): Windows Service + .NET MAUI tray app — confirmed correct as documented
- Developer Platform console: remains a separate Angular app at `console.onevo.io` (was Next.js, now Angular)
- Backend (.NET 10), database (PostgreSQL), SignalR hub channels — unchanged
