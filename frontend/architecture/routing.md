# Routing Architecture

## Route Groups

Next.js App Router route groups organize the app into distinct layout contexts:

| Group | Purpose | Layout | Auth Required |
|:------|:--------|:-------|:--------------|
| `(auth)` | Login, MFA, password reset | Centered card, no chrome | No |
| `(dashboard)` | All authenticated views | Rail + Panel + Topbar + Breadcrumbs | Yes (permission-driven) |

> **No separate `(employee)` route group.** Employee self-service uses the same `(dashboard)` pages with permission-driven views. For example, `/people/leave/` shows own leave with `leave:read-own` and team leave with `leave:read-team`. This avoids duplicate pages and keeps the routing simple.

## Two-Sidebar Architecture

The ONEVO frontend has two distinct sidebar pillars, each backed by a different API source:

| Sidebar | Route Prefix | API Source | Feature Gate |
|:--------|:------------|:-----------|:-------------|
| **HR Sidebar** | `/people`, `/org`, `/calendar` | ONEVO Backend | Always active |
| **Workforce Sidebar** | `/workforce` | ONEVO Backend (presence, monitoring) + WMS API (projects, tasks) | `workforce` and/or `wms_access` |

The Workforce sidebar has two sub-sections:

```
/workforce/
  presence/     ← ONEVO Backend (WorkforcePresence module)
  monitoring/   ← ONEVO Backend (ActivityMonitoring module)
  wms/          ← WMS Backend (Projects, Tasks, Sprints, Chat, OKR)
    projects/
    tasks/
    sprints/
    chat/
    okr/
```

**`/workforce/wms/*` is only rendered when `wms_access: true` in the JWT.** If the tenant does not have WMS enabled, the WMS sub-section is hidden from the sidebar and route access redirects to the Workforce home.

### Unified Calendar View

The calendar page aggregates HR events and WMS project events — no shared DB, frontend merge only:

```typescript
// app/(dashboard)/calendar/page.tsx
const [hrEvents] = useQuery('/api/v1/calendar/events')       // ONEVO API
const [wmsEvents] = useQuery(`${WMS_API_URL}/calendar/events`) // WMS API — only if wms_access
const unified = mergeAndSort([...hrEvents, ...(wmsEvents ?? [])])
```

WMS events only fetched when `wms_access: true`. If WMS is unavailable, HR events still render.

## Route Guard Architecture

### Layer 1: Middleware (Edge Runtime)

Runs on every request at the edge. Handles authentication redirects and tenant resolution.

```tsx
// middleware.ts
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Public routes — no auth needed
  if (isPublicRoute(pathname)) return NextResponse.next();

  // 2. Check auth token
  const token = request.cookies.get('access_token');
  if (!token) {
    return NextResponse.redirect(new URL(`/login?redirect=${pathname}`, request.url));
  }

  // 3. Decode tenant from token, set header for downstream
  const decoded = decodeJwt(token.value);
  const response = NextResponse.next();
  response.headers.set('x-tenant-id', decoded.tenantId);
  response.headers.set('x-user-role', decoded.role);

  // 4. Permission-based route gating (never check role names — check permission keys)
  // Sidebar and page content handle fine-grained permission checks via PermissionGate

  // 5. Feature-gated routes
  if (pathname.startsWith('/workforce') && !decoded.features?.includes('workforce')) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // WMS sub-section requires wms_access claim in JWT
  if (pathname.startsWith('/workforce/wms') && !decoded.wms_access) {
    return NextResponse.redirect(new URL('/workforce', request.url));
  }

  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)'],
};
```

### Layer 2: Layout Guards (Server Components)

Each layout validates the user has access to the section:

```tsx
// app/(dashboard)/layout.tsx
export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession();
  if (!session) redirect('/login');

  // No role-based redirect — all users share the dashboard.
  // Sidebar pillars and page content are permission-gated, not role-gated.
  return (
    <DashboardShell user={session.user}>
      {children}
    </DashboardShell>
  );
}
```

### Layer 3: Component Permission Gates (Client)

Fine-grained permission checks within pages:

```tsx
// Only show "Approve" button if user has leave:approve permission
<PermissionGate permission="leave:approve">
  <Button onClick={handleApprove}>Approve</Button>
</PermissionGate>

// Render different views based on permission
<PermissionGate
  permission="payroll:view-salary"
  fallback={<RestrictedField label="Salary" />}
>
  <SalaryDisplay amount={employee.salary} />
</PermissionGate>
```

## Parallel Routes

Used for modals and slide-over panels that preserve parent route context:

```
app/(dashboard)/people/employees/
├── page.tsx                    # Employee list
├── new/page.tsx                # Full-page create (direct nav fallback)
├── @modal/
│   └── (.)new/page.tsx         # Intercepted: create modal over list
├── [id]/
│   ├── layout.tsx              # Shared layout for detail views
│   ├── loading.tsx             # Skeleton while loading
│   ├── not-found.tsx           # Employee not found
│   ├── page.tsx                # Employee detail (scrollable sections)
│   └── @panel/
│       └── (.)edit/page.tsx    # Intercepted: edit panel over detail
├── components/                 # Colocated feature components
│   ├── EmployeeDataTable.tsx
│   ├── EmployeeDetailSections.tsx
│   ├── EmployeeWizardSteps.tsx
│   └── AvatarUpload.tsx
└── _types.ts                   # Local TypeScript definitions
```

**Behavior:**
- Clicking "Add Employee" from list → shows create form as modal (URL changes to `/people/employees/new`)
- Direct navigation to `/people/employees/new` → shows full-page create form
- Clicking "Edit" on detail page → shows edit panel sliding in from right
- Browser back → dismisses modal/panel, restores list/detail

**Pattern applies to all modules with detail pages.** Each feature folder follows the same convention: `components/` for colocated components, `_types.ts` for local types, `loading.tsx` inside `[id]/` for detail skeletons.

## Breadcrumb Generation

Breadcrumbs are auto-generated from the route hierarchy with display name overrides:

```tsx
// lib/breadcrumbs.ts
const ROUTE_LABELS: Record<string, string> = {
  'people': 'People',
  'employees': 'Employees',
  'leave': 'Leave',
  'workforce': 'Workforce',
  'live': 'Live Dashboard',
  'org': 'Organization',
  'inbox': 'Inbox',
  'admin': 'Admin',
  'settings': 'Settings',
  'alert-rules': 'Alert Rules',
};

// Dynamic segments resolved via API:
// /people/employees/[id] → "People > Employees > John Doe"
// /people/leave/calendar → "People > Leave > Calendar"
// /workforce/live       → "Workforce > Live Dashboard"
// /settings/alert-rules → "Settings > Alert Rules"
```

## Navigation State

```tsx
// Sidebar active state derived from pathname
const pathname = usePathname();
const activePillar = pathname.split('/')[1]; // 'people' | 'workforce' | 'org' | 'calendar' | 'inbox' | 'admin' | 'settings'
const activeSection = pathname.split('/')[2]; // 'presence' | 'monitoring' | 'wms' | 'employees' | 'leave' | etc.
const activeItem = pathname.split('/')[3];    // 'projects' | 'tasks' | 'sprints' | 'live' | etc.

// WMS sub-section active when inside /workforce/wms/*
const isWmsSection = activePillar === 'workforce' && activeSection === 'wms';
```

## Error Routes

```
app/(dashboard)/
├── error.tsx                       # Dashboard-level error boundary
├── not-found.tsx                   # 404 within dashboard
├── people/
│   ├── error.tsx                   # People section error boundary
│   └── employees/
│       ├── error.tsx               # Employee-specific error boundary
│       └── [id]/
│           └── not-found.tsx       # Employee not found (404)
```

## Related

- [[frontend/architecture/app-structure|App Structure]] — full route tree
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR/CSR per route
- [[frontend/cross-cutting/authorization|Authorization]] — permission system details
- [[backend/messaging/error-handling|Error Handling]] — error boundary strategy
