# Dashboard Home Screen — Color Discipline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restrict status colors on the home dashboard (`/`) to red (critical) and amber (warning) only — all other status colors collapse to zinc — and make all home screen charts use violet shades exclusively.

**Architecture:** A `DashboardColorContext` React context provides a `minimal: boolean` flag. The home page wraps its content in `DashboardColorProvider` (which sets `minimal: true`). Each affected component reads this context and swaps status colors to zinc when minimal mode is active. Global tokens and all other pages are untouched.

**Tech Stack:** Next.js 14+ App Router, React, TypeScript, Tailwind CSS, Recharts, Vitest + React Testing Library

**Spec:** `docs/superpowers/specs/2026-04-18-dashboard-home-color-discipline-design.md`

---

## File Map

| Action | Path | Responsibility |
|:-------|:-----|:---------------|
| Create | `app/(dashboard)/components/home/DashboardColorContext.tsx` | Context + provider + hook |
| Modify | `app/(dashboard)/page.tsx` | Wrap content in `DashboardColorProvider` |
| Modify | `app/(dashboard)/components/home/AlertsPanel.tsx` | Zinc border/dot for info + partial severity |
| Modify | `app/(dashboard)/components/home/ActivityFeed.tsx` | All action icons → zinc |
| Modify | `app/(dashboard)/components/home/KPICard.tsx` | Remove green/cyan coloring from secondary KPIs |
| Modify | `app/(dashboard)/components/home/AttendanceChart.tsx` | Violet-only series palette |
| Modify | `app/(dashboard)/components/home/DepartmentChart.tsx` | Violet shades for ring chart |
| Create | `app/(dashboard)/components/home/__tests__/DashboardColorContext.test.tsx` | Context unit tests |
| Create | `app/(dashboard)/components/home/__tests__/AlertsPanel.test.tsx` | Alert color tests |
| Create | `app/(dashboard)/components/home/__tests__/ActivityFeed.test.tsx` | Feed icon color tests |
| Create | `app/(dashboard)/components/home/__tests__/KPICard.test.tsx` | KPI color tests |

---

## Task 1: Create DashboardColorContext

**Files:**
- Create: `app/(dashboard)/components/home/DashboardColorContext.tsx`
- Create: `app/(dashboard)/components/home/__tests__/DashboardColorContext.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// app/(dashboard)/components/home/__tests__/DashboardColorContext.test.tsx
import { render, screen } from '@testing-library/react'
import { DashboardColorProvider, useDashboardColor } from '../DashboardColorContext'

function TestConsumer() {
  const { minimal } = useDashboardColor()
  return <div data-testid="flag">{minimal ? 'minimal' : 'full'}</div>
}

describe('DashboardColorContext', () => {
  it('defaults to full color mode outside provider', () => {
    render(<TestConsumer />)
    expect(screen.getByTestId('flag')).toHaveTextContent('full')
  })

  it('provides minimal=true inside DashboardColorProvider', () => {
    render(
      <DashboardColorProvider>
        <TestConsumer />
      </DashboardColorProvider>
    )
    expect(screen.getByTestId('flag')).toHaveTextContent('minimal')
  })
})
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/DashboardColorContext.test.tsx
```

Expected: FAIL — `DashboardColorContext` not found.

- [ ] **Step 3: Implement the context**

```tsx
// app/(dashboard)/components/home/DashboardColorContext.tsx
'use client'

import { createContext, useContext } from 'react'

interface DashboardColorContextValue {
  minimal: boolean
}

const DashboardColorContext = createContext<DashboardColorContextValue>({ minimal: false })

export function DashboardColorProvider({ children }: { children: React.ReactNode }) {
  return (
    <DashboardColorContext.Provider value={{ minimal: true }}>
      {children}
    </DashboardColorContext.Provider>
  )
}

export function useDashboardColor(): DashboardColorContextValue {
  return useContext(DashboardColorContext)
}
```

- [ ] **Step 4: Run the test to confirm it passes**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/DashboardColorContext.test.tsx
```

Expected: PASS — 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/\(dashboard\)/components/home/DashboardColorContext.tsx \
        app/\(dashboard\)/components/home/__tests__/DashboardColorContext.test.tsx
git commit -m "feat: add DashboardColorContext for home screen minimal color mode"
```

---

## Task 2: Wrap Home Page with Provider

**Files:**
- Modify: `app/(dashboard)/page.tsx`

The home page is a Server Component. `DashboardColorProvider` is a Client Component. Wrap only the rendered output — not the data fetching.

- [ ] **Step 1: Open `app/(dashboard)/page.tsx` and locate the return statement**

Find the outermost JSX element returned by the page component. It will look something like:

```tsx
export default async function DashboardPage() {
  // ... data fetching ...
  return (
    <main className="...">
      {/* dashboard sections */}
    </main>
  )
}
```

- [ ] **Step 2: Wrap the return with DashboardColorProvider**

```tsx
import { DashboardColorProvider } from './components/home/DashboardColorContext'

export default async function DashboardPage() {
  // ... data fetching unchanged ...
  return (
    <DashboardColorProvider>
      <main className="...">
        {/* dashboard sections — unchanged */}
      </main>
    </DashboardColorProvider>
  )
}
```

- [ ] **Step 3: Verify dev server starts without errors**

```bash
npx next dev
```

Open `http://localhost:3000`. Confirm the dashboard home loads. No visual change yet — context is wired but no components read it.

- [ ] **Step 4: Commit**

```bash
git add app/\(dashboard\)/page.tsx
git commit -m "feat: wrap dashboard home in DashboardColorProvider"
```

---

## Task 3: AlertsPanel — Zinc for Info and Partial Severity

**Files:**
- Modify: `app/(dashboard)/components/home/AlertsPanel.tsx`
- Create: `app/(dashboard)/components/home/__tests__/AlertsPanel.test.tsx`

**Severity color rules (final):**
| Severity | Border | Dot | Text |
|:---------|:-------|:----|:-----|
| `critical` | `border-l-[#ef4444]` | `bg-[#ef4444]` | `text-foreground` |
| `warning` | `border-l-[#f59e0b]` | `bg-[#f59e0b]` | `text-foreground` |
| `info` (minimal) | `border-l-zinc-700` | `bg-zinc-600` | `text-muted-foreground` |
| `partial` (minimal) | `border-l-zinc-700` | `bg-zinc-600` | `text-muted-foreground` |

- [ ] **Step 1: Write the failing tests**

```tsx
// app/(dashboard)/components/home/__tests__/AlertsPanel.test.tsx
import { render, screen } from '@testing-library/react'
import { DashboardColorProvider } from '../DashboardColorContext'
import { AlertItem } from '../AlertsPanel'

function wrap(ui: React.ReactNode) {
  return render(<DashboardColorProvider>{ui}</DashboardColorProvider>)
}

describe('AlertItem in minimal color mode', () => {
  it('keeps red border for critical severity', () => {
    wrap(<AlertItem severity="critical" message="Visa expiring" />)
    const item = screen.getByRole('listitem')
    expect(item.className).toContain('border-l-[#ef4444]')
  })

  it('keeps amber border for warning severity', () => {
    wrap(<AlertItem severity="warning" message="Leave pending" />)
    const item = screen.getByRole('listitem')
    expect(item.className).toContain('border-l-[#f59e0b]')
  })

  it('uses zinc border for info severity in minimal mode', () => {
    wrap(<AlertItem severity="info" message="Contract review" />)
    const item = screen.getByRole('listitem')
    expect(item.className).toContain('border-l-zinc-700')
    expect(item.className).not.toContain('border-l-[#06b6d4]')
  })

  it('uses zinc border for partial severity in minimal mode', () => {
    wrap(<AlertItem severity="partial" message="Partial attendance" />)
    const item = screen.getByRole('listitem')
    expect(item.className).toContain('border-l-zinc-700')
    expect(item.className).not.toContain('border-l-[#f97316]')
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/AlertsPanel.test.tsx
```

Expected: FAIL — `AlertItem` not exported or classes don't match.

- [ ] **Step 3: Open `AlertsPanel.tsx` and locate the severity → class mapping**

Find the function or object that maps severity to border/dot/text classes. It will look like:

```tsx
// current — something like this
const severityClasses = {
  critical: { border: 'border-l-[#ef4444]', dot: 'bg-[#ef4444]', text: 'text-foreground' },
  warning:  { border: 'border-l-[#f59e0b]', dot: 'bg-[#f59e0b]', text: 'text-foreground' },
  info:     { border: 'border-l-[#06b6d4]', dot: 'bg-[#06b6d4]', text: 'text-foreground' },
  partial:  { border: 'border-l-[#f97316]', dot: 'bg-[#f97316]', text: 'text-foreground' },
}
```

- [ ] **Step 4: Replace with context-aware severity hook**

Add this hook inside `AlertsPanel.tsx` (above the component):

```tsx
import { useDashboardColor } from './DashboardColorContext'

type AlertSeverity = 'critical' | 'warning' | 'info' | 'partial'

function useSeverityClasses(severity: AlertSeverity) {
  const { minimal } = useDashboardColor()

  if (severity === 'critical') return {
    border: 'border-l-[#ef4444]',
    dot: 'bg-[#ef4444]',
    text: 'text-foreground',
  }
  if (severity === 'warning') return {
    border: 'border-l-[#f59e0b]',
    dot: 'bg-[#f59e0b]',
    text: 'text-foreground',
  }
  if (minimal) return {
    border: 'border-l-zinc-700',
    dot: 'bg-zinc-600',
    text: 'text-muted-foreground',
  }
  if (severity === 'info') return {
    border: 'border-l-[#06b6d4]',
    dot: 'bg-[#06b6d4]',
    text: 'text-foreground',
  }
  return {
    border: 'border-l-[#f97316]',
    dot: 'bg-[#f97316]',
    text: 'text-foreground',
  }
}
```

- [ ] **Step 5: Update `AlertItem` to use the hook and ensure it is exported**

```tsx
export function AlertItem({ severity, message }: { severity: AlertSeverity; message: string }) {
  const classes = useSeverityClasses(severity)
  return (
    <li
      role="listitem"
      className={`flex items-center gap-2 rounded-md bg-background border-l-4 px-3 py-2 ${classes.border}`}
    >
      <span className={`h-2 w-2 shrink-0 rounded-full ${classes.dot}`} />
      <span className={`text-xs ${classes.text}`}>{message}</span>
    </li>
  )
}
```

- [ ] **Step 6: Run tests to confirm they pass**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/AlertsPanel.test.tsx
```

Expected: PASS — 4 tests pass.

- [ ] **Step 7: Commit**

```bash
git add app/\(dashboard\)/components/home/AlertsPanel.tsx \
        app/\(dashboard\)/components/home/__tests__/AlertsPanel.test.tsx
git commit -m "feat: zinc border for info/partial alerts on dashboard home"
```

---

## Task 4: ActivityFeed — All Icons to Zinc

**Files:**
- Modify: `app/(dashboard)/components/home/ActivityFeed.tsx`
- Create: `app/(dashboard)/components/home/__tests__/ActivityFeed.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// app/(dashboard)/components/home/__tests__/ActivityFeed.test.tsx
import { render, screen } from '@testing-library/react'
import { DashboardColorProvider } from '../DashboardColorContext'
import { ActivityFeedItem } from '../ActivityFeed'

describe('ActivityFeedItem in minimal color mode', () => {
  it('renders action icon with zinc color class', () => {
    render(
      <DashboardColorProvider>
        <ActivityFeedItem
          actionType="hire"
          actor="Admin"
          target="John Doe"
          timestamp="2026-04-18T09:00:00Z"
        />
      </DashboardColorProvider>
    )
    const icon = screen.getByTestId('activity-icon')
    expect(icon.className).toContain('text-zinc-600')
    expect(icon.className).not.toMatch(/text-green|text-red|text-cyan|text-amber/)
  })

  it('renders action icon with zinc color class for all action types', () => {
    const actionTypes = ['hire', 'termination', 'leave', 'promotion', 'document'] as const
    actionTypes.forEach((actionType) => {
      const { getByTestId, unmount } = render(
        <DashboardColorProvider>
          <ActivityFeedItem actionType={actionType} actor="Admin" target="Jane" timestamp="2026-04-18T09:00:00Z" />
        </DashboardColorProvider>
      )
      expect(getByTestId('activity-icon').className).toContain('text-zinc-600')
      unmount()
    })
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/ActivityFeed.test.tsx
```

Expected: FAIL.

- [ ] **Step 3: Open `ActivityFeed.tsx` and find the icon color logic**

It likely maps action types to colors:

```tsx
// current — something like this
const actionIconColor = {
  hire: 'text-[#22c55e]',
  termination: 'text-[#ef4444]',
  leave: 'text-[#06b6d4]',
  promotion: 'text-[#8b5cf6]',
  document: 'text-[#f59e0b]',
}
```

- [ ] **Step 4: Replace with context-aware icon color**

Add the import and replace the icon color logic:

```tsx
import { useDashboardColor } from './DashboardColorContext'

type ActivityActionType = 'hire' | 'termination' | 'leave' | 'promotion' | 'document'

const ACTION_ICON_COLORS_FULL: Record<ActivityActionType, string> = {
  hire: 'text-[#22c55e]',
  termination: 'text-[#ef4444]',
  leave: 'text-[#06b6d4]',
  promotion: 'text-[#8b5cf6]',
  document: 'text-[#f59e0b]',
}

function useActionIconColor(actionType: ActivityActionType): string {
  const { minimal } = useDashboardColor()
  return minimal ? 'text-zinc-600' : ACTION_ICON_COLORS_FULL[actionType]
}
```

- [ ] **Step 5: Apply in `ActivityFeedItem`, add `data-testid` to icon element, export it**

```tsx
export function ActivityFeedItem({
  actionType,
  actor,
  target,
  timestamp,
}: {
  actionType: ActivityActionType
  actor: string
  target: string
  timestamp: string
}) {
  const iconColor = useActionIconColor(actionType)
  const Icon = ACTION_ICONS[actionType] // existing icon map — unchanged

  return (
    <div className="flex items-start gap-3 py-2">
      <span data-testid="activity-icon" className={`mt-0.5 shrink-0 ${iconColor}`}>
        <Icon size={14} />
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-foreground">
          <span className="font-medium">{actor}</span> → {target}
        </p>
        <p className="text-[11px] text-muted-foreground">{formatTimestamp(timestamp)}</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Run tests**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/ActivityFeed.test.tsx
```

Expected: PASS — 2 tests pass.

- [ ] **Step 7: Commit**

```bash
git add app/\(dashboard\)/components/home/ActivityFeed.tsx \
        app/\(dashboard\)/components/home/__tests__/ActivityFeed.test.tsx
git commit -m "feat: zinc icons for activity feed on dashboard home"
```

---

## Task 5: Secondary KPI Cards — Remove Status Color from Rates

**Files:**
- Modify: `app/(dashboard)/components/home/KPICard.tsx`
- Create: `app/(dashboard)/components/home/__tests__/KPICard.test.tsx`

Secondary KPIs (Attendance Rate, Avg Productivity Score) currently color the value green/amber/red based on thresholds. In minimal mode: always `text-muted-foreground`, no threshold color.

- [ ] **Step 1: Write the failing tests**

```tsx
// app/(dashboard)/components/home/__tests__/KPICard.test.tsx
import { render, screen } from '@testing-library/react'
import { DashboardColorProvider } from '../DashboardColorContext'
import { SecondaryKPICard } from '../KPICard'

describe('SecondaryKPICard in minimal color mode', () => {
  it('renders rate value without green class even when rate is high', () => {
    render(
      <DashboardColorProvider>
        <SecondaryKPICard label="Attendance Rate" value="96%" rate={96} />
      </DashboardColorProvider>
    )
    const value = screen.getByTestId('kpi-value')
    expect(value.className).toContain('text-muted-foreground')
    expect(value.className).not.toMatch(/text-green|text-\[#22c55e\]/)
  })

  it('renders rate value without red class even when rate is low', () => {
    render(
      <DashboardColorProvider>
        <SecondaryKPICard label="Attendance Rate" value="62%" rate={62} />
      </DashboardColorProvider>
    )
    const value = screen.getByTestId('kpi-value')
    expect(value.className).toContain('text-muted-foreground')
    expect(value.className).not.toMatch(/text-red|text-\[#ef4444\]/)
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/KPICard.test.tsx
```

Expected: FAIL.

- [ ] **Step 3: Find the rate → color logic in `KPICard.tsx`**

Look for something like:

```tsx
// current
function getRateColor(rate: number): string {
  if (rate >= 90) return 'text-[#22c55e]'
  if (rate >= 70) return 'text-[#f59e0b]'
  return 'text-[#ef4444]'
}
```

- [ ] **Step 4: Make it context-aware**

```tsx
import { useDashboardColor } from './DashboardColorContext'

function useRateColor(rate: number): string {
  const { minimal } = useDashboardColor()
  if (minimal) return 'text-muted-foreground'
  if (rate >= 90) return 'text-[#22c55e]'
  if (rate >= 70) return 'text-[#f59e0b]'
  return 'text-[#ef4444]'
}
```

- [ ] **Step 5: Apply in `SecondaryKPICard`, add `data-testid`, export it**

```tsx
export function SecondaryKPICard({
  label,
  value,
  rate,
}: {
  label: string
  value: string
  rate?: number
}) {
  const valueColor = rate !== undefined ? useRateColor(rate) : 'text-muted-foreground'

  return (
    <div className="rounded-lg bg-card border border-border p-4">
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p data-testid="kpi-value" className={`mt-1 text-3xl font-bold font-display ${valueColor}`}>
        {value}
      </p>
    </div>
  )
}
```

- [ ] **Step 6: Run tests**

```bash
npx vitest run app/\(dashboard\)/components/home/__tests__/KPICard.test.tsx
```

Expected: PASS — 2 tests pass.

- [ ] **Step 7: Commit**

```bash
git add app/\(dashboard\)/components/home/KPICard.tsx \
        app/\(dashboard\)/components/home/__tests__/KPICard.test.tsx
git commit -m "feat: muted-foreground for secondary KPI rates on dashboard home"
```

---

## Task 6: AttendanceChart — Violet-Only Series

**Files:**
- Modify: `app/(dashboard)/components/home/AttendanceChart.tsx`

The chart has a primary series (violet, unchanged) and an optional comparison series currently cyan (`#06b6d4`). In minimal mode the comparison uses violet-light (`#8b5cf6`).

No test needed here — Recharts SVG rendering doesn't lend itself to unit tests. Verify visually in the browser.

- [ ] **Step 1: Open `AttendanceChart.tsx` and find the series color definitions**

Look for:

```tsx
const SERIES_COLORS = {
  primary: '#7c3aed',
  comparison: '#06b6d4',
}
// or inline: stroke="#06b6d4"
```

- [ ] **Step 2: Add the context-aware palette hook**

```tsx
import { useDashboardColor } from './DashboardColorContext'

function useAttendancePalette() {
  const { minimal } = useDashboardColor()
  return {
    primary: '#7c3aed',
    comparison: minimal ? '#8b5cf6' : '#06b6d4',
    gradientFill: minimal ? '#7c3aed20' : '#7c3aed20', // unchanged
  }
}
```

- [ ] **Step 3: Replace hardcoded colors with palette**

```tsx
export function AttendanceChart({ data, comparisonData }: AttendanceChartProps) {
  const palette = useAttendancePalette()

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="attendanceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={palette.primary} stopOpacity={0.2} />
            <stop offset="95%" stopColor={palette.primary} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="attendance"
          stroke={palette.primary}
          fill="url(#attendanceFill)"
          strokeWidth={2}
        />
        {comparisonData && (
          <Area
            type="monotone"
            dataKey="comparison"
            stroke={palette.comparison}
            fill="none"
            strokeWidth={2}
            strokeDasharray="4 2"
          />
        )}
        {/* gridlines, axes, tooltip — unchanged */}
      </AreaChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 4: Verify visually**

```bash
npx next dev
```

Open `http://localhost:3000`. Check the attendance chart — if a comparison series is shown, it should be violet-light (`#8b5cf6`), not cyan.

- [ ] **Step 5: Commit**

```bash
git add app/\(dashboard\)/components/home/AttendanceChart.tsx
git commit -m "feat: violet-only series palette for attendance chart on dashboard home"
```

---

## Task 7: DepartmentChart — Violet Shades for Ring Chart

**Files:**
- Modify: `app/(dashboard)/components/home/DepartmentChart.tsx`

The ring chart shows headcount by department. Currently uses `['#7c3aed', '#06b6d4', '#f59e0b', '#22c55e']`. In minimal mode: `['#7c3aed', '#8b5cf6', '#a78bfa', '#4c1d95']`.

- [ ] **Step 1: Open `DepartmentChart.tsx` and find the color array**

Look for:

```tsx
const RING_COLORS = ['#7c3aed', '#06b6d4', '#f59e0b', '#22c55e']
// used as: <Cell fill={RING_COLORS[index % RING_COLORS.length]} />
```

- [ ] **Step 2: Replace with context-aware palette**

```tsx
import { useDashboardColor } from './DashboardColorContext'

const RING_PALETTE_MINIMAL = ['#7c3aed', '#8b5cf6', '#a78bfa', '#4c1d95']
const RING_PALETTE_FULL = ['#7c3aed', '#06b6d4', '#f59e0b', '#22c55e']

function useRingPalette() {
  const { minimal } = useDashboardColor()
  return minimal ? RING_PALETTE_MINIMAL : RING_PALETTE_FULL
}
```

- [ ] **Step 3: Apply in the chart component**

```tsx
export function DepartmentChart({ data }: { data: { name: string; count: number }[] }) {
  const palette = useRingPalette()

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={80}
          paddingAngle={2}
          dataKey="count"
        >
          {data.map((_, index) => (
            <Cell key={index} fill={palette[index % palette.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: 'rgba(10,10,15,0.9)',
            border: '1px solid rgba(139,92,246,0.3)',
            borderRadius: '6px',
            color: '#fafafa',
          }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 4: Verify visually**

```bash
npx next dev
```

Open `http://localhost:3000`. The department ring chart should show violet shades only — no cyan, amber, or green segments.

- [ ] **Step 5: Run the full test suite**

```bash
npx vitest run app/\(dashboard\)/
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/\(dashboard\)/components/home/DepartmentChart.tsx
git commit -m "feat: violet shades palette for department ring chart on dashboard home"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|:-----------------|:-----------|
| Red for critical only | Task 3 — AlertsPanel keeps `#ef4444` |
| Amber for warning only | Task 3 — AlertsPanel keeps `#f59e0b` |
| Zinc for info severity | Task 3 — `border-l-zinc-700` when minimal |
| Zinc for partial severity | Task 3 — same |
| Activity feed icons → zinc | Task 4 — `text-zinc-600` always in minimal |
| Secondary KPI rate color removed | Task 5 — `text-muted-foreground` always in minimal |
| Attendance chart violet-only | Task 6 — comparison series `#8b5cf6` |
| Department chart violet shades | Task 7 — `RING_PALETTE_MINIMAL` |
| Other pages unaffected | Context defaults to `minimal: false` — Task 1 test covers this |
| Global tokens unchanged | Context is component-level — no CSS token mutations |

**Placeholder scan:** None found. All steps include actual code and commands.

**Type consistency:**
- `AlertSeverity` type defined in Task 3, used only in Task 3 ✓
- `ActivityActionType` type defined in Task 4, used only in Task 4 ✓
- `useDashboardColor()` returns `{ minimal: boolean }` — consistent across all tasks ✓
- `DashboardColorProvider` import path same in all tasks: `'./DashboardColorContext'` ✓
