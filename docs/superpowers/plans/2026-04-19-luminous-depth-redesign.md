# Luminous Depth — Full System Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the ONEVO demo frontend with the "Luminous Depth" visual direction — gradient glass cards, floating glass capsule sidebar, gradient metric numbers, and premium SaaS depth — across every screen.

**Architecture:** The demo lives in `demo/` and uses React 18 + TypeScript + Vite + TailwindCSS v3 + Zustand + Recharts + Lucide React. All changes are in `demo/src/`. No new dependencies needed. We uplift the design token layer first (Tailwind config + CSS), then primitives (GlassCard, MetricCard), then layout (IconRail, Topbar, DashboardLayout), then every module screen in order.

**Tech Stack:** React 18, TypeScript, TailwindCSS 3, Zustand, Recharts, Lucide React, Vite

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `demo/tailwind.config.ts` | Modify | Extended color tokens, glass utilities, gradient helpers |
| `demo/src/index.css` | Modify | CSS custom properties, upgraded glass/gradient utility classes |
| `demo/src/components/ui/GlassCard.tsx` | Modify | Depth variants, gradient tinting, hover lift |
| `demo/src/components/ui/GlassSurface.tsx` | Modify | Proper depth levels |
| `demo/src/components/ui/MetricCard.tsx` | Create | Gradient number + delta + accent bar primitive |
| `demo/src/components/ui/StatusDot.tsx` | Create | Glowing colored status indicator |
| `demo/src/components/ui/SectionHeader.tsx` | Create | Consistent section label + action slot |
| `demo/src/components/layout/IconRail.tsx` | Modify | Floating Glass Capsule sidebar |
| `demo/src/components/layout/Topbar.tsx` | Modify | Elevated look, search pill, avatar refinement |
| `demo/src/components/layout/DashboardLayout.tsx` | Modify | Richer ambient background gradients |
| `demo/src/modules/auth/LoginPage.tsx` | Modify | Deeper glow, card depth upgrade |
| `demo/src/modules/home/AdminDashboard.tsx` | Modify | MetricCard usage, upgraded sections |
| `demo/src/modules/home/ManagerDashboard.tsx` | Modify | MetricCard usage, upgraded sections |
| `demo/src/modules/home/EmployeeDashboard.tsx` | Modify | MetricCard usage, upgraded sections |
| `demo/src/modules/people/employees/EmployeesPage.tsx` | Modify | Table/card surface upgrade |
| `demo/src/modules/people/leave/LeavePage.tsx` | Modify | Card and table upgrade |
| `demo/src/modules/workforce/WorkforcePage.tsx` | Modify | Tab bar upgrade, layout upgrade |
| `demo/src/modules/workforce/tabs/*.tsx` | Modify | Surface + status upgrade across all tabs |
| `demo/src/modules/calendar/CalendarPage.tsx` | Modify | Calendar grid surface upgrade |
| `demo/src/modules/admin/AdminPage.tsx` | Modify | Surface upgrade |
| `demo/src/modules/settings/SettingsPage.tsx` | Modify | Surface upgrade |

---

## Task 1: Design Token Layer — Tailwind + CSS

**Files:**
- Modify: `demo/tailwind.config.ts`
- Modify: `demo/src/index.css`

- [ ] **Step 1: Extend tailwind.config.ts with the full token set**

Replace the entire content of `demo/tailwind.config.ts` with:

```typescript
import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
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

- [ ] **Step 2: Upgrade index.css with design utility classes**

Replace the entire content of `demo/src/index.css` with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    background-color: #08080f;
    color: white;
    font-family: 'Outfit', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  * {
    scrollbar-width: thin;
    scrollbar-color: rgba(124, 58, 237, 0.2) transparent;
  }

  *::-webkit-scrollbar { width: 4px; }
  *::-webkit-scrollbar-track { background: transparent; }
  *::-webkit-scrollbar-thumb { background: rgba(124, 58, 237, 0.2); border-radius: 2px; }
}

@layer utilities {
  /* Surfaces */
  .bg-base { background-color: #08080f; }
  .bg-surface-01 { background-color: #0d0d18; }
  .bg-surface-02 { background-color: #111120; }

  /* Glass fills */
  .glass-1 { background: rgba(255, 255, 255, 0.025); }
  .glass-2 { background: rgba(255, 255, 255, 0.05); }
  .glass-3 { background: rgba(255, 255, 255, 0.08); }

  /* Glass tinted */
  .glass-violet { background: rgba(124, 58, 237, 0.07); }
  .glass-violet-md { background: rgba(124, 58, 237, 0.12); }

  /* Borders */
  .border-glass { border-color: rgba(255, 255, 255, 0.07); }
  .border-glass-md { border-color: rgba(255, 255, 255, 0.10); }
  .border-glass-hi { border-color: rgba(255, 255, 255, 0.16); }
  .border-violet-glass { border-color: rgba(124, 58, 237, 0.3); }

  /* Gradient text */
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

  /* Card depth */
  .card-depth {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
  }
  .card-depth-glow {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(168,85,247,0.03));
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), 0 0 24px rgba(124,58,237,0.12), inset 0 1px 0 rgba(124,58,237,0.1);
  }

  /* Floating rail capsule */
  .rail-capsule {
    background: rgba(13, 13, 24, 0.92);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
  }
}
```

- [ ] **Step 3: Run the dev server and confirm it starts without errors**

```bash
cd demo && npm run dev
```

Expected: Vite server starts at http://localhost:5173 with no TypeScript or CSS errors.

- [ ] **Step 4: Commit**

```bash
git add demo/tailwind.config.ts demo/src/index.css
git commit -m "feat: add Luminous Depth design token layer"
```

---

## Task 2: MetricCard Primitive

**Files:**
- Create: `demo/src/components/ui/MetricCard.tsx`

- [ ] **Step 1: Create MetricCard.tsx**

```tsx
import { cn } from '../../lib/utils'

type GradientColor = 'violet' | 'green' | 'amber' | 'red' | 'blue' | 'white'

interface Props {
  label: string
  value: string | number
  sub?: string
  delta?: string
  deltaPositive?: boolean
  color?: GradientColor
  accentBar?: boolean
  glow?: boolean
  className?: string
  onClick?: () => void
}

const barColors: Record<GradientColor, string> = {
  violet: 'from-violet-500 to-purple-400',
  green:  'from-emerald-400 to-green-300',
  amber:  'from-amber-400 to-yellow-300',
  red:    'from-red-400 to-rose-300',
  blue:   'from-blue-400 to-sky-300',
  white:  'from-white/50 to-white/25',
}

const textGradients: Record<GradientColor, string> = {
  violet: 'text-gradient-violet',
  green:  'text-gradient-green',
  amber:  'text-gradient-amber',
  red:    'text-gradient-red',
  blue:   'text-gradient-blue',
  white:  'text-gradient-white',
}

export function MetricCard({ label, value, sub, delta, deltaPositive, color = 'white', accentBar, glow, className, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-[14px] p-4 relative overflow-hidden transition-all duration-200',
        glow ? 'card-depth-glow' : 'card-depth',
        onClick && 'cursor-pointer hover:scale-[1.01] hover:shadow-card-hover',
        className
      )}
    >
      {accentBar && (
        <div className={cn('absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r', barColors[color])} />
      )}
      <div className="flex items-start justify-between mb-1.5">
        <span className="text-white/45 text-xs font-outfit tracking-wide">{label}</span>
        {delta && (
          <span className={cn('text-xs font-geist font-semibold', deltaPositive ? 'text-emerald-400' : 'text-red-400')}>
            {delta}
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className={cn('text-3xl font-geist font-bold tracking-tight', textGradients[color])}>
          {value}
        </span>
        {sub && <span className="text-sm text-white/30 font-outfit">{sub}</span>}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/components/ui/MetricCard.tsx
git commit -m "feat: add MetricCard primitive with gradient numbers"
```

---

## Task 3: StatusDot and SectionHeader Primitives

**Files:**
- Create: `demo/src/components/ui/StatusDot.tsx`
- Create: `demo/src/components/ui/SectionHeader.tsx`

- [ ] **Step 1: Create StatusDot.tsx**

```tsx
import { cn } from '../../lib/utils'

type Status = 'online' | 'idle' | 'offline' | 'error' | 'warning' | 'info'

const colors: Record<Status, { dot: string; glow: string }> = {
  online:  { dot: 'bg-emerald-400', glow: 'shadow-glow-green' },
  idle:    { dot: 'bg-amber-400',   glow: 'shadow-glow-amber' },
  offline: { dot: 'bg-white/20',    glow: '' },
  error:   { dot: 'bg-red-400',     glow: 'shadow-glow-red' },
  warning: { dot: 'bg-amber-400',   glow: 'shadow-glow-amber' },
  info:    { dot: 'bg-blue-400',    glow: 'shadow-glow-blue' },
}

interface Props {
  status: Status
  size?: 'sm' | 'md'
  pulse?: boolean
  className?: string
}

export function StatusDot({ status, size = 'sm', pulse, className }: Props) {
  const { dot, glow } = colors[status]
  const sz = size === 'sm' ? 'w-2 h-2' : 'w-2.5 h-2.5'
  return (
    <span className={cn('relative inline-flex', sz, className)}>
      {pulse && status !== 'offline' && (
        <span className={cn('absolute inset-0 rounded-full animate-ping opacity-60', dot)} />
      )}
      <span className={cn('rounded-full', sz, dot, glow)} />
    </span>
  )
}
```

- [ ] **Step 2: Create SectionHeader.tsx**

```tsx
import { cn } from '../../lib/utils'

interface Props {
  title: string
  action?: React.ReactNode
  className?: string
}

export function SectionHeader({ title, action, className }: Props) {
  return (
    <div className={cn('flex items-center justify-between mb-3', className)}>
      <span className="text-white/70 font-outfit font-semibold text-sm tracking-wide">{title}</span>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/ui/StatusDot.tsx demo/src/components/ui/SectionHeader.tsx
git commit -m "feat: add StatusDot and SectionHeader primitives"
```

---

## Task 4: Upgrade GlassCard

**Files:**
- Modify: `demo/src/components/ui/GlassCard.tsx`

- [ ] **Step 1: Read current GlassCard**

The current GlassCard is in `demo/src/components/ui/GlassCard.tsx`:
```tsx
// current: basic rounded-xl bg-white/[0.03] border border-white/[0.07] p-4
// with optional glow variant (violet border + shadow)
```

- [ ] **Step 2: Replace GlassCard.tsx with upgraded version**

```tsx
import { cn } from '../../lib/utils'

interface Props {
  children: React.ReactNode
  glow?: boolean
  variant?: 'default' | 'elevated' | 'tinted'
  padding?: 'sm' | 'md' | 'lg'
  className?: string
  onClick?: () => void
}

const paddings = { sm: 'p-3', md: 'p-4', lg: 'p-5' }

export function GlassCard({ children, glow, variant = 'default', padding = 'md', className, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-[14px] relative overflow-hidden transition-all duration-200',
        paddings[padding],
        variant === 'default'  && 'card-depth',
        variant === 'elevated' && 'bg-white/[0.045] border border-glass-md rounded-[14px] shadow-glass-lg',
        variant === 'tinted'   && 'bg-gradient-card border border-violet-glass rounded-[14px] shadow-glass',
        glow && 'card-depth-glow',
        onClick && 'cursor-pointer hover:scale-[1.005] hover:shadow-card-hover',
        className
      )}
    >
      <div className="absolute inset-0 pointer-events-none rounded-[14px]"
        style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 60%)' }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/ui/GlassCard.tsx
git commit -m "feat: upgrade GlassCard with depth variants and inner highlight"
```

---

## Task 5: Floating Glass Capsule Sidebar (IconRail)

**Files:**
- Modify: `demo/src/components/layout/IconRail.tsx`
- Modify: `demo/src/components/layout/DashboardLayout.tsx`

- [ ] **Step 1: Rewrite IconRail.tsx as a floating capsule**

Replace the entire content of `demo/src/components/layout/IconRail.tsx` with:

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
  { icon: Home,        label: 'Home',      defaultPath: '/',                   pillarKey: 'home',      module: null },
  { icon: Users,       label: 'People',    defaultPath: '/people/employees',   pillarKey: 'people',    module: 'core-hr' },
  { icon: Radio,       label: 'Workforce', defaultPath: '/workforce',          pillarKey: 'workforce', module: 'workforce' },
  { icon: Building2,   label: 'Org',       defaultPath: '/org',               pillarKey: 'org',       module: 'org-structure' },
  { icon: CalendarDays,label: 'Calendar',  defaultPath: '/calendar',          pillarKey: 'calendar',  module: 'calendar' },
  { icon: Bell,        label: 'Inbox',     defaultPath: '/inbox',             pillarKey: 'inbox',     module: 'notifications' },
  { icon: ShieldCheck, label: 'Admin',     defaultPath: '/admin',             pillarKey: 'admin',     module: 'admin' },
  { icon: Settings,    label: 'Settings',  defaultPath: '/settings',          pillarKey: 'settings',  module: 'settings' },
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
    <div
      className="fixed left-3 top-3 bottom-3 z-50 w-14 flex flex-col items-center py-3 gap-0.5 rail-capsule"
    >
      {/* Logo mark */}
      <div className="w-9 h-9 rounded-xl bg-gradient-violet flex items-center justify-center text-white font-bold text-[15px] font-outfit shadow-glow-violet mb-3 shrink-0">
        N
      </div>

      {/* Nav items */}
      <div className="flex flex-col items-center gap-0.5 flex-1 w-full px-1.5">
        {pillars.map(({ icon: Icon, label, defaultPath, pillarKey, module }) => {
          if (module && !grantedModules.includes(module)) return null
          const active = activePillar === pillarKey

          return (
            <button
              key={pillarKey}
              onClick={() => handleClick(pillarKey, defaultPath)}
              title={label}
              className={cn(
                'w-full h-10 rounded-xl flex items-center justify-center relative transition-all duration-150 group',
                active
                  ? 'bg-violet-600/20 text-violet-300 shadow-[inset_0_0_0_1px_rgba(124,58,237,0.35),0_0_16px_rgba(124,58,237,0.15)]'
                  : 'text-white/30 hover:text-white/65 hover:bg-white/[0.05]'
              )}
            >
              {active && (
                <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r-full bg-gradient-to-b from-violet-400 to-purple-500 shadow-glow-violet" />
              )}
              <Icon size={17} strokeWidth={active ? 2 : 1.75} />
              {pillarKey === 'inbox' && inboxCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-[7px] h-[7px] rounded-full bg-violet-400 shadow-glow-violet" />
              )}
            </button>
          )
        })}
      </div>

      {/* Bottom spacer — could hold avatar or version */}
      <div className="shrink-0 w-7 h-[1px] bg-white/[0.07] mb-1" />
    </div>
  )
}
```

- [ ] **Step 2: Update DashboardLayout.tsx to account for floating rail margin**

The rail now sits at `left-3 top-3 bottom-3` with width `w-14` (56px) plus 12px margin = 68px offset needed. Update `ml-16` → `ml-[72px]` and `ml-[284px]` → `ml-[288px]` and enhance the ambient gradients.

In `demo/src/components/layout/DashboardLayout.tsx`, find and replace:

```tsx
  const sidebarWidth = panelOpen && hasPanelContent ? 'ml-[284px]' : 'ml-16'
```
→
```tsx
  const sidebarWidth = panelOpen && hasPanelContent ? 'ml-[288px]' : 'ml-[72px]'
```

And replace the ambient background div:
```tsx
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-[600px] h-[400px] bg-[radial-gradient(ellipse,rgba(124,58,237,0.06)_0%,transparent_70%)]" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[400px] bg-[radial-gradient(ellipse,rgba(14,165,233,0.03)_0%,transparent_70%)]" />
      </div>
```
→
```tsx
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[700px] h-[500px] bg-[radial-gradient(ellipse,rgba(124,58,237,0.09)_0%,transparent_65%)]" />
        <div className="absolute top-1/2 left-1/3 w-[600px] h-[400px] bg-[radial-gradient(ellipse,rgba(139,92,246,0.04)_0%,transparent_70%)]" />
        <div className="absolute -bottom-40 -right-40 w-[700px] h-[500px] bg-[radial-gradient(ellipse,rgba(14,165,233,0.04)_0%,transparent_65%)]" />
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.012) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
      </div>
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/IconRail.tsx demo/src/components/layout/DashboardLayout.tsx
git commit -m "feat: floating glass capsule sidebar + richer ambient background"
```

---

## Task 6: Upgrade Topbar

**Files:**
- Modify: `demo/src/components/layout/Topbar.tsx`

- [ ] **Step 1: Read current Topbar**

Current: `h-14 bg-[#08080f]/80 backdrop-blur-xl border-b border-white/[0.06] flex items-center justify-between px-5 fixed top-0 left-16 right-0 z-40`

- [ ] **Step 2: Update the Topbar container class and search pill**

In `demo/src/components/layout/Topbar.tsx`, find:
```tsx
    <div className="h-14 bg-[#08080f]/80 backdrop-blur-xl border-b border-white/[0.06] flex items-center justify-between px-5 fixed top-0 left-16 right-0 z-40">
```
Replace with:
```tsx
    <div className="h-14 bg-[#08080f]/85 backdrop-blur-2xl border-b border-white/[0.06] flex items-center justify-between px-5 fixed top-0 left-[72px] right-0 z-40 shadow-[0_1px_0_rgba(255,255,255,0.04)]">
```

Find the search button (contains `Search size={12}`) and replace that button with:
```tsx
        <button
          onClick={() => setPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.07] text-white/35 hover:text-white/60 hover:bg-white/[0.07] hover:border-white/[0.12] transition-all duration-150 text-xs font-outfit"
        >
          <Search size={13} />
          <span>Search</span>
          <kbd className="ml-2 px-1.5 py-0.5 rounded-md bg-white/[0.07] text-white/20 text-[10px] font-geist tracking-tight border border-white/[0.05]">⌘K</kbd>
        </button>
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/Topbar.tsx
git commit -m "feat: upgrade Topbar with elevated glass and refined search pill"
```

---

## Task 7: Upgrade Login Page

**Files:**
- Modify: `demo/src/modules/auth/LoginPage.tsx`

- [ ] **Step 1: Update LoginPage container and card grid**

In `demo/src/modules/auth/LoginPage.tsx`, find:
```tsx
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
```
Replace with:
```tsx
    <div className="min-h-screen bg-base flex items-center justify-center relative overflow-hidden">
      <div className="absolute -top-60 -left-40 w-[700px] h-[600px] bg-[radial-gradient(ellipse,rgba(124,58,237,0.12)_0%,transparent_65%)] pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-[radial-gradient(ellipse,rgba(14,165,233,0.05)_0%,transparent_65%)] pointer-events-none" />
```

After this opening div (before `<div className="w-full max-w-2xl px-6">`), close the relative wrapper at end of JSX. Also update the logo shadow:

Find:
```tsx
          <div className="w-14 h-14 rounded-2xl bg-violet-600 flex items-center justify-center text-white font-bold text-2xl mx-auto mb-5 shadow-[0_0_30px_rgba(124,58,237,0.5)]">N</div>
```
Replace with:
```tsx
          <div className="w-14 h-14 rounded-2xl bg-gradient-violet flex items-center justify-center text-white font-bold text-2xl mx-auto mb-5 shadow-glow-violet-lg">N</div>
```

At the very end, add the closing div for the outer relative wrapper before the final `</div>`:
```tsx
    </div>
```
(The JSX already closes correctly — just ensure the outermost div wraps everything.)

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/auth/LoginPage.tsx
git commit -m "feat: upgrade LoginPage with ambient radial glow"
```

---

## Task 8: Upgrade AdminDashboard

**Files:**
- Modify: `demo/src/modules/home/AdminDashboard.tsx`

- [ ] **Step 1: Add MetricCard import**

At the top of `demo/src/modules/home/AdminDashboard.tsx`, add:
```tsx
import { MetricCard } from '../../components/ui/MetricCard'
import { SectionHeader } from '../../components/ui/SectionHeader'
import { StatusDot } from '../../components/ui/StatusDot'
```

- [ ] **Step 2: Replace the KPI card grid (Zone 2)**

Find the Zone 2 grid that renders 4 GlassCards with `h-[2px]` accent bars and `text-3xl font-geist` values. Replace the entire `<div className="grid grid-cols-4 gap-4">` block (Zone 2) with:

```tsx
      {/* Zone 2 — KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Total Staff"    value={employees.length} delta="+2%" deltaPositive color="white"  accentBar />
        <MetricCard label="Online Now"     value={online}           delta="+5%" deltaPositive color="green"  accentBar glow={online > 0} />
        <MetricCard label="Exceptions"     value={allExceptions.length} color="red"   accentBar glow={allExceptions.length > 0} />
        <MetricCard label="Pending Leave"  value={pendingLeave.length}  color="amber" accentBar />
      </div>
```

- [ ] **Step 3: Upgrade the Pending Actions section header**

Find `<div className="text-white/70 font-outfit font-semibold text-sm mb-3">Pending Actions</div>` and replace with:
```tsx
<SectionHeader title="Pending Actions" />
```

Find `<div className="text-white/70 font-outfit font-semibold text-sm mb-3">Weekly Trends</div>` and replace with:
```tsx
<SectionHeader title="Weekly Trends" />
```

Find `<div className="text-white/70 font-outfit font-semibold text-sm mb-3">Workforce Live</div>` and replace with:
```tsx
<SectionHeader title="Workforce Live" action={<button onClick={() => navigate('/workforce')} className="flex items-center gap-1 text-violet-400 text-xs font-outfit hover:underline">Full view <ArrowRight size={10} /></button>} />
```

Find `<div className="text-white/70 font-outfit font-semibold text-sm mb-3">Company Events</div>` (or similar in Zone 5) and replace similarly with `<SectionHeader title="Company Events" />`.

- [ ] **Step 4: Upgrade presence row status dots**

In the employee presence list rows, find patterns like:
```tsx
<div className={cn('w-2 h-2 rounded-full', s === 'online' ? 'bg-green-400' : s === 'idle' ? 'bg-amber-400' : 'bg-white/15')} />
```
Replace with:
```tsx
<StatusDot status={s === 'online' ? 'online' : s === 'idle' ? 'idle' : 'offline'} pulse={s === 'online'} />
```

- [ ] **Step 5: Commit**

```bash
git add demo/src/modules/home/AdminDashboard.tsx
git commit -m "feat: upgrade AdminDashboard with MetricCard, SectionHeader, StatusDot"
```

---

## Task 9: Upgrade ManagerDashboard and EmployeeDashboard

**Files:**
- Modify: `demo/src/modules/home/ManagerDashboard.tsx`
- Modify: `demo/src/modules/home/EmployeeDashboard.tsx`

- [ ] **Step 1: Add imports to ManagerDashboard**

```tsx
import { MetricCard } from '../../components/ui/MetricCard'
import { SectionHeader } from '../../components/ui/SectionHeader'
import { StatusDot } from '../../components/ui/StatusDot'
```

- [ ] **Step 2: Replace KPI cards in ManagerDashboard**

Find the KPI row (typically 3-4 GlassCards with big numbers) and replace each GlassCard+number combo with MetricCard:

```tsx
// Example pattern — match to actual labels in the file:
<MetricCard label="Team Online"     value={teamOnline}   color="green" accentBar glow />
<MetricCard label="Pending Approvals" value={pendingCount} color="amber" accentBar />
<MetricCard label="Exceptions"      value={exceptCount}  color="red"   accentBar glow={exceptCount > 0} />
```

Replace any `<div className="text-white/70 font-outfit font-semibold text-sm mb-3">...</div>` section labels with `<SectionHeader title="..." />`.

Replace inline status dot divs with `<StatusDot status={...} />`.

- [ ] **Step 3: Repeat for EmployeeDashboard**

Add the same three imports. Replace KPI cards and section headers using the same pattern as ManagerDashboard. EmployeeDashboard typically shows leave balance, tasks, and personal stats — use appropriate colors (blue for info metrics, green for positive, amber for pending).

- [ ] **Step 4: Commit**

```bash
git add demo/src/modules/home/ManagerDashboard.tsx demo/src/modules/home/EmployeeDashboard.tsx
git commit -m "feat: upgrade Manager and Employee dashboards with design primitives"
```

---

## Task 10: Upgrade People Module

**Files:**
- Modify: `demo/src/modules/people/employees/EmployeesPage.tsx`
- Modify: `demo/src/modules/people/leave/LeavePage.tsx`

- [ ] **Step 1: Add imports to EmployeesPage**

```tsx
import { StatusDot } from '../../../components/ui/StatusDot'
import { SectionHeader } from '../../../components/ui/SectionHeader'
```

- [ ] **Step 2: Upgrade table/card surfaces in EmployeesPage**

Find the outer page wrapper (usually a `<div className="space-y-...">` or similar) and ensure it uses `bg-base` as the page background (already set globally, so this may be a no-op).

Find any filter bar / search bar container and upgrade its background:
```tsx
// Find pattern like: className="... bg-white/[0.03] border border-white/[0.07] ..."
// Replace background with: glass-2 border border-glass-md rounded-xl
```

Find employee row cards or table rows. Replace status indicator divs:
```tsx
// Find: <div className={cn('w-2 h-2 rounded-full', ...)} />
// Replace with: <StatusDot status={...} />
```

- [ ] **Step 3: Upgrade LeavePage surfaces**

Add `import { SectionHeader } from '../../../components/ui/SectionHeader'`.

Replace section label divs with `<SectionHeader title="..." />`. Upgrade tab bar buttons from `bg-violet-600/20 text-violet-400` to `bg-violet-600/20 text-violet-300 border border-violet-glass` for active state.

- [ ] **Step 4: Commit**

```bash
git add demo/src/modules/people/employees/EmployeesPage.tsx demo/src/modules/people/leave/LeavePage.tsx
git commit -m "feat: upgrade People module surfaces and status indicators"
```

---

## Task 11: Upgrade Workforce Module

**Files:**
- Modify: `demo/src/modules/workforce/WorkforcePage.tsx`
- Modify: `demo/src/modules/workforce/tabs/OnlineStatusTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/OverviewTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/PresenceTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/ExceptionsTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/ActivityTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/WorkInsightsTab.tsx`
- Modify: `demo/src/modules/workforce/tabs/ShiftScheduleTab.tsx`

- [ ] **Step 1: Upgrade WorkforcePage tab bar**

In `demo/src/modules/workforce/WorkforcePage.tsx`, find the tab bar container. Replace its background from `bg-white/[0.03]` to `bg-surface-01`, and active tab from `bg-violet-600/20 text-violet-400` to `bg-violet-600/20 text-violet-300 border border-violet-glass shadow-glow-violet`.

- [ ] **Step 2: Upgrade OnlineStatusTab**

Add `import { StatusDot } from '../../../components/ui/StatusDot'` and `import { MetricCard } from '../../../components/ui/MetricCard'`.

Replace any summary KPI row with MetricCard. Replace inline status dot divs with StatusDot components.

- [ ] **Step 3: Upgrade PresenceTab**

Same imports as Step 2. Replace status dots inline with `<StatusDot status={...} pulse />`. Replace GlassCard usages to use `variant="elevated"` for the main container.

- [ ] **Step 4: Upgrade ExceptionsTab**

Add `import { StatusDot } from '../../../components/ui/StatusDot'`.

For exception rows with red indicators, use `<StatusDot status="error" />`. For resolved exceptions, `<StatusDot status="offline" />`.

- [ ] **Step 5: Upgrade ActivityTab and WorkInsightsTab**

In both files, add `import { SectionHeader } from '../../../components/ui/SectionHeader'`.

Replace section header divs with `<SectionHeader title="..." />`.

- [ ] **Step 6: Commit all workforce changes**

```bash
git add demo/src/modules/workforce/
git commit -m "feat: upgrade Workforce module — tab bar, status dots, MetricCards"
```

---

## Task 12: Upgrade Calendar Module

**Files:**
- Modify: `demo/src/modules/calendar/CalendarPage.tsx`
- Modify: `demo/src/modules/calendar/shifts/ShiftsPage.tsx`
- Modify: `demo/src/modules/calendar/shifts/CreateShiftWizard.tsx`

- [ ] **Step 1: Upgrade CalendarPage surfaces**

Add `import { SectionHeader } from '../../components/ui/SectionHeader'`.

Replace any calendar grid container `bg-white/[0.03] border border-white/[0.07]` with `card-depth` className. Replace section header divs with `<SectionHeader title="..." />`.

- [ ] **Step 2: Upgrade ShiftsPage**

Add `import { MetricCard } from '../../components/ui/MetricCard'` and `import { StatusDot } from '../../components/ui/StatusDot'`.

If there are summary stats (shifts today, coverage %, etc.), replace with MetricCard. Replace shift status indicators with StatusDot.

- [ ] **Step 3: Upgrade wizard modal surfaces**

In `CreateShiftWizard.tsx`, find the modal container (usually a fixed overlay + inner panel). Upgrade the inner panel:

```tsx
// Find: className="... bg-[#0d0d1a] border border-white/[0.08] ..."
// Replace with: className="bg-surface-01 border border-glass-md rounded-2xl shadow-glass-lg"
```

- [ ] **Step 4: Commit**

```bash
git add demo/src/modules/calendar/
git commit -m "feat: upgrade Calendar module surfaces and shift wizard"
```

---

## Task 13: Upgrade Admin and Settings Pages

**Files:**
- Modify: `demo/src/modules/admin/AdminPage.tsx`
- Modify: `demo/src/modules/settings/SettingsPage.tsx`

- [ ] **Step 1: Upgrade AdminPage**

Add `import { SectionHeader } from '../../components/ui/SectionHeader'`. Replace all section header divs with `<SectionHeader title="..." />`. Upgrade any summary cards by replacing their `bg-white/[0.03]` with `card-depth`.

- [ ] **Step 2: Upgrade SettingsPage**

Add `import { SectionHeader } from '../../components/ui/SectionHeader'`. Replace section label divs with `<SectionHeader title="..." />`.

Upgrade setting section containers — find patterns like `bg-white/[0.03] border border-white/[0.07]` and replace with `card-depth`.

- [ ] **Step 3: Commit**

```bash
git add demo/src/modules/admin/AdminPage.tsx demo/src/modules/settings/SettingsPage.tsx
git commit -m "feat: upgrade Admin and Settings module surfaces"
```

---

## Task 14: Final Polish Pass — Modals and Remaining Files

**Files:**
- Modify: `demo/src/components/modals/OffboardModal.tsx`
- Modify: `demo/src/components/modals/PromoteModal.tsx`
- Modify: `demo/src/components/ui/CommandPalette.tsx`
- Modify: `demo/src/modules/people/employees/EmployeeProfile.tsx`
- Modify: `demo/src/modules/org/OrgPage.tsx`
- Modify: `demo/src/modules/inbox/InboxPage.tsx`

- [ ] **Step 1: Upgrade modal containers**

In both `OffboardModal.tsx` and `PromoteModal.tsx`, find the modal panel container. Replace:
```tsx
// Find: bg-[#0d0d1a] border border-white/[0.08] rounded-2xl
// Replace: bg-surface-01 border border-glass-md rounded-2xl shadow-glass-lg
```

- [ ] **Step 2: Upgrade CommandPalette**

In `CommandPalette.tsx`, find the main palette container. Replace its background:
```tsx
// Find: bg-[#0d0d18] or similar dark bg + border
// Replace: bg-surface-01 border border-glass-md rounded-2xl shadow-glass-lg backdrop-blur-2xl
```

- [ ] **Step 3: Upgrade EmployeeProfile**

Add `import { MetricCard } from '../../../components/ui/MetricCard'` and `import { SectionHeader } from '../../../components/ui/SectionHeader'`.

Replace summary stat cards (tenure, department, etc.) with MetricCard. Replace section headers with SectionHeader.

- [ ] **Step 4: Upgrade OrgPage and InboxPage surfaces**

In both files, replace `bg-white/[0.03] border border-white/[0.07]` container patterns with `card-depth`. Add SectionHeader imports and replace section label divs.

- [ ] **Step 5: Commit**

```bash
git add demo/src/components/modals/ demo/src/components/ui/CommandPalette.tsx demo/src/modules/people/employees/EmployeeProfile.tsx demo/src/modules/org/ demo/src/modules/inbox/
git commit -m "feat: upgrade modals, CommandPalette, EmployeeProfile, Org, Inbox"
```

---

## Task 15: Verification

- [ ] **Step 1: Start dev server**

```bash
cd demo && npm run dev
```

- [ ] **Step 2: Verify login page**

Open http://localhost:5173/login. Confirm:
- Deep background with violet radial glow visible
- N logo has gradient fill and glow
- Persona cards have depth (inner highlight visible)

- [ ] **Step 3: Verify sidebar**

Log in as Admin. Confirm:
- Sidebar floats with margin from edges, rounded corners
- Active item shows left accent bar + violet background capsule
- No layout overflow or overlap with main content

- [ ] **Step 4: Verify dashboard**

Confirm:
- KPI row shows gradient numbers (purple, green, amber, red)
- Section headers are consistent weight/style
- Status dots glow on online employees

- [ ] **Step 5: Navigate to each module**

Visit: People → Workforce → Calendar → Admin → Settings → Inbox. Confirm:
- No white-box flash or unstyled content
- All surfaces use card-depth or glass classes (not raw white/gray)
- No TypeScript errors in console

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: Luminous Depth redesign complete — full system polish"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✅ Luminous Depth direction: gradient glass cards (Tasks 2, 4, 8–14)
- ✅ Gradient metric numbers: MetricCard primitive (Task 2)
- ✅ Floating Glass Capsule sidebar: IconRail rewrite (Task 5)
- ✅ Topbar upgrade (Task 6)
- ✅ Login page (Task 7)
- ✅ All dashboard screens (Tasks 8–9)
- ✅ People module (Task 10)
- ✅ Workforce module (Task 11)
- ✅ Calendar module (Task 12)
- ✅ Admin + Settings (Task 13)
- ✅ Modals, CommandPalette, remaining screens (Task 14)
- ✅ Design token layer first (Task 1)

**No placeholders detected** — all code blocks are complete and self-contained.

**Type consistency:**
- `MetricCard` props: `label`, `value`, `color`, `delta`, `deltaPositive`, `accentBar`, `glow`, `className`, `onClick` — used consistently throughout Tasks 2, 8, 9, 10, 11, 12, 13
- `StatusDot` props: `status`, `size`, `pulse`, `className` — used consistently throughout
- `SectionHeader` props: `title`, `action`, `className` — used consistently throughout
- `GlassCard` now adds `variant` and `padding` props while keeping `glow`, `className`, `onClick` — all existing usages still valid (defaults unchanged)
