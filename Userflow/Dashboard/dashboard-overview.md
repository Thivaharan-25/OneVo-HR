# Dashboard Overview

**Area:** Dashboard  
**Trigger:** User successfully signs in and is redirected to `/dashboard` (every authenticated session)  
**Required Permission(s):** Any of `employees:read`, `workforce:read`, `leave:read` (users with none are redirected to a "no access" page)  
**Related Permissions:** All — each dashboard zone has its own permission gate; the set of visible zones changes per user

---

## Preconditions

- User has a valid JWT access token (issued by login or silent refresh)
- User's account is active
- User has at least one read permission (`employees:read`, `workforce:read`, or `leave:read`)

---

## Flow Steps

### Step 1: Dashboard Page Load

- **UI:** Protected route `/dashboard` validates JWT client-side. If token missing or expired: redirected to landing page. If valid: dashboard skeleton (shimmer cards, violet-tinted) shown while data fetches resolve
- **API:** Three parallel calls on mount:
  1. `GET /api/v1/dashboard` — returns `{ enabledZones: string[] }` (server-filtered by JWT claims)
  2. `GET /api/v1/users/me/dashboard-prefs` — returns saved zone order + added widgets
  3. `GET /api/v1/dashboard/exceptions/active` — Zone 1 data (if WI module enabled)
- **Backend:**
  - `DashboardService.GetEnabledZonesAsync()` — checks `permissions[]`, `granted_modules[]`, `hierarchy_scope` from JWT; returns only zone IDs the user may see
  - `UserDashboardPrefsRepository.GetAsync()` — fetches saved prefs; returns defaults if none saved
  - `ExceptionService.GetActiveCountAsync()` — returns exception count scoped by `hierarchy_scope`
- **Validation:** JWT validated on every request via middleware. Zone list is server-authoritative — frontend never renders a zone the server did not return
- **DB:** `user_dashboard_prefs`, `exceptions` (for Zone 1)

### Step 2: Zone Priority Order Determined

- **UI:** No visible change — computation is client-side. Zones are merged: server's `enabledZones` list (what exists) × user's saved pref order (how they've arranged it). Result: ordered list of zones to render. Zone 1 (Exception Alert Strip) always pinned first if present — cannot be reordered
- **API:** N/A (merge is client-side using data from Step 1)
- **Backend:** N/A
- **Validation:** If a zone is in saved prefs but not in `enabledZones` (permission was revoked): zone silently dropped. No error shown
- **DB:** None

### Step 3: Exception Alert Strip Renders (Zone 1 — conditional)

- **UI:** Rendered only if `enabledZones.includes('exception-alert')`. Pinned above all other zones. Red-tinted strip with `border-left: 3px solid var(--status-critical)`. Content: "N active exceptions · [name] idle Xmin · [name] low activity". Two actions: `Review Now` (→ `/workforce/exceptions`) and `Dismiss` (hides strip until next 30s refresh cycle). If exception count is 0, strip is hidden
- **API:** `GET /api/v1/dashboard/exceptions/active` (already called in Step 1; refreshes every 30s)
  ```json
  { "count": 3, "preview": "Ahmed idle 52min · Sara low activity" }
  ```
- **Backend:** `ExceptionService.GetActiveCountAsync()` — scoped to `hierarchy_scope`; requires `workforce:read` + `workforce_intelligence` module
- **Validation:** Condition: `granted_modules.includes("workforce_intelligence") && openExceptions > 0`
- **DB:** `exceptions`

### Step 4: KPI Cards Render (Zone 2 — conditional)

- **UI:** 4-column responsive grid (collapses to 2-col on narrow viewports). Each card: 2px top color bar, large number (26px, weight 900), small delta badge (↑↓ vs yesterday). Cards visible only if user has the specific permission for that card:
  - Active Now: `workforce:read` + WI module → green bar
  - On Leave Today: `leave:read` → info blue bar
  - Open Exceptions: `workforce:read` + WI module → red bar
  - Avg Productivity: `workforce:read` + WI module → cyan bar
  Absent cards leave no empty slot — grid reflows
- **API:** `GET /api/v1/dashboard/kpis?scope={hierarchy_scope}`
  ```json
  {
    "cards": [
      { "id": "active-now", "label": "My Team Active", "value": 23, "delta": 2, "trend": "up", "color": "active" },
      { "id": "on-leave", "label": "On Leave Today", "value": 4, "delta": -1, "trend": "down", "color": "info" }
    ]
  }
  ```
- **Backend:** `DashboardService.GetKpisAsync()` — `hierarchy_scope: "subordinates"` relabels "Active Now" → "My Team Active" and scopes count to subordinate tree. Returns only cards the user has permission for
- **Validation:** Server returns only permitted cards; frontend renders what it receives
- **DB:** `employees`, `leave_requests`, `exceptions`, `productivity_snapshots`

### Step 5: Pending Actions Render (Zone 3 — conditional)

- **UI:** Panel with action rows, each showing icon, label, count badge, and `View →` link. Shown if user has any approval permission. If user has no approval permissions: self-service mode — shows own leave balance, own payslip status, own expense claims status. Zone never disappears entirely for any authenticated user
- **API:** `GET /api/v1/dashboard/pending-actions`
  ```json
  {
    "selfServiceMode": false,
    "rows": [
      { "type": "leave_request", "label": "Leave Requests", "count": 5, "href": "/inbox?type=leave" },
      { "type": "expense_claim", "label": "Expense Claims", "count": 2, "href": "/inbox?type=expense" }
    ]
  }
  ```
- **Backend:** `DashboardService.GetPendingActionsAsync()` — checks for any `*:approve` permission. If none: returns self-service items. Rows are filtered by individual permission (`leave:approve`, `expense:approve`, `employees:write`, `payroll:approve`)
- **Validation:** Self-service mode activated server-side — never requires a separate frontend permission check
- **DB:** `leave_requests`, `expense_claims`, `employees` (for onboarding), `payroll_runs`

### Step 6: Workforce Live Renders (Zone 4 — conditional)

- **UI:** Rendered only if `enabledZones.includes('workforce-live')`. Live presence bar showing Active / Idle / Alert / Offline counts as colored segments. Top 5 employee rows with status dot and productivity score. "Full view →" link to `/workforce`. Data updates every 30s (polling). If Zone 4 is absent: Zone 3 (Pending Actions) expands to full width via CSS class change (`grid-template-columns: 1fr`)
- **API:** `GET /api/v1/dashboard/workforce-live` — polling `refreshInterval: 30_000`
  ```json
  {
    "presence": { "active": 89, "idle": 12, "alert": 3, "offline": 5 },
    "topEmployees": [
      { "id": "uuid", "name": "Ahmed K.", "status": "active", "score": 94 }
    ],
    "totalTracked": 109
  }
  ```
- **Backend:** `WorkforceService.GetLivePresenceAsync()` — requires `workforce:read` + `workforce_intelligence` module. `IHierarchyScope` scopes to subordinates if `hierarchy_scope != "all"`
- **Validation:** Zone only rendered if server returned it in `enabledZones`
- **DB:** `activity_snapshots`, `presence_records`

### Step 7: Trends & Charts Render (Zone 5 — conditional)

- **UI:** Tab switcher — `Productivity · Attendance · Leave`. Each tab visible only if permission allows. Default active tab: Productivity (if WI module present) or headcount/leave distribution (HR-only fallback). Chart: Recharts area chart, violet gradient fill. Text summary above chart ("Productivity averaged 87% this week, up 3%"). Shared date range selector
- **API:** `GET /api/v1/dashboard/trends?type=productivity&days=14`
  ```json
  {
    "series": [{ "date": "2026-04-01", "value": 84 }, ...],
    "summary": "Productivity averaged 87% this week, up 3% vs last week",
    "unit": "%"
  }
  ```
- **Backend:** `AnalyticsService.GetTrendAsync(type, days, user)` — returns only the type the user has permission for. `workforce:read` for productivity/attendance; `leave:read` for leave
- **Validation:** Backend returns 403 if `type` requested is outside user's permissions
- **DB:** `productivity_snapshots`, `attendance_records`, `leave_requests`

### Step 8: Workforce Events Render (Zone 6 — conditional)

- **UI:** List of upcoming workforce events — NOT personal calendar meetings. Event types: new hires starting this week, payroll cutoff deadlines, performance review cycles closing, bulk leave periods, contract renewals due within 7 days. Each event: icon, title, date chip, optional link. "Calendar →" link navigates to `/calendar`
- **API:** `GET /api/v1/dashboard/workforce-events`
  ```json
  {
    "events": [
      { "type": "new_hire", "title": "3 new hires starting Monday", "date": "2026-04-13", "href": "/people/employees?filter=starting-this-week" },
      { "type": "contract_renewal", "title": "2 contracts renewing within 7 days", "date": "2026-04-17", "href": "/people/employees?filter=contract-renewal" }
    ]
  }
  ```
- **Backend:** `CalendarService.GetWorkforceEventsAsync(tenantId, days: 14)` — pulls from employee data, payroll schedule, performance cycles, leave records
- **Validation:** Requires `employees:read` OR `leave:read`
- **DB:** `employees`, `payroll_runs`, `performance_cycles`, `leave_requests`

### Step 9: Optional Widgets Render (if added via customization)

- **UI:** Any widgets the user added from the Widget Library render after the default zones in their saved position. Each is permission-gated — if permission was revoked since widget was added, widget is silently omitted (no error)
- **API:** Each widget has its own endpoint (e.g., `GET /api/v1/dashboard/widgets/top-performers`)
- **Backend:** Widget endpoints follow same pattern — `[RequirePermission("...")]`, `IHierarchyScope` applied
- **Validation:** Widget IDs in `addedWidgets` that are no longer permitted are dropped silently
- **DB:** Varies per widget

---

## Scope Behaviour by `hierarchy_scope`

| `hierarchy_scope` | KPI numbers | Workforce Live | Pending Actions |
|:-----------------|:------------|:---------------|:----------------|
| `self` | Own data only (leave balance, own score) | Not shown | Own leave/expense requests only (self-service mode) |
| `subordinates` | Team totals (relabelled "My Team...") | Team's live presence | Team's approvals queued |
| `all` | Org-wide | Org-wide | All pending org approvals |

---

## Variations

### HR Manager (no WI module)
- Zone 1 (Exception Alert Strip): absent
- KPI cards: On Leave Today only (no Active Now, no Exceptions, no Avg Productivity)
- Zone 4 (Workforce Live): absent — Zone 3 expands to full width
- Zone 5 (Charts): leave distribution chart (HR fallback)
- Zone 6 (Workforce Events): present

### Team Lead (WI module + `hierarchy_scope: subordinates`)
- Zone 1: present (team exceptions only)
- KPI cards: relabelled — "My Team Active", "My Team On Leave"
- Zone 4: team's live presence only
- Zone 5: team productivity trend

### Employee (`hierarchy_scope: self`, no approval permissions)
- Zone 1: absent
- KPI cards: absent (no `workforce:read` or `leave:read` at org level)
- Zone 3: self-service mode — own leave balance, payslip status
- Zones 4, 5, 6: absent

### Super Admin (`hierarchy_scope: all`, all modules)
- All 6 zones rendered
- All KPI cards at org-wide scope
- All chart tabs available

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| JWT expired mid-session | Refresh token used silently | No disruption if refresh succeeds; redirect to login if refresh fails |
| `GET /api/v1/dashboard` returns empty `enabledZones` | Dashboard renders only Zone 3 (self-service Pending) | Normal dashboard, just very minimal |
| Zone data endpoint fails (non-Zone 1) | Zone renders error state with retry button | "Could not load [zone name]. Retry →" |
| Zone 1 endpoint fails | Strip hidden silently (safety: don't show errors in pinned safety zone) | Strip absent |
| Dashboard prefs corrupted | Fall back to `DashboardPreference.Default()` silently | Default zone order restored |

---

## Events Triggered

- No write events on dashboard load (read-only page)
- `DashboardViewedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by audit log

---

## Related Flows

- [[Userflow/Auth-Access/landing-page|Landing Page]] — the page before this (sign-in entry point)
- [[Userflow/Auth-Access/login-flow|Login Flow]] — full JWT issuance that enables this page
- [[Userflow/Dashboard/dashboard-customization|Dashboard Customization]] — user reorders and adds widgets
- [[Userflow/Exception-Engine/alert-review|Alert Review]] — Zone 1 "Review Now" navigates here
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]] — Zone 4 "Full view →" navigates here
- [[Userflow/Calendar/calendar-event-creation|Calendar]] — Zone 6 "Calendar →" navigates here
- [[Userflow/Notifications/inbox|Inbox]] — Zone 3 action rows link to Inbox filtered views

---

## Module References

- [[frontend/cross-cutting/authorization|Authorization]] — `hasPermission()`, `useJwtClaims()`, `IHierarchyScope`
- [[modules/shared-platform/overview|Shared Platform]] — `DashboardService`, `UserDashboardPrefsRepository`, `GetEnabledZonesAsync()`, `GetKpisAsync()` (dashboard prefs live here; no separate Dashboard module exists)
- [[modules/exception-engine/overview|Exception Engine]] — Zone 1 exception count data
- [[modules/workforce-presence/overview|Workforce Presence]] — Zone 4 live presence data (`presence_records`)
- [[modules/activity-monitoring/overview|Activity Monitoring]] — Zone 4 live activity data (`activity_snapshots`)
- [[modules/productivity-analytics/overview|Productivity Analytics]] — Zone 5 trend data (`AnalyticsService.GetTrendAsync()`)
- [[modules/calendar/overview|Calendar]] — Zone 6 workforce events
- [[modules/notifications/overview|Notifications]] — SignalR push for Zone 1 real-time updates
