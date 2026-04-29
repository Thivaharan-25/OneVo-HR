# 8-Developer Frontend Build Plan — Design Spec

**Date:** 2026-04-28
**Status:** Approved
**Scope:** OneVo main frontend (Vite SPA) + Developer Console (Next.js 15)

---

## 1. Core Decisions

### Stack
- **Build tool:** Vite 8.x (not Next.js — explicit decision)
- **Framework:** React 19
- **Router:** React Router v7 (library mode, config-based in `src/router.tsx`)
- **Language:** TypeScript (strict)
- **Styling:** Tailwind CSS v4
- **Components:** shadcn/ui + Radix
- **Server state:** TanStack Query v5
- **Client state:** Zustand
- **URL state:** React Router `useSearchParams` (not nuqs — Next.js only)
- **Real-time:** SignalR (`@microsoft/signalr`)
- **Forms:** React Hook Form + Zod
- **Sanitization:** DOMPurify (for rich text/doc editor)
- **Error tracking:** Sentry (`@sentry/react`)
- **i18n:** i18next + react-i18next
- **Testing:** Vitest + RTL + Playwright + MSW

### Two Projects
1. **`OneVo/`** — Main tenant-facing SPA (all 8 devs contribute here)
2. **`dev-console/`** — Separate Next.js 15 internal admin app (Dev 8 only)

---

## 2. Team Split

### HR Team (Dev 1–4) — Full-Stack
Own all HR Management modules: backend + frontend.
Reference existing `current-focus/DEV1–4` task files for backend context.

### WMS Team (Dev 5–8) — Frontend-Only (for now)
Own all Work Management System screens.
Backend knowledge base to be provided separately — WMS devs build frontend against stub/mock APIs initially.

---

## 3. Build Order (Foundation-First)

### Week 1 (Sequential)
- **Dev 1** builds the complete Vite foundation (everyone else does backend work while waiting)
- **Dev 8** bootstraps `dev-console/` Next.js 15 app in parallel (fully independent)

### Week 2+ (Full Parallel)
All 8 devs build their feature screens simultaneously. Cross-dev dependencies tracked per task.

---

## 4. Folder Structure

```
OneVo/src/
├── main.tsx, App.tsx, router.tsx
├── pages/               # auth/ + dashboard/ + errors/
├── components/          # ui/, layout/, shared/, hr/, leave/, workforce/,
│                        # exceptions/, org/, calendar/, admin/, settings/, wms/
├── hooks/               # hr/, workforce/, wms/, admin/, shared/
├── lib/
│   ├── api/             # client.ts, index.ts, errors.ts, interceptors/, endpoints/
│   ├── security/        # token-manager.ts, idle-timeout.ts, sanitizer.ts, permission-guard.tsx
│   ├── signalr/         # client.ts
│   └── utils/           # cn.ts, format-date.ts, to-params.ts
├── stores/              # use-auth-store, use-sidebar-store, use-filter-store, use-theme-store
├── types/               # auth, core-hr, org, workforce, notifications, settings, admin, wms/
└── styles/              # globals.css, tokens.css
```

---

## 5. Security Architecture (All in Dev 1 Foundation)

- **Token storage:** In-memory only (`lib/security/token-manager.ts`) — never localStorage
- **Refresh token:** httpOnly cookie (backend-managed)
- **Interceptor chain:** auth → tenant (X-Entity-Id) → correlation (X-Correlation-Id) → error (401/403/429/5xx)
- **Proactive refresh:** Token refreshed 60s before expiry — not on 401
- **Route guards:** `ProtectedRoute` component in router.tsx (redirects, not just hides)
- **Idle timeout:** Auto-logout after inactivity (`lib/security/idle-timeout.ts`)
- **XSS:** DOMPurify for any HTML rendering, React auto-escaping everywhere else
- **Security headers:** `vite.config.ts` for dev; nginx/CDN for production

---

## 6. Developer Assignments

### HR Team

**Dev 1 — Foundation + CoreHR + Leave + Productivity + HR Import**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Vite Foundation | Full project setup, shell layout, security layer, all shared components | Nothing |
| 2 | CoreHR Employee Profile | Employee list/detail/create/edit pages + backend | Task 1 |
| 3 | Leave | Leave requests/calendar/balances/policies + backend | Task 2 + Dev 3 Task 3 |
| 4 | HR Import Onboarding | Bulk import wizard + backend ETL | Task 2 + Dev 2 Task 1 + Dev 3 Task 1 |
| 5 | Productivity Analytics | Reports/dashboard + backend jobs | Dev 3 Task 5 |

**Dev 2 — Auth + Lifecycle + Exception Engine + Notifications**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Auth & Security | JWT/MFA backend + login/MFA/reset pages + token wiring | Dev 1 Task 1 |
| 2 | Employee Lifecycle | Onboarding/offboarding backend + wizard pages | Task 1 + Dev 1 Task 2 |
| 3 | Exception Engine | Alert rules backend + exception dashboard cards | Task 1 + Dev 3 Task 4 |
| 4 | Notifications | Notification backend + bell + inbox + preferences | Task 1 + Dev 4 Task 1 |

**Dev 3 — Org + Skills + Calendar + Presence + Activity Monitoring**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Org Structure | Org chart, departments, teams, job families, legal entities + backend | Dev 1 Task 1 |
| 2 | Skills Core | Skill taxonomy admin, employee skills + backend | Task 1 |
| 3 | Calendar | Unified calendar, schedules, holidays + backend | Task 1 |
| 4 | Workforce Presence Setup | Live presence card grid + backend | Task 1 |
| 5 | Activity Monitoring | Activity detail, productivity cards + backend | Task 4 |

**Dev 4 — Shared Platform + Agent Gateway + Config + Identity + Biometric + Admin**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Shared Platform + Agent Gateway | Feature flags, workflow engine, agent fleet + backend | Dev 1 Task 1 |
| 2 | Configuration (Settings) | All settings pages + backend | Task 1 |
| 3 | Identity Verification | Verification log + review flow + backend | Task 1 + Dev 3 Task 4 |
| 4 | Workforce Presence Biometric | Biometric devices, attendance corrections, overtime + backend | Task 1 + Dev 3 Task 4 |
| 5 | Admin Pages | Users, Roles, Audit, Devices, Compliance pages | Task 1 + Dev 2 Task 1 |

### WMS Team (Frontend-Only)

**Dev 5 — Projects + My Work + Planner**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Projects | Project list/create/detail, board (Kanban), sprints, roadmap | Dev 1 Task 1 |
| 2 | My Work | Assigned tasks across all projects | Task 1 |
| 3 | Planner | Workspace-level sprints, boards, roadmap | Task 1 |

**Dev 6 — Goals + Timesheets + Analytics**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Goals / OKR | Objectives, key results, check-ins, progress tracking | Dev 1 Task 1 |
| 2 | Timesheets | Daily/weekly time logs, timesheet approval, reports | Dev 1 Task 1 |
| 3 | Analytics | Productivity scores, capacity analytics, resource allocation | Dev 1 Task 1 + Dev 3 Task 5 |

**Dev 7 — Docs/Wiki + Chat**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Docs/Wiki | Document list, rich-text viewer/editor (DOMPurify sanitized) | Dev 1 Task 1 |
| 2 | Chat | Channels, DMs, real-time messages via SignalR | Dev 1 Task 1 |

**Dev 8 — Inbox + Dev Console**

| # | Task | Key Deliverables | Blocked By |
|---|---|---|---|
| 1 | Inbox | Unified approvals, task mentions, exception alerts page | Dev 1 Task 1 |
| 2 | Dev Console | Separate Next.js 15 app — Google OAuth, dark theme, all 7 admin modules | Nothing (runs from day 1) |

---

## 7. Task File Format

Each dev gets individual task files in `current-focus/` named `FE-DEV{N}-{module}.md`.
Each file contains:
- Module overview
- Acceptance criteria (checkboxes)
- Frontend pages to build with component list
- API endpoints to consume
- Linked userflow docs
- Cross-dev dependencies

---

## 8. Constraints

- WMS backend knowledge base not yet written — WMS devs (5–8) build against stub API responses initially
- Phase 2 modules (Payroll, Performance, Grievance, Expense, Documents) are NOT in scope
- No offset pagination anywhere — cursor-based only
- `React.lazy()` + Suspense for heavy components — never `next/dynamic()`
- Token never touches localStorage or sessionStorage
