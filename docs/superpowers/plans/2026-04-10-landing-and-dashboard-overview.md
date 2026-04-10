# Landing Page & Dashboard Overview — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the public white-label landing page (`/`) and the authenticated dashboard overview page (`/dashboard`), including all six permission-gated zones, dashboard customization UX, and all supporting API endpoints.

**Architecture:** Two routes — one public (`/`), one protected (`/dashboard`). Both are permission-driven: the landing page loads tenant branding with no auth; the dashboard renders only the zones the user's JWT claims allow. No locked/blurred zones — absent permission = absent DOM. Preferences are stored server-side and applied on load.

**Tech Stack:** Next.js (App Router), TypeScript, Three.js (lazy-loaded), Recharts, @dnd-kit/core, ASP.NET Core backend, PostgreSQL.

**Reference Spec:** `docs/superpowers/specs/2026-04-10-landing-and-dashboard-overview-design.md`  
**Depends on:** `docs/superpowers/specs/2026-04-08-frontend-redesign-design.md` (brand tokens, glass surfaces)

---

## Dev Assignment

| Dev | Scope | Tasks |
|:----|:------|:------|
| **DEV2** | Landing page, Three.js scene, SignInModal, Zone 1 | Tasks 1 (partial), 3, 5 (Zone 1 component) |
| **DEV1** | Dashboard shell, Zones 2+3+5, Prefs API, Customization | Tasks 1 (partial), 4, 5 (shell), 6, 8, 9 |
| **DEV3** | Zone 4 (Workforce Live), Zone 6 (Workforce Events) | Tasks 1 (partial), 7 |
| **DEV4** | Tenant Branding API | Tasks 1 (partial), 2 |

---

## File Map

### Files to Create (Brain Repo — Docs)
- `Userflow/Auth-Access/landing-page.md` — Landing page user flow
- `Userflow/Dashboard/dashboard-overview.md` — Dashboard overview user flow
- `Userflow/Dashboard/dashboard-customization.md` — Dashboard customization user flow

### Files to Create (Frontend — App)
- `src/app/(public)/page.tsx` — Landing page route
- `src/components/landing/WorkforceParticleScene.tsx` — Three.js particle scene
- `src/components/landing/LandingHero.tsx` — Hero left column (eyebrow, H1, subtitle, CTAs, stat counters)
- `src/components/landing/FeaturesStrip.tsx` — 4-column feature strip below hero
- `src/components/auth/SignInModal.tsx` — Shared sign-in modal (used on landing + any future auth entry)
- `src/app/(protected)/dashboard/page.tsx` — Dashboard overview route
- `src/components/dashboard/DashboardShell.tsx` — Zone orchestrator, reads prefs + JWT claims
- `src/components/dashboard/zones/ExceptionAlertStrip.tsx` — Zone 1
- `src/components/dashboard/zones/KpiCardsZone.tsx` — Zone 2
- `src/components/dashboard/zones/PendingActionsZone.tsx` — Zone 3
- `src/components/dashboard/zones/WorkforceLiveZone.tsx` — Zone 4
- `src/components/dashboard/zones/TrendsChartsZone.tsx` — Zone 5
- `src/components/dashboard/zones/WorkforceEventsZone.tsx` — Zone 6
- `src/components/dashboard/customize/CustomizeBar.tsx` — Edit mode instruction bar
- `src/components/dashboard/customize/WidgetLibraryPanel.tsx` — Slide-in widget library
- `src/hooks/useDashboardPrefs.ts` — Prefs fetch + PATCH hook

### Files to Create (Backend)
- `TenantBrandingController.cs` — `GET /api/v1/tenants/current/branding`
- `DashboardController.cs` — all `/api/v1/dashboard/*` endpoints
- `UserDashboardPrefsController.cs` — `GET/PATCH /api/v1/users/me/dashboard-prefs`
- Migration: `user_dashboard_prefs` table

### Files to Modify
- `current-focus/DEV1-*.md` — Add Task 6 (Dashboard) to DEV1 task file
- `current-focus/DEV2-auth-security.md` — Add landing page + SignInModal + Zone 1 to DEV2 scope
- `current-focus/DEV3-activity-monitoring.md` — Add Zone 4 + Zone 6 to DEV3 scope
- `current-focus/DEV4-configuration.md` — Add Tenant Branding API to DEV4 scope

---

## API Reference

All endpoints follow `backend/api-conventions.md`. All protected endpoints require `Authorization: Bearer {jwt}` and `X-Tenant-Id: {tenantId}`.

| Endpoint | Method | Auth | Permission | Owner | Used By |
|:---------|:-------|:-----|:-----------|:------|:--------|
| `/api/v1/tenants/current/branding` | GET | None | None (public) | DEV4 | Landing page |
| `/api/v1/auth/login` | POST | None | None | DEV2 (exists) | SignInModal |
| `/api/v1/dashboard` | GET | JWT | `employees:read` OR `workforce:read` OR `leave:read` | DEV1 | Dashboard shell |
| `/api/v1/dashboard/exceptions/active` | GET | JWT | `workforce:read` + `workforce_intelligence` module | DEV2 | Zone 1 |
| `/api/v1/dashboard/kpis` | GET | JWT | `employees:read` OR `workforce:read` OR `leave:read` | DEV1 | Zone 2 |
| `/api/v1/dashboard/pending-actions` | GET | JWT | Any `*:approve` OR self scope | DEV1 | Zone 3 |
| `/api/v1/dashboard/workforce-live` | GET | JWT | `workforce:read` + `workforce_intelligence` module | DEV3 | Zone 4 |
| `/api/v1/dashboard/trends` | GET | JWT | `workforce:read` OR `leave:read` | DEV1 | Zone 5 |
| `/api/v1/dashboard/workforce-events` | GET | JWT | `employees:read` OR `leave:read` | DEV3 | Zone 6 |
| `/api/v1/users/me/dashboard-prefs` | GET | JWT | Self (any auth user) | DEV1 | Customization |
| `/api/v1/users/me/dashboard-prefs` | PATCH | JWT | Self (any auth user) | DEV1 | Customization |

---

## Task 1 — Userflow Docs (All Devs, documentation pass first)

**Files:**
- Create: `Userflow/Auth-Access/landing-page.md`
- Create: `Userflow/Dashboard/dashboard-overview.md`
- Create: `Userflow/Dashboard/dashboard-customization.md`

- [ ] **Step 1: Verify `Userflow/Dashboard/` folder exists**

```bash
ls Userflow/
```

Create it if missing:
```bash
mkdir -p Userflow/Dashboard
```

- [ ] **Step 2: Confirm landing-page.md is committed**

File should already exist after the plan doc commit. Verify:
```bash
ls Userflow/Auth-Access/landing-page.md
ls Userflow/Dashboard/dashboard-overview.md
ls Userflow/Dashboard/dashboard-customization.md
```

These three files are part of this plan's deliverables and must be created as Task 1 before implementation begins so devs have full API + flow context.

---

## Task 2 — Tenant Branding API (DEV4)

**Files:**
- Create: `TenantBrandingController.cs` (or extend `TenantController.cs` if it exists)
- DB: `tenant_branding` table (verify exists; create migration if not)

**Endpoint:** `GET /api/v1/tenants/current/branding`  
No auth required. Resolves tenant from subdomain via `TenantResolver` (already in Infrastructure). Returns static branding — no sensitive data.

- [ ] **Step 1: Add/verify `tenant_branding` table**

Columns: `tenant_id (FK)`, `logo_url`, `name`, `primary_color (nullable)`, `tagline (nullable)`, `updated_at`

If not present, add migration:
```csharp
migrationBuilder.CreateTable(
    name: "tenant_branding",
    columns: table => new {
        TenantId = table.Column<Guid>(nullable: false),
        LogoUrl = table.Column<string>(maxLength: 500, nullable: true),
        Name = table.Column<string>(maxLength: 200, nullable: false),
        PrimaryColor = table.Column<string>(maxLength: 7, nullable: true), // hex e.g. "#7c3aed"
        Tagline = table.Column<string>(maxLength: 300, nullable: true),
        UpdatedAt = table.Column<DateTimeOffset>(nullable: false)
    }
);
```

- [ ] **Step 2: Create the endpoint**

```csharp
[HttpGet("tenants/current/branding")]
[AllowAnonymous]
public async Task<IResult> GetBranding(
    [FromServices] ITenantResolver tenantResolver,
    [FromServices] IBrandingRepository brandingRepo,
    HttpContext httpContext,
    CancellationToken ct)
{
    var tenant = await tenantResolver.ResolveAsync(httpContext.Request.Host.Host, ct);
    if (tenant is null) return Results.NotFound();

    var branding = await brandingRepo.GetByTenantIdAsync(tenant.Id, ct);

    return Results.Ok(new {
        logoUrl = branding?.LogoUrl,
        name = branding?.Name ?? tenant.Name,
        primaryColor = branding?.PrimaryColor,
        tagline = branding?.Tagline
    });
}
```

- [ ] **Step 3: Add cache header** — `Cache-Control: public, max-age=300` (5 min). Branding changes infrequently; don't bust CDN on every page load.

- [ ] **Step 4: Update `current-focus/DEV4-configuration.md`** — Add this endpoint as a deliverable under Configuration scope.

---

## Task 3 — Landing Page Frontend (DEV2)

**Depends on:** Task 2 (Tenant Branding API)  
**Files:**
- Create: `src/app/(public)/page.tsx`
- Create: `src/components/landing/WorkforceParticleScene.tsx`
- Create: `src/components/landing/LandingHero.tsx`
- Create: `src/components/landing/FeaturesStrip.tsx`
- Create: `src/components/auth/SignInModal.tsx`

Reference spec section 1: `docs/superpowers/specs/2026-04-10-landing-and-dashboard-overview-design.md`

- [ ] **Step 1: Create the public layout and route**

```tsx
// src/app/(public)/page.tsx
import { Suspense } from 'react'
import { LandingHero } from '@/components/landing/LandingHero'
import { FeaturesStrip } from '@/components/landing/FeaturesStrip'
import { LandingNavbar } from '@/components/landing/LandingNavbar'

export default async function LandingPage() {
  // Fetch branding server-side — no auth needed
  const branding = await fetch('/api/v1/tenants/current/branding', {
    next: { revalidate: 300 }
  }).then(r => r.json())

  return (
    <main style={{ '--primary': branding.primaryColor ?? '#7c3aed' } as React.CSSProperties}>
      <LandingNavbar branding={branding} />
      <LandingHero branding={branding} />
      <FeaturesStrip />
      <footer className="landing-footer">
        Powered by ONEVO · © {new Date().getFullYear()} {branding.name} · Privacy Policy · Terms · Contact IT Support
      </footer>
    </main>
  )
}
```

- [ ] **Step 2: Build `LandingHero` — left column**

Eyebrow label, 3-line H1 (line 3 uses brand gradient), subtitle, CTA row (Access Dashboard button → opens SignInModal, Watch Demo ghost button), 4 live stat counters.

Stat counters fetch from:
- `GET /api/v1/dashboard/kpis` for Active Now, Idle/Away, Avg Score (returns 0s for unauthenticated — add a public variant returning only aggregate counts with no employee data; see Step 2a)
- `GET /api/v1/dashboard/exceptions/active` for Alerts count

**Step 2a:** Add a public aggregate endpoint or reuse branding response to include public stats. Decision: extend `GET /api/v1/tenants/current/branding` to include `publicStats: { activeNow, idleAway, alertCount, avgScore }` — all aggregate counts, no PII. DEV4 implements.

Counter animation: `useCountUp(target, 1000)` hook — animates 0 → target over 1s using `requestAnimationFrame`.

- [ ] **Step 3: Build `WorkforceParticleScene` — Three.js right column**

```tsx
// src/components/landing/WorkforceParticleScene.tsx
'use client'
import { useEffect, useRef } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

export function WorkforceParticleScene() {
  const canvasRef = useRef<HTMLDivElement>(null)
  const prefersReduced = useReducedMotion()
  const particleCount = prefersReduced ? 0 : (window.innerWidth < 768 ? 800 : 2400)

  useEffect(() => {
    let scene: any
    // Dynamic import — Three.js never blocks initial paint
    import('three').then(THREE => {
      // Scene setup, particle geometry, scan line, rotation rings
      // sampleHuman(i, n) maps particle index → body region
      // Regions: head (0-10%), neck (10-13%), torso (13-42%),
      //          left arm (42-57%), right arm (57-72%),
      //          left leg (72-86%), right leg (86-100%)
      // Full implementation per spec section 1.4
    })
    return () => scene?.dispose()
  }, [])

  if (prefersReduced) return <div className="scene-placeholder" /> // SVG fallback

  return (
    <div ref={canvasRef} className="particle-scene">
      {/* HUD overlay: corner brackets, data cards, scan progress bar */}
    </div>
  )
}
```

Cyan accent `#00d4ff` used only inside this component. All other UI stays on Violet Electric tokens.

- [ ] **Step 4: Build `SignInModal`**

360px modal, centered overlay `rgba(0,0,0,0.75)` + `backdrop-filter: blur(10px)`. Fields: Work Email, Password, Remember me, Forgot password?. Buttons: Sign In →, Continue with SSO. No "Create account" field.

"Forgot password?" navigates to `/auth/reset-password`. "Continue with SSO" redirects to tenant's SSO provider URL (from branding response). Modal closes on ×, Escape, backdrop click.

Calls `POST /api/v1/auth/login` on submit → stores access token → redirects to `/dashboard`.

- [ ] **Step 5: Update `current-focus/DEV2-auth-security.md`** — Add landing page and SignInModal as frontend deliverables.

---

## Task 4 — Dashboard Preferences API (DEV1 Backend)

**Files:**
- Create: `UserDashboardPrefsController.cs`
- Migration: `user_dashboard_prefs` table

- [ ] **Step 1: Add migration**

```sql
CREATE TABLE user_dashboard_prefs (
  user_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id      UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  zones_json     JSONB NOT NULL DEFAULT '[]',
  added_widgets  JSONB NOT NULL DEFAULT '[]',
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, tenant_id)
);
```

- [ ] **Step 2: GET endpoint**

```csharp
[HttpGet("users/me/dashboard-prefs")]
[RequirePermission(null)] // any authenticated user
public async Task<IResult> GetPrefs(
    [FromServices] IDashboardPrefsRepository repo,
    ICurrentUser currentUser,
    CancellationToken ct)
{
    var prefs = await repo.GetAsync(currentUser.UserId, currentUser.TenantId, ct);
    return Results.Ok(prefs ?? DashboardPreference.Default(currentUser.UserId, currentUser.TenantId));
}
```

Default prefs = all zones visible in spec priority order (1→6), no added widgets.

- [ ] **Step 3: PATCH endpoint**

```csharp
[HttpPatch("users/me/dashboard-prefs")]
[RequirePermission(null)]
public async Task<IResult> PatchPrefs(
    [FromBody] DashboardPrefsPatch patch,
    [FromServices] IDashboardPrefsRepository repo,
    ICurrentUser currentUser,
    CancellationToken ct)
{
    await repo.UpsertAsync(currentUser.UserId, currentUser.TenantId, patch, ct);
    return Results.NoContent();
}
```

```typescript
// DashboardPrefsPatch (TypeScript consumer shape)
interface DashboardPrefsPatch {
  zones?: ZoneConfig[];        // ordered, replaces existing
  addedWidgets?: string[];     // widget IDs, replaces existing
}
```

---

## Task 5 — Dashboard Shell + Zone 1 (DEV1 shell + DEV2 Zone 1)

**Depends on:** Task 4  
**Files:**
- Create: `src/app/(protected)/dashboard/page.tsx`
- Create: `src/components/dashboard/DashboardShell.tsx`
- Create: `src/components/dashboard/zones/ExceptionAlertStrip.tsx` **(DEV2)**

- [ ] **Step 1: Dashboard route (DEV1)**

```tsx
// src/app/(protected)/dashboard/page.tsx
import { DashboardShell } from '@/components/dashboard/DashboardShell'

export default function DashboardPage() {
  return <DashboardShell />
}
```

- [ ] **Step 2: DashboardShell — zone orchestrator (DEV1)**

```tsx
'use client'
export function DashboardShell() {
  const { permissions, grantedModules, hierarchyScope } = useJwtClaims()
  const { prefs, isLoading: prefsLoading } = useDashboardPrefs()
  const { data: enabledZones } = useSWR('/api/v1/dashboard', fetcher)

  // Merge server-enabled zones with user's saved pref order
  const visibleZones = mergeZoneOrder(enabledZones, prefs?.zones)

  if (prefsLoading) return <DashboardSkeleton />

  return (
    <div className="dashboard-grid">
      {/* Zone 1 always pinned first if enabled */}
      {enabledZones.includes('exception-alert') && <ExceptionAlertStrip />}

      {/* Remaining zones in user-preferred order */}
      {visibleZones.map(zone => <ZoneRenderer key={zone.id} zone={zone} />)}
    </div>
  )
}
```

`GET /api/v1/dashboard` returns `{ enabledZones: string[] }` — server already filtered by JWT. Frontend just renders what it receives — no permission checks duplicated in component logic.

- [ ] **Step 3: ExceptionAlertStrip — Zone 1 (DEV2)**

Condition: `enabled_zones.includes('exception-alert')` (server already checked `workforce:read` + WI module).

```tsx
// src/components/dashboard/zones/ExceptionAlertStrip.tsx
export function ExceptionAlertStrip() {
  const { data } = useSWR('/api/v1/dashboard/exceptions/active', fetcher, {
    refreshInterval: 30_000
  })

  if (!data || data.count === 0) return null

  return (
    <div className="exception-strip">
      {/* border-left: 3px solid var(--status-critical), red-tinted bg */}
      <span>{data.count} active exceptions · {data.preview}</span>
      <button onClick={() => router.push('/workforce/exceptions')}>Review Now</button>
      <button onClick={dismiss}>Dismiss</button>
    </div>
  )
}
```

Backend response shape:
```typescript
// GET /api/v1/dashboard/exceptions/active
{
  count: number,
  preview: string   // e.g. "Ahmed idle 52min · Sara low activity"
}
```

- [ ] **Step 4: Backend — `GET /api/v1/dashboard` (DEV1)**

```csharp
[HttpGet("dashboard")]
[RequirePermission("employees:read", "workforce:read", "leave:read", matchAny: true)]
public async Task<IResult> GetDashboard(
    [FromServices] DashboardService svc,
    ICurrentUser currentUser,
    CancellationToken ct)
{
    var enabledZones = await svc.GetEnabledZonesAsync(currentUser, ct);
    return Results.Ok(new { enabledZones });
}
```

`DashboardService.GetEnabledZonesAsync()` returns only zone IDs the user's JWT claims allow (checks `permissions[]`, `granted_modules[]`, `hierarchy_scope`).

---

## Task 6 — KPI Cards + Pending Actions (DEV1)

**Depends on:** Task 5  
**Files:**
- Create: `src/components/dashboard/zones/KpiCardsZone.tsx`
- Create: `src/components/dashboard/zones/PendingActionsZone.tsx`

- [ ] **Step 1: KPI Cards — Zone 2**

```tsx
// GET /api/v1/dashboard/kpis?scope={hierarchy_scope}
// Returns: { activeNow, onLeave, openExceptions, avgProductivity, scope }
```

Backend response adapts to `hierarchy_scope` — if `subordinates`, labels are relabelled automatically in response (`label: "My Team Active"` vs `"Active Now"`). Frontend renders what it receives.

Cards: 2px top color bar (green/amber/red/cyan), large number (26px 900 weight), delta badge (↑↓ vs yesterday). Glass surface with violet glow if count > 0 for alerts.

4-column grid on desktop, collapses to 2-col on small viewports.

- [ ] **Step 2: Pending Actions — Zone 3**

```tsx
// GET /api/v1/dashboard/pending-actions
// Returns: { rows: [{ type, label, count, href }], selfServiceMode: boolean }
```

If user has no `*:approve` permissions, backend sets `selfServiceMode: true` and returns own items (own leave balance, payslips, own expense status). Frontend renders the same component differently based on this flag — no separate component.

Zone 3 grid behaviour: if Zone 4 is absent, CSS class `mid-row--full` applies `grid-template-columns: 1fr` on the mid-row container.

- [ ] **Step 3: Backend `GET /api/v1/dashboard/kpis`**

```csharp
[HttpGet("dashboard/kpis")]
[RequirePermission("employees:read", "workforce:read", "leave:read", matchAny: true)]
public async Task<IResult> GetKpis(ICurrentUser user, CancellationToken ct)
{
    // IHierarchyScope auto-scopes queries to subordinates
    // Returns scoped counts + relabelled display names
}
```

- [ ] **Step 4: Backend `GET /api/v1/dashboard/pending-actions`**

```csharp
[HttpGet("dashboard/pending-actions")]
[RequirePermission(null)] // any auth user — self-service fallback handled internally
public async Task<IResult> GetPendingActions(ICurrentUser user, CancellationToken ct)
{
    bool hasSelfService = !user.HasAnyApprovePermission();
    var rows = hasSelfService
        ? await _svc.GetSelfItemsAsync(user, ct)
        : await _svc.GetApprovalQueueAsync(user, ct);
    return Results.Ok(new { rows, selfServiceMode: hasSelfService });
}
```

---

## Task 7 — Workforce Live + Workforce Events (DEV3)

**Depends on:** Task 5  
**Files:**
- Create: `src/components/dashboard/zones/WorkforceLiveZone.tsx`
- Create: `src/components/dashboard/zones/WorkforceEventsZone.tsx`

- [ ] **Step 1: Workforce Live — Zone 4**

```tsx
// GET /api/v1/dashboard/workforce-live
// Returns: { presence: { active, idle, alert, offline }, topEmployees: [...], totalTracked: number }
// Polling: refreshInterval: 30_000 (WebSocket upgrade: open question #2 in spec)
```

Content: live presence bar (Active/Idle/Alert/Offline counts) + top 5 employee rows with status dot and score + "Full view →" link to `/workforce`.

- [ ] **Step 2: Workforce Events — Zone 6**

```tsx
// GET /api/v1/dashboard/workforce-events
// Returns: { events: [{ type, title, date, href }] }
// Event types: new_hire, payroll_cutoff, review_cycle, bulk_leave, contract_renewal
```

NOT personal calendar meetings. Only org workforce events (new hires this week, contract renewals ≤7 days, payroll cutoffs, performance cycles closing). "Calendar →" link navigates to `/calendar`.

- [ ] **Step 3: Backend `GET /api/v1/dashboard/workforce-live`**

```csharp
[HttpGet("dashboard/workforce-live")]
[RequirePermission("workforce:read")]
[RequireModule("workforce_intelligence")]
public async Task<IResult> GetWorkforceLive(ICurrentUser user, CancellationToken ct)
{
    // IHierarchyScope scopes to subordinates if scope != "all"
    var data = await _wfService.GetLivePresenceAsync(user, ct);
    return Results.Ok(data);
}
```

- [ ] **Step 4: Backend `GET /api/v1/dashboard/workforce-events`**

```csharp
[HttpGet("dashboard/workforce-events")]
[RequirePermission("employees:read", "leave:read", matchAny: true)]
public async Task<IResult> GetWorkforceEvents(ICurrentUser user, CancellationToken ct)
{
    var events = await _calendarService.GetWorkforceEventsAsync(user.TenantId, days: 14, ct);
    return Results.Ok(new { events });
}
```

- [ ] **Step 5: Grid reflow for absent Zone 4**

In `DashboardShell`, apply CSS class to mid-row div:
```tsx
<div className={cx('mid-row', !zoneEnabled('workforce-live') && 'mid-row--full')}>
  <PendingActionsZone />
  {zoneEnabled('workforce-live') && <WorkforceLiveZone />}
</div>
```

```css
.mid-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.mid-row--full { grid-template-columns: 1fr; }
```

---

## Task 8 — Trends & Charts (DEV1)

**Depends on:** Task 5  
**Files:**
- Create: `src/components/dashboard/zones/TrendsChartsZone.tsx`

- [ ] **Step 1: TrendsChartsZone — Zone 5**

```tsx
// GET /api/v1/dashboard/trends?type=productivity&days=14
// GET /api/v1/dashboard/trends?type=attendance&days=14
// GET /api/v1/dashboard/trends?type=leave&days=14
```

Tab switcher: `Productivity · Attendance · Leave`. Tab visible only if permission allows:
- Productivity tab: `workforce:read` + WI module
- Attendance tab: `workforce:read`
- Leave tab: `leave:read`

Default view if WI module absent: headcount trend or leave distribution (HR-only fallback).

Chart: Recharts `<AreaChart>` with ONEVO theme wrapper. Violet gradient fill (20% opacity). Text summary above chart ("Productivity averaged 87% this week, up 3%").

- [ ] **Step 2: Backend `GET /api/v1/dashboard/trends`**

```csharp
[HttpGet("dashboard/trends")]
[RequirePermission("workforce:read", "leave:read", matchAny: true)]
public async Task<IResult> GetTrends(
    [FromQuery] string type,
    [FromQuery] int days,
    ICurrentUser user,
    CancellationToken ct)
{
    // type: "productivity" | "attendance" | "leave"
    // Returns: { series: [{ date, value }], summary: string, unit: string }
}
```

---

## Task 9 — Dashboard Customization UX (DEV1)

**Depends on:** Tasks 5, 6, 7, 8 (all zones must exist)  
**Files:**
- Create: `src/components/dashboard/customize/CustomizeBar.tsx`
- Create: `src/components/dashboard/customize/WidgetLibraryPanel.tsx`
- Modify: `src/components/dashboard/DashboardShell.tsx` — add edit mode state

- [ ] **Step 1: Edit mode state in DashboardShell**

```tsx
const [editMode, setEditMode] = useState(false)
// "Customize" button in topbar right area → setEditMode(true)
// Edit mode: zones get drag handles + × remove buttons
// Save → PATCH /api/v1/users/me/dashboard-prefs → setEditMode(false)
// Reset → PATCH with DashboardPreference.Default() zones
```

- [ ] **Step 2: CustomizeBar**

Appears below topbar when `editMode === true`. Text: "Drag to reorder zones · Click × to hide · Add widgets from the library". Save and Reset to Default buttons pinned right.

- [ ] **Step 3: Zone edit mode decorators**

In each zone component, when `editMode` is true:
- Show drag handle `⠿` (cursor: grab) in zone header
- Show × remove button in zone header
- Zone 1 (`ExceptionAlertStrip`): show `📌 pinned` badge instead — no drag handle, no × button

- [ ] **Step 4: Drag-and-drop with @dnd-kit/core**

```tsx
import { DndContext, closestCenter } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'

<DndContext onDragEnd={handleDragEnd} collisionDetection={closestCenter}>
  <SortableContext items={visibleZones.map(z => z.id)} strategy={verticalListSortingStrategy}>
    {visibleZones.map(zone => <SortableZone key={zone.id} zone={zone} />)}
  </SortableContext>
</DndContext>
```

Reordering is cross-zone (users can promote Zone 5 above Zone 2 if they choose). Zone 1 is excluded from the sortable list — always rendered first.

- [ ] **Step 5: WidgetLibraryPanel**

240px right slide-in panel (CSS: `width: 0` → `240px`, `transition: width 200ms ease-out`). Shows only widgets user has permission for:

| Widget | Permission |
|:-------|:-----------|
| Top Performers | `workforce:read` + WI module |
| Dept Headcount Breakdown | `employees:read` |
| Leave Calendar Preview | `leave:read` |
| Recent Audit Log | `audit:read` |
| Grievance Summary | `grievance:read` |
| Contract Renewals (30d) | `employees:read` |
| My Team Quick Stats | `employees:read`, scope ≠ `self` |

Adding a widget calls `addedWidgets.push(widgetId)` locally, saved on Save button.

- [ ] **Step 6: Save + Reset**

```typescript
// Save
await fetch('/api/v1/users/me/dashboard-prefs', {
  method: 'PATCH',
  body: JSON.stringify({ zones: currentZoneOrder, addedWidgets: currentWidgets })
})

// Reset
await fetch('/api/v1/users/me/dashboard-prefs', {
  method: 'PATCH',
  body: JSON.stringify(DashboardPreference.default())
})
```

---

## Cross-Dev Dependencies

```
DEV4 Task 2 (Branding API)         ──> DEV2 Task 3 (Landing Page needs branding endpoint)
DEV1 Task 4 (Prefs API)            ──> DEV1 Task 5 (Dashboard Shell consumes prefs)
DEV2 Task 3 (SignInModal)          ──> DEV1 Task 5 (Shell reuses SignInModal for auth entry)
DEV1 Task 5 (Shell + Zone 1)       ──> DEV1 Tasks 6, 8, 9 + DEV3 Task 7
DEV3 Task 7 (Zones 4 + 6)         ──> DEV1 Task 9 (Customization must know all zone IDs)
```

**Safe parallel starts:**
- DEV4 Task 2 + DEV1 Task 4 can run in parallel (no dependency between them)
- DEV2 Task 3 (landing page static layout) can start before Task 2 is done; just mock branding until API is ready

---

## Delivery Checklist

- [ ] Task 1 — Userflow docs created and committed
- [ ] Task 2 — Tenant Branding API live (DEV4)
- [ ] Task 3 — Landing page + SignInModal shipped (DEV2)
- [ ] Task 4 — Dashboard prefs API live (DEV1)
- [ ] Task 5 — Dashboard shell + Zone 1 rendering (DEV1 + DEV2)
- [ ] Task 6 — KPI cards + Pending Actions zones (DEV1)
- [ ] Task 7 — Workforce Live + Workforce Events zones (DEV3)
- [ ] Task 8 — Trends & Charts zone (DEV1)
- [ ] Task 9 — Customization UX complete (DEV1)
- [ ] All 3 open questions from spec §4 answered and spec updated before Task 9 ships
