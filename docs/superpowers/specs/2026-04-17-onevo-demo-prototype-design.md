# ONEVO Demo Prototype — Design Spec

**Date:** 2026-04-17  
**Type:** UI-only static prototype  
**Purpose:** Client/investor demo showing the full final design of ONEVO

---

## 1. Overview

A polished, static React + Vite prototype of ONEVO — a multi-tenant white-label SaaS platform for HR Management and Workforce Intelligence. No backend. All data is mock. Simulates real-time events via a `MockEventEngine`. Covers all 15 Phase 1 modules across ~41 pages.

**Goal:** A client/investor can open this in a browser, pick a persona at login, and experience the full product — navigation, dashboards, live alerts, WMS bridge sync — without any backend running.

---

## 2. Tech Stack

- **Vite + React 18** — project scaffold
- **React Router v6** — client-side routing
- **Zustand** — global state (auth persona, live event feed, notifications)
- **shadcn/ui** — base component primitives
- **Tailwind CSS** — utility styling
- **Recharts** — charts (productivity analytics, work insights)
- **Lucide React** — iconography

---

## 3. Architecture

```
src/
├── mock/
│   ├── data/
│   │   ├── tenants.ts          # 2 tenants with different branding
│   │   ├── employees.ts        # 20 mock employees
│   │   ├── presence.ts         # Clock-in/out states, biometric events
│   │   ├── activity.ts         # App usage timelines, screenshots
│   │   ├── leave.ts            # Leave requests, balances, policies
│   │   ├── org.ts              # Departments, teams, hierarchy
│   │   ├── skills.ts           # Skill taxonomy, employee profiles
│   │   ├── exceptions.ts       # Alert rules, fired exception events
│   │   ├── analytics.ts        # Productivity scores, KPI summaries
│   │   ├── notifications.ts    # Inbox items, approval queue
│   │   ├── wms-bridge.ts       # Mock Bridge 1–3a payloads
│   │   └── calendar.ts         # Company events, leave conflicts
│   └── events/
│       └── MockEventEngine.ts  # setInterval loop firing live events into Zustand
├── store/
│   ├── authStore.ts            # Active persona, grantedModules, permissions
│   └── liveStore.ts            # Real-time event feed, inbox badge count
├── layout/
│   ├── DashboardLayout.tsx     # IconRail + ExpansionPanel + Topbar
│   ├── IconRail.tsx            # 64px glass sidebar, 8 pillar icons
│   ├── ExpansionPanel.tsx      # 220px slide-out sub-nav panel
│   └── Topbar.tsx              # Logo, QuickSearch (⌘K), avatar menu
├── modules/                    # One folder per route section
│   ├── auth/
│   ├── home/
│   ├── people/
│   ├── workforce/
│   ├── org/
│   ├── calendar/
│   ├── inbox/
│   ├── admin/
│   └── settings/
└── components/                 # Shared: GlassCard, GlassSurface, PermissionGate, DataTable
```

---

## 4. Login — Persona Selector

No username/password fields. Three demo persona cards:

| Persona | Name | Role |
|---------|------|------|
| Super Admin | Sarah Lim | Full access — all modules, all permissions |
| Manager | James Rajan | Team-scoped — presence, approvals, exception alerts |
| Employee | Aisha Noor | Self-service — my dashboard, leave, skills |

Clicking a persona loads that user's `grantedModules` and permission set into Zustand. Sidebar, dashboards, and all page content react to the active persona automatically.

To switch: topbar avatar menu → "Switch Demo User" → back to login.

---

## 5. Navigation Structure

```
[ONEVO Logo]  ← tenant-swappable (white-label branding demo)
──────────────────────────────────────────
  Home          → Permission-aware dashboard
  People        → Employees · Leave
  Workforce     → Live Dashboard (Activity · Work Insights · Online Status tabs)
  Organization  → Org Chart · Departments · Teams
  Calendar      → Unified calendar
  Inbox ●       → Notifications · Approval queue (violet glow pulse badge)
  Admin         → Users & Roles · Audit Log · Agents · Devices · Compliance
  Settings      → General · Monitoring · Notifications · Integrations
                  Branding · Billing · Alert Rules
──────────────────────────────────────────
```

- Skills lives inside Employee detail page (not standalone nav)
- WMS Bridge status lives inside Settings → Integrations
- Exception alerts surface in Inbox + Settings → Alert Rules
- All sections permission-gated via `hasPermission()` — no hardcoded role names

---

## 6. Module → Route Mapping (~41 pages)

| Section | Pages | Modules Covered |
|---------|-------|-----------------|
| Auth | 4 | Auth |
| Home | 1 (3 persona views) | All modules (summary KPIs) |
| People / Employees | 6 | Core HR |
| People / Leave | 4 | Leave |
| Workforce Live | 4 (tabbed) | Activity Monitoring, Productivity Analytics, Workforce Presence, Identity Verification |
| Organization | 4 | Org Structure |
| Calendar | 2 | Calendar |
| Inbox | 1 | Notifications, Exception Engine alerts, Shared Platform approvals |
| Admin | 6 | Auth (users/roles), Agent Gateway, Configuration, Shared Platform |
| Settings | 8 | Configuration, Notifications, Infrastructure (branding/billing), WMS Bridge (Integrations) |
| **Total** | **~41** | **15 Phase 1 modules** |

---

## 7. MockEventEngine — Real-Time Simulation

A singleton `setInterval` loop starts when the app mounts. Every few seconds it fires one of:

- **Presence flip** — employee status changes (Online → On Break → Offline) on the Workforce Live board
- **Exception alert** — alert fires, violet glow toast appears, Inbox badge increments
- **WMS Bridge tick** — sync log entry added ("Bridge 1: People Sync — 3 records synced 2s ago") in Settings → Integrations
- **Screenshot captured** — new entry on activity timeline
- **Approval request** — new item appears in Inbox queue

**Investor demo moment:** Landing on Workforce Live auto-triggers the engine visibly — within 10 seconds an exception fires, toast slides in, Inbox badge pulses. No interaction needed.

---

## 8. Styling & Design System

Follows the ONEVO frontend design system exactly:

| Token | Value |
|-------|-------|
| Primary font | Outfit (headings, labels) |
| Data font | Geist (numbers, timestamps) |
| Default theme | Dark mode |
| Primary accent | Violet |
| Surface style | Glass (frosted, `GlassSurface` + `GlassCard`) |
| Active glow | Violet border glow on actionable `GlassCard` items |
| Icon library | Lucide React |
| Chart library | Recharts |

**Mock data visual quality:**
- Real employee avatars (DiceBear)
- Realistic Tamil/Malaysian names (target market)
- 30-day trend data on all charts (no flat lines)
- Screenshots grid with app thumbnails (VS Code, Chrome, Slack, Excel placeholders)
- WMS Bridge sync log with realistic timestamps and record counts

**Tenant branding demo:** Settings → Branding page lets viewer swap logo + primary color live, demonstrating white-label capability.

---

## 9. What This Prototype Is NOT

- No real API calls — all data is static mock
- No authentication — persona selection is instant
- No database — no persistence between sessions
- No desktop agent — Agent Gateway shown as status panels only
- No Phase 2 features — Performance, Skills LMS, Payroll, Documents, Grievance, Expense are out of scope

---

## 10. Success Criteria

- [ ] All ~41 pages reachable via navigation
- [ ] All 3 personas show meaningfully different views (sidebar items, dashboard content, data scope)
- [ ] MockEventEngine fires visible real-time events within 10s of loading Workforce Live
- [ ] Tenant branding swap works live on Settings → Branding page
- [ ] WMS Bridge 1–3a mock payloads visible in Settings → Integrations
- [ ] Runs fully offline with no network requests
- [ ] Looks polished enough to present to a client/investor without explanation
