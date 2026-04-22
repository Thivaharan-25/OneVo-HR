# Shift Management → Calendar Sidebar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full shift management experience surfaced in the Calendar sidebar — management view (shifts, templates, assignments), a 4-step create wizard, and a quick reassign modal — all with production-quality UI/UX.

**Architecture:** Calendar gets its own ExpansionPanel sub-nav. `?tab=shifts` renders a `ShiftsPage` management view. A `CreateShiftWizard` modal handles the 4-step creation flow. A `ReassignModal` handles Step 3 in isolation (change an existing employee/department's schedule). The `AssignStep` component is shared between wizard and modal. All state is local React state — no store changes beyond mock data.

**Tech Stack:** React, React Router (`useSearchParams`), Zustand (`navStore`), Lucide icons, Tailwind, existing `GlassCard`, `employees` mock data

---

## Departments derived from employees mock data
Engineering · HR · Finance · Marketing · Operations

## Employees
e1 Sarah Lim (Engineering) · e2 James Rajan (Engineering) · e3 Aisha Noor (Engineering) · e4 Ravi Kumar (HR) · e5 Priya Devi (Finance) · e6 Hafiz Azman (Engineering, Flexible) · e7 Nurul Ain (Marketing) · e8 Vikram Singh (Engineering) · e9 Tan Wei Lin (Operations) · e10 Kavitha Raj (HR)

---

## File Map

| Action | File | Responsibility |
|:-------|:-----|:---------------|
| Modify | `demo/src/store/navStore.ts` | Add `'calendar'` to `PANEL_PILLARS` |
| Modify | `demo/src/components/layout/ExpansionPanel.tsx` | Add calendar sub-nav config |
| Modify | `demo/src/mock/types.ts` | Add `Shift`, `ScheduleTemplate`, `ShiftAssignment` types |
| Create | `demo/src/mock/data/shifts.ts` | Mock shift definitions, templates, assignments |
| Modify | `demo/src/modules/calendar/CalendarPage.tsx` | Revert bad edit, route `?tab=shifts` → ShiftsPage |
| Create | `demo/src/modules/calendar/shifts/ShiftsPage.tsx` | Management view: 3 sections + action triggers |
| Create | `demo/src/modules/calendar/shifts/CreateShiftWizard.tsx` | 4-step modal wizard with step indicator |
| Create | `demo/src/modules/calendar/shifts/WizardStep1.tsx` | Shift definition form (name, times, break, grace) |
| Create | `demo/src/modules/calendar/shifts/WizardStep2.tsx` | Template builder (7-day grid, shift per day) |
| Create | `demo/src/modules/calendar/shifts/AssignStep.tsx` | Reusable assignment UI (multi-select employees + departments, effective date) |
| Create | `demo/src/modules/calendar/shifts/WizardStep4.tsx` | Confirmation summary |
| Create | `demo/src/modules/calendar/shifts/ReassignModal.tsx` | Quick reassign modal (AssignStep only) |
| Verify | `demo/src/modules/workforce/WorkforcePage.tsx` | Confirm ShiftScheduleTab fully removed |

---

### Task 1: Add types and mock data

**Files:**
- Modify: `demo/src/mock/types.ts`
- Create: `demo/src/mock/data/shifts.ts`

- [ ] **Step 1: Add types to `types.ts`**

Add after the last interface:

```ts
export interface Shift {
  id: string
  name: string
  startTime: string | null
  endTime: string | null
  breakDuration: number
  gracePeriod: number | null
}

export type DayKey = 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun'

export interface ScheduleTemplate {
  id: string
  name: string
  days: Record<DayKey, string | 'off'>
}

export interface ShiftAssignment {
  id: string
  templateId: string
  targetType: 'employee' | 'department'
  targetIds: string[]
  effectiveFrom: string
  effectiveTo: string | null
}
```

- [ ] **Step 2: Create `demo/src/mock/data/shifts.ts`**

```ts
import type { Shift, ScheduleTemplate, ShiftAssignment } from '../types'

export const shifts: Shift[] = [
  { id: 'shift-1', name: 'Standard 9-6', startTime: '09:00', endTime: '18:00', breakDuration: 60, gracePeriod: 15 },
  { id: 'shift-2', name: 'Flexible', startTime: null, endTime: null, breakDuration: 60, gracePeriod: null },
  { id: 'shift-3', name: 'Night Shift', startTime: '22:00', endTime: '06:00', breakDuration: 60, gracePeriod: 10 },
]

export const scheduleTemplates: ScheduleTemplate[] = [
  {
    id: 'tpl-1',
    name: 'Standard Weekday',
    days: { Mon: 'shift-1', Tue: 'shift-1', Wed: 'shift-1', Thu: 'shift-1', Fri: 'shift-1', Sat: 'off', Sun: 'off' },
  },
  {
    id: 'tpl-2',
    name: 'Flexible Week',
    days: { Mon: 'shift-2', Tue: 'shift-2', Wed: 'shift-2', Thu: 'shift-2', Fri: 'shift-2', Sat: 'off', Sun: 'off' },
  },
  {
    id: 'tpl-3',
    name: 'Night Crew',
    days: { Mon: 'shift-3', Tue: 'shift-3', Wed: 'shift-3', Thu: 'shift-3', Fri: 'shift-3', Sat: 'off', Sun: 'off' },
  },
]

export const shiftAssignments: ShiftAssignment[] = [
  {
    id: 'asgn-1',
    templateId: 'tpl-1',
    targetType: 'department',
    targetIds: ['Engineering', 'HR', 'Finance', 'Marketing', 'Operations'],
    effectiveFrom: '2024-01-01',
    effectiveTo: null,
  },
  {
    id: 'asgn-2',
    templateId: 'tpl-2',
    targetType: 'employee',
    targetIds: ['e6'],
    effectiveFrom: '2024-01-01',
    effectiveTo: null,
  },
]
```

- [ ] **Step 3: Commit**

```bash
git add demo/src/mock/types.ts demo/src/mock/data/shifts.ts
git commit -m "feat: add Shift, ScheduleTemplate, ShiftAssignment types and mock data"
```

---

### Task 2: Wire Calendar into ExpansionPanel sidebar

**Files:**
- Modify: `demo/src/store/navStore.ts`
- Modify: `demo/src/components/layout/ExpansionPanel.tsx`

- [ ] **Step 1: Add `'calendar'` to PANEL_PILLARS in `navStore.ts`**

```ts
export const PANEL_PILLARS: PillarKey[] = ['people', 'org', 'calendar', 'admin', 'settings']
```

- [ ] **Step 2: Add `Clock`, `CalendarCheck`, `Timer` to lucide imports in `ExpansionPanel.tsx`**

```tsx
import {
  User, CalendarDays, GitBranch, Building2, Users,
  ShieldCheck, ClipboardList, MonitorDot, Laptop, CheckSquare2,
  Settings, Eye, Plug, Palette, Bell, FileText, Clock, CalendarCheck, Timer, type LucideIcon,
} from 'lucide-react'
```

- [ ] **Step 3: Add calendar entry to `subNavConfig` in `ExpansionPanel.tsx`**

Add after the `org` block:

```tsx
calendar: {
  label: 'Calendar',
  items: [
    { label: 'Events', path: '/calendar', icon: CalendarDays },
    { label: 'Shifts & Schedules', path: '/calendar?tab=shifts', icon: Clock },
    { label: 'Attendance Correction', path: '/calendar?tab=attendance', icon: CalendarCheck },
    { label: 'Overtime', path: '/calendar?tab=overtime', icon: Timer },
  ],
},
```

- [ ] **Step 4: Verify**

Navigate to `/calendar` — panel slides open with "Events" and "Shifts & Schedules" items. "Events" is active by default.

- [ ] **Step 5: Commit**

```bash
git add demo/src/store/navStore.ts demo/src/components/layout/ExpansionPanel.tsx
git commit -m "feat: add calendar to PANEL_PILLARS and sub-nav (Events, Shifts & Schedules)"
```

---

### Task 3: Fix CalendarPage routing

**Files:**
- Modify: `demo/src/modules/calendar/CalendarPage.tsx`

Replace entire file (reverts the bad inline edit, adds proper tab routing):

- [ ] **Step 1: Replace CalendarPage.tsx**

```tsx
import { useSearchParams } from 'react-router-dom'
import { calendarEvents } from '../../mock/data/calendar'
import { GlassCard } from '../../components/ui/GlassCard'
import { ShiftsPage } from './shifts/ShiftsPage'

const typeColor: Record<string, string> = {
  holiday: 'bg-red-500/20 text-red-400',
  company: 'bg-blue-500/20 text-blue-400',
  leave: 'bg-yellow-500/20 text-yellow-400',
}

export function CalendarPage() {
  const [searchParams] = useSearchParams()
  const tab = searchParams.get('tab')

  if (tab === 'shifts') return <ShiftsPage />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Calendar</h1>
      <GlassCard>
        <div className="font-outfit font-semibold text-white/70 mb-4">April 2026</div>
        <div className="space-y-3">
          {calendarEvents.map(ev => (
            <div key={ev.id} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
              <span className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${typeColor[ev.type]}`}>{ev.type}</span>
              <span className="text-white text-sm flex-1">{ev.title}</span>
              <span className="text-white/40 text-xs font-geist">
                {(ev as { date?: string }).date ?? (ev as { startDate?: string }).startDate}
              </span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/calendar/CalendarPage.tsx
git commit -m "fix: revert CalendarPage, route ?tab=shifts to ShiftsPage"
```

---

### Task 4: AssignStep — shared multi-select assignment UI

**Files:**
- Create: `demo/src/modules/calendar/shifts/AssignStep.tsx`

This component is used in both the wizard (Step 3) and the quick reassign modal. It handles:
- Two tabs: **Employees** | **Departments**
- Searchable checklist with avatars (employees) or building icons (departments)
- Template picker dropdown
- Effective date — "Permanent" toggle or date range inputs

- [ ] **Step 1: Create `AssignStep.tsx`**

```tsx
import { useState } from 'react'
import { Search, Building2, Check } from 'lucide-react'
import { employees } from '../../../mock/data/employees'
import { scheduleTemplates } from '../../../mock/data/shifts'
import { cn } from '../../../lib/utils'

const DEPARTMENTS = ['Engineering', 'HR', 'Finance', 'Marketing', 'Operations']

export interface AssignStepValue {
  tab: 'employee' | 'department'
  selectedEmployees: string[]
  selectedDepartments: string[]
  templateId: string
  permanent: boolean
  effectiveFrom: string
  effectiveTo: string
}

interface Props {
  value: AssignStepValue
  onChange: (v: AssignStepValue) => void
}

export function AssignStep({ value, onChange }: Props) {
  const [search, setSearch] = useState('')

  const set = (patch: Partial<AssignStepValue>) => onChange({ ...value, ...patch })

  const toggleEmployee = (id: string) => {
    const next = value.selectedEmployees.includes(id)
      ? value.selectedEmployees.filter(e => e !== id)
      : [...value.selectedEmployees, id]
    set({ selectedEmployees: next })
  }

  const toggleDepartment = (dept: string) => {
    const next = value.selectedDepartments.includes(dept)
      ? value.selectedDepartments.filter(d => d !== dept)
      : [...value.selectedDepartments, dept]
    set({ selectedDepartments: next })
  }

  const filteredEmployees = employees.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.department.toLowerCase().includes(search.toLowerCase())
  )

  const filteredDepts = DEPARTMENTS.filter(d =>
    d.toLowerCase().includes(search.toLowerCase())
  )

  const deptCount = (dept: string) => employees.filter(e => e.department === dept).length

  return (
    <div className="space-y-5">
      {/* Template picker */}
      <div>
        <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Schedule Template</label>
        <div className="grid grid-cols-3 gap-2">
          {scheduleTemplates.map(tpl => (
            <button
              key={tpl.id}
              onClick={() => set({ templateId: tpl.id })}
              className={cn(
                'p-3 rounded-xl border text-left transition-all',
                value.templateId === tpl.id
                  ? 'bg-violet-600/20 border-violet-500/40 text-violet-300'
                  : 'bg-white/[0.03] border-white/[0.08] text-white/50 hover:border-white/20 hover:text-white/70'
              )}
            >
              <div className="text-xs font-outfit font-semibold">{tpl.name}</div>
              <div className="text-[10px] mt-0.5 text-current opacity-60">
                {Object.values(tpl.days).filter(d => d !== 'off').length}d / week
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Employee / Department tabs */}
      <div>
        <div className="flex gap-1 mb-3">
          {(['employee', 'department'] as const).map(t => (
            <button
              key={t}
              onClick={() => { set({ tab: t }); setSearch('') }}
              className={cn(
                'px-4 py-1.5 rounded-lg text-xs font-outfit transition-all',
                value.tab === t
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30'
                  : 'text-white/40 hover:text-white/60 border border-transparent'
              )}
            >
              {t === 'employee' ? 'Employees' : 'Departments'}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative mb-2">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder={value.tab === 'employee' ? 'Search employees…' : 'Search departments…'}
            className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg pl-8 pr-3 py-2 text-sm text-white placeholder-white/25 font-geist outline-none focus:border-violet-500/40"
          />
        </div>

        {/* Employees list */}
        {value.tab === 'employee' && (
          <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
            {filteredEmployees.map(emp => {
              const selected = value.selectedEmployees.includes(emp.id)
              return (
                <button
                  key={emp.id}
                  onClick={() => toggleEmployee(emp.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all',
                    selected
                      ? 'bg-violet-600/[0.12] border-violet-500/30'
                      : 'bg-white/[0.02] border-white/[0.05] hover:bg-white/[0.05] hover:border-white/10'
                  )}
                >
                  <img src={emp.avatar} alt={emp.name} className="w-7 h-7 rounded-full border border-white/10 flex-shrink-0" />
                  <div className="flex-1 text-left">
                    <div className={cn('text-xs font-outfit font-medium', selected ? 'text-white' : 'text-white/70')}>{emp.name}</div>
                    <div className="text-[10px] text-white/35">{emp.department} · {emp.jobTitle}</div>
                  </div>
                  <div className={cn(
                    'w-4 h-4 rounded-full border flex items-center justify-center flex-shrink-0 transition-all',
                    selected ? 'bg-violet-500 border-violet-500' : 'border-white/20'
                  )}>
                    {selected && <Check size={10} className="text-white" />}
                  </div>
                </button>
              )
            })}
          </div>
        )}

        {/* Departments list */}
        {value.tab === 'department' && (
          <div className="space-y-1">
            {filteredDepts.map(dept => {
              const selected = value.selectedDepartments.includes(dept)
              return (
                <button
                  key={dept}
                  onClick={() => toggleDepartment(dept)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all',
                    selected
                      ? 'bg-violet-600/[0.12] border-violet-500/30'
                      : 'bg-white/[0.02] border-white/[0.05] hover:bg-white/[0.05] hover:border-white/10'
                  )}
                >
                  <div className={cn(
                    'w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0',
                    selected ? 'bg-violet-500/20' : 'bg-white/[0.06]'
                  )}>
                    <Building2 size={13} className={selected ? 'text-violet-400' : 'text-white/40'} />
                  </div>
                  <div className="flex-1 text-left">
                    <div className={cn('text-xs font-outfit font-medium', selected ? 'text-white' : 'text-white/70')}>{dept}</div>
                    <div className="text-[10px] text-white/35">{deptCount(dept)} employees</div>
                  </div>
                  <div className={cn(
                    'w-4 h-4 rounded-full border flex items-center justify-center flex-shrink-0 transition-all',
                    selected ? 'bg-violet-500 border-violet-500' : 'border-white/20'
                  )}>
                    {selected && <Check size={10} className="text-white" />}
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* Effective date */}
      <div>
        <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Effective Date</label>
        <div className="flex items-center gap-3 mb-3">
          <button
            onClick={() => set({ permanent: !value.permanent })}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-outfit transition-all',
              value.permanent
                ? 'bg-violet-600/20 border-violet-500/40 text-violet-300'
                : 'bg-white/[0.03] border-white/[0.08] text-white/40 hover:text-white/60'
            )}
          >
            <div className={cn('w-3 h-3 rounded-full border', value.permanent ? 'bg-violet-400 border-violet-400' : 'border-white/30')} />
            Permanent
          </button>
        </div>
        {!value.permanent && (
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <div className="text-[10px] text-white/30 mb-1 font-outfit">From</div>
              <input
                type="date"
                value={value.effectiveFrom}
                onChange={e => set({ effectiveFrom: e.target.value })}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white font-geist outline-none focus:border-violet-500/40"
              />
            </div>
            <div className="flex-1">
              <div className="text-[10px] text-white/30 mb-1 font-outfit">To</div>
              <input
                type="date"
                value={value.effectiveTo}
                onChange={e => set({ effectiveTo: e.target.value })}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white font-geist outline-none focus:border-violet-500/40"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/calendar/shifts/AssignStep.tsx
git commit -m "feat: AssignStep shared component — multi-select employees/departments, template picker, effective date"
```

---

### Task 5: Create wizard steps 1, 2, and 4

**Files:**
- Create: `demo/src/modules/calendar/shifts/WizardStep1.tsx`
- Create: `demo/src/modules/calendar/shifts/WizardStep2.tsx`
- Create: `demo/src/modules/calendar/shifts/WizardStep4.tsx`

- [ ] **Step 1: Create `WizardStep1.tsx` — Shift definition form**

```tsx
export interface Step1Value {
  name: string
  startTime: string
  endTime: string
  breakDuration: string
  gracePeriod: string
  isFlexible: boolean
}

interface Props { value: Step1Value; onChange: (v: Step1Value) => void }

export function WizardStep1({ value, onChange }: Props) {
  const set = (patch: Partial<Step1Value>) => onChange({ ...value, ...patch })

  return (
    <div className="space-y-4">
      <div>
        <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Shift Name</label>
        <input
          value={value.name}
          onChange={e => set({ name: e.target.value })}
          placeholder="e.g. Morning, Night Shift"
          className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white placeholder-white/20 font-geist outline-none focus:border-violet-500/40 transition-colors"
        />
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => set({ isFlexible: !value.isFlexible })}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-outfit transition-all ${
            value.isFlexible
              ? 'bg-violet-600/20 border-violet-500/40 text-violet-300'
              : 'bg-white/[0.03] border-white/[0.08] text-white/40 hover:text-white/60'
          }`}
        >
          <div className={`w-3 h-3 rounded-full border ${value.isFlexible ? 'bg-violet-400 border-violet-400' : 'border-white/30'}`} />
          Flexible hours
        </button>
        <span className="text-white/25 text-xs font-outfit">No fixed start/end time</span>
      </div>

      {!value.isFlexible && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Start Time</label>
            <input
              type="time"
              value={value.startTime}
              onChange={e => set({ startTime: e.target.value })}
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white font-geist outline-none focus:border-violet-500/40 transition-colors"
            />
          </div>
          <div>
            <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">End Time</label>
            <input
              type="time"
              value={value.endTime}
              onChange={e => set({ endTime: e.target.value })}
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white font-geist outline-none focus:border-violet-500/40 transition-colors"
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Break Duration (min)</label>
          <input
            type="number"
            min={0}
            value={value.breakDuration}
            onChange={e => set({ breakDuration: e.target.value })}
            placeholder="60"
            className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white font-geist outline-none focus:border-violet-500/40 transition-colors"
          />
        </div>
        <div>
          <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Grace Period (min)</label>
          <input
            type="number"
            min={0}
            value={value.gracePeriod}
            onChange={e => set({ gracePeriod: e.target.value })}
            placeholder="15"
            className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white font-geist outline-none focus:border-violet-500/40 transition-colors"
          />
          <p className="text-white/25 text-[10px] mt-1 font-outfit">Tolerated late arrival before flagging</p>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create `WizardStep2.tsx` — Schedule template builder**

```tsx
import { shifts } from '../../../mock/data/shifts'
import type { DayKey } from '../../../mock/types'
import { cn } from '../../../lib/utils'

const DAYS: DayKey[] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export interface Step2Value {
  templateName: string
  days: Record<DayKey, string>
}

interface Props { value: Step2Value; onChange: (v: Step2Value) => void }

export function WizardStep2({ value, onChange }: Props) {
  const set = (patch: Partial<Step2Value>) => onChange({ ...value, ...patch })
  const setDay = (day: DayKey, shiftId: string) => set({ days: { ...value.days, [day]: shiftId } })

  const activeCount = Object.values(value.days).filter(d => d !== 'off').length

  return (
    <div className="space-y-5">
      <div>
        <label className="text-white/50 text-xs font-outfit uppercase tracking-wider mb-2 block">Template Name</label>
        <input
          value={value.templateName}
          onChange={e => set({ templateName: e.target.value })}
          placeholder="e.g. Standard Weekday, Rotating Week A"
          className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white placeholder-white/20 font-geist outline-none focus:border-violet-500/40 transition-colors"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-white/50 text-xs font-outfit uppercase tracking-wider">Shift per Day</label>
          <span className="text-white/30 text-xs font-outfit">{activeCount} active day{activeCount !== 1 ? 's' : ''}</span>
        </div>
        <div className="grid grid-cols-7 gap-2">
          {DAYS.map(day => (
            <div key={day} className="flex flex-col gap-1.5">
              <div className={cn(
                'text-center text-[10px] font-outfit font-medium py-1 rounded-lg',
                value.days[day] !== 'off' ? 'text-violet-300 bg-violet-500/10' : 'text-white/30'
              )}>
                {day}
              </div>
              <select
                value={value.days[day]}
                onChange={e => setDay(day, e.target.value)}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-1 py-2 text-[10px] text-white font-outfit outline-none focus:border-violet-500/40 transition-colors cursor-pointer"
              >
                <option value="off">Off</option>
                {shifts.map(s => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create `WizardStep4.tsx` — Confirmation summary**

```tsx
import { Check } from 'lucide-react'
import { scheduleTemplates } from '../../../mock/data/shifts'
import { employees } from '../../../mock/data/employees'
import type { Step1Value } from './WizardStep1'
import type { Step2Value } from './WizardStep2'
import type { AssignStepValue } from './AssignStep'

interface Props {
  step1: Step1Value
  step2: Step2Value
  step3: AssignStepValue
}

export function WizardStep4({ step1, step2, step3 }: Props) {
  const template = scheduleTemplates.find(t => t.id === step3.templateId)
  const assignedEmployees = employees.filter(e => step3.selectedEmployees.includes(e.id))
  const activeDays = Object.values(step2.days).filter(d => d !== 'off').length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-center gap-3 py-4">
        <div className="w-12 h-12 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
          <Check size={22} className="text-violet-400" />
        </div>
        <div>
          <div className="text-white font-outfit font-semibold">Ready to create</div>
          <div className="text-white/40 text-xs font-outfit">Review your shift setup below</div>
        </div>
      </div>

      <div className="space-y-3">
        {/* Shift */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
          <div className="text-white/40 text-[10px] font-outfit uppercase tracking-wider mb-2">Shift Definition</div>
          <div className="text-white font-outfit font-semibold text-sm">{step1.name || '—'}</div>
          <div className="text-white/40 text-xs mt-1 font-geist">
            {step1.isFlexible ? 'Flexible hours' : `${step1.startTime} – ${step1.endTime}`}
            {' · '}{step1.breakDuration || '—'}min break
            {step1.gracePeriod ? ` · ${step1.gracePeriod}min grace` : ''}
          </div>
        </div>

        {/* Template */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
          <div className="text-white/40 text-[10px] font-outfit uppercase tracking-wider mb-2">Schedule Template</div>
          <div className="text-white font-outfit font-semibold text-sm">{step2.templateName || '—'}</div>
          <div className="text-white/40 text-xs mt-1 font-outfit">{activeDays} active days / week</div>
        </div>

        {/* Assignment */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06]">
          <div className="text-white/40 text-[10px] font-outfit uppercase tracking-wider mb-2">Assignment</div>
          <div className="text-white font-outfit font-semibold text-sm">
            {template?.name ?? '—'}
          </div>
          {step3.tab === 'employee' && assignedEmployees.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {assignedEmployees.map(e => (
                <div key={e.id} className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">
                  <img src={e.avatar} alt={e.name} className="w-4 h-4 rounded-full" />
                  <span className="text-white/60 text-[10px] font-outfit">{e.name}</span>
                </div>
              ))}
            </div>
          )}
          {step3.tab === 'department' && step3.selectedDepartments.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {step3.selectedDepartments.map(d => (
                <span key={d} className="px-2 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[10px] font-outfit">{d}</span>
              ))}
            </div>
          )}
          <div className="text-white/30 text-[10px] mt-2 font-outfit">
            {step3.permanent ? 'Permanent' : `${step3.effectiveFrom} → ${step3.effectiveTo || 'open'}`}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add demo/src/modules/calendar/shifts/WizardStep1.tsx demo/src/modules/calendar/shifts/WizardStep2.tsx demo/src/modules/calendar/shifts/WizardStep4.tsx
git commit -m "feat: wizard steps 1 (shift form), 2 (template builder), 4 (confirmation)"
```

---

### Task 6: CreateShiftWizard modal

**Files:**
- Create: `demo/src/modules/calendar/shifts/CreateShiftWizard.tsx`

Full 4-step modal with step progress indicator, back/next navigation, and close button.

- [ ] **Step 1: Create `CreateShiftWizard.tsx`**

```tsx
import { useState } from 'react'
import { X, ChevronRight, ChevronLeft } from 'lucide-react'
import { cn } from '../../../lib/utils'
import { WizardStep1, type Step1Value } from './WizardStep1'
import { WizardStep2, type Step2Value } from './WizardStep2'
import { AssignStep, type AssignStepValue } from './AssignStep'
import { WizardStep4 } from './WizardStep4'

const STEPS = ['Shift Definition', 'Schedule Template', 'Assign', 'Confirm']

const defaultStep1: Step1Value = { name: '', startTime: '09:00', endTime: '18:00', breakDuration: '60', gracePeriod: '15', isFlexible: false }
const defaultStep2: Step2Value = {
  templateName: '',
  days: { Mon: 'off', Tue: 'off', Wed: 'off', Thu: 'off', Fri: 'off', Sat: 'off', Sun: 'off' },
}
const defaultStep3: AssignStepValue = {
  tab: 'employee',
  selectedEmployees: [],
  selectedDepartments: [],
  templateId: '',
  permanent: true,
  effectiveFrom: '',
  effectiveTo: '',
}

interface Props { onClose: () => void }

export function CreateShiftWizard({ onClose }: Props) {
  const [step, setStep] = useState(0)
  const [s1, setS1] = useState<Step1Value>(defaultStep1)
  const [s2, setS2] = useState<Step2Value>(defaultStep2)
  const [s3, setS3] = useState<AssignStepValue>(defaultStep3)

  const canNext = [
    !!s1.name && (s1.isFlexible || (!!s1.startTime && !!s1.endTime)),
    !!s2.templateName,
    !!s3.templateId && (s3.selectedEmployees.length > 0 || s3.selectedDepartments.length > 0),
    true,
  ][step]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-[#0e0e1a] border border-white/[0.08] rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-white/[0.06]">
          <div>
            <h2 className="text-white font-outfit font-semibold">Create Shift</h2>
            <p className="text-white/35 text-xs font-outfit mt-0.5">Step {step + 1} of {STEPS.length}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-white/[0.05] hover:bg-white/10 flex items-center justify-center transition-colors">
            <X size={14} className="text-white/50" />
          </button>
        </div>

        {/* Step indicator */}
        <div className="flex px-6 py-4 gap-2">
          {STEPS.map((label, i) => (
            <div key={i} className="flex-1 flex flex-col gap-1.5">
              <div className={cn(
                'h-0.5 rounded-full transition-all duration-300',
                i < step ? 'bg-violet-500' : i === step ? 'bg-violet-400' : 'bg-white/[0.08]'
              )} />
              <span className={cn(
                'text-[10px] font-outfit transition-colors',
                i === step ? 'text-violet-300' : i < step ? 'text-white/40' : 'text-white/20'
              )}>{label}</span>
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="px-6 pb-4 max-h-[60vh] overflow-y-auto">
          {step === 0 && <WizardStep1 value={s1} onChange={setS1} />}
          {step === 1 && <WizardStep2 value={s2} onChange={setS2} />}
          {step === 2 && <AssignStep value={s3} onChange={setS3} />}
          {step === 3 && <WizardStep4 step1={s1} step2={s2} step3={s3} />}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-white/[0.06] bg-white/[0.01]">
          <button
            onClick={() => step === 0 ? onClose() : setStep(step - 1)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-outfit text-white/40 hover:text-white/70 transition-colors"
          >
            <ChevronLeft size={14} />
            {step === 0 ? 'Cancel' : 'Back'}
          </button>
          <button
            onClick={() => step < STEPS.length - 1 ? setStep(step + 1) : onClose()}
            disabled={!canNext}
            className={cn(
              'flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-outfit font-medium transition-all',
              canNext
                ? 'bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-900/30'
                : 'bg-white/[0.04] text-white/25 cursor-not-allowed'
            )}
          >
            {step === STEPS.length - 1 ? 'Done' : 'Next'}
            {step < STEPS.length - 1 && <ChevronRight size={14} />}
          </button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/calendar/shifts/CreateShiftWizard.tsx
git commit -m "feat: 4-step CreateShiftWizard modal with step indicator and validation"
```

---

### Task 7: ReassignModal — quick Step 3 only

**Files:**
- Create: `demo/src/modules/calendar/shifts/ReassignModal.tsx`

- [ ] **Step 1: Create `ReassignModal.tsx`**

```tsx
import { useState } from 'react'
import { X, Check } from 'lucide-react'
import { cn } from '../../../lib/utils'
import { AssignStep, type AssignStepValue } from './AssignStep'
import { employees } from '../../../mock/data/employees'
import type { ShiftAssignment } from '../../../mock/types'

interface Props {
  assignment: ShiftAssignment
  onClose: () => void
}

export function ReassignModal({ assignment, onClose }: Props) {
  const [done, setDone] = useState(false)
  const [value, setValue] = useState<AssignStepValue>({
    tab: assignment.targetType === 'employee' ? 'employee' : 'department',
    selectedEmployees: assignment.targetType === 'employee' ? assignment.targetIds : [],
    selectedDepartments: assignment.targetType === 'department' ? assignment.targetIds : [],
    templateId: assignment.templateId,
    permanent: assignment.effectiveTo === null,
    effectiveFrom: assignment.effectiveFrom,
    effectiveTo: assignment.effectiveTo ?? '',
  })

  const canSave = value.templateId && (value.selectedEmployees.length > 0 || value.selectedDepartments.length > 0)

  if (done) {
    const names = value.tab === 'employee'
      ? employees.filter(e => value.selectedEmployees.includes(e.id)).map(e => e.name).join(', ')
      : value.selectedDepartments.join(', ')

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
        <div className="relative w-full max-w-sm bg-[#0e0e1a] border border-white/[0.08] rounded-2xl shadow-2xl p-8 text-center">
          <div className="w-14 h-14 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mx-auto mb-4">
            <Check size={24} className="text-violet-400" />
          </div>
          <div className="text-white font-outfit font-semibold mb-1">Schedule Updated</div>
          <div className="text-white/40 text-sm font-outfit">{names}</div>
          <button onClick={onClose} className="mt-6 w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-outfit font-medium transition-colors">
            Done
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-[#0e0e1a] border border-white/[0.08] rounded-2xl shadow-2xl overflow-hidden">

        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-white/[0.06]">
          <div>
            <h2 className="text-white font-outfit font-semibold">Change Schedule</h2>
            <p className="text-white/35 text-xs font-outfit mt-0.5">Select employees or departments and assign a template</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-white/[0.05] hover:bg-white/10 flex items-center justify-center transition-colors">
            <X size={14} className="text-white/50" />
          </button>
        </div>

        <div className="px-6 py-5 max-h-[65vh] overflow-y-auto">
          <AssignStep value={value} onChange={setValue} />
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-white/[0.06] bg-white/[0.01]">
          <button onClick={onClose} className="px-4 py-2 rounded-xl text-sm font-outfit text-white/40 hover:text-white/70 transition-colors">
            Cancel
          </button>
          <button
            onClick={() => setDone(true)}
            disabled={!canSave}
            className={cn(
              'px-5 py-2 rounded-xl text-sm font-outfit font-medium transition-all',
              canSave
                ? 'bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-900/30'
                : 'bg-white/[0.04] text-white/25 cursor-not-allowed'
            )}
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/calendar/shifts/ReassignModal.tsx
git commit -m "feat: ReassignModal — quick schedule change with multi-select and success state"
```

---

### Task 8: ShiftsPage — management view

**Files:**
- Create: `demo/src/modules/calendar/shifts/ShiftsPage.tsx`

Three sections: Shifts list · Templates list · Assignments list. "Create Shift" opens wizard. "Change" on an assignment opens ReassignModal.

- [ ] **Step 1: Create `ShiftsPage.tsx`**

```tsx
import { useState } from 'react'
import { Plus, Clock, CalendarDays, Users, Pencil } from 'lucide-react'
import { GlassCard } from '../../../components/ui/GlassCard'
import { shifts, scheduleTemplates, shiftAssignments } from '../../../mock/data/shifts'
import { employees } from '../../../mock/data/employees'
import { CreateShiftWizard } from './CreateShiftWizard'
import { ReassignModal } from './ReassignModal'
import type { ShiftAssignment } from '../../../mock/types'

export function ShiftsPage() {
  const [wizardOpen, setWizardOpen] = useState(false)
  const [reassignTarget, setReassignTarget] = useState<ShiftAssignment | null>(null)

  const getTemplateName = (id: string) => scheduleTemplates.find(t => t.id === id)?.name ?? id

  const assignmentLabel = (a: ShiftAssignment) => {
    if (a.targetType === 'department') return a.targetIds.join(', ')
    return employees.filter(e => a.targetIds.includes(e.id)).map(e => e.name).join(', ')
  }

  const assignmentAvatars = (a: ShiftAssignment) => {
    if (a.targetType !== 'employee') return []
    return employees.filter(e => a.targetIds.includes(e.id))
  }

  return (
    <>
      <div className="space-y-7">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-outfit font-bold text-white">Shifts & Schedules</h1>
            <p className="text-white/35 text-sm font-outfit mt-0.5">Manage shift definitions, templates and assignments</p>
          </div>
          <button
            onClick={() => setWizardOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-outfit font-medium transition-all shadow-lg shadow-violet-900/30"
          >
            <Plus size={15} />
            Create Shift
          </button>
        </div>

        {/* Shift Definitions */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Clock size={14} className="text-white/30" />
            <span className="text-white/40 text-xs font-outfit uppercase tracking-wider">Shift Definitions</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {shifts.map(s => (
              <GlassCard key={s.id}>
                <div className="font-outfit font-semibold text-white/90 text-sm mb-3">{s.name}</div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-white/35">Hours</span>
                    <span className="text-white/65 font-geist">
                      {s.startTime && s.endTime ? `${s.startTime} – ${s.endTime}` : 'Flexible'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/35">Break</span>
                    <span className="text-white/65">{s.breakDuration}min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/35">Grace</span>
                    <span className="text-white/65">{s.gracePeriod != null ? `${s.gracePeriod}min` : '—'}</span>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>

        {/* Schedule Templates */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <CalendarDays size={14} className="text-white/30" />
            <span className="text-white/40 text-xs font-outfit uppercase tracking-wider">Schedule Templates</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {scheduleTemplates.map(tpl => {
              const activeDays = Object.entries(tpl.days).filter(([, v]) => v !== 'off')
              return (
                <GlassCard key={tpl.id}>
                  <div className="font-outfit font-semibold text-white/90 text-sm mb-3">{tpl.name}</div>
                  <div className="flex gap-1">
                    {(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] as const).map(day => {
                      const active = tpl.days[day] !== 'off'
                      return (
                        <div key={day} className={`flex-1 py-1.5 rounded text-center text-[9px] font-outfit ${
                          active ? 'bg-violet-500/20 text-violet-300' : 'bg-white/[0.03] text-white/20'
                        }`}>
                          {day[0]}
                        </div>
                      )
                    })}
                  </div>
                  <div className="text-white/30 text-[10px] font-outfit mt-2">{activeDays.length} active days / week</div>
                </GlassCard>
              )
            })}
          </div>
        </div>

        {/* Assignments */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Users size={14} className="text-white/30" />
            <span className="text-white/40 text-xs font-outfit uppercase tracking-wider">Current Assignments</span>
          </div>
          <GlassCard>
            <div className="divide-y divide-white/[0.05]">
              {shiftAssignments.map(a => {
                const avatars = assignmentAvatars(a)
                return (
                  <div key={a.id} className="flex items-center gap-4 py-3 first:pt-0 last:pb-0">
                    {/* Target */}
                    <div className="flex-1 min-w-0">
                      <div className="text-white/80 text-sm font-outfit font-medium truncate">{assignmentLabel(a)}</div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-outfit ${
                          a.targetType === 'department'
                            ? 'bg-blue-500/10 text-blue-400'
                            : 'bg-violet-500/10 text-violet-400'
                        }`}>
                          {a.targetType === 'department' ? 'Department' : 'Employee'}
                        </span>
                        <span className="text-white/25 text-[10px] font-outfit">
                          {a.effectiveTo ? `${a.effectiveFrom} → ${a.effectiveTo}` : 'Permanent'}
                        </span>
                      </div>
                    </div>

                    {/* Avatars (employees) */}
                    {avatars.length > 0 && (
                      <div className="flex -space-x-1.5">
                        {avatars.slice(0, 5).map(e => (
                          <img key={e.id} src={e.avatar} alt={e.name} className="w-6 h-6 rounded-full border border-[#0e0e1a]" title={e.name} />
                        ))}
                        {avatars.length > 5 && (
                          <div className="w-6 h-6 rounded-full bg-white/10 border border-[#0e0e1a] flex items-center justify-center text-[9px] text-white/50 font-outfit">
                            +{avatars.length - 5}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Template badge */}
                    <div className="text-xs font-outfit text-white/50 bg-white/[0.04] border border-white/[0.06] px-3 py-1 rounded-lg whitespace-nowrap">
                      {getTemplateName(a.templateId)}
                    </div>

                    {/* Change button */}
                    <button
                      onClick={() => setReassignTarget(a)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] text-white/50 hover:text-white/80 text-xs font-outfit transition-all"
                    >
                      <Pencil size={11} />
                      Change
                    </button>
                  </div>
                )
              })}
            </div>
          </GlassCard>
        </div>
      </div>

      {wizardOpen && <CreateShiftWizard onClose={() => setWizardOpen(false)} />}
      {reassignTarget && <ReassignModal assignment={reassignTarget} onClose={() => setReassignTarget(null)} />}
    </>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/modules/calendar/shifts/ShiftsPage.tsx
git commit -m "feat: ShiftsPage management view — shifts, templates, assignments with create and reassign triggers"
```

---

### Task 9: Verify WorkforcePage is clean

- [ ] **Step 1: Open `demo/src/modules/workforce/WorkforcePage.tsx` and confirm**

No `import { ShiftScheduleTab }` · No `{ id: 'shifts' ... }` in tabs array · No `{tab === 'shifts' ...}` in render.

- [ ] **Step 2: Navigate to `/workforce` and confirm no "Shift Schedule" tab visible**

- [ ] **Step 3: Commit if any cleanup was needed**

```bash
git add demo/src/modules/workforce/WorkforcePage.tsx
git commit -m "fix: confirm ShiftScheduleTab fully removed from WorkforcePage"
```
