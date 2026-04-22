# Neutral Chrome Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the violet-dominant glass aesthetic with a neutral monochromatic, light/dark theme-aware chrome across the demo codebase and update the frontend design system docs to match.

**Architecture:** CSS custom properties (`--bg-*`, `--fg-*`, `--border`, etc.) applied via `data-theme="dark|light"` on `<html>` drive all chrome colors. A `ThemeProvider` component manages system preference detection, localStorage persistence, and the toggle. The four layout components (IconRail, ExpansionPanel, Topbar, DashboardLayout) are rewritten to consume these tokens. Violet stays only in data/chart utilities.

**Tech Stack:** Vite 6, React 18, TypeScript 5.6, Tailwind CSS 3.4, Lucide React, Zustand, React Router v6

**Spec:** `docs/superpowers/specs/2026-04-21-neutral-chrome-redesign-design.md`

> **Note:** No test suite exists in this project. Verification steps use `npm run dev` + manual browser checks.

---

### Task 1: Token Foundation — `index.css` + `tailwind.config.ts`

**Files:**
- Modify: `demo/src/index.css`
- Modify: `demo/tailwind.config.ts`

- [ ] **Step 1: Replace `demo/src/index.css` entirely**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ── DARK THEME ─────────────────────────────────────────── */
[data-theme="dark"] {
  --bg-base:       #0a0a0a;
  --bg-surface:    #111111;
  --bg-elevated:   #1a1a1a;
  --bg-overlay:    #222222;
  --bg-hover:      #2a2a2a;
  --border:        #2a2a2a;
  --border-soft:   #1f1f1f;
  --fg-1:          #f5f5f5;
  --fg-2:          #a3a3a3;
  --fg-3:          #666666;
  --fg-4:          #3d3d3d;
  --accent-subtle: #1e1e1e;
  --accent-border: #333333;
  --success:       #22c55e;
  --warning:       #f59e0b;
  --danger:        #ef4444;
  --info:          #3b82f6;
}

/* ── LIGHT THEME ─────────────────────────────────────────── */
[data-theme="light"] {
  --bg-base:       #f5f5f5;
  --bg-surface:    #ffffff;
  --bg-elevated:   #fafafa;
  --bg-overlay:    #f0f0f0;
  --bg-hover:      #ebebeb;
  --border:        #e5e5e5;
  --border-soft:   #efefef;
  --fg-1:          #0a0a0a;
  --fg-2:          #525252;
  --fg-3:          #a3a3a3;
  --fg-4:          #d4d4d4;
  --accent-subtle: #f0f0f0;
  --accent-border: #d4d4d4;
  --success:       #16a34a;
  --warning:       #d97706;
  --danger:        #dc2626;
  --info:          #2563eb;
}

@layer base {
  body {
    background-color: var(--bg-base);
    color: var(--fg-1);
    font-family: 'Outfit', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  * {
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
  }

  *::-webkit-scrollbar { width: 4px; }
  *::-webkit-scrollbar-track { background: transparent; }
  *::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
}

@layer utilities {
  /* Glass fills — used in data cards only */
  .glass-1 { background: rgba(255, 255, 255, 0.025); }
  .glass-2 { background: rgba(255, 255, 255, 0.05); }
  .glass-3 { background: rgba(255, 255, 255, 0.08); }

  /* Borders */
  .border-glass    { border-color: rgba(255, 255, 255, 0.07); }
  .border-glass-md { border-color: rgba(255, 255, 255, 0.10); }
  .border-glass-hi { border-color: rgba(255, 255, 255, 0.16); }

  /* Gradient text — data cards only */
  .text-gradient-violet {
    background: linear-gradient(135deg, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .text-gradient-green {
    background: linear-gradient(135deg, #34d399, #6ee7b7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .text-gradient-amber {
    background: linear-gradient(135deg, #fbbf24, #fde68a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .text-gradient-red {
    background: linear-gradient(135deg, #f87171, #fca5a5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .text-gradient-blue {
    background: linear-gradient(135deg, #60a5fa, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .text-gradient-white {
    background: linear-gradient(135deg, #ffffff, #cbd5e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* Card depth — neutral, no violet glow */
  .card-depth {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
  }
}
```

- [ ] **Step 2: Update `demo/tailwind.config.ts` — change darkMode strategy**

Replace only the `darkMode` line (line 3):

```ts
// Before:
darkMode: 'class',

// After:
darkMode: ['selector', '[data-theme="dark"]'],
```

Full updated file for reference:

```ts
import type { Config } from 'tailwindcss'

export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        geist: ['Geist Mono', 'monospace'],
      },
      colors: {
        violet: {
          DEFAULT: '#7C3AED',
          glow: '#8B5CF6',
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        surface: {
          base: '#08080f',
          '01': '#0d0d18',
          '02': '#111120',
          '03': '#161628',
        },
        glass: {
          '01': 'rgba(255,255,255,0.025)',
          '02': 'rgba(255,255,255,0.05)',
          '03': 'rgba(255,255,255,0.08)',
          border: 'rgba(255,255,255,0.07)',
          'border-md': 'rgba(255,255,255,0.10)',
          'border-hi': 'rgba(255,255,255,0.16)',
        },
      },
      backgroundImage: {
        'gradient-violet': 'linear-gradient(135deg, #7c3aed, #a855f7)',
        'gradient-card': 'linear-gradient(135deg, rgba(124,58,237,0.08), rgba(168,85,247,0.04))',
        'gradient-metric-purple': 'linear-gradient(135deg, #a78bfa, #c084fc)',
        'gradient-metric-green': 'linear-gradient(135deg, #34d399, #6ee7b7)',
        'gradient-metric-amber': 'linear-gradient(135deg, #fbbf24, #fde68a)',
        'gradient-metric-red': 'linear-gradient(135deg, #f87171, #fca5a5)',
        'gradient-metric-blue': 'linear-gradient(135deg, #60a5fa, #93c5fd)',
        'gradient-metric-white': 'linear-gradient(135deg, #ffffff, #e2e8f0)',
      },
      boxShadow: {
        'glow-violet': '0 0 24px rgba(124,58,237,0.25)',
        'glow-violet-lg': '0 0 48px rgba(124,58,237,0.35)',
        'glow-green': '0 0 16px rgba(52,211,153,0.35)',
        'glow-amber': '0 0 16px rgba(251,191,36,0.35)',
        'glow-red': '0 0 16px rgba(248,113,113,0.35)',
        'glow-blue': '0 0 16px rgba(96,165,250,0.35)',
        glass: '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
        'glass-lg': '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08)',
        'card-hover': '0 12px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1)',
      },
      animation: {
        'pulse-dot': 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0', transform: 'translateY(4px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
} satisfies Config
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/index.css demo/tailwind.config.ts
git commit -m "feat: add neutral CSS token system and update tailwind darkMode selector"
```

---

### Task 2: Theme Infrastructure — `ThemeProvider.tsx` + `main.tsx`

**Files:**
- Create: `demo/src/components/ui/ThemeProvider.tsx`
- Modify: `demo/src/main.tsx`

- [ ] **Step 1: Create `demo/src/components/ui/ThemeProvider.tsx`**

```tsx
import { createContext, useContext, useEffect, useState } from 'react'

export type Theme = 'dark' | 'light' | 'system'

interface ThemeContextValue {
  theme: Theme
  setTheme: (t: Theme) => void
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: 'system',
  setTheme: () => {},
})

function resolveAndApply(theme: Theme) {
  const root = document.documentElement
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    root.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
  } else {
    root.setAttribute('data-theme', theme)
  }
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    return (localStorage.getItem('theme') as Theme) ?? 'system'
  })

  // Apply on every theme change
  useEffect(() => {
    resolveAndApply(theme)
  }, [theme])

  // When in system mode, track OS changes
  useEffect(() => {
    if (theme !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => resolveAndApply('system')
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [theme])

  function setTheme(t: Theme) {
    localStorage.setItem('theme', t)
    setThemeState(t)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return useContext(ThemeContext)
}
```

- [ ] **Step 2: Replace `demo/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { ThemeProvider } from './components/ui/ThemeProvider'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
)
```

Note: The old `document.documentElement.classList.add('dark')` line is removed — ThemeProvider handles initial theme application.

- [ ] **Step 3: Quick smoke check**

Run: `cd demo && npm run dev`

Open `http://localhost:5173`. The page should load without errors. Background will be dark (`#0a0a0a`) if your OS is in dark mode, light (`#f5f5f5`) if light mode. Check DevTools → `<html>` element has `data-theme="dark"` or `"light"` attribute.

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/ui/ThemeProvider.tsx demo/src/main.tsx
git commit -m "feat: add ThemeProvider with system preference detection and localStorage persistence"
```

---

### Task 3: DashboardLayout

**Files:**
- Modify: `demo/src/components/layout/DashboardLayout.tsx`

- [ ] **Step 1: Replace `demo/src/components/layout/DashboardLayout.tsx`**

```tsx
import { Outlet, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useNavStore, PANEL_PILLARS, type PillarKey } from '../../store/navStore'
import { IconRail } from './IconRail'
import { Topbar } from './Topbar'
import { ExpansionPanel } from './ExpansionPanel'
import { useMockEventEngine } from '../../hooks/useMockEventEngine'
import { useEffect } from 'react'
import { cn } from '../../lib/utils'

function pathToPillar(pathname: string): PillarKey {
  if (pathname.startsWith('/people')) return 'people'
  if (pathname.startsWith('/workforce')) return 'workforce'
  if (pathname.startsWith('/org')) return 'org'
  if (pathname.startsWith('/calendar')) return 'calendar'
  if (pathname.startsWith('/inbox')) return 'inbox'
  if (pathname.startsWith('/admin')) return 'admin'
  if (pathname.startsWith('/settings')) return 'settings'
  return 'home'
}

export function DashboardLayout() {
  const personaKey = useAuthStore((s) => s.personaKey)
  const { setActivePillar, panelOpen, activePillar } = useNavStore()
  const location = useLocation()
  useMockEventEngine()

  useEffect(() => {
    setActivePillar(pathToPillar(location.pathname))
  }, [location.pathname]) // eslint-disable-line

  if (!personaKey) return <Navigate to="/login" replace />

  const hasPanelContent = PANEL_PILLARS.includes(activePillar as PillarKey)
  // Rail is 64px (w-16), expansion panel is 220px — total open: 284px
  const sidebarWidth = panelOpen && hasPanelContent ? 'ml-[284px]' : 'ml-16'

  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-[var(--fg-1)]">
      <IconRail />
      <ExpansionPanel />
      <Topbar />

      <main
        className={cn(
          'pt-12 min-h-screen relative z-10',
          'transition-[margin-left] duration-200 ease-in-out',
          sidebarWidth
        )}
      >
        <div className="p-6 max-w-[1400px]">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/components/layout/DashboardLayout.tsx
git commit -m "feat: remove ambient violet gradients from DashboardLayout, use neutral tokens"
```

---

### Task 4: IconRail

**Files:**
- Modify: `demo/src/components/layout/IconRail.tsx`

- [ ] **Step 1: Replace `demo/src/components/layout/IconRail.tsx`**

```tsx
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
  { icon: ShieldCheck,  label: 'Admin',     defaultPath: '/admin',            pillarKey: 'admin',     module: 'admin' },
  { icon: Settings,     label: 'Settings',  defaultPath: '/settings',         pillarKey: 'settings',  module: 'settings' },
]

export function IconRail() {
  const navigate = useNavigate()
  const inboxCount = useLiveStore((s) => s.inboxCount)
  const grantedModules = useAuthStore((s) => s.grantedModules)
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
    <div className="fixed left-0 top-[48px] bottom-0 z-50 w-16 flex flex-col items-center py-4 bg-[var(--bg-surface)] border-r border-[var(--border)]">
      <div className="flex-1 flex flex-col items-center gap-0.5 w-full px-2">
        {pillars.map(({ icon: Icon, label, defaultPath, pillarKey, module }) => {
          if (module && !grantedModules.includes(module)) return null
          const active = activePillar === pillarKey

          return (
            <button
              key={pillarKey}
              onClick={() => handleClick(pillarKey, defaultPath)}
              title={label}
              className={cn(
                'w-full flex flex-col items-center justify-center py-3 rounded-lg relative transition-colors duration-150',
                active
                  ? 'text-[var(--fg-1)]'
                  : 'text-[var(--fg-3)] hover:text-[var(--fg-2)] hover:bg-[var(--bg-hover)]'
              )}
            >
              <Icon size={16} strokeWidth={active ? 2 : 1.75} />
              {active && (
                <span className="mt-1.5 w-1 h-1 rounded-full bg-[var(--fg-1)]" />
              )}
              {pillarKey === 'inbox' && inboxCount > 0 && (
                <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-[var(--danger)]" />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify visually**

Run `npm run dev`. Check:
- Rail is flush to the left edge (no gap, no rounded pill container)
- Rail background matches page surface (neutral dark or light)
- Icons are visibly smaller (16px vs old 24px)
- Clicking a pillar: active icon turns bright (`var(--fg-1)`), small dot appears below it
- No violet glow or bloom animation

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/IconRail.tsx
git commit -m "feat: restyle IconRail — flush rail, 16px icons, neutral active state"
```

---

### Task 5: ExpansionPanel

**Files:**
- Modify: `demo/src/components/layout/ExpansionPanel.tsx`

- [ ] **Step 1: Replace `demo/src/components/layout/ExpansionPanel.tsx`**

```tsx
import { useNavigate, useLocation } from 'react-router-dom'
import { useNavStore } from '../../store/navStore'
import { cn } from '../../lib/utils'
import {
  User, CalendarDays, GitBranch, Building2, Users,
  ShieldCheck, ClipboardList, MonitorDot, Laptop, CheckSquare2,
  Settings, Eye, Plug, Palette, Bell, FileText, Clock,
  LayoutDashboard, CalendarCheck, Timer,
  type LucideIcon,
} from 'lucide-react'

type SubNavItem = {
  label: string
  path: string
  icon: LucideIcon
}

const subNavConfig: Record<string, { label: string; items: SubNavItem[] }> = {
  people: {
    label: 'People',
    items: [
      { label: 'Employees', path: '/people/employees', icon: User },
      { label: 'Leave',     path: '/people/leave',     icon: CalendarDays },
      { label: 'Documents', path: '/people/documents', icon: FileText },
    ],
  },
  workforce: {
    label: 'Workforce',
    items: [
      { label: 'Overview', path: '/workforce', icon: LayoutDashboard },
    ],
  },
  org: {
    label: 'Organization',
    items: [
      { label: 'Org Chart',      path: '/org',                    icon: GitBranch },
      { label: 'Departments',    path: '/org?tab=departments',    icon: Building2 },
      { label: 'Teams',          path: '/org?tab=teams',          icon: Users },
      { label: 'Job Families',   path: '/org?tab=job-families',   icon: FileText },
      { label: 'Legal Entities', path: '/org?tab=legal-entities', icon: ShieldCheck },
      { label: 'Cost Centers',   path: '/org?tab=cost-centers',   icon: ClipboardList },
    ],
  },
  calendar: {
    label: 'Calendar',
    items: [
      { label: 'Events',               path: '/calendar',                 icon: CalendarDays },
      { label: 'Shifts & Schedules',   path: '/calendar?tab=shifts',     icon: Clock },
      { label: 'Attendance Correction',path: '/calendar?tab=attendance', icon: CalendarCheck },
      { label: 'Overtime',             path: '/calendar?tab=overtime',   icon: Timer },
    ],
  },
  admin: {
    label: 'Admin',
    items: [
      { label: 'Users & Roles', path: '/admin',               icon: ShieldCheck },
      { label: 'Audit Log',     path: '/admin?tab=audit',     icon: ClipboardList },
      { label: 'Agents',        path: '/admin?tab=agents',    icon: MonitorDot },
      { label: 'Devices',       path: '/admin?tab=devices',   icon: Laptop },
      { label: 'Compliance',    path: '/admin?tab=compliance',icon: CheckSquare2 },
    ],
  },
  settings: {
    label: 'Settings',
    items: [
      { label: 'General',      path: '/settings',                  icon: Settings },
      { label: 'Monitoring',   path: '/settings?tab=monitoring',   icon: Eye },
      { label: 'Integrations', path: '/settings?tab=integrations', icon: Plug },
      { label: 'Branding',     path: '/settings?tab=branding',     icon: Palette },
      { label: 'Alert Rules',  path: '/settings?tab=alerts',       icon: Bell },
    ],
  },
}

function isItemActive(itemPath: string, pathname: string, search: string): boolean {
  const [itemPathname, itemQuery] = itemPath.split('?')
  const itemParams = new URLSearchParams(itemQuery ?? '')
  const itemTab = itemParams.get('tab')
  if (itemTab) {
    if (pathname !== itemPathname) return false
    const currentTab = new URLSearchParams(search).get('tab')
    return itemTab === currentTab
  }
  if (!itemQuery) {
    if (new URLSearchParams(search).get('tab')) return false
    return pathname === itemPathname || pathname.startsWith(itemPathname + '/')
  }
  return pathname === itemPathname
}

export function ExpansionPanel() {
  const { activePillar, panelOpen } = useNavStore()
  const navigate = useNavigate()
  const location = useLocation()

  const config = activePillar ? subNavConfig[activePillar] : null

  return (
    <aside
      className={cn(
        'fixed top-[48px] left-16 bottom-0 w-[220px] z-30',
        'flex flex-col',
        'bg-[var(--bg-surface)]',
        'border-r border-[var(--border)]',
        'transition-transform duration-200 ease-in-out',
        panelOpen && config ? 'translate-x-0' : '-translate-x-full'
      )}
    >
      {config && (
        <div className="flex-1 overflow-y-auto p-3 pt-5">
          {/* Section title */}
          <div className="text-[var(--fg-3)] text-[11px] font-outfit uppercase tracking-[0.14em] mb-4 px-2.5">
            {config.label}
          </div>

          <nav className="space-y-0.5">
            {config.items.map(item => {
              const active = isItemActive(item.path, location.pathname, location.search)
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-outfit transition-colors duration-150 text-left',
                    active
                      ? 'bg-[var(--accent-subtle)] text-[var(--fg-1)] border border-[var(--accent-border)]'
                      : 'text-[var(--fg-3)] hover:text-[var(--fg-2)] hover:bg-[var(--bg-hover)] border border-transparent'
                  )}
                >
                  <item.icon
                    size={15}
                    className={cn(
                      'shrink-0 transition-colors duration-150',
                      active ? 'text-[var(--fg-1)]' : 'text-[var(--fg-4)]'
                    )}
                  />
                  {item.label}
                </button>
              )
            })}
          </nav>
        </div>
      )}

      {config && (
        <div className="shrink-0 px-4 pb-4">
          <div className="h-px bg-[var(--border-soft)]" />
        </div>
      )}
    </aside>
  )
}
```

- [ ] **Step 2: Verify visually**

Run `npm run dev`. Click a pillar with sub-items (e.g. People). Check:
- Panel slides in from left as before
- Section title "PEOPLE" shows in neutral muted color (no violet)
- Active item has subtle neutral bg + thin border (no violet glow or gradient left-bar)
- Inactive items are dimmed; hover brightens them
- Panel background matches the rail (neutral dark/light surface)

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/ExpansionPanel.tsx
git commit -m "feat: restyle ExpansionPanel — neutral active state, remove violet glow elements"
```

---

### Task 6: Topbar

**Files:**
- Modify: `demo/src/components/layout/Topbar.tsx`

- [ ] **Step 1: Replace `demo/src/components/layout/Topbar.tsx`**

```tsx
import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { useNavigate, useLocation } from 'react-router-dom'
import { LogOut, Search, Bell, ChevronRight, Sun, Moon, Monitor } from 'lucide-react'
import { useLiveStore } from '../../store/liveStore'
import { CommandPalette } from '../ui/CommandPalette'
import { useTheme, type Theme } from '../ui/ThemeProvider'

const pathLabels: Record<string, string> = {
  people: 'People',
  employees: 'Employees',
  leave: 'Leave',
  workforce: 'Workforce Live',
  org: 'Organization',
  calendar: 'Calendar',
  inbox: 'Inbox',
  admin: 'Admin',
  settings: 'Settings',
}

function getBreadcrumbs(pathname: string): string[] {
  const parts = pathname.split('/').filter(Boolean)
  if (parts.length === 0) return ['Home']
  return parts
    .filter(p => !/^[a-z0-9]{2,4}$/.test(p) || isNaN(Number(p[0])))
    .map(p => pathLabels[p] ?? p)
}

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
  const location = useLocation()
  const inboxCount = useLiveStore((s) => s.inboxCount)
  const [paletteOpen, setPaletteOpen] = useState(false)
  const { theme, setTheme } = useTheme()

  const breadcrumbs = getBreadcrumbs(location.pathname)
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

  return (
    <>
    <div className="h-12 bg-[var(--bg-surface)] border-b border-[var(--border)] flex items-center justify-between pl-0 pr-5 fixed top-0 left-0 right-0 z-40">
      {/* Logo zone — matches rail width (w-16 = 64px) */}
      <div className="w-16 shrink-0 flex items-center justify-center">
        <div className="w-8 h-8 rounded-lg bg-[var(--fg-1)] flex items-center justify-center font-bold text-[14px] font-outfit text-[var(--bg-base)]">
          N
        </div>
      </div>

      {/* Separator */}
      <div className="w-px h-5 bg-[var(--border)] shrink-0 mr-4" />

      {/* Breadcrumbs */}
      <div className="flex-1 flex items-center gap-1.5 min-w-0">
        <span className="text-sm font-outfit font-semibold shrink-0" style={{ color: tenantColor }}>
          {tenantName}
        </span>
        {breadcrumbs.map((crumb, i) => (
          <div key={i} className="flex items-center gap-1.5 min-w-0">
            <ChevronRight size={12} className="text-[var(--fg-4)] shrink-0" />
            <span className={`text-[13px] font-outfit truncate ${
              i === breadcrumbs.length - 1
                ? 'text-[var(--fg-2)]'
                : 'text-[var(--fg-4)]'
            }`}>
              {crumb}
            </span>
          </div>
        ))}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-1.5 shrink-0">
        {/* Search */}
        <button
          onClick={() => setPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border)] text-[var(--fg-3)] hover:text-[var(--fg-1)] hover:border-[var(--fg-4)] transition-all duration-150 text-xs font-outfit"
        >
          <Search size={13} />
          <span>Search</span>
          <kbd className="ml-2 px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--fg-3)] text-[10px] font-geist border border-[var(--border)]">⌘K</kbd>
        </button>

        {/* Bell / Inbox */}
        <button
          onClick={() => navigate('/inbox')}
          className="relative w-8 h-8 flex items-center justify-center rounded-lg text-[var(--fg-3)] hover:text-[var(--fg-2)] hover:bg-[var(--bg-hover)] transition-colors"
        >
          <Bell size={15} />
          {inboxCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-[16px] h-[16px] bg-[var(--fg-1)] rounded-full text-[9px] flex items-center justify-center text-[var(--bg-base)] font-bold">
              {inboxCount > 9 ? '9+' : inboxCount}
            </span>
          )}
        </button>

        {/* Theme toggle — cycles system → light → dark */}
        <button
          onClick={cycleTheme}
          title={`Theme: ${theme}`}
          className="w-8 h-8 flex items-center justify-center rounded-lg text-[var(--fg-3)] hover:text-[var(--fg-1)] hover:bg-[var(--bg-hover)] transition-colors"
        >
          <ThemeIcon theme={theme} />
        </button>

        <div className="w-px h-5 bg-[var(--border)] mx-0.5" />

        {/* Avatar */}
        <div className="flex items-center gap-2.5 pl-1">
          <div className="relative">
            <img
              src={user?.avatar}
              alt={user?.name}
              className="w-7 h-7 rounded-full border border-[var(--border)]"
            />
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[var(--success)] border-2 border-[var(--bg-surface)]" />
          </div>
          <div className="hidden md:block leading-none">
            <div className="text-[var(--fg-1)] text-[13px] font-outfit">{user?.name}</div>
            <div className="text-[var(--fg-3)] text-[11px] font-outfit mt-0.5">{user?.jobTitle}</div>
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

- [ ] **Step 2: Full visual verification**

Run `npm run dev`. Check all of these:

| Check | Expected |
|---|---|
| Topbar height | Visibly shorter than before (48px) |
| Logo mark | Neutral square — white `N` on dark, black `N` on light |
| Topbar background | Matches rail + panel surface (no frosted glass) |
| Inbox badge (when count > 0) | White pill (dark mode) / black pill (light mode) — no violet |
| Theme toggle button | Sun/Moon/Monitor icon visible right of bell |
| Click theme toggle | Cycles system → light → dark → system; page background changes |
| Refresh after toggle | Theme persists (localStorage) |
| Search box | Neutral border/bg — no violet on hover |
| Avatar online dot | Green, no violet border |

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/Topbar.tsx
git commit -m "feat: restyle Topbar — 48px, neutral colors, add theme toggle"
```

---

### Task 7: Frontend Docs Updates

**Files:**
- Modify: `frontend/design-system/foundations/color-tokens.md`
- Modify: `frontend/design-system/theming/dark-mode.md`
- Modify: `frontend/design-system/patterns/navigation-patterns.md`
- Modify: `frontend/design-system/foundations/iconography.md`

- [ ] **Step 1: Update `frontend/design-system/foundations/color-tokens.md`**

Replace the entire CSS block under `## CSS Custom Properties` with:

```css
/* CSS custom properties — applied via data-theme attribute on <html> */

[data-theme="dark"] {
  --bg-base:       #0a0a0a;
  --bg-surface:    #111111;
  --bg-elevated:   #1a1a1a;
  --bg-overlay:    #222222;
  --bg-hover:      #2a2a2a;
  --border:        #2a2a2a;
  --border-soft:   #1f1f1f;
  --fg-1:          #f5f5f5;   /* primary text */
  --fg-2:          #a3a3a3;   /* secondary text */
  --fg-3:          #666666;   /* muted text */
  --fg-4:          #3d3d3d;   /* disabled / separator */
  --accent-subtle: #1e1e1e;   /* active item background */
  --accent-border: #333333;   /* active item border */
  --success:       #22c55e;
  --warning:       #f59e0b;
  --danger:        #ef4444;
  --info:          #3b82f6;
}

[data-theme="light"] {
  --bg-base:       #f5f5f5;
  --bg-surface:    #ffffff;
  --bg-elevated:   #fafafa;
  --bg-overlay:    #f0f0f0;
  --bg-hover:      #ebebeb;
  --border:        #e5e5e5;
  --border-soft:   #efefef;
  --fg-1:          #0a0a0a;
  --fg-2:          #525252;
  --fg-3:          #a3a3a3;
  --fg-4:          #d4d4d4;
  --accent-subtle: #f0f0f0;
  --accent-border: #d4d4d4;
  --success:       #16a34a;
  --warning:       #d97706;
  --danger:        #dc2626;
  --info:          #2563eb;
}
```

Update the Semantic Color Usage table:

| Purpose | Token |
|:--------|:------|
| Page background | `bg-[var(--bg-base)]` |
| Card / panel surface | `bg-[var(--bg-surface)]` |
| Elevated surface | `bg-[var(--bg-elevated)]` |
| Hover state | `bg-[var(--bg-hover)]` |
| Primary text | `text-[var(--fg-1)]` |
| Secondary text | `text-[var(--fg-2)]` |
| Muted / label text | `text-[var(--fg-3)]` |
| Separator / disabled | `text-[var(--fg-4)]` |
| Border | `border-[var(--border)]` |
| Soft border | `border-[var(--border-soft)]` |
| Active item bg | `bg-[var(--accent-subtle)]` |
| Active item border | `border-[var(--accent-border)]` |
| Online / success | `text-[var(--success)]` |
| Warning | `text-[var(--warning)]` |
| Error / critical | `text-[var(--danger)]` |
| Info | `text-[var(--info)]` |

Remove the Violet Electric section and Gradients table entries for primary gradient. Keep chart-fill gradient.

- [ ] **Step 2: Update `frontend/design-system/theming/dark-mode.md`**

Replace the `## Strategy` section:

```markdown
## Strategy

- **Default:** System preference (`prefers-color-scheme`) — resolved on first load
- **User override:** Theme toggle button in Topbar (Sun / Moon / Monitor icon). Cycles: system → light → dark
- **Persistence:** `localStorage` key `theme` — values: `"system"` | `"light"` | `"dark"`
- **Attribute:** `data-theme="dark"` or `data-theme="light"` on `<html>` element
- **Dark is the hero mode:** The design is dark-first. Light mode is fully supported.
```

Replace the `## Implementation` → Root Layout section with:

```tsx
// src/components/ui/ThemeProvider.tsx
// Reads localStorage on mount, applies data-theme to <html>,
// tracks prefers-color-scheme when in "system" mode.
// Exposes useTheme() → { theme: 'dark' | 'light' | 'system', setTheme }

// src/main.tsx
<ThemeProvider>
  <App />
</ThemeProvider>
```

Replace the CSS variable blocks with the `[data-theme="dark"]` / `[data-theme="light"]` blocks from Task 7 Step 1 above.

Replace the `ThemeToggle` code example:

```tsx
function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const order = ['system', 'light', 'dark'] as const
  const cycle = () => setTheme(order[(order.indexOf(theme) + 1) % order.length])

  return (
    <button onClick={cycle} title={`Theme: ${theme}`}>
      {theme === 'dark' ? <Moon size={14} /> : theme === 'light' ? <Sun size={14} /> : <Monitor size={14} />}
    </button>
  )
}
```

- [ ] **Step 3: Update `frontend/design-system/patterns/navigation-patterns.md`**

In the `### Icon Rail` table, update:

| Property | Value |
|:---------|:------|
| Width | 64px |
| Surface | `bg-[var(--bg-surface)]` |
| Border | `border-r border-[var(--border)]` |
| Position | Flush left edge (`left-0`) |
| Active indicator | 4px neutral dot (`bg-[var(--fg-1)]`) below icon — visible only when active |
| Icon size | 16px (`size={16}`) |
| Active icon color | `text-[var(--fg-1)]` |
| Inactive icon color | `text-[var(--fg-3)]` |
| Hover | `text-[var(--fg-2)] bg-[var(--bg-hover)]` |

In the `### Expansion Panel` table, update:

| Property | Value |
|:---------|:------|
| Width | 220px |
| Surface | `bg-[var(--bg-surface)]` |
| Border | `border-r border-[var(--border)]` |
| Pillar header | Outfit 11px uppercase, `text-[var(--fg-3)]` |
| Sub-item font | Outfit 13px, `text-[var(--fg-3)]` |
| Active item | `bg-[var(--accent-subtle)] border border-[var(--accent-border)] text-[var(--fg-1)]` |
| Animation | `translateX` 200ms ease (unchanged) |

In the `## Topbar` section, update height to **48px** and add theme toggle row to the element table:

| Element | Position | Behavior |
|:--------|:---------|:---------|
| Theme Toggle | Right (before divider) | Sun/Moon/Monitor — cycles system→light→dark, persists to localStorage |

- [ ] **Step 4: Update `frontend/design-system/foundations/iconography.md`**

**Change 1:** In the Size Scale table, update the `md` row usage (line 17):

```markdown
| `md` | `h-5 w-5` | 20px | Stat card icons, page feature icons |
```

(Remove "Sidebar nav items" — nav rail now uses `sm` 16px.)

**Change 2:** Replace the entire `### Sidebar Nav Item` code example (lines 88–99):

```tsx
### Sidebar Nav Item
```tsx
// Icon rail — neutral active state, 16px icon
<button className={cn(
  'flex flex-col items-center justify-center py-3 rounded-lg transition-colors duration-150',
  isActive
    ? 'text-[var(--fg-1)]'
    : 'text-[var(--fg-3)] hover:text-[var(--fg-2)] hover:bg-[var(--bg-hover)]'
)}>
  <Users size={16} strokeWidth={isActive ? 2 : 1.75} />
  {isActive && <span className="mt-1.5 w-1 h-1 rounded-full bg-[var(--fg-1)]" />}
</button>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/design-system/foundations/color-tokens.md \
        frontend/design-system/theming/dark-mode.md \
        frontend/design-system/patterns/navigation-patterns.md \
        frontend/design-system/foundations/iconography.md
git commit -m "docs: update design system to neutral chrome token system"
```

---

### Task 8: Final Full Verification

- [ ] **Step 1: Run the dev server**

```bash
cd demo && npm run dev
```

Open `http://localhost:5173`.

- [ ] **Step 2: Verify all states**

Login as any persona, then check:

| Scenario | Expected |
|---|---|
| Dark mode (default) | Near-black bg, neutral rail + panel |
| Click theme toggle once | Light mode: off-white bg, white rail |
| Click twice | Dark mode again |
| Refresh | Theme persists |
| OS dark → light (if testable) | System mode tracks OS change |
| Click People pillar | Panel slides in, "PEOPLE" label shows, items listed |
| Click Employees | Active item: subtle bg + thin border, no violet |
| Click Home | Panel closes, Home icon active with small dot |
| Inbox count > 0 | White/black badge pill — no violet |
| Check all routes | Content area margins correct (not overlapping rail) |

- [ ] **Step 3: Build check**

```bash
cd demo && npm run build
```

Expected: build completes with no TypeScript errors.
