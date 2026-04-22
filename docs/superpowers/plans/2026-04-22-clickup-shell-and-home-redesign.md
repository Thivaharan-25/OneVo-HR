# ClickUp Shell + Permission-Ranked Home Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the ONEVO demo shell to match the ClickUp design pattern (full-width topbar, dark icon rail with labels, white secondary sidebar with "+ Create") and replace the hardcoded 3-persona home page with a permission-ranked widget system that surfaces each user's most actionable content first.

**Architecture:** Light theme as new default. Shell is restructured so the topbar spans full width above both the icon rail and expansion panel. The home page replaces `AdminDashboard`/`ManagerDashboard`/`EmployeeDashboard` with a widget registry that filters by `grantedModules`/`permissions` and ranks by urgency tier (Tier 1 = action required → Tier 2 = today's status → Tier 3 = browse). Each widget is a self-contained component reading from existing mock data stores.

**Tech Stack:** React 18, TypeScript, Tailwind CSS 3, Zustand, Lucide React, Vite (demo at `demo/`)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `demo/src/components/ui/ThemeProvider.tsx` | Modify | Default theme: `'system'` → `'light'` |
| `demo/src/index.css` | Modify | Light theme tokens (ClickUp values) + card/glass light-mode overrides |
| `demo/src/components/layout/Topbar.tsx` | Modify | Full-width, workspace name left, search centered, remove breadcrumbs |
| `demo/src/components/layout/IconRail.tsx` | Modify | Remove logo slot, add text labels, position below topbar (`top-12`), width `w-14` |
| `demo/src/components/layout/ExpansionPanel.tsx` | Modify | Add "+ Create" header, update item styling, fix `left-14` offset |
| `demo/src/components/layout/DashboardLayout.tsx` | Modify | Update margins for `w-14` rail and full-width topbar |
| `demo/src/components/ui/GlassCard.tsx` | Modify | Light-mode card style for `elevated` variant |
| `demo/src/components/ui/MetricCard.tsx` | Modify | Light-mode gradient text overrides |
| `demo/src/modules/home/homeWidgets.ts` | **Create** | Widget registry — definitions, ranking, permission filter |
| `demo/src/modules/home/widgets/PendingLeaveWidget.tsx` | **Create** | Tier-1: pending leave approvals (requires `leave:approve`) |
| `demo/src/modules/home/widgets/ActiveExceptionsWidget.tsx` | **Create** | Tier-1: active workforce exceptions (requires `exceptions:read`) |
| `demo/src/modules/home/widgets/MyLeaveWidget.tsx` | **Create** | Tier-1: own leave balances (requires `leave:read`) |
| `demo/src/modules/home/widgets/WorkforceStatusWidget.tsx` | **Create** | Tier-2: team presence status (requires `workforce:read`) |
| `demo/src/modules/home/widgets/HeadcountWidget.tsx` | **Create** | Tier-2: employee headcount metrics (requires `employees:read`) |
| `demo/src/modules/home/widgets/UpcomingEventsWidget.tsx` | **Create** | Tier-2: next calendar events (requires `calendar` module) |
| `demo/src/modules/home/HomePage.tsx` | Modify | Replace 3 hardcoded dashboards with aurora hero + widget grid |
| `demo/src/modules/home/AdminDashboard.tsx` | **Delete** | Replaced by widget system |
| `demo/src/modules/home/ManagerDashboard.tsx` | **Delete** | Replaced by widget system |
| `demo/src/modules/home/EmployeeDashboard.tsx` | **Delete** | Replaced by widget system |
| `Userflow/Home/home-overview.md` | **Create** | Documents permission-ranked home page flow |
| `Userflow/README.md` | Modify | Add Home section to flow index |

---

## Task 1: Default to Light Theme

**Files:**
- Modify: `demo/src/components/ui/ThemeProvider.tsx`

- [ ] **Step 1: Change the default fallback from `'system'` to `'light'`**

In `ThemeProvider.tsx`, find:
```typescript
const [theme, setThemeState] = useState<Theme>(() => {
  return (localStorage.getItem('theme') as Theme) ?? 'system'
})
```
Replace with:
```typescript
const [theme, setThemeState] = useState<Theme>(() => {
  return (localStorage.getItem('theme') as Theme) ?? 'light'
})
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Start dev server and confirm light theme is default**

```bash
cd demo && npm run dev
```
Open http://localhost:5173. Clear localStorage (`localStorage.clear()` in DevTools console then refresh). The app should render with a white/light background, not dark.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/ui/ThemeProvider.tsx
git commit -m "feat(demo): default theme to light"
```

---

## Task 2: Light Theme CSS Tokens + Card/Glass Overrides

**Files:**
- Modify: `demo/src/index.css`

- [ ] **Step 1: Replace the `[data-theme="light"]` token block**

Find the existing `[data-theme="light"]` block and replace it entirely:

```css
/* ── LIGHT THEME ─────────────────────────────────────────── */
[data-theme="light"] {
  --bg-base:       #f9fafb;
  --bg-surface:    #ffffff;
  --bg-elevated:   #f3f4f6;
  --bg-overlay:    #eef2f7;
  --bg-hover:      #f3f4f6;
  --border:        #e5e7eb;
  --border-soft:   #f0f2f5;
  --fg-1:          #111827;
  --fg-2:          #374151;
  --fg-3:          #6b7280;
  --fg-4:          #9ca3af;
  --accent-subtle: #f5f3ff;
  --accent-border: #c7d2fe;
  --success:       #16a34a;
  --warning:       #d97706;
  --danger:        #dc2626;
  --info:          #2563eb;
}
```

- [ ] **Step 2: Add light-mode overrides for card-depth shadow, glass utilities, and gradient text**

After the `@layer utilities` closing brace, append:

```css
/* ── LIGHT MODE OVERRIDES ──────────────────────────────── */
[data-theme="light"] .card-depth {
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
}
[data-theme="light"] .glass-1 { background: rgba(0, 0, 0, 0.015); }
[data-theme="light"] .glass-2 { background: rgba(0, 0, 0, 0.025); }
[data-theme="light"] .glass-3 { background: rgba(0, 0, 0, 0.04); }
[data-theme="light"] .border-glass    { border-color: rgba(0, 0, 0, 0.05); }
[data-theme="light"] .border-glass-md { border-color: rgba(0, 0, 0, 0.07); }
[data-theme="light"] .border-glass-hi { border-color: rgba(0, 0, 0, 0.10); }

[data-theme="light"] .text-gradient-violet {
  background: linear-gradient(135deg, #6d28d9, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .text-gradient-green {
  background: linear-gradient(135deg, #059669, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .text-gradient-amber {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .text-gradient-red {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .text-gradient-blue {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .text-gradient-white {
  background: none;
  -webkit-text-fill-color: var(--fg-1);
  color: var(--fg-1);
}
```

- [ ] **Step 3: Verify and check in browser**

```bash
cd demo && npx tsc --noEmit
```
In the running dev server with light theme active, check that:
- The background is `#f9fafb` (very light gray, not pure white)
- Cards appear with white `#ffffff` surfaces and `#e5e7eb` borders
- No dark glass artifacts on any page

- [ ] **Step 4: Commit**

```bash
git add demo/src/index.css
git commit -m "feat(demo): ClickUp light theme tokens and glass overrides"
```

---

## Task 3: Full-Width Topbar with Workspace Name

**Files:**
- Modify: `demo/src/components/layout/Topbar.tsx`

- [ ] **Step 1: Replace the Topbar component entirely**

Full replacement of `demo/src/components/layout/Topbar.tsx`:

```typescript
import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'
import { LogOut, Search, Bell, Sun, Moon, Monitor, ChevronDown } from 'lucide-react'
import { useLiveStore } from '../../store/liveStore'
import { CommandPalette } from '../ui/CommandPalette'
import { useTheme, type Theme } from '../ui/ThemeProvider'

const themeOrder: Theme[] = ['system', 'light', 'dark']

function ThemeIcon({ theme }: { theme: Theme }) {
  if (theme === 'dark') return <Moon size={14} />
  if (theme === 'light') return <Sun size={14} />
  return <Monitor size={14} />
}

export function Topbar() {
  const { user, tenantName, tenantColor } = useAuthStore()
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()
  const inboxCount = useLiveStore((s) => s.inboxCount)
  const [paletteOpen, setPaletteOpen] = useState(false)
  const { theme, setTheme } = useTheme()

  const handleLogout = () => { logout(); navigate('/login') }

  function cycleTheme() {
    const next = themeOrder[(themeOrder.indexOf(theme) + 1) % themeOrder.length]
    setTheme(next)
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setPaletteOpen(o => !o)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const initials = tenantName
    .split(' ')
    .map(w => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <>
    <div className="fixed top-0 left-0 right-0 h-12 z-50 flex items-center px-4 gap-3 bg-[var(--bg-surface)] border-b border-[var(--border)]">

      {/* Left: workspace */}
      <div className="flex items-center gap-2 shrink-0">
        <div
          className="w-6 h-6 rounded-md flex items-center justify-center text-white font-bold text-[11px] font-outfit shrink-0"
          style={{ background: tenantColor }}
        >
          {initials}
        </div>
        <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit whitespace-nowrap flex items-center gap-1">
          {tenantName}
          <ChevronDown size={12} className="text-[var(--fg-3)]" />
        </span>
      </div>

      <div className="w-px h-5 bg-[var(--border)] mx-1 shrink-0" />

      {/* Center: search */}
      <div className="flex-1 flex justify-center">
        <button
          onClick={() => setPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border)] text-[var(--fg-3)] hover:text-[var(--fg-1)] hover:border-[var(--fg-4)] transition-all duration-150 text-xs font-outfit w-[280px]"
        >
          <Search size={13} />
          <span>Search</span>
          <kbd className="ml-auto px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--fg-3)] text-[10px] font-geist border border-[var(--border)]">Ctrl K</kbd>
        </button>
      </div>

      {/* Right: actions + avatar */}
      <div className="flex items-center gap-1 shrink-0">

        {/* Inbox */}
        <button
          onClick={() => navigate('/inbox')}
          className="relative w-8 h-8 flex items-center justify-center rounded-lg text-[var(--fg-3)] hover:text-[var(--fg-2)] hover:bg-[var(--bg-hover)] transition-colors"
        >
          <Bell size={15} />
          {inboxCount > 0 && (
            <span className="absolute top-1 right-1 w-[7px] h-[7px] bg-[var(--danger)] rounded-full border border-[var(--bg-surface)]" />
          )}
        </button>

        {/* Theme toggle */}
        <button
          onClick={cycleTheme}
          title={`Theme: ${theme}`}
          className="w-8 h-8 flex items-center justify-center rounded-lg text-[var(--fg-3)] hover:text-[var(--fg-1)] hover:bg-[var(--bg-hover)] transition-colors"
        >
          <ThemeIcon theme={theme} />
        </button>

        <div className="w-px h-5 bg-[var(--border)] mx-1" />

        {/* Avatar */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <img
              src={user?.avatar}
              alt={user?.name}
              className="w-7 h-7 rounded-full border border-[var(--border)]"
            />
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[var(--success)] border-2 border-[var(--bg-surface)]" />
          </div>
          <div className="hidden md:block leading-none">
            <div className="text-[var(--fg-1)] text-[12px] font-semibold font-outfit">{user?.name}</div>
            <div className="text-[var(--fg-3)] text-[10px] font-outfit mt-0.5">{user?.jobTitle}</div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="text-[var(--fg-4)] hover:text-[var(--fg-2)] transition-colors ml-1"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </div>

    <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  )
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Visual check**

In the dev server: topbar should be full-width (not inset after the rail). Left side shows tenant name with colored initial. Center has the search bar. Right has bell, theme toggle, avatar.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/layout/Topbar.tsx
git commit -m "feat(demo): full-width topbar with workspace name"
```

---

## Task 4: Icon Rail — Labels + Position Below Topbar

**Files:**
- Modify: `demo/src/components/layout/IconRail.tsx`

- [ ] **Step 1: Replace IconRail entirely**

```typescript
import { Home, Users, Radio, Building2, CalendarDays, Bell, Settings, ShieldCheck, type LucideIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useLiveStore } from '../../store/liveStore'
import { useAuthStore } from '../../store/authStore'
import { useNavStore, PANEL_PILLARS, type PillarKey } from '../../store/navStore'
import { cn } from '../../lib/utils'

const pillars: Array<{
  icon: LucideIcon
  label: string
  defaultPath: string
  pillarKey: PillarKey
  module: string | null
}> = [
  { icon: Home,         label: 'Home',      defaultPath: '/',                 pillarKey: 'home',      module: null },
  { icon: Users,        label: 'People',    defaultPath: '/people/employees', pillarKey: 'people',    module: 'core-hr' },
  { icon: Radio,        label: 'Workforce', defaultPath: '/workforce',        pillarKey: 'workforce', module: 'workforce' },
  { icon: Building2,    label: 'Org',       defaultPath: '/org',              pillarKey: 'org',       module: 'org-structure' },
  { icon: CalendarDays, label: 'Calendar',  defaultPath: '/calendar',         pillarKey: 'calendar',  module: 'calendar' },
  { icon: Bell,         label: 'Inbox',     defaultPath: '/inbox',            pillarKey: 'inbox',     module: 'notifications' },
]

const utilityPillars: Array<{
  icon: LucideIcon
  label: string
  defaultPath: string
  pillarKey: PillarKey
  module: string | null
}> = [
  { icon: ShieldCheck, label: 'Admin',    defaultPath: '/admin',    pillarKey: 'admin',    module: 'admin' },
  { icon: Settings,    label: 'Settings', defaultPath: '/settings', pillarKey: 'settings', module: 'settings' },
]

function RailItem({
  icon: Icon,
  label,
  pillarKey,
  defaultPath,
  module,
  active,
  badge,
  onClick,
}: {
  icon: LucideIcon
  label: string
  pillarKey: PillarKey
  defaultPath: string
  module: string | null
  active: boolean
  badge?: number
  onClick: () => void
}) {
  const grantedModules = useAuthStore((s) => s.grantedModules)
  if (module && !grantedModules.includes(module)) return null

  return (
    <button
      onClick={onClick}
      title={label}
      className={cn(
        'relative w-[44px] py-1.5 flex flex-col items-center gap-0.5 rounded-lg transition-colors duration-150',
        active
          ? 'bg-[rgba(129,140,248,0.18)] text-[#818cf8]'
          : 'text-[#6b7280] hover:bg-[rgba(255,255,255,0.07)] hover:text-[#9ca3af]'
      )}
    >
      <Icon size={18} strokeWidth={1.8} />
      <span className={cn('text-[9px] font-medium leading-none', active ? 'text-[#818cf8]' : 'text-[#6b7280]')}>
        {label}
      </span>
      {badge != null && badge > 0 && (
        <span className="absolute top-1 right-1 w-[6px] h-[6px] rounded-full bg-red-500" />
      )}
    </button>
  )
}

export function IconRail() {
  const navigate = useNavigate()
  const inboxCount = useLiveStore((s) => s.inboxCount)
  const { activePillar, togglePillar, setActivePillar } = useNavStore()

  const handleClick = (pillarKey: PillarKey, defaultPath: string) => {
    if (PANEL_PILLARS.includes(pillarKey)) {
      togglePillar(pillarKey)
      navigate(defaultPath)
    } else {
      setActivePillar(pillarKey)
      navigate(defaultPath)
    }
  }

  return (
    <div className="fixed left-0 top-12 bottom-0 z-40 w-14 flex flex-col items-center py-2 gap-1 bg-[#1e1e2e] border-r border-[rgba(255,255,255,0.06)]">
      {pillars.map(p => (
        <RailItem
          key={p.pillarKey}
          {...p}
          active={activePillar === p.pillarKey}
          badge={p.pillarKey === 'inbox' ? inboxCount : undefined}
          onClick={() => handleClick(p.pillarKey, p.defaultPath)}
        />
      ))}

      <div className="flex-1" />

      {utilityPillars.map(p => (
        <RailItem
          key={p.pillarKey}
          {...p}
          active={activePillar === p.pillarKey}
          onClick={() => handleClick(p.pillarKey, p.defaultPath)}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Visual check**

The icon rail should: start below the topbar (not overlapping it), be 56px wide (`w-14`), show icon + text label for each pillar, show Home/People/Workforce/Org/Calendar/Inbox in the top group, Admin/Settings pinned to the bottom. Active item has indigo background tint.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/layout/IconRail.tsx
git commit -m "feat(demo): icon rail with labels, positioned below topbar"
```

---

## Task 5: Expansion Panel — "+ Create" Header + Updated Offsets

**Files:**
- Modify: `demo/src/components/layout/ExpansionPanel.tsx`

- [ ] **Step 1: Update the `<aside>` positioning and add "+ Create" header**

Find the `return (` block in `ExpansionPanel.tsx`. Replace the entire return with:

```typescript
  return (
    <aside
      className={cn(
        'fixed top-12 left-14 bottom-0 w-[220px] z-30',
        'flex flex-col',
        'bg-[var(--bg-surface)]',
        'border-r border-[var(--border)]',
        'transition-transform duration-200 ease-in-out',
        panelOpen && config ? 'translate-x-0' : '-translate-x-full'
      )}
    >
      {config && (
        <>
          {/* Header with Create button */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-soft)] shrink-0">
            <span className="text-[14px] font-bold text-[var(--fg-1)] font-outfit">{config.label}</span>
            <button className="flex items-center gap-1 bg-[var(--fg-1)] text-[var(--bg-surface)] rounded-md px-2.5 py-1 text-[11px] font-semibold font-outfit hover:opacity-90 transition-opacity">
              <span className="text-base leading-none">+</span> Create
            </button>
          </div>

          <div className="flex-1 overflow-y-auto py-2 px-2">
            <nav className="space-y-0.5">
              {config.items.map(item => {
                const active = isItemActive(item.path, location.pathname, location.search)
                return (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={cn(
                      'w-full flex items-center gap-2.5 h-9 px-3 rounded-lg text-[13px] font-outfit text-left',
                      'transition-colors duration-150',
                      active
                        ? 'bg-[var(--bg-elevated)] text-[var(--fg-1)] font-medium'
                        : 'text-[var(--fg-2)] hover:text-[var(--fg-1)] hover:bg-[var(--bg-hover)]'
                    )}
                  >
                    <item.icon
                      size={16}
                      strokeWidth={1.8}
                      className={cn(
                        'shrink-0 transition-colors duration-150',
                        active ? 'text-[var(--info)]' : 'text-[var(--fg-4)]'
                      )}
                    />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </nav>
          </div>
        </>
      )}
    </aside>
  )
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Visual check**

When clicking People, Workforce, Org, Calendar, Admin, or Settings in the icon rail: the expansion panel should slide in from the left. It must start below the topbar (not overlapping it). The header shows the section name + black "+ Create" pill. Nav items have icons with hover highlight.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/layout/ExpansionPanel.tsx
git commit -m "feat(demo): expansion panel Create header and ClickUp item style"
```

---

## Task 6: Dashboard Layout — Update Margin Offsets

**Files:**
- Modify: `demo/src/components/layout/DashboardLayout.tsx`

- [ ] **Step 1: Update the `sidebarWidth` calculation**

Find:
```typescript
  const sidebarWidth = panelOpen && hasPanelContent ? 'ml-[284px]' : 'ml-16'
```
Replace with:
```typescript
  // Rail is w-14 (56px), expansion panel is 220px — total open: 276px
  const sidebarWidth = panelOpen && hasPanelContent ? 'ml-[276px]' : 'ml-14'
```

- [ ] **Step 2: Verify the main `<div>` still has `pt-12` for topbar offset**

The `<main>` tag should already have `pt-12`. Confirm it reads:
```typescript
      <main
        className={cn(
          'pt-12 min-h-screen relative z-10',
          'transition-[margin-left] duration-200 ease-in-out',
          sidebarWidth
        )}
      >
```

- [ ] **Step 3: Verify TypeScript and visual check**

```bash
cd demo && npx tsc --noEmit
```

In browser: the main content area should not be hidden behind the icon rail or topbar. Navigate to People — panel slides in. Content shifts right cleanly. No overlap with topbar.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/layout/DashboardLayout.tsx
git commit -m "feat(demo): update layout margins for 56px rail and full-width topbar"
```

---

## Task 7: GlassCard Light-Mode Elevated Variant

**Files:**
- Modify: `demo/src/components/ui/GlassCard.tsx`

- [ ] **Step 1: Fix the `elevated` variant to be theme-aware**

Find in `GlassCard.tsx`:
```typescript
        variant === 'elevated' && 'bg-white/[0.045] border border-glass-md rounded-[14px] shadow-glass-lg',
```
Replace with:
```typescript
        variant === 'elevated' && 'bg-[var(--bg-elevated)] border border-[var(--border)] rounded-[14px] shadow-glass-lg',
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```

- [ ] **Step 3: Visual check**

Check the AdminDashboard or any page that uses `<GlassCard variant="elevated">` — it should render as a light card with `#f3f4f6` background and visible border in light mode.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/ui/GlassCard.tsx
git commit -m "fix(demo): GlassCard elevated variant adapts to light theme"
```

---

## Task 8: Home Widget Registry

**Files:**
- Create: `demo/src/modules/home/homeWidgets.ts`

- [ ] **Step 1: Create the widget registry**

```typescript
import type { ComponentType } from 'react'

export type WidgetTier = 1 | 2

export interface HomeWidgetDef {
  id: string
  tier: WidgetTier
  colSpan: 1 | 2
  requiredPermission?: string
  requiredModule?: string
  // component is registered separately to avoid circular imports
}

export const WIDGET_REGISTRY: HomeWidgetDef[] = [
  // Tier 1 — action required
  {
    id: 'pending-leave',
    tier: 1,
    colSpan: 1,
    requiredPermission: 'leave:approve',
  },
  {
    id: 'active-exceptions',
    tier: 1,
    colSpan: 1,
    requiredPermission: 'exceptions:read',
  },
  {
    id: 'my-leave',
    tier: 1,
    colSpan: 1,
    requiredModule: 'leave',
  },
  // Tier 2 — today's status
  {
    id: 'workforce-status',
    tier: 2,
    colSpan: 2,
    requiredPermission: 'workforce:read',
  },
  {
    id: 'headcount',
    tier: 2,
    colSpan: 1,
    requiredPermission: 'employees:read',
  },
  {
    id: 'upcoming-events',
    tier: 2,
    colSpan: 1,
    requiredModule: 'calendar',
  },
]

/**
 * Returns widget definitions visible to this user, sorted tier-1 first.
 * The 'my-leave' widget is suppressed when the user also has leave:approve
 * (they see 'pending-leave' which is more relevant for approvers).
 */
export function getVisibleWidgets(
  permissions: string[],
  grantedModules: string[]
): HomeWidgetDef[] {
  const hasApprove = permissions.includes('leave:approve')

  return WIDGET_REGISTRY
    .filter(w => {
      if (w.id === 'my-leave' && hasApprove) return false
      if (w.requiredPermission && !permissions.includes(w.requiredPermission)) return false
      if (w.requiredModule && !grantedModules.includes(w.requiredModule)) return false
      return true
    })
    .sort((a, b) => a.tier - b.tier)
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add demo/src/modules/home/homeWidgets.ts
git commit -m "feat(demo): home widget registry with permission-ranked filtering"
```

---

## Task 9: Tier-1 Action Widgets

**Files:**
- Create: `demo/src/modules/home/widgets/PendingLeaveWidget.tsx`
- Create: `demo/src/modules/home/widgets/ActiveExceptionsWidget.tsx`
- Create: `demo/src/modules/home/widgets/MyLeaveWidget.tsx`

- [ ] **Step 1: Create PendingLeaveWidget**

```typescript
// demo/src/modules/home/widgets/PendingLeaveWidget.tsx
import { useNavigate } from 'react-router-dom'
import { CalendarDays, ArrowRight } from 'lucide-react'
import { leaveRequests } from '../../mock/data/leave'
import { employees } from '../../mock/data/employees'
import { cn } from '../../../lib/utils'

const TYPE_COLORS: Record<string, string> = {
  Annual: 'bg-blue-100 text-blue-700',
  Medical: 'bg-red-100 text-red-700',
  Emergency: 'bg-orange-100 text-orange-700',
  Compassionate: 'bg-purple-100 text-purple-700',
  Unpaid: 'bg-gray-100 text-gray-600',
}

export function PendingLeaveWidget() {
  const navigate = useNavigate()
  const pending = leaveRequests.filter(l => l.status === 'pending').slice(0, 4)

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <CalendarDays size={16} className="text-[var(--info)]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">Leave Approvals</span>
          {pending.length > 0 && (
            <span className="bg-[var(--danger)] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">
              {pending.length}
            </span>
          )}
        </div>
        <button
          onClick={() => navigate('/people/leave')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          View all <ArrowRight size={11} />
        </button>
      </div>

      {pending.length === 0 ? (
        <div className="px-4 py-6 text-center text-[12px] text-[var(--fg-3)]">
          No pending leave requests
        </div>
      ) : (
        <div className="divide-y divide-[var(--border-soft)]">
          {pending.map(req => {
            const emp = employees.find(e => e.id === req.employeeId)
            return (
              <div key={req.id} className="flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--bg-hover)] transition-colors">
                <img src={emp?.avatar} alt={emp?.name} className="w-7 h-7 rounded-full border border-[var(--border)] shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-[12px] font-medium text-[var(--fg-1)] truncate">{emp?.name}</div>
                  <div className="text-[10px] text-[var(--fg-3)]">{req.startDate} · {req.days}d</div>
                </div>
                <span className={cn('text-[10px] font-medium px-2 py-0.5 rounded-full', TYPE_COLORS[req.type] ?? 'bg-gray-100 text-gray-600')}>
                  {req.type}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Create ActiveExceptionsWidget**

```typescript
// demo/src/modules/home/widgets/ActiveExceptionsWidget.tsx
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, ArrowRight } from 'lucide-react'
import { exceptionEvents } from '../../mock/data/exceptions'
import { employees } from '../../mock/data/employees'
import { useLiveStore } from '../../../store/liveStore'
import { cn } from '../../../lib/utils'

const SEVERITY_STYLE: Record<string, string> = {
  high:   'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low:    'bg-blue-100 text-blue-700',
}

export function ActiveExceptionsWidget() {
  const navigate = useNavigate()
  const liveExceptions = useLiveStore((s) => s.liveExceptions)
  const allActive = [...exceptionEvents, ...liveExceptions].filter(e => !e.resolved).slice(0, 4)

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} className="text-[var(--warning)]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">Active Exceptions</span>
          {allActive.length > 0 && (
            <span className="bg-[var(--warning)] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">
              {allActive.length}
            </span>
          )}
        </div>
        <button
          onClick={() => navigate('/workforce')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          View all <ArrowRight size={11} />
        </button>
      </div>

      {allActive.length === 0 ? (
        <div className="px-4 py-6 text-center text-[12px] text-[var(--fg-3)]">
          No active exceptions
        </div>
      ) : (
        <div className="divide-y divide-[var(--border-soft)]">
          {allActive.map((ex, i) => {
            const emp = employees.find(e => e.id === ex.employeeId)
            const label = ex.type.replace(/_/g, ' ')
            return (
              <div key={ex.id ?? i} className="flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--bg-hover)] transition-colors">
                <img src={emp?.avatar} alt={emp?.name} className="w-7 h-7 rounded-full border border-[var(--border)] shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-[12px] font-medium text-[var(--fg-1)] capitalize truncate">{label}</div>
                  <div className="text-[10px] text-[var(--fg-3)] truncate">{emp?.name}</div>
                </div>
                <span className={cn('text-[10px] font-medium px-2 py-0.5 rounded-full capitalize', SEVERITY_STYLE[ex.severity] ?? 'bg-gray-100 text-gray-600')}>
                  {ex.severity}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create MyLeaveWidget**

```typescript
// demo/src/modules/home/widgets/MyLeaveWidget.tsx
import { useNavigate } from 'react-router-dom'
import { Palmtree, ArrowRight } from 'lucide-react'
import { leaveBalances, leaveRequests } from '../../mock/data/leave'
import { useAuthStore } from '../../../store/authStore'

export function MyLeaveWidget() {
  const navigate = useNavigate()
  const userId = useAuthStore((s) => s.user?.id)
  const myBalances = leaveBalances.filter(b => b.employeeId === userId).slice(0, 3)
  const myPending = leaveRequests.filter(l => l.employeeId === userId && l.status === 'pending')

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <Palmtree size={16} className="text-[var(--success)]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">My Leave</span>
        </div>
        <button
          onClick={() => navigate('/people/leave')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          View <ArrowRight size={11} />
        </button>
      </div>

      <div className="px-4 py-3 space-y-2">
        {myBalances.length === 0 ? (
          <div className="text-[12px] text-[var(--fg-3)] text-center py-3">No leave data</div>
        ) : myBalances.map(b => (
          <div key={b.type} className="flex items-center justify-between">
            <span className="text-[12px] text-[var(--fg-2)] font-outfit">{b.type} Leave</span>
            <div className="flex items-center gap-2">
              <div className="w-20 h-1.5 rounded-full bg-[var(--border)] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[var(--success)]"
                  style={{ width: `${(b.remaining / b.entitled) * 100}%` }}
                />
              </div>
              <span className="text-[11px] font-semibold text-[var(--fg-1)] font-geist w-12 text-right">
                {b.remaining}/{b.entitled}d
              </span>
            </div>
          </div>
        ))}
        {myPending.length > 0 && (
          <div className="text-[11px] text-[var(--warning)] font-medium mt-1">
            {myPending.length} request{myPending.length > 1 ? 's' : ''} pending approval
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add demo/src/modules/home/widgets/
git commit -m "feat(demo): tier-1 home widgets — leave approvals, exceptions, my leave"
```

---

## Task 10: Tier-2 Status Widgets

**Files:**
- Create: `demo/src/modules/home/widgets/WorkforceStatusWidget.tsx`
- Create: `demo/src/modules/home/widgets/HeadcountWidget.tsx`
- Create: `demo/src/modules/home/widgets/UpcomingEventsWidget.tsx`

- [ ] **Step 1: Create WorkforceStatusWidget**

```typescript
// demo/src/modules/home/widgets/WorkforceStatusWidget.tsx
import { useNavigate } from 'react-router-dom'
import { Radio, ArrowRight } from 'lucide-react'
import { employees } from '../../mock/data/employees'
import { useLiveStore } from '../../../store/liveStore'
import { cn } from '../../../lib/utils'

const STATUS_STYLE: Record<string, { dot: string; label: string; text: string }> = {
  online:       { dot: 'bg-emerald-400', label: 'Online',      text: 'text-emerald-600' },
  break:        { dot: 'bg-amber-400',   label: 'On Break',    text: 'text-amber-600' },
  offline:      { dot: 'bg-gray-300',    label: 'Offline',     text: 'text-gray-400' },
  'clocked-out':{ dot: 'bg-red-400',     label: 'Clocked Out', text: 'text-red-500' },
}

export function WorkforceStatusWidget() {
  const navigate = useNavigate()
  const presenceStatuses = useLiveStore((s) => s.presenceStatuses)

  const online = employees.filter(e => presenceStatuses[e.id] === 'online').length
  const onBreak = employees.filter(e => presenceStatuses[e.id] === 'break').length
  const clockedOut = employees.filter(e => presenceStatuses[e.id] === 'clocked-out').length
  const offline = employees.length - online - onBreak - clockedOut

  const recentOnline = employees
    .filter(e => presenceStatuses[e.id] === 'online')
    .slice(0, 6)

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <Radio size={16} className="text-[var(--success)]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">Workforce Status</span>
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] text-[var(--fg-3)]">Live</span>
          </div>
        </div>
        <button
          onClick={() => navigate('/workforce')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          View all <ArrowRight size={11} />
        </button>
      </div>

      <div className="px-4 py-3">
        <div className="grid grid-cols-4 gap-2 mb-3">
          {[
            { count: online,    ...STATUS_STYLE.online },
            { count: onBreak,   ...STATUS_STYLE.break },
            { count: clockedOut,...STATUS_STYLE['clocked-out'] },
            { count: offline,   ...STATUS_STYLE.offline },
          ].map(s => (
            <div key={s.label} className="text-center bg-[var(--bg-elevated)] rounded-lg p-2">
              <div className={cn('text-[18px] font-bold font-geist', s.text)}>{s.count}</div>
              <div className="flex items-center justify-center gap-1 mt-0.5">
                <span className={cn('w-1.5 h-1.5 rounded-full', s.dot)} />
                <span className="text-[9px] text-[var(--fg-3)]">{s.label}</span>
              </div>
            </div>
          ))}
        </div>

        {recentOnline.length > 0 && (
          <div className="flex items-center gap-1">
            <div className="flex -space-x-2">
              {recentOnline.map(e => (
                <img
                  key={e.id}
                  src={e.avatar}
                  alt={e.name}
                  title={e.name}
                  className="w-6 h-6 rounded-full border-2 border-[var(--bg-surface)]"
                />
              ))}
            </div>
            <span className="text-[11px] text-[var(--fg-3)] ml-1">{online} currently online</span>
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create HeadcountWidget**

```typescript
// demo/src/modules/home/widgets/HeadcountWidget.tsx
import { useNavigate } from 'react-router-dom'
import { Users, ArrowRight } from 'lucide-react'
import { employees } from '../../mock/data/employees'
import { leaveRequests } from '../../mock/data/leave'

export function HeadcountWidget() {
  const navigate = useNavigate()
  const total = employees.length
  const onLeaveToday = leaveRequests.filter(l => {
    const today = new Date().toISOString().split('T')[0]
    return l.status === 'approved' && l.startDate <= today && l.endDate >= today
  }).length
  const active = total - onLeaveToday

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <Users size={16} className="text-[var(--info)]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">Headcount</span>
        </div>
        <button
          onClick={() => navigate('/people/employees')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          View <ArrowRight size={11} />
        </button>
      </div>
      <div className="px-4 py-3 grid grid-cols-3 gap-2">
        <div className="text-center">
          <div className="text-[22px] font-bold text-[var(--fg-1)] font-geist">{total}</div>
          <div className="text-[10px] text-[var(--fg-3)]">Total</div>
        </div>
        <div className="text-center">
          <div className="text-[22px] font-bold text-emerald-600 font-geist">{active}</div>
          <div className="text-[10px] text-[var(--fg-3)]">Active</div>
        </div>
        <div className="text-center">
          <div className="text-[22px] font-bold text-amber-600 font-geist">{onLeaveToday}</div>
          <div className="text-[10px] text-[var(--fg-3)]">On Leave</div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create UpcomingEventsWidget**

```typescript
// demo/src/modules/home/widgets/UpcomingEventsWidget.tsx
import { useNavigate } from 'react-router-dom'
import { CalendarDays, ArrowRight } from 'lucide-react'
import { calendarEvents } from '../../mock/data/calendar'

const TYPE_COLOR: Record<string, string> = {
  company:  'bg-purple-100 text-purple-700',
  team:     'bg-blue-100 text-blue-700',
  personal: 'bg-gray-100 text-gray-600',
  review:   'bg-amber-100 text-amber-700',
  holiday:  'bg-green-100 text-green-700',
}

export function UpcomingEventsWidget() {
  const navigate = useNavigate()
  const today = new Date().toISOString().split('T')[0]

  const upcoming = (calendarEvents as Array<{ id: string; title: string; start_date: string; event_type: string }>)
    .filter(e => e.start_date >= today)
    .sort((a, b) => a.start_date.localeCompare(b.start_date))
    .slice(0, 4)

  return (
    <div className="card-depth rounded-[14px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <CalendarDays size={16} className="text-[#a78bfa]" strokeWidth={1.8} />
          <span className="text-[13px] font-semibold text-[var(--fg-1)] font-outfit">Upcoming Events</span>
        </div>
        <button
          onClick={() => navigate('/calendar')}
          className="flex items-center gap-1 text-[11px] text-[var(--fg-3)] hover:text-[var(--fg-1)] transition-colors"
        >
          Calendar <ArrowRight size={11} />
        </button>
      </div>
      <div className="divide-y divide-[var(--border-soft)]">
        {upcoming.length === 0 ? (
          <div className="px-4 py-6 text-center text-[12px] text-[var(--fg-3)]">No upcoming events</div>
        ) : upcoming.map(ev => (
          <div key={ev.id} className="flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--bg-hover)] transition-colors">
            <div className="text-[10px] font-semibold text-[var(--fg-3)] w-10 shrink-0 font-geist">
              {ev.start_date.slice(5)}
            </div>
            <div className="flex-1 text-[12px] text-[var(--fg-1)] truncate">{ev.title}</div>
            <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${TYPE_COLOR[ev.event_type] ?? 'bg-gray-100 text-gray-600'}`}>
              {ev.event_type}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```

Note: if `calendarEvents` has a different shape than assumed, check `demo/src/mock/data/calendar.ts` and adjust the `start_date` / `title` / `event_type` field names to match.

- [ ] **Step 5: Commit**

```bash
git add demo/src/modules/home/widgets/
git commit -m "feat(demo): tier-2 home widgets — workforce status, headcount, upcoming events"
```

---

## Task 11: Home Page — Aurora Hero + Permission-Ranked Widget Grid

**Files:**
- Modify: `demo/src/modules/home/HomePage.tsx`
- Delete: `demo/src/modules/home/AdminDashboard.tsx`
- Delete: `demo/src/modules/home/ManagerDashboard.tsx`
- Delete: `demo/src/modules/home/EmployeeDashboard.tsx`

- [ ] **Step 1: Replace `HomePage.tsx` entirely**

```typescript
import { useAuthStore } from '../../store/authStore'
import { getVisibleWidgets } from './homeWidgets'
import { PendingLeaveWidget } from './widgets/PendingLeaveWidget'
import { ActiveExceptionsWidget } from './widgets/ActiveExceptionsWidget'
import { MyLeaveWidget } from './widgets/MyLeaveWidget'
import { WorkforceStatusWidget } from './widgets/WorkforceStatusWidget'
import { HeadcountWidget } from './widgets/HeadcountWidget'
import { UpcomingEventsWidget } from './widgets/UpcomingEventsWidget'
import type { HomeWidgetDef } from './homeWidgets'

const WIDGET_COMPONENTS: Record<string, React.ComponentType> = {
  'pending-leave':    PendingLeaveWidget,
  'active-exceptions': ActiveExceptionsWidget,
  'my-leave':         MyLeaveWidget,
  'workforce-status': WorkforceStatusWidget,
  'headcount':        HeadcountWidget,
  'upcoming-events':  UpcomingEventsWidget,
}

function WidgetRenderer({ def }: { def: HomeWidgetDef }) {
  const Component = WIDGET_COMPONENTS[def.id]
  if (!Component) return null
  return (
    <div className={def.colSpan === 2 ? 'col-span-2' : 'col-span-1'}>
      <Component />
    </div>
  )
}

export function HomePage() {
  const user = useAuthStore((s) => s.user)
  const permissions = useAuthStore((s) => s.permissions)
  const grantedModules = useAuthStore((s) => s.grantedModules)

  const widgets = getVisibleWidgets(permissions, grantedModules)

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="relative min-h-screen">

      {/* Aurora glow */}
      <div
        className="pointer-events-none absolute top-0 left-0 right-0 h-64"
        style={{
          background: [
            'radial-gradient(ellipse 60% 120px at 50% 0px, rgba(167,139,250,0.18) 0%, transparent 70%)',
            'radial-gradient(ellipse 40% 80px at 30% -10px, rgba(96,165,250,0.12) 0%, transparent 60%)',
            'radial-gradient(ellipse 40% 80px at 70% -10px, rgba(244,114,182,0.10) 0%, transparent 60%)',
          ].join(', '),
        }}
      />

      {/* Hero */}
      <div className="relative flex flex-col items-center pt-10 pb-8">
        {/* ONEVO bloom logo */}
        <div className="w-12 h-12 mb-3">
          <svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
            <ellipse cx="32" cy="20" rx="10" ry="6" fill="url(#h1)" transform="rotate(-30 32 20)" opacity="0.9"/>
            <ellipse cx="36" cy="28" rx="10" ry="6" fill="url(#h2)" transform="rotate(30 36 28)" opacity="0.9"/>
            <ellipse cx="26" cy="36" rx="10" ry="6" fill="url(#h3)" transform="rotate(90 26 36)" opacity="0.9"/>
            <ellipse cx="16" cy="28" rx="10" ry="6" fill="url(#h4)" transform="rotate(150 16 28)" opacity="0.9"/>
            <ellipse cx="20" cy="20" rx="10" ry="6" fill="url(#h5)" transform="rotate(210 20 20)" opacity="0.9"/>
            <circle cx="26" cy="27" r="5" fill="white" opacity="0.9"/>
            <defs>
              <linearGradient id="h1" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#a78bfa"/><stop offset="1" stopColor="#7c3aed"/></linearGradient>
              <linearGradient id="h2" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#f472b6"/><stop offset="1" stopColor="#ec4899"/></linearGradient>
              <linearGradient id="h3" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#60a5fa"/><stop offset="1" stopColor="#3b82f6"/></linearGradient>
              <linearGradient id="h4" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#34d399"/><stop offset="1" stopColor="#10b981"/></linearGradient>
              <linearGradient id="h5" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fbbf24"/><stop offset="1" stopColor="#f59e0b"/></linearGradient>
            </defs>
          </svg>
        </div>

        <h1 className="text-[26px] font-extrabold text-[var(--fg-1)] tracking-tight font-outfit mb-1">
          ONEVO<sup className="text-[11px] font-normal text-[var(--fg-4)] ml-0.5">™</sup>
        </h1>
        <p className="text-[13px] text-[var(--fg-3)] font-outfit mb-1">
          {greeting}, {user?.name?.split(' ')[0]} —{' '}
          <span className="text-[var(--fg-2)]">here's what needs your attention</span>
        </p>
      </div>

      {/* Permission-ranked widget grid */}
      {widgets.length > 0 ? (
        <div className="grid grid-cols-2 gap-4">
          {widgets.map(def => (
            <WidgetRenderer key={def.id} def={def} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-[13px] text-[var(--fg-3)]">
          No modules enabled. Contact your administrator.
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Delete the three old dashboard files**

```bash
rm demo/src/modules/home/AdminDashboard.tsx
rm demo/src/modules/home/ManagerDashboard.tsx
rm demo/src/modules/home/EmployeeDashboard.tsx
```

- [ ] **Step 3: Verify TypeScript**

```bash
cd demo && npx tsc --noEmit
```
Expected: no errors. If calendar mock data fields differ (Step 3 of Task 10 note), fix `UpcomingEventsWidget.tsx` field names first.

- [ ] **Step 4: Visual check — all 3 personas**

In the running dev server, log in as each persona and confirm:
- **Admin** (Sarah Lim): sees PendingLeave + ActiveExceptions + WorkforceStatus (full row) + Headcount + UpcomingEvents. Does NOT see MyLeave (suppressed since she has `leave:approve`).
- **Manager** (James Rajan): sees PendingLeave + ActiveExceptions + WorkforceStatus (full row) + UpcomingEvents. Does NOT see Headcount (no `employees:read`). Does NOT see MyLeave.
- **Employee** (Aisha Noor): sees MyLeave + UpcomingEvents. No workforce/exceptions/headcount (lacks those modules).

- [ ] **Step 5: Commit**

```bash
git add demo/src/modules/home/
git commit -m "feat(demo): permission-ranked home page with aurora hero and widget grid"
```

---

## Task 12: Userflow — Home Page Documentation

**Files:**
- Create: `Userflow/Home/home-overview.md`
- Modify: `Userflow/README.md`

- [ ] **Step 1: Create `Userflow/Home/home-overview.md`**

```markdown
# Home Page Overview

**Area:** Platform Shell  
**Trigger:** User logs in or navigates to `/`  
**Required Permission(s):** Any (page is always accessible; content varies by permissions)

## Purpose

The home page is the user's mission control. It surfaces the most actionable content first, determined entirely by `grantedModules` and `permissions` — not by role label. A user with `leave:approve` always sees pending leave requests before anything else, regardless of their role name.

## Widget Ranking Logic

Widgets are selected and ranked by tier:

| Tier | Meaning | Shown when |
|---|---|---|
| 1 | Action required | Pending items exist that only this user can resolve |
| 2 | Today's status | User has read access to a module with live/daily data |

Within each tier, widgets appear in the order defined in `homeWidgets.ts`.

## Widget → Permission Map

| Widget | Required | Notes |
|---|---|---|
| Pending Leave Approvals | `leave:approve` | Shows pending leave requests for the user to approve |
| Active Exceptions | `exceptions:read` | Shows unresolved workforce exceptions |
| My Leave Balance | `leave` module | Suppressed when user also has `leave:approve` |
| Workforce Status | `workforce:read` | Live presence counts (online, break, clocked-out) |
| Headcount | `employees:read` | Total / active / on-leave counts |
| Upcoming Events | `calendar` module | Next company, team, or review events |

## Persona Examples

**Super Admin** (all modules):  
Pending Leave → Active Exceptions → Workforce Status (full row) → Headcount → Upcoming Events

**Manager** (`leave:approve`, `workforce:read`, `calendar`):  
Pending Leave → Active Exceptions → Workforce Status (full row) → Upcoming Events

**Employee** (`leave` module, `calendar` module):  
My Leave Balance → Upcoming Events

## Flow Steps

1. User authenticates → redirected to `/`
2. `getVisibleWidgets(permissions, grantedModules)` filters `WIDGET_REGISTRY` and sorts by tier
3. Home page renders aurora hero with personalized greeting
4. Widget grid renders filtered/ranked widgets (2-column layout; `colSpan:2` widgets span full width)
5. Each widget links to its relevant module for full detail

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]] — precondition
- [[Userflow/Leave/leave-approval|Leave Approval]] — destination from Pending Leave widget
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]] — destination from Workforce Status widget
```

- [ ] **Step 2: Add Home section to `Userflow/README.md`**

Open `Userflow/README.md`. After the last existing section (or at the top of the flows list), add:

```markdown
## Home — (no specific permission required)

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Home/home-overview\|Home Page Overview]] | Permission-ranked widget dashboard on login | Documented | MUST |
```

- [ ] **Step 3: Commit**

```bash
git add Userflow/Home/ Userflow/README.md
git commit -m "docs(userflow): home page overview and widget ranking logic"
```

---

## Self-Review

**Spec coverage check:**
- ✅ ClickUp chrome (full-width topbar, dark rail with labels, white sidebar with Create button) — Tasks 3–6
- ✅ Light theme as default with dark theme still toggleable — Tasks 1–2
- ✅ Permission-ranked home page — Tasks 8–11
- ✅ Module polish (glass/card light-mode) — Tasks 2, 7
- ✅ Userflow documentation — Task 12
- ✅ Three hardcoded dashboards replaced — Task 11

**Placeholder scan:** None found — all steps contain actual code.

**Type consistency check:**
- `HomeWidgetDef.id` is used as key in both `WIDGET_REGISTRY` (Task 8) and `WIDGET_COMPONENTS` (Task 11) ✅
- `getVisibleWidgets` signature `(permissions: string[], grantedModules: string[])` matches call site in `HomePage.tsx` ✅
- All widget files import from paths relative to `demo/src/modules/home/widgets/` ✅
- `calendarEvents` field names (`start_date`, `title`, `event_type`) — flagged in Task 10 Step 4 to verify against actual mock data ✅

**One risk:** `demo/src/mock/data/calendar.ts` field naming is not confirmed. Task 10 Step 4 explicitly calls this out. Fix `UpcomingEventsWidget.tsx` field names if TypeScript errors appear there.
