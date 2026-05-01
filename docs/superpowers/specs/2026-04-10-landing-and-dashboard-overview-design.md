# ONEVO — Landing Page & Dashboard Overview Design

**Date:** 2026-04-10  
**Status:** Approved (brainstorming session completed)  
**Depends on:** `2026-04-08-frontend-redesign-design.md` (brand tokens, surface treatment, sidebar structure)

---

## 1. White-Label Landing Page (`{tenant}.onevo.app`)

### 1.1 Layout — Option C: Branded Hero + Login CTA

Full-page layout, no separate marketing site. The landing page IS the login gateway, wrapped in tenant branding.

```
┌──────────────────────────────────────────────────────────────┐
│  NAVBAR: [Tenant Logo + Name]          [Help] [Sign In →]    │
├───────────────────────────┬──────────────────────────────────┤
│                           │                                  │
│  HERO LEFT                │  HERO RIGHT                      │
│  ─ Eyebrow label          │  3D Scene (full height)          │
│  ─ H1 headline (3 lines)  │  Particle human figure           │
│  ─ Subtitle paragraph     │  + Scan line sweeping up         │
│  ─ CTA buttons (2)        │  + Floating HUD data cards       │
│  ─ Live stat counters     │  + Corner brackets               │
│                           │                                  │
├───────────────────────────┴──────────────────────────────────┤
│  FEATURES STRIP (4 columns)                                  │
├──────────────────────────────────────────────────────────────┤
│  FOOTER: "Powered by ONEVO" · Privacy · Terms                │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Navbar

- Height: 56px, `position: fixed`, glassmorphism surface (brand spec)
- Left: tenant logo mark (32×32, rounded) + tenant company name
- Right: `System Live` status pill (green dot + "System Live") + `Sign In →` button
- `Sign In →` opens the modal (does NOT navigate to a separate page)
- No ONEVO branding in the navbar — tenant-first

### 1.3 Hero — Left Column

**Eyebrow:** small uppercase label + horizontal rule
```
WORKFORCE INTELLIGENCE  ────
```

**H1 Headline (3 lines, clamp 36–58px, weight 900, letter-spacing -2px):**
```
See your
workforce.
Right now.
```
Line 3 uses brand gradient: `linear-gradient(90deg, var(--primary), var(--primary-light))`

**Subtitle:** 14px, `var(--text-secondary)`, left border accent `rgba(primary, 0.3)`, max-width 380px.

**CTA Row:**
- Primary: `Access Dashboard` → opens Sign In modal
- Ghost: `Watch 2-min Demo` → (future: demo video)

**Live Stat Counters (4 items, animate in on load):**
| Stat | Color | Example |
|:-----|:------|:--------|
| Active Now | `--status-active` | 1,089 |
| Idle / Away | `--status-warning` | 143 |
| Alerts | `--status-critical` | 7 |
| Avg Score | `--primary` | 87% |

Counter animates from 0 → target over ~1s with `requestAnimationFrame`. Separated by 1px vertical dividers.

### 1.4 Hero — Right Column (3D Scene)

**Technology:** Three.js  
**Concept:** "Surveillance intelligence — your workforce, understood in real-time"

**3D Elements (layered):**
1. **Particle human silhouette** — 2,400 particles scatter from random positions and assemble into a standing human figure over ~2.8s (cubic ease-in-out). After formation, particles breathe with subtle per-particle oscillation.
2. **Cyan scan line** — horizontal plane sweeps from feet to head every 4s. As it passes particles, they briefly brighten. Communicates "active scanning".
3. **Base grid** — `THREE.GridHelper`, fades in with the figure, low opacity.
4. **Rotation rings** — two `TorusGeometry` rings at floor level, slow counter-rotation.
5. **Mouse parallax** — entire figure group tilts ±0.3rad following cursor position (smooth lerp, factor 0.04).

**HUD Overlay (HTML, absolute positioned over canvas):**
- Corner brackets (top-left, top-right, bottom-left, bottom-right) — `1px solid var(--scan-color)`, 20×20px
- Center crosshair — low opacity
- 4 floating data cards (CSS `position: absolute`, `backdrop-filter: blur`):
  - `card-identity` — "Identity Verified · Ahmed K. · Device: WKSTN-0042"
  - `card-activity` — "87% Productivity · Active App: VS Code · Keys: 1,247"
  - `card-attendance` — "Online 5h 14m · Check-in: 09:00 · Breaks: 2"
  - `card-alert` — "⚡ Exception Alert · Idle > 45 min · Sara M."
- Scan progress bar at bottom — "Scanning workforce..." + animated fill bar

**Color:** Primary accent `#00d4ff` (electric cyan) used exclusively in the 3D scene. All other UI uses the brand's Violet Electric tokens. The 3D scene intentionally reads as "tech/surveillance" while the rest of the page stays on-brand.

### 1.5 Features Strip

4-column grid below the hero fold, dark surface `var(--bg-raised)`, border-top.

| Icon | Title | Description | Badge |
|:-----|:------|:------------|:------|
| 📡 | Real-time Activity | Keyboard, mouse, active apps — every 2 minutes | `Live · Every 2 min` |
| 🛡️ | Identity Verification | Photo-based check-ins. Configurable intervals. | `Biometric · On policy` |
| ⚡ | Exception Engine | Idle too long? Low activity? Instant alerts + escalation. | `Auto · Every 5 min` |
| 👥 | Full HR Lifecycle | Hire to offboard. Leave, payroll, performance, documents. | `Integrated · HR + WI` |

### 1.6 Footer

Single row: `Powered by ONEVO · © {year} {Tenant Name} · Privacy Policy · Terms · Contact IT Support`  
Font size 11px, `var(--text-muted)`. "ONEVO" links to onevo.app (opens new tab).

### 1.7 Sign In Modal

Triggered by: "Sign In →" button, "Access Dashboard" CTA.

```
┌──────────────────────────────┐
│  [Tenant Logo]  Tenant Name  │
│                              │
│  Sign in                     │
│  Access your dashboard       │
│                              │
│  Work Email ─────────────    │
│  Password   ─────────────    │
│                              │
│  [Remember me]  [Forgot pw?] │
│                              │
│  [Sign In →]                 │
│                              │
│  ──── or ────                │
│                              │
│  [🔒 Continue with SSO]      │
└──────────────────────────────┘
```

- Width: 360px, centered in overlay
- Overlay: `rgba(0,0,0,0.75)` + `backdrop-filter: blur(10px)`
- Close: × button, Escape key, backdrop click
- "Forgot password?" → navigates to `/auth/reset-password` (separate page, already specced in userflow docs)
- "Continue with SSO" → redirects to tenant SSO provider (configured in tenant settings)
- No "Create account" — users are invited by admin only

### 1.8 White-Label Customisation Points

Tenant controls (set in Tenant Settings):
| Field | Where used |
|:------|:-----------|
| `tenant.logo_url` | Navbar logo, modal logo |
| `tenant.name` | Navbar text, modal subtitle, footer |
| `tenant.primary_color` | Overrides `--primary` CSS variable for this tenant |
| `tenant.tagline` | Hero subtitle (optional override) |

If `tenant.primary_color` is set, the hero gradient, CTA buttons, and KPI borders inherit that color. The 3D scan accent (`#00d4ff`) stays fixed — it's part of the product identity.

---

## 2. Dashboard Overview Page (`/dashboard`)

### 2.1 Permission Model for Rendering

The dashboard frontend reads three claims from the JWT:

```typescript
interface DashboardClaims {
  permissions: string[];        // e.g. ["employees:read", "leave:approve", ...]
  hierarchy_scope: "self" | "subordinates" | "all";
  granted_modules: string[];    // e.g. ["hr", "workforce_intelligence"]
}
```

**Rule:** If a zone requires a permission or module the user doesn't have, the zone is **not rendered at all** — no blur, no lock icon, no placeholder. The DOM is clean.

The server's `GET /api/v1/dashboard` already applies the same rules and returns only the widgets the user may see. The frontend renders what the API returns, guarded by `hasPermission()` checks. No hardcoded role names in frontend component logic.

**Job family is not used for UI rendering.** It's an HR record concept; dashboard layout is determined solely by the three JWT claims above.

### 2.2 Dashboard Zone Priority Order

Priority drives vertical position. Zones render top-to-bottom in this order. If a zone is absent (no permission), layout reflows — no empty gaps.

```
┌─────────────────────────────────────────────────────────────┐
│  ZONE 1 ── Exception Alert Strip (conditional, pinned top)  │
├──────────────────────────────────────────────────────────────┤
│  ZONE 2 ── KPI Cards (4-column grid)                        │
├──────────────────────┬───────────────────────────────────────┤
│  ZONE 3              │  ZONE 4                              │
│  Pending Actions     │  Workforce Live                      │
│  (left col)          │  (right col)                         │
├──────────────────────┴──────────────┬────────────────────────┤
│  ZONE 5                             │  ZONE 6               │
│  Trends & Charts (2/3 width)        │  Workforce Events     │
│                                     │  (1/3 width)          │
└─────────────────────────────────────┴────────────────────────┘
```

### 2.3 Zone Specifications

#### Zone 1 — Exception Alert Strip
- **Condition:** `granted_modules.includes("workforce_intelligence") && openExceptions > 0`
- **Position:** Pinned above all zones. Cannot be removed by user customization (safety-critical).
- **Visual:** `border-left: 3px solid var(--status-critical)`, red-tinted background
- **Content:** "N active exceptions · [name] idle Xmin · [name] low activity"
- **Actions:** `Review Now` (navigates to `/workforce/exceptions`) · `Dismiss` (hides strip until next refresh)

#### Zone 2 — KPI Cards
- **Condition:** User has any of: `employees:read`, `workforce:view`, `leave:read`
- **Layout:** 4-column responsive grid (collapses to 2-col on narrow viewports)
- **Cards (all conditional on specific permission):**

| Card | Permission Required | Scope |
|:-----|:--------------------|:------|
| Active Now | `workforce:view` + WI module | `hierarchy_scope` |
| On Leave Today | `leave:read` | `hierarchy_scope` |
| Open Exceptions | `workforce:view` + WI module | `hierarchy_scope` |
| Avg Productivity | `workforce:view` + WI module | `hierarchy_scope` |

- **Scope adaptation:** `hierarchy_scope: "subordinates"` relabels "Active Now" → "My Team Active" and scopes the number to the user's subordinate tree.
- **Visual:** 2px top color bar per card (green/amber/red/cyan), large number (26px, weight 900), small delta badge (↑↓ vs yesterday).

#### Zone 3 — Pending Actions
- **Condition:** User has any approval permission (`leave:approve`, `expense:approve`, `employees:write`, `payroll:approve`)
- **Layout:** Panel with action rows, each showing name, meta, count badge
- **Action rows (each conditional):**

| Row | Permission | Who sees it |
|:----|:-----------|:------------|
| Leave Requests | `leave:approve` | HR Manager, Team Lead, Super Admin |
| Expense Claims | `expense:approve` | HR Manager, Super Admin |
| Onboardings Today | `employees:write` | HR Manager, Super Admin |
| Payroll Run Due | `payroll:approve` | HR Manager, Super Admin |

- **Employee self-service view:** If user has no approval permissions, Zone 3 shows their own pending items (leave balance, payslips due) rather than disappearing entirely.

#### Zone 4 — Workforce Live
- **Condition:** `granted_modules.includes("workforce_intelligence") && hasPermission("workforce:view")`
- **When absent:** Zone 3 (Pending Actions) expands to full width — `grid-template-columns: 1fr` on mid-row.
- **Content:** Live presence bar (Active/Idle/Alert/Offline counts) + top employee rows with status and score + "Full view →" link to `/workforce`
- **Data freshness:** Polling every 30s or WebSocket push (per `monitoring-toggles` config)

#### Zone 5 — Trends & Charts
- **Condition:** `hasPermission("workforce:view") || hasPermission("leave:read")`
- **Default view:** Productivity trend (14-day bar chart) — requires WI module
- **Fallback view (HR-only):** Headcount trend or leave distribution chart
- **Tab switcher:** `Productivity · Attendance · Leave` (tabs visible only if permission allows each)
- **Chart library:** Recharts (already in tech stack)

#### Zone 6 — Workforce Events
- **Condition:** `hasPermission("employees:read") || hasPermission("leave:read")`
- **NOT personal calendar meetings.** Shows workforce events only:
  - New hires starting today/this week
  - Payroll cutoff deadlines
  - Performance review cycles closing
  - Bulk leave periods
  - Contract renewals due within 7 days
- **Link:** `Calendar →` navigates to `/calendar`

### 2.4 Scope Behaviour by `hierarchy_scope`

| `hierarchy_scope` | KPI numbers | Workforce Live | Pending Actions |
|:------------------|:------------|:---------------|:----------------|
| `self` | Own data only (leave balance, own score) | Not shown | Own leave/expense requests only |
| `subordinates` | Team totals (relabelled) | Team's live presence | Team's approvals queued |
| `all` | Org-wide | Org-wide | All pending org approvals |

### 2.5 Dashboard Customization

Users can customize their dashboard within permission boundaries. **Permissions gate the ceiling — users control the layout within it.**

#### Rules
1. Zone 1 (Exception Alert Strip) is **always pinned** — non-removable, non-reorderable.
2. All other default zones can be hidden or reordered.
3. Users can add optional widgets from the Widget Library (permission-gated).
4. Preferences are saved server-side (`PATCH /api/v1/users/me/dashboard-prefs`), not localStorage — persists across devices.
5. "Reset to default" available at all times.

#### Edit Mode UX

Triggered by `Customize` button in topbar right area.

In edit mode:
- A "Customize mode" bar appears below the topbar with instructions
- Each zone gets: drag handle (⠿) + × remove button in the zone header
- Widget Library panel slides in from the right (240px)
- Zone borders become dashed with hover highlight
- Save / Reset to Default buttons appear in the page header

#### Widget Library (Available to Add)

All widgets in the library are permission-gated — users only see widgets their permissions support:

| Widget | Icon | Permission Required |
|:-------|:-----|:--------------------|
| Top Performers | 🏆 | `workforce:view` + WI module |
| Dept Headcount Breakdown | 🏢 | `employees:read` |
| Leave Calendar Preview | 📆 | `leave:read` |
| Recent Audit Log | 📝 | `settings:system` |
| Grievance Summary | ⚠️ | `grievance:read` |
| Contract Renewals (30d) | 🔄 | `employees:read` |
| My Team Quick Stats | 👥 | `employees:read`, scope ≠ `self` |

#### Data Model

```typescript
interface DashboardPreference {
  userId: string;
  tenantId: string;
  zones: ZoneConfig[];          // ordered list of visible zones
  addedWidgets: string[];       // widget IDs added beyond defaults
  updatedAt: string;            // ISO timestamp
}

interface ZoneConfig {
  id: string;                   // e.g. "kpi-cards", "pending-actions"
  visible: boolean;
  order: number;
}
```

---

## 3. Implementation Notes

### Landing Page
- Route: `/` (public, no auth required)
- Component: `LandingPage` — tenant branding loaded from `GET /api/v1/tenants/current/branding` (no auth, resolves from subdomain)
- Three.js loaded lazily (dynamic import) to avoid blocking initial paint
- Particle count: 2,400 on desktop, reduce to 800 on `prefers-reduced-motion` or mobile
- Sign In modal: `SignInModal` component, shared with all auth entry points

### Dashboard Overview
- Route: `/dashboard` (protected, requires valid JWT)
- Component: `DashboardOverviewPage`
- Data: `GET /api/v1/dashboard` returns `{ widgets: Widget[] }` — server filters by JWT claims
- Customization data: `GET /api/v1/users/me/dashboard-prefs` on mount; `PATCH` on save
- Zone components are individually lazy-loaded — if `workforce_intelligence` module is absent, its chunk never downloads
- Drag-and-drop: use `@dnd-kit/core` (already planned in tech stack)

### No "Not In Your Plan" UI
Per the authorization principle in `frontend/cross-cutting/authorization.md`:  
> *"Frontend authorization is a UX concern: don't show things the user can't access."*

The dashboard never renders locked/blurred zones, upgrade prompts, or "contact admin" placeholders. Absent permission = absent UI. No exceptions.

---

## 4. Open Questions (for build time)

1. **3D performance budget** — at what device memory threshold do we fall back from 2,400 particles to SVG/CSS animation?
2. **Polling vs WebSocket for Zone 4** — confirm if the WI module delivers server-sent events or requires client polling.
3. **Drag-and-drop scope** — does reordering affect only same-row zones, or can users promote Zone 5 (Charts) above Zone 2 (KPIs)?
4. **Employee self-service Zone 3** — confirm what "own items" look like for users with scope `self` and no approval permissions.
