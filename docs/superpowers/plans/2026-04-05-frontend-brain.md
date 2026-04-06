# Frontend Brain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a complete frontend secondary brain at `frontend/` that guides the React/Next.js team in building the ONEVO dashboard — covering both HR Management and Workforce Intelligence UI.

**Architecture:** Next.js 14 (App Router) + Tailwind CSS + shadcn/ui. TanStack Query for server state, Zustand for client state, SignalR for real-time, React Hook Form + Zod for forms. Hosted on Vercel.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Tremor, TanStack Query v5, Zustand, nuqs, SignalR, Vitest, React Testing Library, Playwright

**Spec:** `docs/superpowers/specs/2026-04-05-onevo-monitoring-redesign.md` (Section 9)

---

### Task 1: Create frontend/README.md

**Files:**
- Create: `frontend/README.md`

- [ ] **Step 1: Create the frontend README**

```markdown
# ONEVO — Frontend Secondary Brain

The AI-optimized knowledge base for the ONEVO frontend development team (React/Next.js). This is the single source of truth for frontend architecture, design system, page specifications, and coding conventions.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read `AI_CONTEXT/project-context.md` for frontend overview
3. Read `AI_CONTEXT/current-focus.md` for frontend delivery priorities
4. Check `AI_CONTEXT/known-issues.md` before writing any code

## The Backend Brain

Backend architecture docs live in the parent directory (`../`). The frontend brain references backend module names and API contracts but does not duplicate them.

## Structure

```
frontend/
├── AI_CONTEXT/                  # AI reads these FIRST
│   ├── project-context.md       # What the frontend is, architecture overview
│   ├── tech-stack.md            # Next.js 14, Tailwind, shadcn/ui, etc.
│   ├── current-focus.md         # Frontend delivery plan
│   ├── rules.md                 # AI agent rules for React/TypeScript
│   ├── known-issues.md          # Frontend gotchas
│   └── changelog.md             # Knowledge base update log
├── .cursor/rules/               # Cursor AI auto-injected context
│   ├── project-context.mdc      # Always-on: project identity
│   ├── coding-standards.mdc     # Active on .tsx/.ts files
│   └── ai-behavior.mdc          # Hallucination prevention
├── docs/
│   ├── architecture/            # App structure, state management, API, real-time
│   ├── design-system/           # Components, layouts, charts, colors, typography
│   ├── pages/                   # Page specifications per pillar
│   ├── security/                # Auth flow, RBAC frontend
│   └── guides/                  # Coding standards, testing
└── decisions/                   # Frontend architecture decisions
```

## Key Principles

1. **Server Components by default** — use `'use client'` only when needed
2. **shadcn/ui components** — copy-paste, own the code, no vendor lock
3. **TanStack Query for server state** — never store API data in Zustand
4. **Permission-gated rendering** — every feature behind `<PermissionGate>`
5. **Real-time via SignalR** — live dashboards, alerts, presence
6. **Responsive** — desktop-first, but all pages must work on tablet
```

- [ ] **Step 2: Commit**

```bash
git add frontend/README.md
git commit -m "docs: create frontend brain README"
```

---

### Task 2: Create frontend/AI_CONTEXT/project-context.md

**Files:**
- Create: `frontend/AI_CONTEXT/project-context.md`

- [ ] **Step 1: Create project-context.md**

```markdown
# Frontend Project Context: ONEVO

## 1. Overview

- **Project:** ONEVO Frontend Dashboard
- **Framework:** Next.js 14 (App Router)
- **Hosting:** Vercel
- **Backend:** .NET 9 REST API (see `../AI_CONTEXT/project-context.md`)
- **Status:** Active development — follows backend module delivery

## 2. What This Frontend Does

The ONEVO frontend is a multi-tenant SaaS dashboard serving three user types:

| User Type | What They See | Route Group |
|:----------|:-------------|:------------|
| **Admin/HR/Manager** | Full dashboard — HR modules + Workforce Intelligence | `(dashboard)` |
| **Employee** | Self-service — own data, leave requests, performance | `(employee-self-service)` |
| **Unauthenticated** | Login, forgot password, MFA | `(auth)` |

## 3. Two-Pillar Navigation

The sidebar navigation mirrors the backend's two-pillar architecture:

```
Sidebar
├── Overview (landing dashboard)
├── HR Management
│   ├── Employees
│   ├── Leave
│   ├── Performance
│   ├── Payroll
│   ├── Skills & Learning
│   ├── Documents
│   ├── Grievance
│   └── Expense
├── Workforce Intelligence
│   ├── Live Dashboard          ← Real-time workforce status
│   ├── Employee Activity       ← Drill-down per employee
│   ├── Reports                 ← Daily/Weekly/Monthly
│   ├── Exceptions              ← Alert management
│   └── Verification Logs       ← Identity verification history
├── Organization
│   ├── Departments
│   ├── Teams
│   └── Job Families
└── Settings
    ├── General
    ├── Monitoring              ← Feature toggles, employee overrides
    ├── Notifications
    ├── Integrations
    └── Billing
```

## 4. Key Frontend Concepts

### Permission-Based Rendering

Every section is gated by RBAC permissions from the backend JWT:

```tsx
<PermissionGate permission="workforce:view">
  <WorkforceDashboard />
</PermissionGate>
```

If user lacks permission, the sidebar item is hidden and the route returns 403.

### Monitoring Feature Awareness

The frontend must check tenant monitoring configuration before rendering workforce pages:
- If Activity Monitoring is OFF → hide app usage charts
- If Screenshots are OFF → hide screenshot timeline
- If Identity Verification is OFF → hide verification logs

This is fetched once on login and cached in Zustand.

### Real-Time Updates

SignalR channels push live data to dashboards:

| Channel | UI Update |
|:--------|:---------|
| `workforce-live` | Live dashboard cards (active/idle counts) |
| `exception-alerts` | Toast notification + badge count |
| `activity-feed` | Employee detail page live update |
| `agent-status` | Agent health indicator |

### Multi-Tenant Theming

Each tenant can customize branding via `tenant_branding` table:
- Logo, primary color, accent color
- Applied via CSS custom properties at the `(dashboard)` layout level

## 5. API Integration

- Base URL from environment: `NEXT_PUBLIC_API_URL`
- Auth: JWT in Authorization header (access token from memory)
- Refresh: HttpOnly cookie, auto-refresh via interceptor
- Error format: RFC 7807 Problem Details
- Correlation: `X-Correlation-Id` header on every request

## 6. What We Are NOT Building

- Mobile app (Flutter — Phase 2)
- AI chatbot widget (Nexis — Phase 2)
- WorkManage Pro UI (separate team)
- Desktop agent UI (MAUI — see `../agent/`)
```

- [ ] **Step 2: Commit**

```bash
git add frontend/AI_CONTEXT/project-context.md
git commit -m "docs: create frontend project context"
```

---

### Task 3: Create frontend/AI_CONTEXT/tech-stack.md

**Files:**
- Create: `frontend/AI_CONTEXT/tech-stack.md`

- [ ] **Step 1: Create tech-stack.md**

```markdown
# Frontend Tech Stack: ONEVO

## Core Framework

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Framework | Next.js | 14+ | App Router, Server Components |
| Language | TypeScript | 5.x | Strict mode enabled |
| Styling | Tailwind CSS | 3.x | Utility-first, design tokens via CSS vars |
| Components | shadcn/ui | Latest | Copy-paste component library (Radix primitives) |
| Icons | Lucide React | Latest | Consistent icon set, tree-shakeable |

## State Management

| Type | Technology | Version | Use Case |
|:-----|:-----------|:--------|:---------|
| Server state | TanStack Query | v5 | API data fetching, caching, mutations |
| Client state | Zustand | 4.x | Sidebar, filters, monitoring config cache |
| Form state | React Hook Form | 7.x | All forms |
| Form validation | Zod | 3.x | Schema validation (mirrors backend FluentValidation) |
| URL state | nuqs | Latest | Search params, filters, pagination in URL |

## Data Visualization

| Category | Technology | Use Case |
|:---------|:-----------|:---------|
| Standard charts | Recharts | Line, bar, pie, area charts |
| Dashboard blocks | Tremor | KPI cards, sparklines, progress bars |
| Activity timeline | Custom (Tailwind) | Horizontal day timeline (active/idle/break segments) |
| Heatmaps | Custom (CSS Grid) | Activity heatmap (hourly intensity) |

## Real-Time

| Technology | Purpose |
|:-----------|:--------|
| @microsoft/signalr | SignalR client for WebSocket connections |
| TanStack Query invalidation | SignalR events trigger query cache invalidation |

## API Client

| Category | Technology | Notes |
|:---------|:-----------|:------|
| HTTP client | ky or fetch wrapper | Lightweight, interceptor-friendly |
| API types | Generated from OpenAPI spec | Kiota or openapi-typescript |
| Error handling | RFC 7807 parser | Standard Problem Details parsing |

## Testing

| Type | Technology | Coverage Target |
|:-----|:-----------|:---------------|
| Unit | Vitest | Utility functions, hooks, stores |
| Component | React Testing Library | All shared components |
| Integration | React Testing Library + MSW | Page-level tests with mocked API |
| E2E | Playwright | Critical user flows (login, dashboard, leave request) |
| Visual | Storybook (optional) | Design system documentation |

## Build & Deploy

| Category | Technology |
|:---------|:-----------|
| Hosting | Vercel |
| CI/CD | GitHub Actions |
| Linting | ESLint (flat config) + Prettier |
| Type checking | tsc --noEmit in CI |
| Bundle analysis | @next/bundle-analyzer |

## NOT Using

| Technology | Reason |
|:-----------|:-------|
| Redux | TanStack Query + Zustand is simpler and sufficient |
| CSS Modules | Tailwind covers all styling needs |
| MUI / Ant Design | shadcn/ui gives more control, no vendor lock |
| GraphQL | Backend exposes REST APIs |
| Socket.io | Using SignalR (matches backend) |
```

- [ ] **Step 2: Commit**

```bash
git add frontend/AI_CONTEXT/tech-stack.md
git commit -m "docs: create frontend tech stack"
```

---

### Task 4: Create frontend/AI_CONTEXT/rules.md

**Files:**
- Create: `frontend/AI_CONTEXT/rules.md`

- [ ] **Step 1: Create rules.md**

```markdown
# Frontend AI Agent Rules: ONEVO

## 1. General Rules

- **Source of Truth:** Frontend brain files in `frontend/AI_CONTEXT/` take precedence. Backend context in `../AI_CONTEXT/`.
- **Hallucination Prevention:** If information is not in these docs, state it's unknown. DO NOT invent API endpoints, component props, or page layouts.
- **Token Efficiency:** Reuse existing components from shadcn/ui. Don't recreate what exists.

## 2. TypeScript / React Rules

### File Naming

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Components | `PascalCase.tsx` | `EmployeeTable.tsx`, `LiveDashboard.tsx` |
| Hooks | `camelCase.ts` | `useEmployees.ts`, `useSignalR.ts` |
| Utilities | `camelCase.ts` | `formatDuration.ts`, `parseApiError.ts` |
| Types | `PascalCase.ts` | `Employee.ts`, `ActivitySnapshot.ts` |
| Pages | `page.tsx` (Next.js convention) | `app/(dashboard)/workforce/live/page.tsx` |
| Layouts | `layout.tsx` | `app/(dashboard)/layout.tsx` |
| API routes | `route.ts` | Only for BFF patterns (rare) |

### Component Patterns

```tsx
// ALWAYS: Use Server Components by default
// app/(dashboard)/workforce/live/page.tsx
export default async function LiveDashboardPage() {
  // Server-side data fetching here
  return <LiveDashboard />;
}

// ALWAYS: Mark client components explicitly
// components/workforce/live-dashboard.tsx
'use client';
export function LiveDashboard() {
  const { data } = useWorkforceLive();
  return <div>...</div>;
}

// ALWAYS: Use PermissionGate for protected UI
<PermissionGate permission="workforce:view">
  <WorkforceSidebar />
</PermissionGate>

// ALWAYS: Use TanStack Query for API data
const { data, isLoading, error } = useQuery({
  queryKey: ['workforce', 'live'],
  queryFn: () => api.workforce.getLive(),
  refetchInterval: 30_000, // 30s polling fallback
});

// NEVER: Store API data in Zustand
// Zustand is for UI state only (sidebar open, selected filters)
```

### Hook Patterns

```tsx
// Custom hooks wrap TanStack Query
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => api.employees.list(filters),
  });
}

// Mutations with optimistic updates
export function useApproveLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.leave.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
    },
  });
}
```

### Patterns to AVOID

```tsx
// NEVER: useEffect for data fetching
useEffect(() => {
  fetch('/api/employees').then(r => r.json()).then(setData); // BAD
}, []);

// NEVER: Prop drilling beyond 2 levels — use composition or context
<Parent data={data}>
  <Child data={data}>
    <GrandChild data={data} /> // BAD — use context or compose
  </Child>
</Parent>

// NEVER: Inline styles
<div style={{ color: 'red' }}> // BAD — use Tailwind classes

// NEVER: any type
const data: any = response; // BAD — always type
```

## 3. API Integration Rules

- API client is a singleton with interceptors (auth, refresh, correlation-id)
- All API types are generated from OpenAPI spec — NEVER hand-write API types
- Handle loading, error, and empty states for every data fetch
- Use `useSuspenseQuery` with Suspense boundaries for page-level data
- Use `useQuery` with `isLoading`/`isError` for component-level data

## 4. Styling Rules

- Use Tailwind utility classes — no custom CSS files except for global tokens
- Use `cn()` utility (from shadcn/ui) for conditional class merging
- Design tokens via CSS custom properties in `globals.css`
- Dark mode support via Tailwind `dark:` prefix (use `next-themes`)
- Responsive: desktop-first, `md:` for tablet, `sm:` for mobile

## 5. Testing Rules

- Every shared component needs a React Testing Library test
- Every custom hook needs a Vitest test
- Test user behavior, not implementation: `getByRole`, not `getByTestId`
- Use MSW (Mock Service Worker) for API mocking in tests
- E2E tests for critical flows: login → dashboard → view reports → logout

## 6. Accessibility Rules

- All interactive elements must be keyboard accessible
- Use semantic HTML (`<nav>`, `<main>`, `<aside>`, `<table>`)
- All images need `alt` text
- Color contrast ratio ≥ 4.5:1 (WCAG AA)
- shadcn/ui components handle most a11y — don't override aria attributes
```

- [ ] **Step 2: Commit**

```bash
git add frontend/AI_CONTEXT/rules.md
git commit -m "docs: create frontend AI agent rules"
```

---

### Task 5: Create frontend/AI_CONTEXT/current-focus.md

**Files:**
- Create: `frontend/AI_CONTEXT/current-focus.md`

- [ ] **Step 1: Create current-focus.md**

```markdown
# Frontend Current Focus: ONEVO

**Last Updated:** 2026-04-05
**Current Phase:** Phase 1 — Frontend follows backend module delivery
**Approach:** Build frontend pages as backend APIs become available

---

## Frontend Delivery Plan

Frontend development starts after Week 1 backend foundation is complete (Auth, Infrastructure, Org Structure ready).

### Wave 1 (Week 2-3): Foundation + Core Pages
> Goal: App shell, auth flow, core HR pages for modules completed in Week 1-2

| Priority | Page/Feature | Backend Dependency | Key Components |
|:---------|:------------|:-------------------|:--------------|
| P0 | App shell (sidebar, topbar, layout) | Auth API | Sidebar, TopBar, PermissionGate |
| P0 | Login + MFA | Auth API | LoginForm, MFAChallenge |
| P0 | Employee list + detail | CoreHR API | EmployeeTable, EmployeeProfile |
| P1 | Department tree | OrgStructure API | DepartmentTree, OrgChart |
| P1 | Settings pages | Configuration API | SettingsLayout, TenantSettings |
| P1 | Monitoring settings | Configuration API | MonitoringToggles, EmployeeOverrides |

### Wave 2 (Week 3-4): Workforce Intelligence
> Goal: Live dashboard, activity views, exception management

| Priority | Page/Feature | Backend Dependency | Key Components |
|:---------|:------------|:-------------------|:--------------|
| P0 | Live Workforce Dashboard | ActivityMonitoring + WorkforcePresence APIs | LiveDashboard, PresenceCards, DeptBreakdown, ExceptionPanel |
| P0 | Employee Activity Detail | ActivityMonitoring API | ActivityTimeline, AppUsageChart, MeetingLog, IntensityChart |
| P1 | Exception Management | ExceptionEngine API | AlertList, AlertActions, EscalationView |
| P1 | Reports (Daily/Weekly/Monthly) | ProductivityAnalytics API | ReportView, TrendChart, DeptSummaryTable |
| P1 | Verification Logs | IdentityVerification API | VerificationLog, PhotoViewer |

### Wave 3 (Week 4-5): HR Modules + Polish
> Goal: Leave, performance, payroll pages + employee self-service

| Priority | Page/Feature | Backend Dependency | Key Components |
|:---------|:------------|:-------------------|:--------------|
| P0 | Leave Management | Leave API | LeaveRequestForm, LeaveCalendar, EntitlementView |
| P0 | Employee Self-Service Dashboard | Multiple APIs | MyDashboard, MyTimeline, MyAppUsage |
| P1 | Performance Reviews | Performance API | ReviewCycle, GoalTracker, FeedbackForm |
| P1 | Payroll Overview | Payroll API | PayrollRunList, PayslipView |
| P2 | Skills & Learning | Skills API | SkillMatrix, CourseList, CertTracker |
| P2 | Documents | Documents API | DocumentList, VersionHistory |
| P2 | Grievance + Expense | Grievance + Expense APIs | CaseList, ExpenseForm |

## What We Are NOT Building (Frontend)

- Mobile-responsive employee app (Flutter — Phase 2)
- AI chatbot widget (Nexis — Phase 2)
- WorkManage Pro UI (separate team)
- Desktop agent UI (MAUI — see ../agent/)
```

- [ ] **Step 2: Commit**

```bash
git add frontend/AI_CONTEXT/current-focus.md
git commit -m "docs: create frontend delivery plan"
```

---

### Task 6: Create frontend/AI_CONTEXT/known-issues.md + changelog.md

**Files:**
- Create: `frontend/AI_CONTEXT/known-issues.md`
- Create: `frontend/AI_CONTEXT/changelog.md`

- [ ] **Step 1: Create known-issues.md**

```markdown
# Frontend Known Issues & Gotchas: ONEVO

**Last Updated:** 2026-04-05

## Gotchas

- **Server Components vs Client Components:** Next.js App Router defaults to Server Components. Any component using hooks (`useState`, `useEffect`, TanStack Query, Zustand, SignalR) MUST have `'use client'` at the top. Page-level files can be Server Components that import Client Components.

- **JWT Storage:** Access token is stored in memory (JavaScript variable), NOT localStorage or cookies. This means it's lost on page refresh — the app auto-refreshes via the HttpOnly refresh token cookie on mount. Don't try to read the JWT from cookies.

- **SignalR Connection Lifecycle:** The SignalR connection is established once at the `(dashboard)` layout level and shared via context. Don't create new connections per page. Disconnect only on logout.

- **Monitoring Config Cache:** Tenant monitoring configuration (which features are ON/OFF) is fetched once on login and stored in Zustand. This cache is invalidated when the admin changes settings (via SignalR event). Don't re-fetch on every page navigation.

- **Permission Flash:** When using `<PermissionGate>`, the component briefly renders nothing while permissions load. Use the shell layout's loading state to prevent layout shift. Don't add individual loading spinners inside permission gates.

- **API Error Format:** All backend errors follow RFC 7807 Problem Details. Parse `type`, `title`, `detail`, `status`, and `errors` (for validation). Don't assume error responses are plain strings.

- **Date Handling:** Backend sends `DateTimeOffset` as ISO 8601 strings. Use `date-fns` for formatting (NOT `moment`). Display all times in the user's local timezone unless explicitly showing UTC (like audit logs).

- **Workforce Live Dashboard Polling:** The live dashboard uses SignalR for real-time updates, with a 30-second polling fallback (`refetchInterval: 30_000`). Don't remove the polling — it handles SignalR disconnection gracefully.

- **Table Component:** Use shadcn/ui DataTable with TanStack Table for all tables. Don't build custom table components. Pagination, sorting, and filtering are handled via URL params (nuqs).

## Active Bugs

| ID | Description | Severity | Status |
|:---|:------------|:---------|:-------|
| - | No active bugs yet (frontend in initial development) | - | - |
```

- [ ] **Step 2: Create changelog.md**

```markdown
# Frontend Brain Changelog

## 2026-04-05 — Initial Creation

- Created frontend secondary brain
- Defined tech stack: Next.js 14, Tailwind, shadcn/ui, TanStack Query, Zustand
- Defined app structure with route groups
- Created page specifications for Workforce Intelligence
- Created design system documentation
- Created coding standards and testing guides
```

- [ ] **Step 3: Commit**

```bash
git add frontend/AI_CONTEXT/known-issues.md frontend/AI_CONTEXT/changelog.md
git commit -m "docs: create frontend known issues and changelog"
```

---

### Task 7: Create frontend/.cursor/rules/

**Files:**
- Create: `frontend/.cursor/rules/project-context.mdc`
- Create: `frontend/.cursor/rules/coding-standards.mdc`
- Create: `frontend/.cursor/rules/ai-behavior.mdc`

- [ ] **Step 1: Create project-context.mdc**

```markdown
---
description: ONEVO Frontend — always-on project identity
globs: *
---

# ONEVO Frontend

You are working on the ONEVO frontend — a multi-tenant SaaS dashboard built with Next.js 14 (App Router), Tailwind CSS, and shadcn/ui.

## Key Facts
- Two-pillar product: HR Management + Workforce Intelligence
- Backend: .NET 9 REST API (docs in ../AI_CONTEXT/)
- State: TanStack Query (server) + Zustand (client)
- Real-time: SignalR for live dashboards and alerts
- Auth: JWT (memory) + refresh token (HttpOnly cookie)
- Every UI feature is behind PermissionGate
- Monitoring features are configurable per tenant — always check config before rendering monitoring UI

## Before Writing Code
1. Read `frontend/AI_CONTEXT/rules.md` for conventions
2. Check `frontend/AI_CONTEXT/known-issues.md` for gotchas
3. Use existing shadcn/ui components — don't recreate
4. Follow existing patterns in the codebase
```

- [ ] **Step 2: Create coding-standards.mdc**

```markdown
---
description: ONEVO Frontend coding standards
globs: **/*.{tsx,ts,jsx,js}
---

# Frontend Coding Standards

- TypeScript strict mode — no `any`, no `@ts-ignore`
- Server Components by default — `'use client'` only when hooks are needed
- TanStack Query for all API data — never `useEffect` for fetching
- Zustand for UI-only state — never store API data in Zustand
- React Hook Form + Zod for all forms
- Tailwind utility classes — no inline styles, no CSS modules
- `cn()` from shadcn/ui for conditional classes
- All shared components in `components/ui/` (shadcn) or `components/shared/`
- Feature-specific components in `components/{feature}/`
- Custom hooks in `hooks/`
- API client functions in `lib/api/`
- Types in `types/`
```

- [ ] **Step 3: Create ai-behavior.mdc**

```markdown
---
description: Hallucination prevention for ONEVO frontend
globs: *
---

# AI Behavior Rules

- DO NOT invent API endpoints. Check `../docs/architecture/module-catalog.md` for available APIs.
- DO NOT guess component props. Check `frontend/docs/design-system/component-catalog.md`.
- DO NOT assume permissions exist. Check `../AI_CONTEXT/rules.md` for the permission list.
- DO NOT create new shadcn/ui components when one already exists. Run `npx shadcn-ui@latest add` for new ones.
- If unsure about backend behavior, state it's unknown — don't guess.
- Always check `frontend/AI_CONTEXT/known-issues.md` before writing code that touches auth, SignalR, or data fetching.
```

- [ ] **Step 4: Commit**

```bash
git add frontend/.cursor/rules/
git commit -m "docs: create frontend Cursor rules"
```

---

### Task 8: Create frontend/docs/architecture/

**Files:**
- Create: `frontend/docs/architecture/README.md`
- Create: `frontend/docs/architecture/app-structure.md`
- Create: `frontend/docs/architecture/state-management.md`
- Create: `frontend/docs/architecture/api-integration.md`
- Create: `frontend/docs/architecture/real-time.md`
- Create: `frontend/docs/architecture/monitoring-data-flow.md`

- [ ] **Step 1: Create README.md**

```markdown
# Frontend Architecture: ONEVO

## Overview

Next.js 14 App Router application with three route groups:

| Route Group | Layout | Purpose |
|:------------|:-------|:--------|
| `(auth)` | Minimal (centered card) | Login, forgot password, MFA |
| `(dashboard)` | Sidebar + Topbar | Admin/HR/Manager dashboard |
| `(employee-self-service)` | Simplified sidebar | Employee-facing views |

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [App Structure](app-structure.md) | Route hierarchy, layouts, file organization |
| [State Management](state-management.md) | TanStack Query, Zustand, SignalR state |
| [API Integration](api-integration.md) | API client, auth headers, error handling |
| [Real-Time](real-time.md) | SignalR channels, event handling |
| [Monitoring Data Flow](monitoring-data-flow.md) | How activity data reaches the dashboard |
```

- [ ] **Step 2: Create app-structure.md**

Full Next.js App Router structure as defined in the spec (Section 9 — Route Structure). Include:
- Complete `app/` directory tree with all route groups
- Layout hierarchy explanation
- File colocation rules (page.tsx, layout.tsx, loading.tsx, error.tsx)
- Component organization:
  ```
  components/
  ├── ui/                    # shadcn/ui components (Button, Card, Dialog, etc.)
  ├── shared/                # App-wide shared components (PermissionGate, DataTable, PageHeader)
  ├── layout/                # Sidebar, TopBar, UserMenu, NotificationBell
  ├── workforce/             # Workforce Intelligence components
  │   ├── live-dashboard.tsx
  │   ├── presence-cards.tsx
  │   ├── activity-timeline.tsx
  │   ├── app-usage-chart.tsx
  │   ├── intensity-chart.tsx
  │   ├── exception-panel.tsx
  │   └── meeting-log.tsx
  ├── hr/                    # HR Management components
  │   ├── employee-table.tsx
  │   ├── leave-calendar.tsx
  │   └── ...
  └── settings/              # Settings components
      ├── monitoring-toggles.tsx
      └── employee-overrides.tsx
  ```

- [ ] **Step 3: Create state-management.md**

Document the state management strategy from the spec:
- TanStack Query for server state (query keys, cache invalidation patterns)
- Zustand stores:
  - `useSidebarStore` — sidebar open/close
  - `useFilterStore` — active filters per page
  - `useMonitoringConfigStore` — cached tenant monitoring config
  - `useAuthStore` — current user, permissions, tenant info
- SignalR → TanStack Query invalidation pattern
- URL state with nuqs (filters, pagination, date ranges)
- React Hook Form + Zod for form state

- [ ] **Step 4: Create api-integration.md**

Document:
- API client singleton with interceptors
- Auth header injection (Bearer token from memory)
- Auto-refresh flow (401 → refresh → retry)
- RFC 7807 error parsing
- X-Correlation-Id header
- API module organization:
  ```
  lib/api/
  ├── client.ts              # Base API client with interceptors
  ├── auth.ts                # Login, refresh, logout
  ├── employees.ts           # Employee CRUD
  ├── workforce.ts           # Live dashboard, activity, presence
  ├── exceptions.ts          # Exception alerts
  ├── analytics.ts           # Reports, summaries
  ├── monitoring-config.ts   # Monitoring settings, overrides
  └── ...
  ```
- Type generation from OpenAPI spec

- [ ] **Step 5: Create real-time.md**

Document:
- SignalR connection setup (single connection at layout level)
- Channel subscription pattern
- Event → query invalidation mapping:
  ```
  workforce-live event → invalidate ['workforce', 'live']
  exception-alerts event → invalidate ['exceptions'] + show toast
  activity-feed event → invalidate ['activity', employeeId]
  agent-status event → invalidate ['agents', 'health']
  ```
- Reconnection strategy (auto-reconnect with exponential backoff)
- Connection state UI indicator
- Polling fallback configuration

- [ ] **Step 6: Create monitoring-data-flow.md**

Document how monitoring data flows from agent to dashboard:
```
Desktop Agent → Agent Gateway API → Activity Monitoring (DB) → REST API → TanStack Query → React Components
                                                                         ↕
                                  Exception Engine → SignalR → TanStack Query invalidation → Toast/Badge
```

Include:
- Which API endpoints power which dashboard components
- Refresh intervals per component
- How monitoring config affects what's shown (conditional rendering based on feature toggles)

- [ ] **Step 7: Commit**

```bash
git add frontend/docs/architecture/
git commit -m "docs: create frontend architecture documentation"
```

---

### Task 9: Create frontend/docs/design-system/

**Files:**
- Create: `frontend/docs/design-system/README.md`
- Create: `frontend/docs/design-system/component-catalog.md`
- Create: `frontend/docs/design-system/layout-patterns.md`
- Create: `frontend/docs/design-system/data-visualization.md`
- Create: `frontend/docs/design-system/color-tokens.md`
- Create: `frontend/docs/design-system/typography.md`

- [ ] **Step 1: Create README.md**

Overview of the design system: shadcn/ui base, Tailwind tokens, chart components, layout patterns.

- [ ] **Step 2: Create component-catalog.md**

Document all shared components with usage. Key sections:

**From shadcn/ui (installed):**
Button, Card, Dialog, DropdownMenu, Input, Label, Select, Table, Tabs, Toast, Tooltip, Badge, Avatar, Switch, Separator, Sheet, Skeleton, Popover, Command (for search), Calendar (date picker)

**Custom shared components:**

| Component | Purpose | Props |
|:----------|:--------|:------|
| `PermissionGate` | Conditionally render based on RBAC permission | `permission: string`, `children`, `fallback?` |
| `PageHeader` | Page title + breadcrumbs + actions | `title`, `breadcrumbs`, `actions` |
| `DataTable` | TanStack Table wrapper with sorting, filtering, pagination | `columns`, `data`, `searchKey?`, `filterOptions?` |
| `StatCard` | KPI metric card (used in dashboards) | `title`, `value`, `trend?`, `icon?`, `color?` |
| `StatusBadge` | Colored badge for status values | `status: 'active' | 'idle' | 'absent' | 'on_leave'` |
| `ActivityTimeline` | Horizontal day timeline bar | `segments: TimeSegment[]` |
| `EmptyState` | Placeholder when no data | `icon`, `title`, `description`, `action?` |
| `LoadingSkeleton` | Consistent skeleton for pages | `variant: 'table' | 'cards' | 'detail'` |

- [ ] **Step 3: Create layout-patterns.md**

Document:
- Dashboard shell layout (sidebar + topbar + content area)
- Sidebar responsive behavior (collapsible on mobile)
- Page layout patterns: list page, detail page, settings page, dashboard page
- Grid system for dashboard cards (responsive: 4 cols desktop, 2 tablet, 1 mobile)
- Split view pattern (list on left, detail on right for employee activity)

- [ ] **Step 4: Create data-visualization.md**

Document chart patterns used across the app:

| Chart Type | Library | Used In |
|:-----------|:--------|:--------|
| Line chart | Recharts `<LineChart>` | Activity intensity over day |
| Bar chart | Recharts `<BarChart>` | App usage breakdown |
| Horizontal bar | Recharts `<BarChart layout="vertical">` | Department active % |
| Pie/Donut | Recharts `<PieChart>` | Device usage split |
| Area chart | Recharts `<AreaChart>` | Weekly trends |
| Sparkline | Tremor `<SparkChart>` | Inline trend in tables |
| KPI card | Tremor `<Card>` + custom | Headline metrics |
| Progress bar | Tremor `<ProgressBar>` | Active percentage |
| Heatmap | Custom (CSS Grid + Tailwind) | Hourly activity intensity |
| Timeline | Custom (Tailwind) | Day timeline (active/idle/break segments) |

Include color conventions for charts:
- Active/productive: green shades
- Idle: amber/yellow
- Meetings: blue
- Break: gray
- Alert/exception: red

- [ ] **Step 5: Create color-tokens.md**

Define CSS custom property tokens:

```css
:root {
  /* Brand */
  --brand-primary: 238 75% 64%;     /* Indigo - primary actions */
  --brand-secondary: 270 70% 72%;   /* Purple - accent */

  /* Status */
  --status-active: 142 71% 45%;     /* Green */
  --status-idle: 38 92% 50%;        /* Amber */
  --status-absent: 0 84% 60%;       /* Red */
  --status-on-leave: 217 91% 60%;   /* Blue */
  --status-meeting: 199 89% 48%;    /* Cyan */

  /* Severity */
  --severity-info: 217 91% 60%;
  --severity-warning: 38 92% 50%;
  --severity-critical: 0 84% 60%;

  /* Surface (dark mode default) */
  --bg-primary: 222 47% 6%;
  --bg-secondary: 222 47% 9%;
  --bg-tertiary: 222 47% 12%;
  --border: 222 30% 18%;
  --text-primary: 220 20% 93%;
  --text-secondary: 220 15% 65%;
  --text-muted: 220 15% 45%;
}
```

Both light and dark mode tokens.

- [ ] **Step 6: Create typography.md**

Define font scale, heading hierarchy, monospace for data/numbers:

```css
/* Font: Inter (system fallback: system-ui) */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace; /* For numbers, timestamps */

/* Scale */
--text-xs: 0.75rem;    /* 12px - badges, labels */
--text-sm: 0.875rem;   /* 14px - body, table cells */
--text-base: 1rem;     /* 16px - primary body */
--text-lg: 1.125rem;   /* 18px - section headers */
--text-xl: 1.25rem;    /* 20px - page subtitles */
--text-2xl: 1.5rem;    /* 24px - page titles */
--text-3xl: 1.875rem;  /* 30px - dashboard KPI numbers */
```

- [ ] **Step 7: Commit**

```bash
git add frontend/docs/design-system/
git commit -m "docs: create frontend design system documentation"
```

---

### Task 10: Create frontend/docs/pages/ — Workforce Intelligence

**Files:**
- Create: `frontend/docs/pages/README.md`
- Create: `frontend/docs/pages/pillar2-workforce/live-dashboard.md`
- Create: `frontend/docs/pages/pillar2-workforce/employee-activity.md`
- Create: `frontend/docs/pages/pillar2-workforce/reports.md`
- Create: `frontend/docs/pages/pillar2-workforce/exceptions.md`
- Create: `frontend/docs/pages/pillar2-workforce/settings.md`

- [ ] **Step 1: Create README.md**

Page catalog listing all pages in the app, organized by route group and pillar. Mark priority (P0/P1/P2) and backend dependency for each.

- [ ] **Step 2: Create live-dashboard.md**

Full spec for the Live Workforce Dashboard page (`/workforce/live`) as designed in brainstorming:
- Route: `app/(dashboard)/workforce/live/page.tsx`
- Permission: `workforce:view`
- Layout wireframe (the ASCII mockup from Section 5)
- Components used: StatCard (x5), DeptBreakdownChart, ActivityHeatmap, ExceptionPanel, EmployeeListTable
- Data sources: `GET /api/v1/workforce/live` (SignalR channel: `workforce-live`)
- Filters: department, team, status (active/idle/absent)
- Refresh: SignalR push + 30s polling fallback
- Conditional rendering: hide sections based on monitoring config

- [ ] **Step 3: Create employee-activity.md**

Full spec for Employee Activity Detail page (`/workforce/activity/[employeeId]`):
- Route: `app/(dashboard)/workforce/activity/[employeeId]/page.tsx`
- Permission: `workforce:view` (own data: `workforce:view-own`)
- Layout wireframe (the ASCII mockup from Section 5)
- Components: DaySummaryCards, ActivityTimeline, AppUsageChart, IntensityLineChart, MeetingLog, DeviceUsagePie
- Data sources: `GET /api/v1/workforce/activity/{employeeId}?date=YYYY-MM-DD`
- Date picker for historical view
- Conditional: hide screenshots section if screenshots OFF

- [ ] **Step 4: Create reports.md**

Spec for Reports page (`/workforce/reports`):
- Three tabs: Daily, Weekly, Monthly
- Daily: headline metrics, auto-generated key observations, department summary table
- Weekly: same + trend charts
- Monthly: same + performance patterns, comparative insights
- Export: CSV/Excel download buttons
- Permission: `analytics:view` (export: `analytics:export`)

- [ ] **Step 5: Create exceptions.md**

Spec for Exception Management page (`/workforce/exceptions`):
- Active alerts list with severity badges
- Actions: acknowledge, dismiss, escalate, add note
- Filter by: severity, department, rule type, date range, status
- Alert detail side panel (click to expand)
- Escalation timeline view
- Permission: `exceptions:view` (actions: `exceptions:manage`)

- [ ] **Step 6: Create settings.md**

Spec for Monitoring Settings page (`/settings/monitoring`):
- Industry profile selector
- Global feature toggles (ON/OFF switches)
- Identity verification policy form
- Exception rules editor (add/edit/delete rules with threshold config)
- Escalation chain editor
- Privacy mode selector (full/partial/covert)
- Employee monitoring overrides sub-page (`/settings/monitoring/overrides`)
  - Employee search + select
  - Per-employee feature toggle overrides
  - Bulk override by department/team/job family
- Permission: `monitoring:configure`

- [ ] **Step 7: Commit**

```bash
git add frontend/docs/pages/
git commit -m "docs: create workforce intelligence page specifications"
```

---

### Task 11: Create frontend/docs/pages/ — HR & Shared Pages

**Files:**
- Create: `frontend/docs/pages/pillar1-hr/employees.md`
- Create: `frontend/docs/pages/pillar1-hr/leave.md`
- Create: `frontend/docs/pages/pillar1-hr/performance.md`
- Create: `frontend/docs/pages/shared/login.md`
- Create: `frontend/docs/pages/shared/employee-self-service.md`

- [ ] **Step 1: Create employees.md**

Spec for Employee pages:
- List: searchable, filterable DataTable with employee cards
- Detail: tabbed profile (personal, employment, salary, documents, attendance, activity)
- Create/Edit: multi-step form with validation
- Permission: `employees:read`, `employees:write`

- [ ] **Step 2: Create leave.md**

Spec for Leave Management:
- Leave request form (date range, type, reason)
- Leave calendar (team view)
- Entitlement dashboard
- Approval queue (for managers)
- Permission: `leave:read`, `leave:create`, `leave:approve`

- [ ] **Step 3: Create performance.md**

Spec for Performance Management:
- Review cycle dashboard
- Self/manager/peer assessment forms
- Goal tracker (OKR hierarchy)
- Recognition feed
- Optional: productivity score integration from Workforce Intelligence
- Permission: `performance:read`, `performance:write`

- [ ] **Step 4: Create login.md**

Spec for Auth pages:
- Login form (email + password)
- MFA challenge (TOTP, email OTP)
- Forgot password flow
- No sidebar, centered card layout
- Redirect to dashboard on success

- [ ] **Step 5: Create employee-self-service.md**

Spec for Employee Self-Service dashboard (`/my-dashboard`):
- Own work summary (hours, active%, meetings, intensity) — as designed in brainstorming
- Own timeline and app usage
- Weekly trend chart
- "What's being tracked" transparency footer
- No comparison with colleagues, no rankings
- Permission: read-own data only

- [ ] **Step 6: Commit**

```bash
git add frontend/docs/pages/pillar1-hr/ frontend/docs/pages/shared/
git commit -m "docs: create HR and shared page specifications"
```

---

### Task 12: Create frontend/docs/security/ and guides/

**Files:**
- Create: `frontend/docs/security/auth-flow.md`
- Create: `frontend/docs/security/rbac-frontend.md`
- Create: `frontend/docs/guides/coding-standards.md`
- Create: `frontend/docs/guides/testing.md`

- [ ] **Step 1: Create auth-flow.md**

Document frontend auth flow:
- Login → receive access token (memory) + refresh token (HttpOnly cookie)
- Auth context provider wrapping the app
- Auto-refresh interceptor (401 → POST /auth/refresh → retry original)
- Protected route middleware (Next.js middleware.ts checking auth cookie)
- Logout flow (clear memory + POST /auth/logout + redirect)
- Session timeout handling (30 min idle → prompt → logout)

- [ ] **Step 2: Create rbac-frontend.md**

Document:
- How permissions flow: JWT → decode → AuthContext → PermissionGate
- PermissionGate component implementation
- Sidebar items conditionally rendered based on permissions
- API error handling for 403 (show "Access Denied" page)
- Permission groups for Workforce Intelligence:
  ```
  workforce:view → see live dashboard, activity pages
  workforce:manage → manage monitoring settings
  exceptions:view → see exception alerts
  exceptions:manage → acknowledge/dismiss/escalate alerts
  monitoring:configure → change monitoring settings
  analytics:view → see reports
  analytics:export → download reports
  verification:view → see verification logs
  ```

- [ ] **Step 3: Create coding-standards.md**

Detailed coding standards (expand on rules.md):
- File/folder organization
- Import ordering (React → Next → third-party → local)
- Component patterns (composition over props drilling)
- Error boundary placement
- Loading state patterns
- Form patterns with React Hook Form + Zod
- API error handling patterns

- [ ] **Step 4: Create testing.md**

Testing guide:
- Test file naming: `*.test.tsx` colocated with component
- Vitest setup with jsdom
- MSW handlers for API mocking
- React Testing Library patterns (user-centric queries)
- Playwright E2E test structure
- What to test vs what not to test
- Example test for PermissionGate, DataTable, LiveDashboard

- [ ] **Step 5: Commit**

```bash
git add frontend/docs/security/ frontend/docs/guides/
git commit -m "docs: create frontend security and coding guides"
```

---

### Task 13: Final review — Frontend Brain consistency check

- [ ] **Step 1: Verify all cross-references**

Check that:
- Component names are consistent between component-catalog.md and page specs
- Permission names match between rbac-frontend.md and backend rules.md
- API endpoint references match backend module-catalog.md
- Tech stack versions are consistent across all files
- Route paths match between app-structure.md and page specs
- SignalR channel names match between real-time.md and backend event-catalog.md

- [ ] **Step 2: Commit any fixes**

```bash
git add frontend/
git commit -m "docs: frontend brain consistency fixes"
```
