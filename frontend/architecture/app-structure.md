# Frontend App Structure

> **Note:** A second frontend app (`dev-console`) exists for platform administration â€” see `developer-platform/frontend/app-structure.md` for details. This document covers the primary ONEVO tenant-facing app only.

> **Stack:** This app runs on **Vite + React 19 + React Router v7** â€” not Next.js. There is no file-based routing, no `app/` directory, no `page.tsx`/`layout.tsx` conventions, no parallel routes (`@panel`, `@modal`), and no intercepting routes (`(.)edit`). All routes are defined in `src/router.tsx`. Page components live in `src/pages/`. Loading states use React Suspense. Edit panels and create modals use React Router nested routes with `<Outlet />` or controlled modal state.

## Route Tree

All 22 backend modules + 9 WMS modules mapped to ~63 frontend pages. Single route tree with permission-driven views (no separate employee self-service group).

### Authorization Model

**Hybrid permissions â€” not traditional fixed-role RBAC:**
1. **Custom roles** â€” tenants create roles with custom names and assign granular permissions
2. **Per-employee overrides** â€” individual employees can be granted/revoked specific module/feature access independent of their role

**Never hardcode role names.** Always check permission keys (e.g., `leave:read`, `leave:approve`, `payroll:write`).

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
â”œâ”€â”€ main.tsx                           # Entry: React 19, StrictMode, mount <App />
â”œâ”€â”€ App.tsx                            # Provider stack + <RouterProvider router={router} />
â”œâ”€â”€ router.tsx                         # ALL routes defined here using createBrowserRouter()
â”‚
â”œâ”€â”€ lib/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ client.ts                         # Fetch wrapper â€” runs interceptor chain
â”‚   â”‚   â”œâ”€â”€ index.ts                          # Re-exports apiClient + all endpoint modules
â”‚   â”‚   â”œâ”€â”€ errors.ts                         # ApiError, AuthError, ProblemDetails type
â”‚   â”‚   â”œâ”€â”€ interceptors/
â”‚   â”‚   â”‚   â”œâ”€â”€ session.interceptor.ts        # Ensures cookie-backed session is fresh
â”‚   â”‚   â”‚   â”œâ”€â”€ tenant.interceptor.ts         # Injects X-Entity-Id from active entity in authStore
â”‚   â”‚   â”‚   â”œâ”€â”€ correlation.interceptor.ts    # Injects X-Correlation-Id (crypto.randomUUID)
â”‚   â”‚   â”‚   â””â”€â”€ error.interceptor.ts          # 401 retry after refresh; toast on 4xx/5xx
â”‚   â”‚   â””â”€â”€ endpoints/
â”‚   â”‚       â”œâ”€â”€ auth.ts
â”‚   â”‚       â”œâ”€â”€ employees.ts
â”‚   â”‚       â”œâ”€â”€ leave.ts
â”‚   â”‚       â”œâ”€â”€ org.ts
â”‚   â”‚       â”œâ”€â”€ workforce.ts
â”‚   â”‚       â”œâ”€â”€ calendar.ts
â”‚   â”‚       â”œâ”€â”€ notifications.ts
â”‚   â”‚       â”œâ”€â”€ settings.ts
â”‚   â”‚       â”œâ”€â”€ admin.ts
â”‚   â”‚       â”œâ”€â”€ agents.ts
â”‚   â”‚       â”œâ”€â”€ identity.ts
â”‚   â”‚       â””â”€â”€ wms/
â”‚   â”‚           â”œâ”€â”€ projects.ts
â”‚   â”‚           â”œâ”€â”€ tasks.ts
â”‚   â”‚           â”œâ”€â”€ planner.ts
â”‚   â”‚           â”œâ”€â”€ goals.ts
â”‚   â”‚           â”œâ”€â”€ docs.ts
â”‚   â”‚           â”œâ”€â”€ time.ts
â”‚   â”‚           â””â”€â”€ chat.ts
â”‚   â”œâ”€â”€ security/
â”‚   â”‚   â”œâ”€â”€ csrf.ts                           # CSRF header helper for cookie-authenticated mutations
â”‚   â”‚   â”œâ”€â”€ idle-timeout.ts                   # Auto-logout after inactivity
â”‚   â”‚   â”œâ”€â”€ sanitizer.ts                      # DOMPurify wrapper â€” used on all user-generated HTML
â”‚   â”‚   â””â”€â”€ permission-guard.tsx              # <ProtectedRoute> component + redirect to /403
â”‚   â”œâ”€â”€ signalr/
â”‚   â”‚   â””â”€â”€ client.ts                         # HubConnectionBuilder setup; re-export hub instance
â”‚   â”œâ”€â”€ i18n.ts                               # i18next init (browser language detector + HTTP backend)
â”‚   â””â”€â”€ utils/
â”‚       â”œâ”€â”€ cn.ts                             # clsx + tailwind-merge shorthand
â”‚       â”œâ”€â”€ format-date.ts                    # date-fns wrappers
â”‚       â””â”€â”€ to-params.ts                      # Object â†’ URLSearchParams
â”‚
â”œâ”€â”€ stores/
â”‚   â”œâ”€â”€ use-auth-store.ts                     # Zustand: current user, activeEntityId, token expiry
â”‚   â”œâ”€â”€ use-sidebar-store.ts                  # Zustand: expanded pillar, active item
â”‚   â””â”€â”€ use-filter-store.ts                   # Zustand: per-module filter state
â”‚
â”‚â”€â”€ â”€â”€â”€ AUTH PAGES (public, no nav) â”€â”€â”€â”€
â”‚
â”œâ”€â”€ pages/auth/
â”‚   â”œâ”€â”€ AuthLayout.tsx                 # Centered card, brand logo â€” wraps auth pages via <Outlet />
â”‚   â”œâ”€â”€ LoginPage.tsx                  # Email + password
â”‚   â”œâ”€â”€ ForgotPasswordPage.tsx         # Password reset request
â”‚   â”œâ”€â”€ ResetPasswordPage.tsx          # Token-based reset
â”‚   â””â”€â”€ MfaPage.tsx                    # TOTP verification
â”‚
â”‚â”€â”€ â”€â”€â”€ DASHBOARD PAGES (authenticated, sidebar + topbar) â”€â”€â”€â”€
â”‚
â”œâ”€â”€ pages/dashboard/
â”‚   â”œâ”€â”€ DashboardLayout.tsx            # NavRail + ExpansionPanel + Topbar + <Outlet />
â”‚   â”œâ”€â”€ HomePage.tsx                   # Permission-aware landing dashboard
â”‚   â”œâ”€â”€ InboxPage.tsx                  # Unified approvals, tasks, mentions, exception alerts
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ PILLAR 1: PEOPLE â”€â”€â”€â”€
â”‚   â”‚
â”‚   â”œâ”€â”€ people/employees/
â”‚   â”‚   â”œâ”€â”€ EmployeesPage.tsx          # Employee directory (DataTable + search + filters)
â”‚   â”‚   â”œâ”€â”€ EmployeeNewPage.tsx        # Create employee â€” multi-step wizard
â”‚   â”‚   â””â”€â”€ EmployeeDetailPage.tsx     # Employee detail â€” scrollable sections + slide-over edit panel
â”‚   â”‚                                  # (edit panel = <EditEmployeeModal /> opened via state, not route)
â”‚   â”‚
â”‚   â”œâ”€â”€ people/leave/
â”‚   â”‚   â”œâ”€â”€ LeavePage.tsx              # Leave requests (own or team view)
â”‚   â”‚   â”œâ”€â”€ LeaveCalendarPage.tsx      # Team leave calendar
â”‚   â”‚   â”œâ”€â”€ LeaveBalancesPage.tsx      # Per-type balance cards
â”‚   â”‚   â””â”€â”€ LeavePoliciesPage.tsx      # Policy CRUD
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ PILLAR 2: WORKFORCE + WMS â”€â”€â”€â”€
â”‚   â”‚
â”‚   â”œâ”€â”€ workforce/
â”‚   â”‚   â”œâ”€â”€ WorkforcePage.tsx          # Presence â€” live employee card grid
â”‚   â”‚   â”œâ”€â”€ WorkforceEmployeePage.tsx  # /workforce/:employeeId â€” activity detail
â”‚   â”‚   â”œâ”€â”€ WorkforceAnalyticsPage.tsx # Productivity scores + capacity analytics
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ projects/
â”‚   â”‚   â”‚   â”œâ”€â”€ ProjectsPage.tsx       # All projects in company tenant scope
â”‚   â”‚   â”‚   â”œâ”€â”€ ProjectNewPage.tsx     # Create project
â”‚   â”‚   â”‚   â”œâ”€â”€ ProjectDetailPage.tsx  # /workforce/projects/:id â€” overview (epics, milestones, members)
â”‚   â”‚   â”‚   â”œâ”€â”€ ProjectBoardPage.tsx   # Kanban / list view of tasks
â”‚   â”‚   â”‚   â”œâ”€â”€ ProjectSprintsPage.tsx # Sprint management
â”‚   â”‚   â”‚   â””â”€â”€ ProjectRoadmapPage.tsx # Timeline view of epics and milestones
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ MyWorkPage.tsx             # My assigned tasks across all projects
â”‚   â”‚   â”œâ”€â”€ PlannerPage.tsx            # Workspace-level sprints, boards, roadmap
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ goals/
â”‚   â”‚   â”‚   â”œâ”€â”€ GoalsPage.tsx          # OKR overview â€” objectives and key results
â”‚   â”‚   â”‚   â””â”€â”€ GoalDetailPage.tsx     # /workforce/goals/:id â€” key results + check-ins
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ docs/
â”‚   â”‚   â”‚   â”œâ”€â”€ DocsPage.tsx           # Documents + Wiki list
â”‚   â”‚   â”‚   â””â”€â”€ DocDetailPage.tsx      # /workforce/docs/:id â€” document/wiki page (sanitized HTML)
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ time/
â”‚   â”‚   â”‚   â”œâ”€â”€ TimePage.tsx           # My timesheet
â”‚   â”‚   â”‚   â””â”€â”€ TimeReportsPage.tsx    # Time reports (personal and team)
â”‚   â”‚   â”‚
â”‚   â”‚   â””â”€â”€ ChatPage.tsx               # Channels, DMs, message threads (real-time SignalR)
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ CROSS-CUTTING â”€â”€â”€â”€
â”‚   â”‚
â”‚   â”œâ”€â”€ calendar/
â”‚   â”‚   â”œâ”€â”€ CalendarPage.tsx           # Unified calendar (leave, holidays, review cycles)
â”‚   â”‚   â”œâ”€â”€ SchedulePage.tsx           # Shift schedules
â”‚   â”‚   â”œâ”€â”€ AttendancePage.tsx         # Attendance corrections
â”‚   â”‚   â””â”€â”€ OvertimePage.tsx           # Overtime requests and approvals
â”‚   â”‚
â”‚   â”œâ”€â”€ notifications/
â”‚   â”‚   â”œâ”€â”€ NotificationsPage.tsx      # Notification inbox
â”‚   â”‚   â””â”€â”€ NotificationPreferencesPage.tsx # Channel preferences
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ PILLAR 3: ORGANIZATION â”€â”€â”€â”€
â”‚   â”‚
â”‚   â”œâ”€â”€ org/
â”‚   â”‚   â”œâ”€â”€ OrgPage.tsx                # Org chart
â”‚   â”‚   â”œâ”€â”€ DepartmentsPage.tsx        # Department management
â”‚   â”‚   â”œâ”€â”€ TeamsPage.tsx              # Team management
â”‚   â”‚   â”œâ”€â”€ job-families/
â”‚   â”‚   â”‚   â”œâ”€â”€ JobFamiliesPage.tsx    # Job family list
â”‚   â”‚   â”‚   â””â”€â”€ JobFamilyDetailPage.tsx # /org/job-families/:id + associated roles
â”‚   â”‚   â””â”€â”€ legal-entities/
â”‚   â”‚       â”œâ”€â”€ LegalEntitiesPage.tsx  # Legal entity list + hierarchy view
â”‚   â”‚       â””â”€â”€ LegalEntityDetailPage.tsx # /org/legal-entities/:id + settings
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ PILLAR 4: ADMIN â”€â”€â”€â”€
â”‚   â”‚
â”‚   â”œâ”€â”€ admin/
â”‚   â”‚   â”œâ”€â”€ UsersPage.tsx              # People Access â€” user management + role assignment
â”‚   â”‚   â”œâ”€â”€ RolesPage.tsx              # Permissions â€” role and permission management
â”‚   â”‚   â”œâ”€â”€ AuditPage.tsx              # Activity Trail â€” audit log viewer
â”‚   â”‚   â”œâ”€â”€ agents/
â”‚   â”‚   â”‚   â”œâ”€â”€ AgentsPage.tsx         # Desktop agent fleet
â”‚   â”‚   â”‚   â””â”€â”€ AgentDetailPage.tsx    # /admin/agents/:id â€” agent detail + commands
â”‚   â”‚   â”œâ”€â”€ DevicesPage.tsx            # Hardware terminals
â”‚   â”‚   â””â”€â”€ CompliancePage.tsx         # Data & Privacy â€” GDPR, data governance
â”‚   â”‚
â”‚   â”‚â”€â”€ â”€â”€â”€ PILLAR 5: SETTINGS â”€â”€â”€â”€
â”‚   â”‚
â”‚   â””â”€â”€ settings/
â”‚       â”œâ”€â”€ GeneralPage.tsx            # Tenant settings
â”‚       â”œâ”€â”€ SystemPage.tsx             # Monitoring feature toggles + feature flags (merged)
â”‚       â”œâ”€â”€ NotificationsSettingsPage.tsx # Channel config (org-level)
â”‚       â”œâ”€â”€ IntegrationsPage.tsx       # SSO, LMS, payroll providers
â”‚       â”œâ”€â”€ BrandingPage.tsx           # Logo, colors, domain
â”‚       â”œâ”€â”€ BillingPage.tsx            # Subscription & plan
â”‚       â””â”€â”€ AlertsPage.tsx             # Alert rule configuration
â”‚
â””â”€â”€ pages/errors/
    â”œâ”€â”€ NotFoundPage.tsx               # 404
    â”œâ”€â”€ ForbiddenPage.tsx              # 403
    â””â”€â”€ ErrorPage.tsx                  # Global error boundary fallback
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
In Vite + React Router, edit panels are opened via local state or a URL query param â€” not intercepting routes.

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

## Module â†’ Route Mapping

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
| 15 | org-structure | `/org/` | Departments, teams, org chart, job families, company profile |
| 16 | payroll | Employee detail `#pay-benefits` section | Phase 2 |
| 17 | performance | Employee detail section | Phase 2 |
| 18 | productivity-analytics | `/workforce` (card score), `/workforce/analytics` | Card score + dedicated analytics page |
| 19 | reporting-engine | Accessible via Quick Search (âŒ˜K) | No dedicated route |
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


### Responsive Layout Components

Responsive behavior is centralized in shared shell primitives instead of repeated page-level viewport checks:

```text
src/components/layout/
|-- ShellLayout.tsx             # Responsive shell wrapper: topbar, rail, panel, drawer, content
|-- Topbar.tsx                  # Responsive entity/search/actions header
|-- NavRail.tsx                 # Laptop/desktop rail navigation
|-- ExpansionPanel.tsx          # Desktop/laptop secondary navigation panel
|-- MobileNavDrawer.tsx         # Mobile/tablet drawer using the same pillar config
|-- ResponsivePage.tsx          # Page padding, width, overflow, and header slots
`-- BreakpointProvider.tsx      # Shared breakpoint state for shell/page adaptations
```

Pages may adjust their own content density, but the shell, navigation, topbar, drawer, and base page spacing should come from these shared components.

### Dashboard Layout (`src/pages/dashboard/DashboardLayout.tsx`)

The shell uses a **floating-cards** layout â€” every element is a separate rounded card with `8px` body padding and `6px` gaps between cards. See [[frontend/design-system/components/shell-layout|Shell Layout]] for the full implementation pattern.

- **Icon Rail:** **52px** floating dark card (`#17181F`, radius 12px). Permission-gated; visible on laptop/desktop and replaced by `MobileNavDrawer` on mobile/tablet. See [[frontend/design-system/components/nav-rail|Nav Rail]].
- **Topbar:** **40px** height, floating white/dark card (radius 10px) with compact mobile/tablet variants. See [[frontend/architecture/topbar|Topbar Architecture]] for pixel-precise spec.
- **Expansion Panel:** **210px** floating card, width+opacity animation (220ms ease-out); hidden/collapsed below desktop. See [[frontend/design-system/components/expansion-panel|Expansion Panel]].
- **Pillar visibility:** Permission-gated via `hasPermission()` â€” never hardcode role names
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

> `PermissionProvider` loads both role-level and per-employee-override permissions on mount and exposes them via `usePermissions()`. `usePermissions().hasPermission(key)` is the only correct way to gate UI â€” never read role names directly.

## Colocated Component Pattern

Feature components start colocated in the route's `components/` folder, then get promoted when reused.

**Three-tier hierarchy â€” one location at a time:**

| Scope | Location |
|---|---|
| Used by only one route | `app/(dashboard)/.../components/` (colocated) |
| Used by 2+ pages within the same module | `components/{module}/` â€” e.g. `components/hr/`, `components/org/`, `components/wms/` |
| Used across different modules | `components/shared/` |

> **WMS boundary:** Components for WMS routes (`/workforce/projects`, `/workforce/goals`, `/workforce/docs`, etc.) go in `components/wms/`, not `components/workforce/`. Workforce Intelligence (presence cards, activity monitoring, identity verification) lives in `components/workforce/`. The two share the `/workforce/` URL prefix but are distinct product domains â€” never mix their component directories.

**Promotion rule:** when a component moves to a higher tier, **delete the colocated copy**. Never keep both. Duplicating causes them to diverge silently.

**`_types.ts` scope:**
- âœ… Form schemas, column definitions, local UI state shapes
- âŒ API response shapes â€” those belong in `types/{module}.ts`, not here

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

Apply to: org charts, kanban boards, roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets. Never use `next/dynamic()` â€” that is a Next.js API.

## Page Count

| Section | Pages |
|---------|-------|
| Auth | 4 |
| People (Employees + Leave) | ~12 |
| Workforce Presence | ~2 |
| Workforce WMS (Projects, My Work, Planner, Goals, Docs, Time, Analytics) | ~18 |
| Org (Chart, Departments, Teams, Job Families, Company Profile) | ~8 |
| Calendar (Calendar, Schedules, Attendance, Overtime) | ~4 |
| Chat | ~1 |
| Inbox | 1 |
| Admin | ~6 |
| Settings | ~7 |
| **Total** | **~63** |

## Related

- [[frontend/architecture/routing|Routing]] â€” Route guards, middleware, breadcrumbs
- [[frontend/architecture/module-boundaries|Module Boundaries]] â€” Code splitting, import rules, component promotion path
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] â€” SSR vs CSR per route
- [[frontend/cross-cutting/authorization|Authorization]] â€” Permission system details
- [[frontend/data-layer/state-management|State Management]] â€” TanStack Query + Zustand

