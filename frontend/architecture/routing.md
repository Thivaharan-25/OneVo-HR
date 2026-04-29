# Routing Architecture

> This app uses **React Router v7 in library mode** — routes are defined in `src/router.tsx` using `createBrowserRouter()`. There is no file-based routing, no middleware.ts, no Next.js `@modal`/`@panel` parallel routes, and no intercepting routes. All route guards are React components.

## Route Groups

| Group | Layout Component | Auth Required |
|:------|:----------------|:--------------|
| Auth | `AuthLayout` — centered card, no nav | No |
| Dashboard | `DashboardLayout` — NavRail + ExpansionPanel + Topbar + `<Outlet />` | Yes |

> **No separate employee self-service group.** Employee self-service uses the same dashboard pages with permission-driven views. `/people/leave/` shows own leave with `leave:read-own` and team leave with `leave:read-team`.

## Route Config Pattern

All routes defined in a single file:

```tsx
// src/router.tsx
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { ProtectedRoute } from '@/lib/security/permission-guard';

export const router = createBrowserRouter([
  // Auth — public
  {
    element: <AuthLayout />,
    children: [
      { path: '/login',            element: <LoginPage /> },
      { path: '/forgot-password',  element: <ForgotPasswordPage /> },
      { path: '/reset-password',   element: <ResetPasswordPage /> },
      { path: '/mfa',              element: <MfaPage /> },
    ],
  },

  // Dashboard — authenticated
  {
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <HomePage /> },
      { path: '/inbox', element: <InboxPage /> },

      // People
      { path: '/people/employees',     element: <ProtectedRoute permission="employees:read"><EmployeesPage /></ProtectedRoute> },
      { path: '/people/employees/new', element: <ProtectedRoute permission="employees:write"><EmployeeNewPage /></ProtectedRoute> },
      { path: '/people/employees/:id', element: <ProtectedRoute permission="employees:read"><EmployeeDetailPage /></ProtectedRoute> },
      { path: '/people/leave',         element: <ProtectedRoute permission="leave:read"><LeavePage /></ProtectedRoute> },
      { path: '/people/leave/calendar',element: <ProtectedRoute permission="leave:read"><LeaveCalendarPage /></ProtectedRoute> },
      { path: '/people/leave/balances',element: <ProtectedRoute permission="leave:read"><LeaveBalancesPage /></ProtectedRoute> },
      { path: '/people/leave/policies',element: <ProtectedRoute permission="leave:manage"><LeavePoliciesPage /></ProtectedRoute> },

      // Workforce
      { path: '/workforce',              element: <ProtectedRoute permission="workforce:read"><WorkforcePage /></ProtectedRoute> },
      { path: '/workforce/:employeeId',  element: <ProtectedRoute permission="workforce:read"><WorkforceEmployeePage /></ProtectedRoute> },
      { path: '/workforce/analytics',    element: <ProtectedRoute permission="analytics:read"><WorkforceAnalyticsPage /></ProtectedRoute> },
      { path: '/workforce/projects',     element: <ProtectedRoute permission="projects:read"><ProjectsPage /></ProtectedRoute> },
      { path: '/workforce/projects/new', element: <ProtectedRoute permission="projects:write"><ProjectNewPage /></ProtectedRoute> },
      { path: '/workforce/projects/:id',         element: <ProtectedRoute permission="projects:read"><ProjectDetailPage /></ProtectedRoute> },
      { path: '/workforce/projects/:id/board',   element: <ProtectedRoute permission="tasks:read"><ProjectBoardPage /></ProtectedRoute> },
      { path: '/workforce/projects/:id/sprints', element: <ProtectedRoute permission="planning:read"><ProjectSprintsPage /></ProtectedRoute> },
      { path: '/workforce/projects/:id/roadmap', element: <ProtectedRoute permission="planning:read"><ProjectRoadmapPage /></ProtectedRoute> },
      { path: '/workforce/my-work',  element: <ProtectedRoute permission="tasks:read"><MyWorkPage /></ProtectedRoute> },
      { path: '/workforce/planner',  element: <ProtectedRoute permission="planning:read"><PlannerPage /></ProtectedRoute> },
      { path: '/workforce/goals',    element: <ProtectedRoute permission="goals:read"><GoalsPage /></ProtectedRoute> },
      { path: '/workforce/goals/:id',element: <ProtectedRoute permission="goals:read"><GoalDetailPage /></ProtectedRoute> },
      { path: '/workforce/docs',     element: <ProtectedRoute permission="docs:read"><DocsPage /></ProtectedRoute> },
      { path: '/workforce/docs/:id', element: <ProtectedRoute permission="docs:read"><DocDetailPage /></ProtectedRoute> },
      { path: '/workforce/time',         element: <ProtectedRoute permission="time:read"><TimePage /></ProtectedRoute> },
      { path: '/workforce/time/reports', element: <ProtectedRoute permission="time:read"><TimeReportsPage /></ProtectedRoute> },
      { path: '/chat', element: <ProtectedRoute permission="chat:read"><ChatPage /></ProtectedRoute> },

      // Org
      { path: '/org',                       element: <ProtectedRoute permission="org:read"><OrgPage /></ProtectedRoute> },
      { path: '/org/departments',           element: <ProtectedRoute permission="org:read"><DepartmentsPage /></ProtectedRoute> },
      { path: '/org/teams',                 element: <ProtectedRoute permission="org:read"><TeamsPage /></ProtectedRoute> },
      { path: '/org/job-families',          element: <ProtectedRoute permission="org:manage"><JobFamiliesPage /></ProtectedRoute> },
      { path: '/org/job-families/:id',      element: <ProtectedRoute permission="org:manage"><JobFamilyDetailPage /></ProtectedRoute> },
      { path: '/org/legal-entities',        element: <ProtectedRoute permission="org:manage"><LegalEntitiesPage /></ProtectedRoute> },
      { path: '/org/legal-entities/:id',    element: <ProtectedRoute permission="org:manage"><LegalEntityDetailPage /></ProtectedRoute> },

      // Calendar
      { path: '/calendar',            element: <ProtectedRoute permission="calendar:read"><CalendarPage /></ProtectedRoute> },
      { path: '/calendar/schedule',   element: <ProtectedRoute permission="schedule:read"><SchedulePage /></ProtectedRoute> },
      { path: '/calendar/attendance', element: <ProtectedRoute permission="attendance:read"><AttendancePage /></ProtectedRoute> },
      { path: '/calendar/overtime',   element: <ProtectedRoute permission="overtime:read"><OvertimePage /></ProtectedRoute> },

      // Notifications
      { path: '/notifications',             element: <NotificationsPage /> },
      { path: '/notifications/preferences', element: <NotificationPreferencesPage /> },

      // Admin
      { path: '/admin/users',      element: <ProtectedRoute permission="admin:users"><UsersPage /></ProtectedRoute> },
      { path: '/admin/roles',      element: <ProtectedRoute permission="admin:roles"><RolesPage /></ProtectedRoute> },
      { path: '/admin/audit',      element: <ProtectedRoute permission="admin:audit"><AuditPage /></ProtectedRoute> },
      { path: '/admin/agents',     element: <ProtectedRoute permission="admin:agents"><AgentsPage /></ProtectedRoute> },
      { path: '/admin/agents/:id', element: <ProtectedRoute permission="admin:agents"><AgentDetailPage /></ProtectedRoute> },
      { path: '/admin/devices',    element: <ProtectedRoute permission="admin:devices"><DevicesPage /></ProtectedRoute> },
      { path: '/admin/compliance', element: <ProtectedRoute permission="admin:compliance"><CompliancePage /></ProtectedRoute> },

      // Settings
      { path: '/settings/general',       element: <ProtectedRoute permission="settings:read"><GeneralPage /></ProtectedRoute> },
      { path: '/settings/system',        element: <ProtectedRoute permission="settings:system"><SystemPage /></ProtectedRoute> },
      { path: '/settings/notifications', element: <ProtectedRoute permission="settings:notifications"><NotificationsSettingsPage /></ProtectedRoute> },
      { path: '/settings/integrations',  element: <ProtectedRoute permission="settings:integrations"><IntegrationsPage /></ProtectedRoute> },
      { path: '/settings/branding',      element: <ProtectedRoute permission="settings:branding"><BrandingPage /></ProtectedRoute> },
      { path: '/settings/billing',       element: <ProtectedRoute permission="settings:billing"><BillingPage /></ProtectedRoute> },
      { path: '/settings/alert-rules',   element: <ProtectedRoute permission="settings:alerts"><AlertsPage /></ProtectedRoute> },
    ],
  },

  // Errors
  { path: '/403', element: <ForbiddenPage /> },
  { path: '*',    element: <NotFoundPage /> },
]);
```

## Route Guard Architecture

### Layer 1: ProtectedRoute Component

Replaces Next.js middleware. Runs in the browser at render time.

```tsx
// lib/security/permission-guard.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/use-auth-store';

interface Props {
  permission?: string;
  children: ReactNode;
}

export function ProtectedRoute({ permission, children }: Props) {
  const { user, hasPermission } = useAuthStore();
  const location = useLocation();

  if (!user) {
    // Preserve intended destination for redirect after login
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
}
```

### Layer 2: PermissionGate (Component-Level)

Fine-grained UI hiding within pages — does NOT replace route guards:

```tsx
// Only show "Approve" button if user has leave:approve
<PermissionGate permission="leave:approve">
  <Button onClick={handleApprove}>Approve</Button>
</PermissionGate>

// Render different content based on permission
<PermissionGate
  permission="payroll:view-salary"
  fallback={<RestrictedField label="Salary" />}
>
  <SalaryDisplay amount={employee.salary} />
</PermissionGate>
```

### Layer 3: Feature Gates (Tenant Feature Flags)

WMS routes only render when the tenant has the feature enabled:

```tsx
// Sidebar hides WMS items when feature is off
const { hasFeature } = useAuthStore();

// WMS sub-routes redirect when feature is not enabled
{ path: '/workforce/projects', element: (
  <ProtectedRoute permission="projects:read">
    {hasFeature('wms:projects') ? <ProjectsPage /> : <Navigate to="/workforce" replace />}
  </ProtectedRoute>
)}
```

## Edit Panels and Modals

Replacing Next.js parallel routes (`@panel`, `@modal`). Use local state or a URL query param:

```tsx
// EmployeeDetailPage.tsx — edit panel via local state
const [editSection, setEditSection] = useState<string | null>(null);

return (
  <>
    <EmployeeDetailSections onEdit={setEditSection} />
    {editSection && (
      <SlideOverPanel open onClose={() => setEditSection(null)}>
        <EditEmployeeSection section={editSection} />
      </SlideOverPanel>
    )}
  </>
);

// EmployeesPage.tsx — create modal via URL param (preserves bookmarkability)
const [searchParams, setSearchParams] = useSearchParams();
const showCreate = searchParams.get('action') === 'new';
```

## Breadcrumb Generation

Derived from `useLocation()` — no file-system magic needed:

```tsx
// lib/utils/breadcrumbs.ts
import { useLocation } from 'react-router-dom';

const ROUTE_LABELS: Record<string, string> = {
  people: 'People', employees: 'Employees', leave: 'Leave',
  workforce: 'Workforce', org: 'Organization', calendar: 'Calendar',
  admin: 'Admin', settings: 'Settings', 'alert-rules': 'Alert Rules',
};

export function useBreadcrumbs() {
  const { pathname } = useLocation();
  const segments = pathname.split('/').filter(Boolean);

  return segments.map((segment, i) => ({
    label: ROUTE_LABELS[segment] ?? segment,
    href: '/' + segments.slice(0, i + 1).join('/'),
    isCurrent: i === segments.length - 1,
  }));
}
```

## Navigation State

```tsx
import { useLocation } from 'react-router-dom';

const { pathname } = useLocation();
const activePillar = pathname.split('/')[1]; // 'people' | 'workforce' | 'org' | etc.
const activeItem  = pathname.split('/')[2];  // 'employees' | 'leave' | 'projects' | etc.
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — full page file tree
- [[frontend/cross-cutting/authorization|Authorization]] — permission system details
- [[frontend/lib/security/permission-guard|Permission Guard]] — route guard implementation
