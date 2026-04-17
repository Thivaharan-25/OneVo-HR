# ONEVO Demo Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished React + Vite UI-only prototype of ONEVO (multi-tenant white-label SaaS) covering all 15 Phase 1 modules across ~41 pages, with mock data and simulated real-time events, for client/investor demos.

**Architecture:** Single Vite + React app with React Router v6. All data served from static mock files. A `MockEventEngine` singleton fires live events into Zustand every few seconds. Persona-based login seeds different auth states.

**Tech Stack:** Vite, React 18, React Router v6, Zustand, shadcn/ui, Tailwind CSS, Recharts, Lucide React, DiceBear Avatars

**Knowledge Base:** `onevo-hr-brain/` — read these before building:
- `frontend/architecture/app-structure.md` — route tree, layout system
- `frontend/design-system/components/component-catalog.md` — GlassCard, GlassSurface, IconRail, ExpansionPanel
- `frontend/cross-cutting/authorization.md` — PermissionGate, permission format
- `ADE-START-HERE.md` — module list and purpose of each

---

## Phase 1: Foundation

### Task 1: Scaffold Project

**Files:**
- Create: `package.json`
- Create: `vite.config.ts`
- Create: `tailwind.config.ts`
- Create: `src/main.tsx`
- Create: `src/App.tsx`
- Create: `index.html`

- [ ] **Step 1: Scaffold Vite + React + TypeScript**

```bash
npm create vite@latest onevo-demo -- --template react-ts
cd onevo-demo
npm install
```

- [ ] **Step 2: Install dependencies**

```bash
npm install react-router-dom zustand recharts lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @shadcn/ui
npx shadcn@latest init
```

- [ ] **Step 3: Configure Tailwind — replace `tailwind.config.ts`**

```ts
import type { Config } from 'tailwindcss'
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        geist: ['Geist', 'monospace'],
      },
      colors: {
        violet: { DEFAULT: '#7C3AED', glow: '#8B5CF6' },
        glass: { DEFAULT: 'rgba(255,255,255,0.05)', light: 'rgba(255,255,255,0.08)' },
      },
    },
  },
  plugins: [],
} satisfies Config
```

- [ ] **Step 4: Add Google Fonts to `index.html`**

```html
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 5: Set dark mode on `<html>` in `src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

document.documentElement.classList.add('dark')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>
)
```

- [ ] **Step 6: Commit**

```bash
git add . && git commit -m "feat: scaffold Vite + React + Tailwind + shadcn"
```

---

### Task 2: Mock Data Layer

**Files:**
- Create: `src/mock/data/tenants.ts`
- Create: `src/mock/data/employees.ts`
- Create: `src/mock/data/presence.ts`
- Create: `src/mock/data/activity.ts`
- Create: `src/mock/data/leave.ts`
- Create: `src/mock/data/org.ts`
- Create: `src/mock/data/skills.ts`
- Create: `src/mock/data/exceptions.ts`
- Create: `src/mock/data/analytics.ts`
- Create: `src/mock/data/notifications.ts`
- Create: `src/mock/data/wms-bridge.ts`
- Create: `src/mock/data/calendar.ts`
- Create: `src/mock/types.ts`

- [ ] **Step 1: Create shared types — `src/mock/types.ts`**

```ts
export type PresenceStatus = 'online' | 'break' | 'offline' | 'clocked-out'
export type LeaveStatus = 'pending' | 'approved' | 'rejected'
export type ExceptionSeverity = 'low' | 'medium' | 'high' | 'critical'

export interface Tenant {
  id: string; name: string; logo: string; primaryColor: string; slug: string
}
export interface Employee {
  id: string; tenantId: string; name: string; avatar: string
  department: string; team: string; jobTitle: string; email: string
  status: PresenceStatus; managerId: string | null; employmentType: 'full-time' | 'part-time' | 'contract'
}
export interface LeaveRequest {
  id: string; employeeId: string; type: string; startDate: string
  endDate: string; status: LeaveStatus; days: number; reason: string
}
export interface ExceptionEvent {
  id: string; employeeId: string; type: string; severity: ExceptionSeverity
  message: string; timestamp: string; resolved: boolean
}
export interface Notification {
  id: string; type: 'approval' | 'alert' | 'mention' | 'info'
  title: string; body: string; timestamp: string; read: boolean
}
export interface WmsBridgeLog {
  bridgeId: string; bridgeName: string; direction: string
  recordCount: number; status: 'success' | 'error'; timestamp: string
}
export interface ActivityEntry {
  employeeId: string; appName: string; duration: number
  category: 'productive' | 'neutral' | 'unproductive'; timestamp: string
}
export interface ProductivityScore {
  employeeId: string; date: string; score: number
  activeHours: number; idleHours: number; topApp: string
}
```

- [ ] **Step 2: Create tenant mock — `src/mock/data/tenants.ts`**

```ts
import type { Tenant } from '../types'

export const tenants: Tenant[] = [
  { id: 't1', name: 'Nexus Corp', logo: '/logos/nexus.svg', primaryColor: '#7C3AED', slug: 'nexus' },
  { id: 't2', name: 'Pinnacle HR', logo: '/logos/pinnacle.svg', primaryColor: '#0EA5E9', slug: 'pinnacle' },
]
export const activeTenant = tenants[0]
```

- [ ] **Step 3: Create employee mock — `src/mock/data/employees.ts`**

```ts
import type { Employee } from '../types'

export const employees: Employee[] = [
  { id: 'e1', tenantId: 't1', name: 'Sarah Lim', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sarah', department: 'Engineering', team: 'Platform', jobTitle: 'Super Admin', email: 'sarah@nexus.com', status: 'online', managerId: null, employmentType: 'full-time' },
  { id: 'e2', tenantId: 't1', name: 'James Rajan', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=james', department: 'Engineering', team: 'Platform', jobTitle: 'Engineering Manager', email: 'james@nexus.com', status: 'online', managerId: 'e1', employmentType: 'full-time' },
  { id: 'e3', tenantId: 't1', name: 'Aisha Noor', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=aisha', department: 'Engineering', team: 'Platform', jobTitle: 'Software Engineer', email: 'aisha@nexus.com', status: 'online', managerId: 'e2', employmentType: 'full-time' },
  { id: 'e4', tenantId: 't1', name: 'Ravi Kumar', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=ravi', department: 'HR', team: 'Talent', jobTitle: 'HR Specialist', email: 'ravi@nexus.com', status: 'break', managerId: 'e2', employmentType: 'full-time' },
  { id: 'e5', tenantId: 't1', name: 'Priya Devi', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=priya', department: 'Finance', team: 'Accounts', jobTitle: 'Finance Analyst', email: 'priya@nexus.com', status: 'offline', managerId: 'e2', employmentType: 'full-time' },
  { id: 'e6', tenantId: 't1', name: 'Hafiz Azman', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=hafiz', department: 'Engineering', team: 'Mobile', jobTitle: 'Mobile Developer', email: 'hafiz@nexus.com', status: 'online', managerId: 'e2', employmentType: 'full-time' },
  { id: 'e7', tenantId: 't1', name: 'Nurul Ain', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=nurul', department: 'Marketing', team: 'Growth', jobTitle: 'Marketing Lead', email: 'nurul@nexus.com', status: 'online', managerId: 'e1', employmentType: 'full-time' },
  { id: 'e8', tenantId: 't1', name: 'Vikram Singh', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=vikram', department: 'Engineering', team: 'Backend', jobTitle: 'Senior Engineer', email: 'vikram@nexus.com', status: 'clocked-out', managerId: 'e2', employmentType: 'full-time' },
  { id: 'e9', tenantId: 't1', name: 'Tan Wei Lin', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=tanwei', department: 'Operations', team: 'Support', jobTitle: 'Ops Coordinator', email: 'tanwei@nexus.com', status: 'online', managerId: 'e1', employmentType: 'contract' },
  { id: 'e10', tenantId: 't1', name: 'Kavitha Raj', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=kavitha', department: 'HR', team: 'Talent', jobTitle: 'Recruiter', email: 'kavitha@nexus.com', status: 'break', managerId: 'e4', employmentType: 'full-time' },
]
```

- [ ] **Step 4: Create presence mock — `src/mock/data/presence.ts`**

```ts
export const presenceEvents = [
  { employeeId: 'e1', type: 'clock-in', timestamp: '2026-04-17T08:01:00Z' },
  { employeeId: 'e2', type: 'clock-in', timestamp: '2026-04-17T08:15:00Z' },
  { employeeId: 'e3', type: 'clock-in', timestamp: '2026-04-17T08:30:00Z' },
  { employeeId: 'e4', type: 'clock-in', timestamp: '2026-04-17T08:45:00Z' },
  { employeeId: 'e4', type: 'break-start', timestamp: '2026-04-17T10:30:00Z' },
  { employeeId: 'e5', type: 'clock-in', timestamp: '2026-04-17T09:00:00Z' },
  { employeeId: 'e5', type: 'clock-out', timestamp: '2026-04-17T12:00:00Z' },
]

export const biometricEvents = [
  { employeeId: 'e1', type: 'fingerprint', result: 'verified', timestamp: '2026-04-17T08:01:05Z' },
  { employeeId: 'e3', type: 'face', result: 'verified', timestamp: '2026-04-17T08:30:02Z' },
  { employeeId: 'e6', type: 'fingerprint', result: 'failed', timestamp: '2026-04-17T08:55:10Z' },
]
```

- [ ] **Step 5: Create activity mock — `src/mock/data/activity.ts`**

```ts
import type { ActivityEntry } from '../types'

export const activityFeed: ActivityEntry[] = [
  { employeeId: 'e1', appName: 'VS Code', duration: 120, category: 'productive', timestamp: '2026-04-17T09:00:00Z' },
  { employeeId: 'e1', appName: 'Chrome', duration: 45, category: 'neutral', timestamp: '2026-04-17T10:00:00Z' },
  { employeeId: 'e1', appName: 'Slack', duration: 30, category: 'productive', timestamp: '2026-04-17T10:45:00Z' },
  { employeeId: 'e2', appName: 'Excel', duration: 90, category: 'productive', timestamp: '2026-04-17T09:00:00Z' },
  { employeeId: 'e2', appName: 'YouTube', duration: 20, category: 'unproductive', timestamp: '2026-04-17T11:30:00Z' },
  { employeeId: 'e3', appName: 'VS Code', duration: 180, category: 'productive', timestamp: '2026-04-17T08:30:00Z' },
  { employeeId: 'e3', appName: 'GitHub', duration: 60, category: 'productive', timestamp: '2026-04-17T11:30:00Z' },
]

export const screenshots = [
  { employeeId: 'e1', url: 'https://placehold.co/320x200?text=VS+Code', timestamp: '2026-04-17T09:30:00Z' },
  { employeeId: 'e1', url: 'https://placehold.co/320x200?text=Chrome', timestamp: '2026-04-17T10:00:00Z' },
  { employeeId: 'e2', url: 'https://placehold.co/320x200?text=Excel', timestamp: '2026-04-17T09:15:00Z' },
  { employeeId: 'e3', url: 'https://placehold.co/320x200?text=VS+Code', timestamp: '2026-04-17T08:45:00Z' },
]
```

- [ ] **Step 6: Create leave mock — `src/mock/data/leave.ts`**

```ts
import type { LeaveRequest } from '../types'

export const leaveRequests: LeaveRequest[] = [
  { id: 'l1', employeeId: 'e3', type: 'Annual', startDate: '2026-04-28', endDate: '2026-04-30', status: 'pending', days: 3, reason: 'Family vacation' },
  { id: 'l2', employeeId: 'e4', type: 'Medical', startDate: '2026-04-20', endDate: '2026-04-21', status: 'approved', days: 2, reason: 'Doctor appointment' },
  { id: 'l3', employeeId: 'e5', type: 'Annual', startDate: '2026-05-05', endDate: '2026-05-09', status: 'approved', days: 5, reason: 'Holiday' },
  { id: 'l4', employeeId: 'e6', type: 'Unpaid', startDate: '2026-05-12', endDate: '2026-05-12', status: 'rejected', days: 1, reason: 'Personal errand' },
]

export const leaveBalances = [
  { employeeId: 'e3', type: 'Annual', entitled: 14, used: 5, pending: 3, remaining: 6 },
  { employeeId: 'e3', type: 'Medical', entitled: 14, used: 2, pending: 0, remaining: 12 },
]
```

- [ ] **Step 7: Create remaining mock files**

`src/mock/data/exceptions.ts`:
```ts
import type { ExceptionEvent } from '../types'
export const exceptionEvents: ExceptionEvent[] = [
  { id: 'ex1', employeeId: 'e4', type: 'Late Clock-In', severity: 'low', message: 'Ravi Kumar clocked in 45 minutes late', timestamp: '2026-04-17T08:45:00Z', resolved: false },
  { id: 'ex2', employeeId: 'e5', type: 'Unproductive App Usage', severity: 'medium', message: 'Priya Devi used YouTube for 20 min during work hours', timestamp: '2026-04-17T11:32:00Z', resolved: false },
  { id: 'ex3', employeeId: 'e6', type: 'Biometric Failure', severity: 'high', message: 'Hafiz Azman fingerprint verification failed 3 times', timestamp: '2026-04-17T08:55:00Z', resolved: true },
  { id: 'ex4', employeeId: 'e8', type: 'No Clock-In', severity: 'critical', message: 'Vikram Singh has not clocked in today', timestamp: '2026-04-17T09:30:00Z', resolved: false },
]
```

`src/mock/data/analytics.ts`:
```ts
import type { ProductivityScore } from '../types'
export const productivityScores: ProductivityScore[] = [
  { employeeId: 'e1', date: '2026-04-17', score: 92, activeHours: 7.2, idleHours: 0.8, topApp: 'VS Code' },
  { employeeId: 'e2', date: '2026-04-17', score: 78, activeHours: 6.5, idleHours: 1.5, topApp: 'Excel' },
  { employeeId: 'e3', date: '2026-04-17', score: 88, activeHours: 7.0, idleHours: 1.0, topApp: 'VS Code' },
  { employeeId: 'e4', date: '2026-04-17', score: 61, activeHours: 5.0, idleHours: 3.0, topApp: 'Chrome' },
]
export const weeklyTrend = [
  { date: '2026-04-11', avg: 74 }, { date: '2026-04-12', avg: 71 },
  { date: '2026-04-13', avg: 79 }, { date: '2026-04-14', avg: 76 },
  { date: '2026-04-15', avg: 82 }, { date: '2026-04-16', avg: 80 },
  { date: '2026-04-17', avg: 83 },
]
```

`src/mock/data/notifications.ts`:
```ts
import type { Notification } from '../types'
export const notifications: Notification[] = [
  { id: 'n1', type: 'approval', title: 'Leave Request', body: 'Aisha Noor has requested 3 days annual leave', timestamp: '2026-04-17T09:00:00Z', read: false },
  { id: 'n2', type: 'alert', title: 'Exception Detected', body: 'Vikram Singh has not clocked in today', timestamp: '2026-04-17T09:30:00Z', read: false },
  { id: 'n3', type: 'mention', title: 'Mentioned by James', body: 'You were mentioned in the Audit Log review', timestamp: '2026-04-17T10:00:00Z', read: true },
  { id: 'n4', type: 'info', title: 'WMS Sync Complete', body: 'Bridge 1: 12 employee records synced successfully', timestamp: '2026-04-17T08:05:00Z', read: true },
]
```

`src/mock/data/wms-bridge.ts`:
```ts
import type { WmsBridgeLog } from '../types'
export const wmsBridgeLogs: WmsBridgeLog[] = [
  { bridgeId: 'b1', bridgeName: 'People Sync', direction: 'HR → WMS', recordCount: 12, status: 'success', timestamp: '2026-04-17T08:05:00Z' },
  { bridgeId: 'b2', bridgeName: 'Availability', direction: 'HR → WMS', recordCount: 8, status: 'success', timestamp: '2026-04-17T08:10:00Z' },
  { bridgeId: 'b3', bridgeName: 'Work Activity', direction: 'WMS → HR', recordCount: 34, status: 'success', timestamp: '2026-04-17T08:15:00Z' },
  { bridgeId: 'b3a', bridgeName: 'Skills Profile Read', direction: 'HR → WMS', recordCount: 5, status: 'success', timestamp: '2026-04-17T08:20:00Z' },
]
```

`src/mock/data/org.ts`:
```ts
export const departments = [
  { id: 'd1', name: 'Engineering', headCount: 6, managerId: 'e2' },
  { id: 'd2', name: 'HR', headCount: 2, managerId: 'e4' },
  { id: 'd3', name: 'Finance', headCount: 1, managerId: 'e5' },
  { id: 'd4', name: 'Marketing', headCount: 1, managerId: 'e7' },
  { id: 'd5', name: 'Operations', headCount: 1, managerId: 'e9' },
]
export const teams = [
  { id: 'tm1', name: 'Platform', departmentId: 'd1', memberIds: ['e1', 'e2', 'e3'] },
  { id: 'tm2', name: 'Mobile', departmentId: 'd1', memberIds: ['e6'] },
  { id: 'tm3', name: 'Backend', departmentId: 'd1', memberIds: ['e8'] },
]
```

`src/mock/data/skills.ts`:
```ts
export const skillCategories = [
  { id: 'sc1', name: 'Technical', skills: [
    { id: 's1', name: 'React', proficiencyLevels: ['Beginner','Developing','Proficient','Advanced','Expert'] },
    { id: 's2', name: '.NET', proficiencyLevels: ['Beginner','Developing','Proficient','Advanced','Expert'] },
    { id: 's3', name: 'PostgreSQL', proficiencyLevels: ['Beginner','Developing','Proficient','Advanced','Expert'] },
  ]},
  { id: 'sc2', name: 'Soft Skills', skills: [
    { id: 's4', name: 'Leadership', proficiencyLevels: ['Beginner','Developing','Proficient','Advanced','Expert'] },
    { id: 's5', name: 'Communication', proficiencyLevels: ['Beginner','Developing','Proficient','Advanced','Expert'] },
  ]},
]
export const employeeSkills = [
  { employeeId: 'e3', skillId: 's1', proficiency: 4, status: 'validated', source: 'self' },
  { employeeId: 'e3', skillId: 's2', proficiency: 3, status: 'pending', source: 'self' },
  { employeeId: 'e3', skillId: 's3', proficiency: 2, status: 'validated', source: 'manager' },
]
```

`src/mock/data/calendar.ts`:
```ts
export const calendarEvents = [
  { id: 'c1', title: 'Company Holiday — Hari Raya', date: '2026-04-29', type: 'holiday' },
  { id: 'c2', title: 'Q2 All-Hands', date: '2026-04-22', type: 'company' },
  { id: 'c3', title: 'Aisha Leave', startDate: '2026-04-28', endDate: '2026-04-30', type: 'leave', employeeId: 'e3' },
  { id: 'c4', title: 'Ravi Medical Leave', startDate: '2026-04-20', endDate: '2026-04-21', type: 'leave', employeeId: 'e4' },
]
```

- [ ] **Step 8: Commit**

```bash
git add src/mock && git commit -m "feat: add mock data layer"
```

---

### Task 3: Zustand Stores

**Files:**
- Create: `src/store/authStore.ts`
- Create: `src/store/liveStore.ts`

- [ ] **Step 1: Create authStore — `src/store/authStore.ts`**

```ts
import { create } from 'zustand'

export type PersonaKey = 'admin' | 'manager' | 'employee'

interface AuthState {
  personaKey: PersonaKey | null
  user: { id: string; name: string; avatar: string; jobTitle: string } | null
  grantedModules: string[]
  permissions: string[]
  tenantId: string
  tenantName: string
  tenantLogo: string
  tenantColor: string
  login: (persona: PersonaKey) => void
  logout: () => void
  updateBranding: (name: string, color: string) => void
}

const personas: Record<PersonaKey, Omit<AuthState, 'login' | 'logout' | 'updateBranding' | 'tenantName' | 'tenantLogo' | 'tenantColor'>> = {
  admin: {
    personaKey: 'admin',
    user: { id: 'e1', name: 'Sarah Lim', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sarah', jobTitle: 'Super Admin' },
    grantedModules: ['core-hr','leave','org-structure','workforce','activity-monitoring','identity-verification','exception-engine','productivity-analytics','calendar','notifications','admin','settings','skills'],
    permissions: ['employees:read','employees:write','leave:read','leave:approve','workforce:read','exceptions:read','exceptions:resolve','admin:read','admin:write','settings:write','skills:manage'],
    tenantId: 't1',
  },
  manager: {
    personaKey: 'manager',
    user: { id: 'e2', name: 'James Rajan', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=james', jobTitle: 'Engineering Manager' },
    grantedModules: ['core-hr','leave','workforce','activity-monitoring','exception-engine','productivity-analytics','calendar','notifications','skills'],
    permissions: ['employees:read','leave:read','leave:approve','workforce:read','exceptions:read','skills:validate'],
    tenantId: 't1',
  },
  employee: {
    personaKey: 'employee',
    user: { id: 'e3', name: 'Aisha Noor', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=aisha', jobTitle: 'Software Engineer' },
    grantedModules: ['leave','calendar','notifications','skills'],
    permissions: ['leave:read','leave:write','skills:write'],
    tenantId: 't1',
  },
}

export const useAuthStore = create<AuthState>((set) => ({
  personaKey: null,
  user: null,
  grantedModules: [],
  permissions: [],
  tenantId: 't1',
  tenantName: 'Nexus Corp',
  tenantLogo: '/logos/nexus.svg',
  tenantColor: '#7C3AED',
  login: (persona) => set({ ...personas[persona], tenantName: 'Nexus Corp', tenantLogo: '/logos/nexus.svg', tenantColor: '#7C3AED' }),
  logout: () => set({ personaKey: null, user: null, grantedModules: [], permissions: [] }),
  updateBranding: (name, color) => set({ tenantName: name, tenantColor: color }),
}))

export const useHasPermission = (permission: string) =>
  useAuthStore((s) => s.permissions.includes(permission))

export const useIsModuleGranted = (module: string) =>
  useAuthStore((s) => s.grantedModules.includes(module))
```

- [ ] **Step 2: Create liveStore — `src/store/liveStore.ts`**

```ts
import { create } from 'zustand'
import type { ExceptionEvent, Notification } from '../mock/types'

interface LiveState {
  presenceStatuses: Record<string, string>
  liveExceptions: ExceptionEvent[]
  liveNotifications: Notification[]
  inboxCount: number
  wmsSyncLog: Array<{ bridgeName: string; recordCount: number; timestamp: string }>
  updatePresence: (employeeId: string, status: string) => void
  addException: (event: ExceptionEvent) => void
  addNotification: (n: Notification) => void
  addWmsLog: (entry: { bridgeName: string; recordCount: number; timestamp: string }) => void
}

export const useLiveStore = create<LiveState>((set) => ({
  presenceStatuses: { e1: 'online', e2: 'online', e3: 'online', e4: 'break', e5: 'offline', e6: 'online', e7: 'online', e8: 'clocked-out', e9: 'online', e10: 'break' },
  liveExceptions: [],
  liveNotifications: [],
  inboxCount: 2,
  wmsSyncLog: [],
  updatePresence: (employeeId, status) =>
    set((s) => ({ presenceStatuses: { ...s.presenceStatuses, [employeeId]: status } })),
  addException: (event) =>
    set((s) => ({ liveExceptions: [event, ...s.liveExceptions].slice(0, 20), inboxCount: s.inboxCount + 1 })),
  addNotification: (n) =>
    set((s) => ({ liveNotifications: [n, ...s.liveNotifications].slice(0, 20), inboxCount: s.inboxCount + 1 })),
  addWmsLog: (entry) =>
    set((s) => ({ wmsSyncLog: [entry, ...s.wmsSyncLog].slice(0, 10) })),
}))
```

- [ ] **Step 3: Commit**

```bash
git add src/store && git commit -m "feat: add Zustand auth + live stores"
```

---

### Task 4: MockEventEngine

**Files:**
- Create: `src/mock/events/MockEventEngine.ts`
- Create: `src/hooks/useMockEventEngine.ts`

- [ ] **Step 1: Create engine — `src/mock/events/MockEventEngine.ts`**

```ts
import { useLiveStore } from '../../store/liveStore'

const presenceCycle: Record<string, string[]> = {
  e4: ['online', 'break', 'online', 'break'],
  e5: ['offline', 'online', 'offline'],
  e10: ['break', 'online', 'break'],
}
const presenceIndexes: Record<string, number> = {}

const exceptionPool = [
  { type: 'Late Clock-In', severity: 'low' as const, employeeId: 'e4', message: 'Ravi Kumar clocked in 45 min late' },
  { type: 'Unproductive App', severity: 'medium' as const, employeeId: 'e5', message: 'Priya Devi used YouTube during work hours' },
  { type: 'No Clock-In', severity: 'critical' as const, employeeId: 'e8', message: 'Vikram Singh has not clocked in' },
]

const bridgePool = [
  { bridgeName: 'People Sync', recordCount: 3 },
  { bridgeName: 'Availability', recordCount: 7 },
  { bridgeName: 'Work Activity', recordCount: 14 },
]

let tick = 0

export function startMockEventEngine() {
  return setInterval(() => {
    tick++
    const store = useLiveStore.getState()

    // Every 4 ticks: flip a presence status
    if (tick % 4 === 0) {
      const employeeId = Object.keys(presenceCycle)[Math.floor(Math.random() * 3)]
      const cycle = presenceCycle[employeeId]
      presenceIndexes[employeeId] = ((presenceIndexes[employeeId] ?? 0) + 1) % cycle.length
      store.updatePresence(employeeId, cycle[presenceIndexes[employeeId]])
    }

    // Every 7 ticks: fire an exception
    if (tick % 7 === 0) {
      const ex = exceptionPool[tick % exceptionPool.length]
      store.addException({ id: `live-ex-${tick}`, resolved: false, timestamp: new Date().toISOString(), ...ex })
    }

    // Every 10 ticks: WMS bridge sync tick
    if (tick % 10 === 0) {
      const bridge = bridgePool[tick % bridgePool.length]
      store.addWmsLog({ ...bridge, timestamp: new Date().toISOString() })
    }
  }, 3000)
}
```

- [ ] **Step 2: Create hook — `src/hooks/useMockEventEngine.ts`**

```ts
import { useEffect } from 'react'
import { startMockEventEngine } from '../mock/events/MockEventEngine'

export function useMockEventEngine() {
  useEffect(() => {
    const interval = startMockEventEngine()
    return () => clearInterval(interval)
  }, [])
}
```

- [ ] **Step 3: Commit**

```bash
git add src/mock/events src/hooks && git commit -m "feat: add MockEventEngine"
```

---

### Task 5: Layout System

**Files:**
- Create: `src/components/layout/IconRail.tsx`
- Create: `src/components/layout/ExpansionPanel.tsx`
- Create: `src/components/layout/Topbar.tsx`
- Create: `src/components/layout/DashboardLayout.tsx`
- Create: `src/components/ui/GlassCard.tsx`
- Create: `src/components/ui/GlassSurface.tsx`
- Create: `src/components/ui/PermissionGate.tsx`

- [ ] **Step 1: Create glass primitives — `src/components/ui/GlassSurface.tsx`**

```tsx
import { cn } from '../../lib/utils'

interface Props { children: React.ReactNode; variant?: 'default' | 'light'; className?: string }

export function GlassSurface({ children, variant = 'default', className }: Props) {
  return (
    <div className={cn(
      'backdrop-blur-md border border-white/10',
      variant === 'default' ? 'bg-white/5' : 'bg-white/8',
      className
    )}>
      {children}
    </div>
  )
}
```

`src/components/ui/GlassCard.tsx`:
```tsx
import { cn } from '../../lib/utils'

interface Props { children: React.ReactNode; glow?: boolean; className?: string; onClick?: () => void }

export function GlassCard({ children, glow, className, onClick }: Props) {
  return (
    <div onClick={onClick} className={cn(
      'rounded-xl backdrop-blur-md bg-white/5 border border-white/10 p-4',
      glow && 'border-violet-500/60 shadow-[0_0_15px_rgba(124,58,237,0.3)]',
      onClick && 'cursor-pointer hover:bg-white/8 transition-colors',
      className
    )}>
      {children}
    </div>
  )
}
```

`src/components/ui/PermissionGate.tsx`:
```tsx
import { useAuthStore } from '../../store/authStore'

interface Props { permission?: string; module?: string; children: React.ReactNode; fallback?: React.ReactNode }

export function PermissionGate({ permission, module, children, fallback = null }: Props) {
  const permissions = useAuthStore((s) => s.permissions)
  const grantedModules = useAuthStore((s) => s.grantedModules)
  if (permission && !permissions.includes(permission)) return <>{fallback}</>
  if (module && !grantedModules.includes(module)) return <>{fallback}</>
  return <>{children}</>
}
```

- [ ] **Step 2: Create IconRail — `src/components/layout/IconRail.tsx`**

```tsx
import { Home, Users, Radio, Building2, CalendarDays, Bell, Settings, Shield } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useLiveStore } from '../../store/liveStore'
import { useIsModuleGranted } from '../../store/authStore'
import { cn } from '../../lib/utils'

const pillars = [
  { icon: Home, label: 'Home', path: '/', module: null },
  { icon: Users, label: 'People', path: '/people', module: 'core-hr' },
  { icon: Radio, label: 'Workforce', path: '/workforce', module: 'workforce' },
  { icon: Building2, label: 'Organization', path: '/org', module: 'org-structure' },
  { icon: CalendarDays, label: 'Calendar', path: '/calendar', module: 'calendar' },
  { icon: Bell, label: 'Inbox', path: '/inbox', module: 'notifications' },
  { icon: Shield, label: 'Admin', path: '/admin', module: 'admin' },
  { icon: Settings, label: 'Settings', path: '/settings', module: 'settings' },
]

export function IconRail() {
  const navigate = useNavigate()
  const location = useLocation()
  const inboxCount = useLiveStore((s) => s.inboxCount)

  return (
    <div className="w-16 h-screen bg-white/5 backdrop-blur-md border-r border-white/10 flex flex-col items-center py-4 gap-2 fixed left-0 top-0 z-50">
      <div className="w-8 h-8 rounded-lg bg-violet-600 mb-4 flex items-center justify-center text-white font-bold text-xs">N</div>
      {pillars.map(({ icon: Icon, label, path, module }) => {
        const granted = useIsModuleGranted(module ?? '')
        if (module && !granted) return null
        const active = location.pathname.startsWith(path) && path !== '/' || location.pathname === path
        return (
          <button key={path} onClick={() => navigate(path)} title={label}
            className={cn('w-10 h-10 rounded-lg flex items-center justify-center relative transition-colors',
              active ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white hover:bg-white/10'
            )}>
            <Icon size={18} />
            {label === 'Inbox' && inboxCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-violet-500 rounded-full text-[10px] flex items-center justify-center text-white animate-pulse">
                {inboxCount}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 3: Create Topbar — `src/components/layout/Topbar.tsx`**

```tsx
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'

export function Topbar() {
  const { user, tenantName, tenantColor } = useAuthStore()
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div className="h-14 bg-white/5 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6 fixed top-0 left-16 right-0 z-40">
      <span className="font-outfit font-semibold text-white/80" style={{ color: tenantColor }}>{tenantName}</span>
      <div className="flex items-center gap-3">
        <span className="text-white/50 text-sm font-geist">{user?.jobTitle}</span>
        <img src={user?.avatar} alt={user?.name} className="w-8 h-8 rounded-full border border-white/20" />
        <span className="text-white/80 text-sm">{user?.name}</span>
        <button onClick={handleLogout} className="text-white/40 hover:text-white/80 ml-2"><LogOut size={16} /></button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create DashboardLayout — `src/components/layout/DashboardLayout.tsx`**

```tsx
import { Outlet, Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { IconRail } from './IconRail'
import { Topbar } from './Topbar'
import { useMockEventEngine } from '../../hooks/useMockEventEngine'

export function DashboardLayout() {
  const personaKey = useAuthStore((s) => s.personaKey)
  useMockEventEngine()

  if (!personaKey) return <Navigate to="/login" replace />

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <IconRail />
      <Topbar />
      <main className="ml-16 pt-14 p-6 min-h-screen">
        <Outlet />
      </main>
    </div>
  )
}
```

- [ ] **Step 5: Wire routes in `src/App.tsx`**

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { DashboardLayout } from './components/layout/DashboardLayout'
import { LoginPage } from './modules/auth/LoginPage'
import { HomePage } from './modules/home/HomePage'
import { EmployeesPage } from './modules/people/employees/EmployeesPage'
import { LeavePage } from './modules/people/leave/LeavePage'
import { WorkforcePage } from './modules/workforce/WorkforcePage'
import { OrgPage } from './modules/org/OrgPage'
import { CalendarPage } from './modules/calendar/CalendarPage'
import { InboxPage } from './modules/inbox/InboxPage'
import { AdminPage } from './modules/admin/AdminPage'
import { SettingsPage } from './modules/settings/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/people/employees/*" element={<EmployeesPage />} />
          <Route path="/people/leave/*" element={<LeavePage />} />
          <Route path="/workforce/*" element={<WorkforcePage />} />
          <Route path="/org/*" element={<OrgPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/inbox" element={<InboxPage />} />
          <Route path="/admin/*" element={<AdminPage />} />
          <Route path="/settings/*" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add src/components src/App.tsx && git commit -m "feat: add layout system (IconRail, Topbar, DashboardLayout)"
```

---

### Task 6: Login Page

**Files:**
- Create: `src/modules/auth/LoginPage.tsx`

- [ ] **Step 1: Create login page — `src/modules/auth/LoginPage.tsx`**

```tsx
import { useNavigate } from 'react-router-dom'
import { useAuthStore, PersonaKey } from '../../store/authStore'
import { GlassCard } from '../../components/ui/GlassCard'

const personas: Array<{ key: PersonaKey; name: string; role: string; seed: string; description: string }> = [
  { key: 'admin', name: 'Sarah Lim', role: 'Super Admin', seed: 'sarah', description: 'Full platform access — all modules, all settings' },
  { key: 'manager', name: 'James Rajan', role: 'Engineering Manager', seed: 'james', description: 'Team view — presence, approvals, exception alerts' },
  { key: 'employee', name: 'Aisha Noor', role: 'Software Engineer', seed: 'aisha', description: 'Self-service — my dashboard, leave, skills' },
]

export function LoginPage() {
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()

  const handleSelect = (key: PersonaKey) => { login(key); navigate('/') }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-full max-w-2xl px-6">
        <div className="text-center mb-10">
          <div className="w-12 h-12 rounded-xl bg-violet-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">N</div>
          <h1 className="text-3xl font-outfit font-bold text-white">Sign in to ONEVO</h1>
          <p className="text-white/50 mt-2">Choose a demo persona to explore the platform</p>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {personas.map((p) => (
            <GlassCard key={p.key} glow onClick={() => handleSelect(p.key)} className="text-center cursor-pointer group">
              <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${p.seed}`}
                alt={p.name} className="w-16 h-16 rounded-full mx-auto mb-3 border-2 border-violet-500/50" />
              <div className="font-outfit font-semibold text-white">{p.name}</div>
              <div className="text-violet-400 text-sm mt-1">{p.role}</div>
              <div className="text-white/40 text-xs mt-2">{p.description}</div>
            </GlassCard>
          ))}
        </div>
        <p className="text-center text-white/30 text-xs mt-8">ONEVO Demo — No real authentication</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add src/modules/auth && git commit -m "feat: add persona-based login page"
```

---

## Phase 2: Core Pages

### Task 7: Home Dashboard

**Files:**
- Create: `src/modules/home/HomePage.tsx`
- Create: `src/modules/home/AdminDashboard.tsx`
- Create: `src/modules/home/ManagerDashboard.tsx`
- Create: `src/modules/home/EmployeeDashboard.tsx`

- [ ] **Step 1: Create AdminDashboard — `src/modules/home/AdminDashboard.tsx`**

```tsx
import { GlassCard } from '../../components/ui/GlassCard'
import { employees } from '../../mock/data/employees'
import { exceptionEvents } from '../../mock/data/exceptions'
import { wmsBridgeLogs } from '../../mock/data/wms-bridge'
import { weeklyTrend } from '../../mock/data/analytics'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export function AdminDashboard() {
  const online = employees.filter(e => e.status === 'online').length
  const openExceptions = exceptionEvents.filter(e => !e.resolved).length

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Overview</h1>
      <div className="grid grid-cols-4 gap-4">
        <GlassCard><div className="text-white/50 text-sm">Total Employees</div><div className="text-3xl font-geist font-bold text-white mt-1">{employees.length}</div></GlassCard>
        <GlassCard><div className="text-white/50 text-sm">Online Now</div><div className="text-3xl font-geist font-bold text-green-400 mt-1">{online}</div></GlassCard>
        <GlassCard glow={openExceptions > 0}><div className="text-white/50 text-sm">Open Exceptions</div><div className="text-3xl font-geist font-bold text-red-400 mt-1">{openExceptions}</div></GlassCard>
        <GlassCard><div className="text-white/50 text-sm">WMS Bridges</div><div className="text-3xl font-geist font-bold text-violet-400 mt-1">{wmsBridgeLogs.length} active</div></GlassCard>
      </div>
      <GlassCard>
        <div className="text-white/70 font-outfit font-semibold mb-4">Avg Productivity — Last 7 Days</div>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={weeklyTrend}>
            <XAxis dataKey="date" tick={{ fill: '#ffffff50', fontSize: 11 }} />
            <YAxis tick={{ fill: '#ffffff50', fontSize: 11 }} domain={[60, 100]} />
            <Tooltip contentStyle={{ background: '#1f1f2e', border: '1px solid #ffffff20', borderRadius: 8 }} />
            <Line type="monotone" dataKey="avg" stroke="#7C3AED" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 2: Create ManagerDashboard — `src/modules/home/ManagerDashboard.tsx`**

```tsx
import { GlassCard } from '../../components/ui/GlassCard'
import { employees } from '../../mock/data/employees'
import { exceptionEvents } from '../../mock/data/exceptions'
import { useLiveStore } from '../../store/liveStore'
import { useAuthStore } from '../../store/authStore'

const statusColor: Record<string, string> = {
  online: 'bg-green-400', break: 'bg-yellow-400', offline: 'bg-gray-500', 'clocked-out': 'bg-red-400'
}

export function ManagerDashboard() {
  const presenceStatuses = useLiveStore((s) => s.presenceStatuses)
  const userId = useAuthStore((s) => s.user?.id)
  const team = employees.filter(e => e.managerId === userId)
  const openExceptions = exceptionEvents.filter(e => !e.resolved)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">My Team</h1>
      <div className="grid grid-cols-2 gap-6">
        <GlassCard>
          <div className="text-white/70 font-outfit font-semibold mb-4">Team Presence</div>
          <div className="space-y-3">
            {team.map(emp => (
              <div key={emp.id} className="flex items-center gap-3">
                <img src={emp.avatar} alt={emp.name} className="w-8 h-8 rounded-full" />
                <div className="flex-1">
                  <div className="text-white text-sm">{emp.name}</div>
                  <div className="text-white/40 text-xs">{emp.jobTitle}</div>
                </div>
                <div className={`w-2 h-2 rounded-full ${statusColor[presenceStatuses[emp.id] ?? 'offline']}`} />
                <span className="text-white/40 text-xs capitalize">{presenceStatuses[emp.id]}</span>
              </div>
            ))}
          </div>
        </GlassCard>
        <GlassCard glow={openExceptions.length > 0}>
          <div className="text-white/70 font-outfit font-semibold mb-4">Open Exceptions</div>
          {openExceptions.length === 0
            ? <div className="text-white/30 text-sm">No open exceptions</div>
            : openExceptions.map(ex => (
              <div key={ex.id} className="mb-3 p-2 rounded-lg bg-white/5">
                <div className="text-white text-sm">{ex.type}</div>
                <div className="text-white/50 text-xs mt-1">{ex.message}</div>
              </div>
            ))
          }
        </GlassCard>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create EmployeeDashboard — `src/modules/home/EmployeeDashboard.tsx`**

```tsx
import { GlassCard } from '../../components/ui/GlassCard'
import { useAuthStore } from '../../store/authStore'
import { leaveBalances } from '../../mock/data/leave'
import { productivityScores } from '../../mock/data/analytics'
import { calendarEvents } from '../../mock/data/calendar'

export function EmployeeDashboard() {
  const user = useAuthStore((s) => s.user)
  const balance = leaveBalances.find(b => b.employeeId === user?.id && b.type === 'Annual')
  const score = productivityScores.find(p => p.employeeId === user?.id)
  const upcoming = calendarEvents.filter(e => e.type !== 'leave').slice(0, 3)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">My Day</h1>
      <div className="grid grid-cols-3 gap-4">
        <GlassCard>
          <div className="text-white/50 text-sm">Productivity Score</div>
          <div className="text-3xl font-geist font-bold text-violet-400 mt-1">{score?.score ?? '—'}%</div>
          <div className="text-white/30 text-xs mt-1">{score?.activeHours}h active · {score?.idleHours}h idle</div>
        </GlassCard>
        <GlassCard>
          <div className="text-white/50 text-sm">Annual Leave Left</div>
          <div className="text-3xl font-geist font-bold text-green-400 mt-1">{balance?.remaining ?? '—'} days</div>
          <div className="text-white/30 text-xs mt-1">{balance?.used} used · {balance?.pending} pending</div>
        </GlassCard>
        <GlassCard>
          <div className="text-white/50 text-sm">Top App Today</div>
          <div className="text-2xl font-outfit font-bold text-white mt-1">{score?.topApp ?? '—'}</div>
        </GlassCard>
      </div>
      <GlassCard>
        <div className="text-white/70 font-outfit font-semibold mb-3">Upcoming Events</div>
        {upcoming.map(ev => (
          <div key={ev.id} className="flex items-center gap-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-violet-400" />
            <span className="text-white text-sm">{ev.title}</span>
            <span className="text-white/30 text-xs ml-auto">{(ev as any).date}</span>
          </div>
        ))}
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 4: Create HomePage — `src/modules/home/HomePage.tsx`**

```tsx
import { useAuthStore } from '../../store/authStore'
import { AdminDashboard } from './AdminDashboard'
import { ManagerDashboard } from './ManagerDashboard'
import { EmployeeDashboard } from './EmployeeDashboard'

export function HomePage() {
  const personaKey = useAuthStore((s) => s.personaKey)
  if (personaKey === 'admin') return <AdminDashboard />
  if (personaKey === 'manager') return <ManagerDashboard />
  return <EmployeeDashboard />
}
```

- [ ] **Step 5: Commit**

```bash
git add src/modules/home && git commit -m "feat: add home dashboard (admin/manager/employee views)"
```

---

## Phase 3: People Section

### Task 8: Employees Pages

**Files:**
- Create: `src/modules/people/employees/EmployeesPage.tsx`
- Create: `src/modules/people/employees/EmployeeDetailPage.tsx`

- [ ] **Step 1: Create EmployeesPage — `src/modules/people/employees/EmployeesPage.tsx`**

```tsx
import { Routes, Route } from 'react-router-dom'
import { employees } from '../../../mock/data/employees'
import { useLiveStore } from '../../../store/liveStore'
import { GlassCard } from '../../../components/ui/GlassCard'
import { useNavigate } from 'react-router-dom'
import { EmployeeDetailPage } from './EmployeeDetailPage'

const statusColor: Record<string, string> = {
  online: 'text-green-400', break: 'text-yellow-400', offline: 'text-gray-400', 'clocked-out': 'text-red-400'
}

function EmployeeList() {
  const presenceStatuses = useLiveStore((s) => s.presenceStatuses)
  const navigate = useNavigate()
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-outfit font-bold text-white">Employees</h1>
        <button className="px-4 py-2 bg-violet-600 rounded-lg text-white text-sm font-outfit hover:bg-violet-700">+ Add Employee</button>
      </div>
      <GlassCard className="p-0 overflow-hidden">
        <table className="w-full">
          <thead><tr className="border-b border-white/10">
            <th className="text-left p-4 text-white/40 text-sm font-outfit">Employee</th>
            <th className="text-left p-4 text-white/40 text-sm font-outfit">Department</th>
            <th className="text-left p-4 text-white/40 text-sm font-outfit">Job Title</th>
            <th className="text-left p-4 text-white/40 text-sm font-outfit">Status</th>
          </tr></thead>
          <tbody>
            {employees.map(emp => (
              <tr key={emp.id} onClick={() => navigate(`/people/employees/${emp.id}`)}
                className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors">
                <td className="p-4 flex items-center gap-3">
                  <img src={emp.avatar} alt={emp.name} className="w-8 h-8 rounded-full" />
                  <div>
                    <div className="text-white text-sm">{emp.name}</div>
                    <div className="text-white/40 text-xs">{emp.email}</div>
                  </div>
                </td>
                <td className="p-4 text-white/70 text-sm">{emp.department}</td>
                <td className="p-4 text-white/70 text-sm">{emp.jobTitle}</td>
                <td className={`p-4 text-sm capitalize font-geist ${statusColor[presenceStatuses[emp.id] ?? 'offline']}`}>
                  {presenceStatuses[emp.id] ?? 'offline'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  )
}

export function EmployeesPage() {
  return (
    <Routes>
      <Route index element={<EmployeeList />} />
      <Route path=":id" element={<EmployeeDetailPage />} />
    </Routes>
  )
}
```

- [ ] **Step 2: Create EmployeeDetailPage — `src/modules/people/employees/EmployeeDetailPage.tsx`**

```tsx
import { useParams, useNavigate } from 'react-router-dom'
import { employees } from '../../../mock/data/employees'
import { employeeSkills, skillCategories } from '../../../mock/data/skills'
import { leaveBalances } from '../../../mock/data/leave'
import { GlassCard } from '../../../components/ui/GlassCard'
import { ArrowLeft } from 'lucide-react'

export function EmployeeDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const emp = employees.find(e => e.id === id)
  if (!emp) return <div className="text-white/50">Employee not found</div>

  const skills = employeeSkills.filter(s => s.employeeId === id)
  const balance = leaveBalances.filter(b => b.employeeId === id)

  return (
    <div className="space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-white/50 hover:text-white text-sm">
        <ArrowLeft size={16} /> Back
      </button>
      <div className="flex items-center gap-6">
        <img src={emp.avatar} alt={emp.name} className="w-20 h-20 rounded-full border-2 border-violet-500/50" />
        <div>
          <h1 className="text-2xl font-outfit font-bold text-white">{emp.name}</h1>
          <div className="text-violet-400">{emp.jobTitle}</div>
          <div className="text-white/40 text-sm">{emp.department} · {emp.team} · {emp.email}</div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-3">Leave Balances</div>
          {balance.length === 0 ? <div className="text-white/30 text-sm">No data</div> : balance.map(b => (
            <div key={b.type} className="flex justify-between mb-2">
              <span className="text-white/70 text-sm">{b.type}</span>
              <span className="text-white font-geist text-sm">{b.remaining} / {b.entitled} days</span>
            </div>
          ))}
        </GlassCard>
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-3">Skills</div>
          {skills.length === 0 ? <div className="text-white/30 text-sm">No skills declared</div> : skills.map(s => {
            const cat = skillCategories.flatMap(c => c.skills).find(sk => sk.id === s.skillId)
            return (
              <div key={s.skillId} className="flex justify-between mb-2">
                <span className="text-white/70 text-sm">{cat?.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${s.status === 'validated' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                  {s.status}
                </span>
              </div>
            )
          })}
        </GlassCard>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add src/modules/people/employees && git commit -m "feat: add employees list + detail pages"
```

---

### Task 9: Leave Pages

**Files:**
- Create: `src/modules/people/leave/LeavePage.tsx`

- [ ] **Step 1: Create LeavePage — `src/modules/people/leave/LeavePage.tsx`**

```tsx
import { useState } from 'react'
import { leaveRequests, leaveBalances } from '../../../mock/data/leave'
import { employees } from '../../../mock/data/employees'
import { GlassCard } from '../../../components/ui/GlassCard'
import { useAuthStore } from '../../../store/authStore'

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500/20 text-yellow-400',
  approved: 'bg-green-500/20 text-green-400',
  rejected: 'bg-red-500/20 text-red-400',
}

export function LeavePage() {
  const personaKey = useAuthStore((s) => s.personaKey)
  const userId = useAuthStore((s) => s.user?.id)
  const [activeTab, setActiveTab] = useState<'requests' | 'balances'>('requests')

  const requests = personaKey === 'employee'
    ? leaveRequests.filter(r => r.employeeId === userId)
    : leaveRequests

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-outfit font-bold text-white">Leave</h1>
        <button className="px-4 py-2 bg-violet-600 rounded-lg text-white text-sm hover:bg-violet-700">+ Apply</button>
      </div>
      <div className="flex gap-2 mb-4">
        {(['requests', 'balances'] as const).map(t => (
          <button key={t} onClick={() => setActiveTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-outfit capitalize transition-colors ${activeTab === t ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>
      {activeTab === 'requests' && (
        <GlassCard className="p-0 overflow-hidden">
          <table className="w-full">
            <thead><tr className="border-b border-white/10">
              <th className="text-left p-4 text-white/40 text-sm">Employee</th>
              <th className="text-left p-4 text-white/40 text-sm">Type</th>
              <th className="text-left p-4 text-white/40 text-sm">Dates</th>
              <th className="text-left p-4 text-white/40 text-sm">Days</th>
              <th className="text-left p-4 text-white/40 text-sm">Status</th>
            </tr></thead>
            <tbody>
              {requests.map(r => {
                const emp = employees.find(e => e.id === r.employeeId)
                return (
                  <tr key={r.id} className="border-b border-white/5">
                    <td className="p-4 text-white text-sm">{emp?.name}</td>
                    <td className="p-4 text-white/70 text-sm">{r.type}</td>
                    <td className="p-4 text-white/70 text-sm font-geist">{r.startDate} → {r.endDate}</td>
                    <td className="p-4 text-white/70 text-sm font-geist">{r.days}</td>
                    <td className="p-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${statusColors[r.status]}`}>{r.status}</span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </GlassCard>
      )}
      {activeTab === 'balances' && (
        <div className="grid grid-cols-3 gap-4">
          {leaveBalances.filter(b => personaKey === 'employee' ? b.employeeId === userId : true).map(b => (
            <GlassCard key={`${b.employeeId}-${b.type}`}>
              <div className="text-white/50 text-sm">{b.type} Leave</div>
              <div className="text-3xl font-geist font-bold text-white mt-1">{b.remaining}</div>
              <div className="text-white/30 text-xs mt-1">of {b.entitled} days · {b.used} used</div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add src/modules/people/leave && git commit -m "feat: add leave requests + balances pages"
```

---

## Phase 4: Workforce Live

### Task 10: Workforce Live Page

**Files:**
- Create: `src/modules/workforce/WorkforcePage.tsx`
- Create: `src/modules/workforce/tabs/ActivityTab.tsx`
- Create: `src/modules/workforce/tabs/WorkInsightsTab.tsx`
- Create: `src/modules/workforce/tabs/OnlineStatusTab.tsx`

- [ ] **Step 1: Create WorkforcePage — `src/modules/workforce/WorkforcePage.tsx`**

```tsx
import { useState } from 'react'
import { ActivityTab } from './tabs/ActivityTab'
import { WorkInsightsTab } from './tabs/WorkInsightsTab'
import { OnlineStatusTab } from './tabs/OnlineStatusTab'

const tabs = ['Activity', 'Work Insights', 'Online Status'] as const
type Tab = typeof tabs[number]

export function WorkforcePage() {
  const [active, setActive] = useState<Tab>('Online Status')
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Workforce Live</h1>
      <div className="flex gap-2">
        {tabs.map(t => (
          <button key={t} onClick={() => setActive(t)}
            className={`px-4 py-2 rounded-lg text-sm font-outfit transition-colors ${active === t ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>
      {active === 'Activity' && <ActivityTab />}
      {active === 'Work Insights' && <WorkInsightsTab />}
      {active === 'Online Status' && <OnlineStatusTab />}
    </div>
  )
}
```

- [ ] **Step 2: Create OnlineStatusTab — `src/modules/workforce/tabs/OnlineStatusTab.tsx`**

```tsx
import { employees } from '../../../mock/data/employees'
import { biometricEvents } from '../../../mock/data/presence'
import { useLiveStore } from '../../../store/liveStore'
import { GlassCard } from '../../../components/ui/GlassCard'

const statusColor: Record<string, string> = {
  online: 'bg-green-400', break: 'bg-yellow-400', offline: 'bg-gray-500', 'clocked-out': 'bg-red-400'
}

export function OnlineStatusTab() {
  const presenceStatuses = useLiveStore((s) => s.presenceStatuses)
  const liveExceptions = useLiveStore((s) => s.liveExceptions)

  const grouped = {
    online: employees.filter(e => presenceStatuses[e.id] === 'online'),
    break: employees.filter(e => presenceStatuses[e.id] === 'break'),
    offline: employees.filter(e => ['offline', 'clocked-out'].includes(presenceStatuses[e.id] ?? '')),
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(grouped).map(([status, emps]) => (
          <GlassCard key={status}>
            <div className="flex items-center gap-2 mb-3">
              <div className={`w-2 h-2 rounded-full ${statusColor[status]}`} />
              <span className="text-white/70 font-outfit capitalize">{status}</span>
              <span className="text-white/40 text-sm ml-auto">{emps.length}</span>
            </div>
            {emps.map(emp => (
              <div key={emp.id} className="flex items-center gap-2 mb-2">
                <img src={emp.avatar} alt={emp.name} className="w-7 h-7 rounded-full" />
                <span className="text-white/80 text-sm">{emp.name}</span>
              </div>
            ))}
          </GlassCard>
        ))}
      </div>
      {liveExceptions.length > 0 && (
        <GlassCard glow>
          <div className="font-outfit font-semibold text-white/70 mb-3">Live Alerts</div>
          {liveExceptions.slice(0, 5).map(ex => (
            <div key={ex.id} className="flex items-start gap-3 mb-3 p-2 rounded-lg bg-white/5">
              <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${ex.severity === 'critical' ? 'bg-red-400' : ex.severity === 'high' ? 'bg-orange-400' : ex.severity === 'medium' ? 'bg-yellow-400' : 'bg-blue-400'}`} />
              <div>
                <div className="text-white text-sm">{ex.type}</div>
                <div className="text-white/40 text-xs">{ex.message}</div>
              </div>
            </div>
          ))}
        </GlassCard>
      )}
      <GlassCard>
        <div className="font-outfit font-semibold text-white/70 mb-3">Biometric Events</div>
        {biometricEvents.map((ev, i) => {
          const emp = employees.find(e => e.id === ev.employeeId)
          return (
            <div key={i} className="flex items-center gap-3 mb-2">
              <img src={emp?.avatar} alt={emp?.name} className="w-7 h-7 rounded-full" />
              <span className="text-white/70 text-sm">{emp?.name}</span>
              <span className="text-white/40 text-xs">{ev.type}</span>
              <span className={`ml-auto text-xs ${ev.result === 'verified' ? 'text-green-400' : 'text-red-400'}`}>{ev.result}</span>
            </div>
          )
        })}
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 3: Create ActivityTab — `src/modules/workforce/tabs/ActivityTab.tsx`**

```tsx
import { activityFeed, screenshots } from '../../../mock/data/activity'
import { employees } from '../../../mock/data/employees'
import { GlassCard } from '../../../components/ui/GlassCard'

const categoryColor: Record<string, string> = {
  productive: 'bg-green-500/20 text-green-400',
  neutral: 'bg-blue-500/20 text-blue-400',
  unproductive: 'bg-red-500/20 text-red-400',
}

export function ActivityTab() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-3">App Usage Feed</div>
          {activityFeed.map((entry, i) => {
            const emp = employees.find(e => e.id === entry.employeeId)
            return (
              <div key={i} className="flex items-center gap-3 mb-3">
                <img src={emp?.avatar} alt={emp?.name} className="w-7 h-7 rounded-full flex-shrink-0" />
                <div className="flex-1">
                  <div className="text-white text-sm">{emp?.name} · <span className="text-violet-400">{entry.appName}</span></div>
                  <div className="text-white/40 text-xs">{entry.duration} min</div>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${categoryColor[entry.category]}`}>{entry.category}</span>
              </div>
            )
          })}
        </GlassCard>
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-3">Screenshots</div>
          <div className="grid grid-cols-2 gap-2">
            {screenshots.map((s, i) => {
              const emp = employees.find(e => e.id === s.employeeId)
              return (
                <div key={i} className="rounded-lg overflow-hidden border border-white/10">
                  <img src={s.url} alt="screenshot" className="w-full" />
                  <div className="p-2 bg-white/5">
                    <div className="text-white/60 text-xs">{emp?.name}</div>
                    <div className="text-white/30 text-xs font-geist">{new Date(s.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create WorkInsightsTab — `src/modules/workforce/tabs/WorkInsightsTab.tsx`**

```tsx
import { productivityScores, weeklyTrend } from '../../../mock/data/analytics'
import { employees } from '../../../mock/data/employees'
import { GlassCard } from '../../../components/ui/GlassCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export function WorkInsightsTab() {
  const chartData = productivityScores.map(s => {
    const emp = employees.find(e => e.id === s.employeeId)
    return { name: emp?.name?.split(' ')[0] ?? s.employeeId, score: s.score }
  })

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-4">Today's Productivity Scores</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fill: '#ffffff50', fontSize: 11 }} />
              <YAxis tick={{ fill: '#ffffff50', fontSize: 11 }} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: '#1f1f2e', border: '1px solid #ffffff20', borderRadius: 8 }} />
              <Bar dataKey="score" fill="#7C3AED" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-4">7-Day Avg Trend</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weeklyTrend}>
              <XAxis dataKey="date" tick={{ fill: '#ffffff50', fontSize: 10 }} />
              <YAxis tick={{ fill: '#ffffff50', fontSize: 11 }} domain={[60, 100]} />
              <Tooltip contentStyle={{ background: '#1f1f2e', border: '1px solid #ffffff20', borderRadius: 8 }} />
              <Line type="monotone" dataKey="avg" stroke="#7C3AED" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>
      <GlassCard>
        <div className="font-outfit font-semibold text-white/70 mb-3">Employee Breakdown</div>
        <table className="w-full">
          <thead><tr className="border-b border-white/10">
            <th className="text-left p-3 text-white/40 text-sm">Employee</th>
            <th className="text-left p-3 text-white/40 text-sm">Score</th>
            <th className="text-left p-3 text-white/40 text-sm">Active Hours</th>
            <th className="text-left p-3 text-white/40 text-sm">Top App</th>
          </tr></thead>
          <tbody>
            {productivityScores.map(s => {
              const emp = employees.find(e => e.id === s.employeeId)
              return (
                <tr key={s.employeeId} className="border-b border-white/5">
                  <td className="p-3 text-white text-sm">{emp?.name}</td>
                  <td className="p-3 font-geist text-violet-400">{s.score}%</td>
                  <td className="p-3 font-geist text-white/70">{s.activeHours}h</td>
                  <td className="p-3 text-white/70 text-sm">{s.topApp}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add src/modules/workforce && git commit -m "feat: add Workforce Live page (Activity, Work Insights, Online Status tabs)"
```

---

## Phase 5: Remaining Sections

### Task 11: Organization

**Files:**
- Create: `src/modules/org/OrgPage.tsx`

- [ ] **Step 1: Create OrgPage — `src/modules/org/OrgPage.tsx`**

```tsx
import { useState } from 'react'
import { departments, teams } from '../../mock/data/org'
import { employees } from '../../mock/data/employees'
import { GlassCard } from '../../components/ui/GlassCard'

export function OrgPage() {
  const [tab, setTab] = useState<'chart' | 'departments' | 'teams'>('chart')

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Organization</h1>
      <div className="flex gap-2">
        {(['chart', 'departments', 'teams'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-outfit capitalize transition-colors ${tab === t ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white'}`}>
            {t === 'chart' ? 'Org Chart' : t}
          </button>
        ))}
      </div>
      {tab === 'chart' && (
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-4">Org Chart</div>
          <div className="flex flex-col items-center gap-6">
            {employees.filter(e => !e.managerId).map(ceo => (
              <div key={ceo.id} className="flex flex-col items-center">
                <div className="flex flex-col items-center p-3 rounded-xl border border-violet-500/40 bg-violet-500/10">
                  <img src={ceo.avatar} alt={ceo.name} className="w-12 h-12 rounded-full mb-2" />
                  <div className="text-white font-outfit text-sm">{ceo.name}</div>
                  <div className="text-violet-400 text-xs">{ceo.jobTitle}</div>
                </div>
                <div className="w-px h-6 bg-white/20" />
                <div className="flex gap-4">
                  {employees.filter(e => e.managerId === ceo.id).map(mgr => (
                    <div key={mgr.id} className="flex flex-col items-center">
                      <div className="flex flex-col items-center p-3 rounded-xl border border-white/10 bg-white/5">
                        <img src={mgr.avatar} alt={mgr.name} className="w-10 h-10 rounded-full mb-2" />
                        <div className="text-white text-sm">{mgr.name}</div>
                        <div className="text-white/40 text-xs">{mgr.jobTitle}</div>
                      </div>
                      <div className="w-px h-4 bg-white/20" />
                      <div className="flex gap-2">
                        {employees.filter(e => e.managerId === mgr.id).map(rep => (
                          <div key={rep.id} className="flex flex-col items-center p-2 rounded-lg border border-white/10 bg-white/5">
                            <img src={rep.avatar} alt={rep.name} className="w-8 h-8 rounded-full mb-1" />
                            <div className="text-white/70 text-xs text-center">{rep.name.split(' ')[0]}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
      {tab === 'departments' && (
        <div className="grid grid-cols-3 gap-4">
          {departments.map(d => {
            const manager = employees.find(e => e.id === d.managerId)
            return (
              <GlassCard key={d.id}>
                <div className="font-outfit font-semibold text-white">{d.name}</div>
                <div className="text-white/40 text-sm mt-1">{d.headCount} employees</div>
                {manager && <div className="flex items-center gap-2 mt-3">
                  <img src={manager.avatar} alt={manager.name} className="w-6 h-6 rounded-full" />
                  <span className="text-white/60 text-xs">{manager.name}</span>
                </div>}
              </GlassCard>
            )
          })}
        </div>
      )}
      {tab === 'teams' && (
        <div className="grid grid-cols-3 gap-4">
          {teams.map(t => {
            const dept = departments.find(d => d.id === t.departmentId)
            return (
              <GlassCard key={t.id}>
                <div className="font-outfit font-semibold text-white">{t.name}</div>
                <div className="text-white/40 text-xs mt-1">{dept?.name}</div>
                <div className="flex gap-1 mt-3">
                  {t.memberIds.map(mid => {
                    const emp = employees.find(e => e.id === mid)
                    return <img key={mid} src={emp?.avatar} alt={emp?.name} className="w-7 h-7 rounded-full border border-white/20" />
                  })}
                </div>
              </GlassCard>
            )
          })}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add src/modules/org && git commit -m "feat: add org chart, departments, teams pages"
```

---

### Task 12: Calendar, Inbox, Admin, Settings

**Files:**
- Create: `src/modules/calendar/CalendarPage.tsx`
- Create: `src/modules/inbox/InboxPage.tsx`
- Create: `src/modules/admin/AdminPage.tsx`
- Create: `src/modules/settings/SettingsPage.tsx`

- [ ] **Step 1: Create CalendarPage — `src/modules/calendar/CalendarPage.tsx`**

```tsx
import { calendarEvents } from '../../mock/data/calendar'
import { GlassCard } from '../../components/ui/GlassCard'

const typeColor: Record<string, string> = {
  holiday: 'bg-red-500/20 text-red-400',
  company: 'bg-blue-500/20 text-blue-400',
  leave: 'bg-yellow-500/20 text-yellow-400',
}

export function CalendarPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Calendar</h1>
      <GlassCard>
        <div className="font-outfit font-semibold text-white/70 mb-4">April 2026</div>
        <div className="space-y-3">
          {calendarEvents.map(ev => (
            <div key={ev.id} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
              <span className={`text-xs px-2 py-1 rounded-full ${typeColor[ev.type]}`}>{ev.type}</span>
              <span className="text-white text-sm">{ev.title}</span>
              <span className="text-white/40 text-xs font-geist ml-auto">{(ev as any).date ?? (ev as any).startDate}</span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  )
}
```

- [ ] **Step 2: Create InboxPage — `src/modules/inbox/InboxPage.tsx`**

```tsx
import { notifications } from '../../mock/data/notifications'
import { useLiveStore } from '../../store/liveStore'
import { GlassCard } from '../../components/ui/GlassCard'

const typeIcon: Record<string, string> = { approval: '✅', alert: '🚨', mention: '💬', info: 'ℹ️' }

export function InboxPage() {
  const liveNotifications = useLiveStore((s) => s.liveNotifications)
  const all = [...liveNotifications, ...notifications]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Inbox</h1>
      <div className="space-y-3">
        {all.map((n, i) => (
          <GlassCard key={n.id ?? i} glow={!n.read} className="flex items-start gap-4">
            <span className="text-xl">{typeIcon[n.type]}</span>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-white font-outfit text-sm font-semibold">{n.title}</span>
                <span className="text-white/30 text-xs font-geist">{new Date(n.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="text-white/60 text-sm mt-1">{n.body}</div>
            </div>
            {!n.read && <div className="w-2 h-2 rounded-full bg-violet-400 flex-shrink-0 mt-1" />}
          </GlassCard>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create AdminPage — `src/modules/admin/AdminPage.tsx`**

```tsx
import { useState } from 'react'
import { employees } from '../../mock/data/employees'
import { GlassCard } from '../../components/ui/GlassCard'
import { PermissionGate } from '../../components/ui/PermissionGate'

const tabs = ['Users & Roles', 'Audit Log', 'Agents', 'Devices', 'Compliance'] as const

export function AdminPage() {
  const [tab, setTab] = useState<typeof tabs[number]>('Users & Roles')
  return (
    <PermissionGate module="admin" fallback={<div className="text-white/50">Access denied</div>}>
      <div className="space-y-6">
        <h1 className="text-2xl font-outfit font-bold text-white">Admin</h1>
        <div className="flex gap-2 flex-wrap">
          {tabs.map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-2 rounded-lg text-sm font-outfit transition-colors ${tab === t ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white'}`}>
              {t}
            </button>
          ))}
        </div>
        {tab === 'Users & Roles' && (
          <GlassCard className="p-0 overflow-hidden">
            <table className="w-full">
              <thead><tr className="border-b border-white/10">
                <th className="text-left p-4 text-white/40 text-sm">User</th>
                <th className="text-left p-4 text-white/40 text-sm">Role</th>
                <th className="text-left p-4 text-white/40 text-sm">Department</th>
              </tr></thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp.id} className="border-b border-white/5">
                    <td className="p-4 flex items-center gap-3">
                      <img src={emp.avatar} alt={emp.name} className="w-7 h-7 rounded-full" />
                      <span className="text-white text-sm">{emp.name}</span>
                    </td>
                    <td className="p-4 text-white/60 text-sm">{emp.jobTitle}</td>
                    <td className="p-4 text-white/60 text-sm">{emp.department}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>
        )}
        {tab === 'Audit Log' && (
          <GlassCard>
            <div className="space-y-3">
              {['Sarah Lim updated employee Aisha Noor', 'James Rajan approved leave request #l2', 'System: WMS Bridge 1 sync completed', 'Sarah Lim created role: HR Manager'].map((entry, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-white/5">
                  <div className="w-2 h-2 rounded-full bg-violet-400 flex-shrink-0" />
                  <span className="text-white/70 text-sm">{entry}</span>
                  <span className="text-white/30 text-xs ml-auto font-geist">2026-04-17 0{8+i}:00</span>
                </div>
              ))}
            </div>
          </GlassCard>
        )}
        {tab === 'Agents' && (
          <GlassCard>
            <div className="font-outfit font-semibold text-white/70 mb-3">Desktop Agents</div>
            {employees.slice(0, 5).map(emp => (
              <div key={emp.id} className="flex items-center gap-3 mb-3 p-2 rounded-lg bg-white/5">
                <img src={emp.avatar} alt={emp.name} className="w-7 h-7 rounded-full" />
                <div>
                  <div className="text-white text-sm">{emp.name}</div>
                  <div className="text-white/40 text-xs">v2.1.4 · Windows 11</div>
                </div>
                <span className="ml-auto text-green-400 text-xs">Online</span>
              </div>
            ))}
          </GlassCard>
        )}
        {tab === 'Devices' && (
          <GlassCard>
            <div className="text-white/50 text-sm">5 registered devices — all compliant</div>
          </GlassCard>
        )}
        {tab === 'Compliance' && (
          <GlassCard>
            <div className="space-y-3">
              {['GDPR Data Retention Policy — Active', 'Screenshot Audit Trail — Enabled', 'Biometric Data Encryption — AES-256', 'Employee Consent Forms — 10/10 signed'].map((item, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-white/5">
                  <span className="text-green-400">✓</span>
                  <span className="text-white/70 text-sm">{item}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        )}
      </div>
    </PermissionGate>
  )
}
```

- [ ] **Step 4: Create SettingsPage — `src/modules/settings/SettingsPage.tsx`**

```tsx
import { useState } from 'react'
import { GlassCard } from '../../components/ui/GlassCard'
import { wmsBridgeLogs } from '../../mock/data/wms-bridge'
import { useLiveStore } from '../../store/liveStore'
import { useAuthStore } from '../../store/authStore'

const tabs = ['General', 'Monitoring', 'Integrations', 'Branding', 'Alert Rules'] as const

export function SettingsPage() {
  const [tab, setTab] = useState<typeof tabs[number]>('General')
  const wmsSyncLog = useLiveStore((s) => s.wmsSyncLog)
  const { tenantName, tenantColor, updateBranding } = useAuthStore()
  const [brandName, setBrandName] = useState(tenantName)
  const [brandColor, setBrandColor] = useState(tenantColor)
  const allBridgeLogs = [...wmsSyncLog, ...wmsBridgeLogs]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-outfit font-bold text-white">Settings</h1>
      <div className="flex gap-2 flex-wrap">
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-outfit transition-colors ${tab === t ? 'bg-violet-600 text-white' : 'text-white/50 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>
      {tab === 'General' && (
        <GlassCard>
          <div className="space-y-4">
            <div><div className="text-white/50 text-sm mb-1">Tenant Name</div><div className="text-white font-outfit">{tenantName}</div></div>
            <div><div className="text-white/50 text-sm mb-1">Plan</div><div className="text-white font-outfit">Full Suite</div></div>
            <div><div className="text-white/50 text-sm mb-1">Timezone</div><div className="text-white font-outfit">Asia/Kuala_Lumpur (UTC+8)</div></div>
          </div>
        </GlassCard>
      )}
      {tab === 'Monitoring' && (
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-4">Monitoring Toggles</div>
          <div className="space-y-4">
            {[
              { label: 'Screenshot Capture', enabled: true },
              { label: 'App Usage Tracking', enabled: true },
              { label: 'Biometric Verification', enabled: true },
              { label: 'Idle Detection', enabled: true },
              { label: 'Screen Recording', enabled: false },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-white/70 text-sm">{item.label}</span>
                <div className={`w-10 h-5 rounded-full transition-colors ${item.enabled ? 'bg-violet-600' : 'bg-white/20'} relative cursor-pointer`}>
                  <div className={`w-4 h-4 rounded-full bg-white absolute top-0.5 transition-all ${item.enabled ? 'right-0.5' : 'left-0.5'}`} />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
      {tab === 'Integrations' && (
        <div className="space-y-4">
          <GlassCard>
            <div className="font-outfit font-semibold text-white/70 mb-3">WMS Bridge Status</div>
            <div className="grid grid-cols-2 gap-3 mb-4">
              {[{name:'People Sync',dir:'HR→WMS'},{name:'Availability',dir:'HR→WMS'},{name:'Work Activity',dir:'WMS→HR'},{name:'Skills Read',dir:'HR→WMS'}].map(b => (
                <div key={b.name} className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <div className="text-green-400 text-xs font-outfit font-semibold">{b.name}</div>
                  <div className="text-white/40 text-xs mt-1">{b.dir} · Active</div>
                </div>
              ))}
            </div>
          </GlassCard>
          <GlassCard>
            <div className="font-outfit font-semibold text-white/70 mb-3">Sync Log</div>
            {allBridgeLogs.map((log, i) => (
              <div key={i} className="flex items-center gap-3 mb-2 p-2 rounded-lg bg-white/5">
                <div className="w-2 h-2 rounded-full bg-green-400 flex-shrink-0" />
                <span className="text-white/70 text-sm">{log.bridgeName}</span>
                <span className="text-white/40 text-xs">{log.direction ?? ''}</span>
                <span className="text-white/40 text-xs font-geist ml-auto">{log.recordCount} records · {new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </GlassCard>
        </div>
      )}
      {tab === 'Branding' && (
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-4">Tenant Branding</div>
          <div className="space-y-4">
            <div>
              <label className="text-white/50 text-sm block mb-1">Company Name</label>
              <input value={brandName} onChange={e => setBrandName(e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-violet-500" />
            </div>
            <div>
              <label className="text-white/50 text-sm block mb-1">Primary Color</label>
              <div className="flex items-center gap-3">
                <input type="color" value={brandColor} onChange={e => setBrandColor(e.target.value)}
                  className="w-10 h-10 rounded-lg border border-white/20 bg-transparent cursor-pointer" />
                <span className="text-white/50 text-sm font-geist">{brandColor}</span>
              </div>
            </div>
            <button onClick={() => updateBranding(brandName, brandColor)}
              className="px-4 py-2 bg-violet-600 rounded-lg text-white text-sm hover:bg-violet-700">
              Apply Branding
            </button>
            <p className="text-white/30 text-xs">Changes apply to topbar logo name and accent color across the platform — demonstrating white-label capability.</p>
          </div>
        </GlassCard>
      )}
      {tab === 'Alert Rules' && (
        <GlassCard>
          <div className="font-outfit font-semibold text-white/70 mb-3">Exception Rules</div>
          {[
            { rule: 'Late Clock-In', threshold: '> 30 min after shift start', severity: 'low' },
            { rule: 'Unproductive App', threshold: '> 15 min during work hours', severity: 'medium' },
            { rule: 'Biometric Failure', threshold: '3 consecutive failures', severity: 'high' },
            { rule: 'No Clock-In', threshold: '60 min after shift start', severity: 'critical' },
          ].map(r => (
            <div key={r.rule} className="flex items-center gap-3 mb-3 p-3 rounded-lg bg-white/5">
              <div>
                <div className="text-white text-sm font-outfit">{r.rule}</div>
                <div className="text-white/40 text-xs">{r.threshold}</div>
              </div>
              <span className={`ml-auto text-xs px-2 py-1 rounded-full ${r.severity === 'critical' ? 'bg-red-500/20 text-red-400' : r.severity === 'high' ? 'bg-orange-500/20 text-orange-400' : r.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-blue-500/20 text-blue-400'}`}>
                {r.severity}
              </span>
            </div>
          ))}
        </GlassCard>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add src/modules/calendar src/modules/inbox src/modules/admin src/modules/settings && git commit -m "feat: add calendar, inbox, admin, settings pages"
```

---

## Final Task: Polish & Verify

- [ ] **Step 1: Run the app**

```bash
npm run dev
```

- [ ] **Step 2: Verify all routes load without errors**

Navigate to each route: `/login`, `/`, `/people/employees`, `/people/leave`, `/workforce`, `/org`, `/calendar`, `/inbox`, `/admin`, `/settings`

- [ ] **Step 3: Verify persona switching**

- Login as each persona → confirm sidebar shows/hides correct items
- Admin sees all 8 pillars; Employee sees only People, Calendar, Inbox

- [ ] **Step 4: Verify MockEventEngine**

- Navigate to Workforce Live → Online Status tab
- Wait 10–30 seconds
- Confirm: presence status changes, live alert fires with violet glow, Inbox badge increments

- [ ] **Step 5: Verify tenant branding**

- Navigate to Settings → Branding
- Change company name and color → click Apply
- Confirm topbar name and accent color update live

- [ ] **Step 6: Verify WMS bridge logs**

- Navigate to Settings → Integrations
- Wait 30 seconds
- Confirm new sync log entries appear (MockEventEngine fires every ~30s)

- [ ] **Step 7: Final commit**

```bash
git add . && git commit -m "feat: ONEVO demo prototype complete — all 15 Phase 1 modules, mock data, live events"
```
