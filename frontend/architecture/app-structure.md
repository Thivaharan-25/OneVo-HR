# Frontend App Structure

> **Note:** A second frontend app (`dev-console`) exists for platform administration — see `developer-platform/frontend/app-structure.md` for details. This document covers the primary ONEVO tenant-facing app only.

> **Stack:** This app runs on **Vite + React 19 + React Router v7** — not Next.js. There is no file-based routing, no `app/` directory, no `page.tsx`/`layout.tsx` conventions, no parallel routes (`@panel`, `@modal`), and no intercepting routes (`(.)edit`). All routes are defined in `src/router.tsx`. Page components live in `src/pages/`. Loading states use React Suspense. Edit panels and create modals use React Router nested routes with `<Outlet />` or controlled modal state.

## Route Tree

All 22 backend modules + 9 WMS modules mapped to ~63 frontend pages. Single route tree with permission-driven views (no separate employee self-service group).

### Authorization Model

**Hybrid permissions — not traditional fixed-role RBAC:**
1. **Custom roles** — tenants create roles with custom names and assign granular permissions
2. **Per-employee overrides** — individual employees can be granted/revoked specific module/feature access independent of their role

**Never hardcode role names.** Always check permission keys (e.g., `leave:read`, `leave:approve`, `payroll:manage`).

```tsx
// Permission check evaluates BOTH role permissions AND employee-level overrides
const { hasPermission } = usePermissions();

const canViewTeam = hasPermission('leave:read:team');
const canApprove = hasPermission('leave:approve');
const canManagePolicies = hasPermission('leave:manage');
```

---

```
src/
├── main.tsx                           # Entry: React 19, StrictMode, mount <App />
├── App.tsx                            # Provider stack + <RouterProvider router={router} />
├── router.tsx                         # ALL routes defined here using createBrowserRouter()
│
│── ─── AUTH PAGES (public, no nav) ────
│
├── pages/auth/
│   ├── AuthLayout.tsx                 # Centered card, brand logo — wraps auth pages via <Outlet />
│   ├── LoginPage.tsx                  # Email + password
│   ├── ForgotPasswordPage.tsx         # Password reset request
│   ├── ResetPasswordPage.tsx          # Token-based reset
│   └── MfaPage.tsx                    # TOTP/SMS verification
│
│── ─── DASHBOARD PAGES (authenticated, sidebar + topbar) ────
│
├── pages/dashboard/
│   ├── DashboardLayout.tsx            # NavRail + ExpansionPanel + Topbar + <Outlet />
│   ├── HomePage.tsx                   # Permission-aware landing dashboard
│   ├── InboxPage.tsx                  # Unified approvals, tasks, mentions, exception alerts
│   │
│   │── ─── PILLAR 1: PEOPLE ────
│   │
│   ├── people/employees/
│   │   ├── EmployeesPage.tsx          # Employee directory (DataTable + search + filters)
│   │   ├── EmployeeNewPage.tsx        # Create employee — multi-step wizard
│   │   └── EmployeeDetailPage.tsx     # Employee detail — scrollable sections + slide-over edit panel
│   │                                  # (edit panel = <EditEmployeeModal /> opened via state, not route)
│   │
│   ├── people/leave/
│   │   ├── LeavePage.tsx              # Leave requests (own or team view)
│   │   ├── LeaveCalendarPage.tsx      # Team leave calendar
│   │   ├── LeaveBalancesPage.tsx      # Per-type balance cards
│   │   └── LeavePoliciesPage.tsx      # Policy CRUD
│   │
│   │── ─── PILLAR 2: WORKFORCE + WMS ────
│   │
│   ├── workforce/
│   │   ├── WorkforcePage.tsx          # Presence — live employee card grid
│   │   ├── WorkforceEmployeePage.tsx  # /workforce/:employeeId — activity detail
│   │   ├── WorkforceAnalyticsPage.tsx # Productivity scores + capacity analytics
│   │   │
│   │   ├── projects/
│   │   │   ├── ProjectsPage.tsx       # All projects in entity scope
│   │   │   ├── ProjectNewPage.tsx     # Create project
│   │   │   ├── ProjectDetailPage.tsx  # /workforce/projects/:id — overview (epics, milestones, members)
│   │   │   ├── ProjectBoardPage.tsx   # Kanban / list view of tasks
│   │   │   ├── ProjectSprintsPage.tsx # Sprint management
│   │   │   └── ProjectRoadmapPage.tsx # Timeline view of epics and milestones
│   │   │
│   │   ├── MyWorkPage.tsx             # My assigned tasks across all projects
│   │   ├── PlannerPage.tsx            # Workspace-level sprints, boards, roadmap
│   │   │
│   │   ├── goals/
│   │   │   ├── GoalsPage.tsx          # OKR overview — objectives and key results
│   │   │   └── GoalDetailPage.tsx     # /workforce/goals/:id — key results + check-ins
│   │   │
│   │   ├── docs/
│   │   │   ├── DocsPage.tsx           # Documents + Wiki list
│   │   │   └── DocDetailPage.tsx      # /workforce/docs/:id — document/wiki page (sanitized HTML)
│   │   │
│   │   ├── time/
│   │   │   ├── TimePage.tsx           # My timesheet
│   │   │   └── TimeReportsPage.tsx    # Time reports (personal and team)
│   │   │
│   │   └── ChatPage.tsx               # Channels, DMs, message threads (real-time SignalR)
│   │
│   │── ─── CROSS-CUTTING ────
│   │
│   ├── calendar/
│   │   ├── CalendarPage.tsx           # Unified calendar (leave, holidays, review cycles)
│   │   ├── SchedulePage.tsx           # Shift schedules
│   │   ├── AttendancePage.tsx         # Attendance corrections
│   │   └── OvertimePage.tsx           # Overtime requests and approvals
│   │
│   ├── notifications/
│   │   ├── NotificationsPage.tsx      # Notification inbox
│   │   └── NotificationPreferencesPage.tsx # Channel preferences
│   │
│   │── ─── PILLAR 3: ORGANIZATION ────
│   │
│   ├── org/
│   │   ├── OrgPage.tsx                # Org chart
│   │   ├── DepartmentsPage.tsx        # Department management
│   │   ├── TeamsPage.tsx              # Team management
│   │   ├── job-families/
│   │   │   ├── JobFamiliesPage.tsx    # Job family list
│   │   │   └── JobFamilyDetailPage.tsx # /org/job-families/:id + associated roles
│   │   └── legal-entities/
│   │       ├── LegalEntitiesPage.tsx  # Legal entity list + hierarchy view
│   │       └── LegalEntityDetailPage.tsx # /org/legal-entities/:id + settings
│   │
│   │── ─── PILLAR 4: ADMIN ────
│   │
│   ├── admin/
│   │   ├── UsersPage.tsx              # People Access — user management + role assignment
│   │   ├── RolesPage.tsx              # Permissions — role and permission management
│   │   ├── AuditPage.tsx              # Activity Trail — audit log viewer
│   │   ├── agents/
│   │   │   ├── AgentsPage.tsx         # Desktop agent fleet
│   │   │   └── AgentDetailPage.tsx    # /admin/agents/:id — agent detail + commands
│   │   ├── DevicesPage.tsx            # Hardware terminals
│   │   └── CompliancePage.tsx         # Data & Privacy — GDPR, data governance
│   │
│   │── ─── PILLAR 5: SETTINGS ────
│   │
│   └── settings/
│       ├── GeneralPage.tsx            # Tenant settings
│       ├── SystemPage.tsx             # Monitoring feature toggles + feature flags (merged)
│       ├── NotificationsSettingsPage.tsx # Channel config (org-level)
│       ├── IntegrationsPage.tsx       # SSO, LMS, payroll providers
│       ├── BrandingPage.tsx           # Logo, colors, domain
│       ├── BillingPage.tsx            # Subscription & plan
│       └── AlertsPage.tsx             # Alert rule configuration
│
└── pages/errors/
    ├── NotFoundPage.tsx               # 404
    ├── ForbiddenPage.tsx              # 403
    └── ErrorPage.tsx                  # Global error boundary fallback
```

**Route config pattern in `router.tsx`:**

```tsx
// src/router.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/lib/security/permission-guard';

export const router = createBrowserRouter([
  // Auth routes (public)
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/forgot-password', element: <ForgotPasswordPage /> },
      { path: '/reset-password', element: <ResetPasswordPage /> },
      { path: '/mfa', element: <MfaPage /> },
    ],
  },
  // Dashboard routes (authenticated)
  {
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/inbox', element: <InboxPage /> },
      // People
      { path: '/people/employees', element: <ProtectedRoute permission="employees:read"><EmployeesPage /></ProtectedRoute> },
      { path: '/people/employees/new', element: <ProtectedRoute permission="employees:write"><EmployeeNewPage /></ProtectedRoute> },
      { path: '/people/employees/:id', element: <ProtectedRoute permission="employees:read"><EmployeeDetailPage /></ProtectedRoute> },
      // ... all other routes
    ],
  },
  { path: '/403', element: <ForbiddenPage /> },
  { path: '*', element: <NotFoundPage /> },
]);
```

**Edit panels / modals (replacing Next.js parallel routes):**
In Vite + React Router, edit panels are opened via local state or a URL query param — not intercepting routes.

```tsx
// EmployeeDetailPage.tsx
const [editSection, setEditSection] = useState<string | null>(null);

return (
  <>
    <EmployeeDetailSections onEdit={setEditSection} />
    {editSection && (
      <EditEmployeePanel section={editSection} onClose={() => setEditSection(null)} />
    )}
  </>
);
```

**Loading states (replacing Next.js `loading.tsx`):**
Use React Suspense boundaries around async data components.

```tsx
<Suspense fallback={<TableSkeleton rows={10} />}>
  <EmployeeDetailSections employeeId={id} />
</Suspense>
```

## Module → Route Mapping

| # | Backend Module | Route(s) | Notes |
|---|---|---|-------|
| 1 | activity-monitoring | `/workforce` (card productivity data), `/workforce/[employeeId]` (activity detail) | Replaces Activity tab |
| 2 | agent-gateway | `/admin/agents/` | Fleet overview, agent detail |
| 3 | auth | `(auth)/`, `/admin/users/`, `/admin/roles/` | Login/MFA + user/role management |
| 4 | calendar | `/calendar` | Unified (leave, holidays, reviews) |
| 5 | configuration | `/settings/general`, `/settings/monitoring` | Tenant config + overrides |
| 6 | core-hr | `/people/employees/` | Profile + lifecycle |
| 7 | documents | Employee detail `#documents` section | Permission-gated section in employee profile |
| 8 | exception-engine | `/settings/alert-rules`, escalated cards on `/workforce` | Rule config in settings; alerts surface as card escalation |
| 9 | expense | Employee detail section | Phase 2 |
| 10 | grievance | Employee detail section | Phase 2 |
| 11 | identity-verification | `/workforce` (online status dot on cards) | Replaces Online Status tab |
| 12 | infrastructure | No pages | Backend-only |
| 13 | leave | `/people/leave/` | Requests, calendar, balances, policies |
| 14 | notifications | `/notifications/`, `/settings/notifications` | Inbox + preferences + org config |
| 15 | org-structure | `/org/` | Departments, teams, org chart, job families, legal entities |
| 16 | payroll | Employee detail `#pay-benefits` section | Phase 2 |
| 17 | performance | Employee detail section | Phase 2 |
| 18 | productivity-analytics | `/workforce` (card score), `/workforce/analytics` | Card score + dedicated analytics page |
| 19 | reporting-engine | Accessible via Quick Search (⌘K) | No dedicated route |
| 20 | shared-platform | `/admin/`, `/settings/` | Spread across admin + settings |
| 21 | skills | `/org/job-families/`, Employee detail section | Job family taxonomy + employee skill records |
| 22 | workforce-presence | `/workforce` (presence cards) | Replaces Online Status tab |
| WMS | project | `/workforce/projects/` | Project management |
| WMS | task | `/workforce/projects/[id]/board`, `/workforce/my-work` | Task management |
| WMS | planning | `/workforce/planner`, `/workforce/projects/[id]/sprints`, `/workforce/projects/[id]/roadmap` | Sprints, boards, roadmap |
| WMS | okr | `/workforce/goals/` | Goals and OKRs |
| WMS | collab (docs/wiki) | `/workforce/docs/` | Documents and Wiki |
| WMS | collab (comments) | Embedded within tasks, projects, docs | Contextual, not a nav item |
| WMS | time | `/workforce/time/` | Timesheets and time logs |
| WMS | resource | `/workforce/analytics` (capacity section) | Capacity and allocation |
| WMS | chat | `/chat` | Channels, DMs, messages |

## Layout System

### Dashboard Layout (`src/pages/dashboard/DashboardLayout.tsx`)

The shell uses a **floating-cards** layout — every element is a separate rounded card with `8px` body padding and `6px` gaps between cards. See [[frontend/design-system/components/shell-layout|Shell Layout]] for the full implementation pattern.

- **Icon Rail:** **52px** floating dark card (`#17181F`, radius 12px). Permission-gated, always visible. See [[frontend/design-system/components/nav-rail|Nav Rail]].
- **Topbar:** **40px** height, floating white/dark card (radius 10px). See [[frontend/architecture/topbar|Topbar Architecture]] for pixel-precise spec.
- **Expansion Panel:** **210px** floating card, width+opacity animation (220ms ease-out). See [[frontend/design-system/components/expansion-panel|Expansion Panel]].
- **Pillar visibility:** Permission-gated via `hasPermission()` — never hardcode role names
- Renders `<Outlet />` from React Router for all child pages

### Auth Layout (`src/pages/auth/AuthLayout.tsx`)
- Centered card, brand logo, no navigation, renders `<Outlet />`

## Provider Stack (App.tsx)

```tsx
// src/App.tsx
import { RouterProvider } from 'react-router-dom';
import { router } from './router';

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <PermissionProvider>     {/* Loads role + employee-level permissions */}
          <SignalRProvider>
            <ThemeProvider>
              <ToastProvider>
                <RouterProvider router={router} />
              </ToastProvider>
            </ThemeProvider>
          </SignalRProvider>
        </PermissionProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
```

## Colocated Component Pattern

Feature components start colocated in the route's `components/` folder, then get promoted when reused.

**Three-tier hierarchy — one location at a time:**

| Scope | Location |
|---|---|
| Used by only one route | `app/(dashboard)/.../components/` (colocated) |
| Used by 2+ pages within the same module | `components/{module}/` — e.g. `components/hr/`, `components/org/`, `components/wms/` |
| Used across different modules | `components/shared/` |

> **WMS boundary:** Components for WMS routes (`/workforce/projects`, `/workforce/goals`, `/workforce/docs`, etc.) go in `components/wms/`, not `components/workforce/`. Workforce Intelligence (presence cards, activity monitoring, identity verification) lives in `components/workforce/`. The two share the `/workforce/` URL prefix but are distinct product domains — never mix their component directories.

**Promotion rule:** when a component moves to a higher tier, **delete the colocated copy**. Never keep both. Duplicating causes them to diverge silently.

**`_types.ts` scope:**
- ✅ Form schemas, column definitions, local UI state shapes
- ❌ API response shapes — those belong in `types/{module}.ts`, not here

**Heavy components use `React.lazy()` + `<Suspense>`:**

```tsx
import { lazy, Suspense } from 'react';

const OrgChart    = lazy(() => import('@/components/org/org-chart'));
const KanbanBoard = lazy(() => import('@/components/wms/kanban-board'));

// Usage:
<Suspense fallback={<ChartSkeleton height={600} />}>
  <OrgChart data={orgData} />
</Suspense>
```

Apply to: org charts, kanban boards, roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets. Never use `next/dynamic()` — that is a Next.js API.

## Page Count

| Section | Pages |
|---------|-------|
| Auth | 4 |
| People (Employees + Leave) | ~12 |
| Workforce Presence | ~2 |
| Workforce WMS (Projects, My Work, Planner, Goals, Docs, Time, Analytics) | ~18 |
| Org (Chart, Departments, Teams, Job Families, Legal Entities) | ~8 |
| Calendar (Calendar, Schedules, Attendance, Overtime) | ~4 |
| Chat | ~1 |
| Inbox | 1 |
| Admin | ~6 |
| Settings | ~7 |
| **Total** | **~63** |

## Related

- [[frontend/architecture/routing|Routing]] — Route guards, middleware, breadcrumbs
- [[frontend/architecture/module-boundaries|Module Boundaries]] — Code splitting, import rules, component promotion path
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR vs CSR per route
- [[frontend/cross-cutting/authorization|Authorization]] — Permission system details
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand
