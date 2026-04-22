# Team Creation Hierarchy — Demo Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the React demo to show hierarchy-scoped team creation, the bypass grant Security tab UI, and a bypass-aware calendar participant picker.

**Architecture:** Mock data first → utility functions → UI. Each task builds on the previous. The demo is a Vite + React + TypeScript app with Tailwind CSS and Lucide icons. All data is in-memory mock — no API calls.

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Lucide React, Vite. All files are in `demo/src/`.

---

## File Map

| File | Change Type |
|---|---|
| `demo/src/mock/types.ts` | Add new types; update `Department` and `Employee` |
| `demo/src/mock/data/org.ts` | Restructure departments with hierarchy + add bypass mock data |
| `demo/src/mock/data/employees.ts` | Add `departmentId` field to all employees |
| `demo/src/mock/utils/hierarchyScope.ts` | **New file** — scope resolution utilities |
| `demo/src/modules/org/OrgPage.tsx` | Add Create Team button + `CreateTeamModal` with tier-aware form |
| `demo/src/modules/people/employees/EmployeeProfile.tsx` | Add Security tab with Bypass Grants section |
| `demo/src/modules/calendar/CalendarPage.tsx` | Replace individual audience text input with employee search picker showing bypass badge |

---

## Task 1: Update mock types

**Files:**
- Modify: `demo/src/mock/types.ts`

- [ ] **Step 1: Read the current file**

Open `demo/src/mock/types.ts` and note the existing `Employee` and any org types.

- [ ] **Step 2: Add new types and update existing ones**

Add the following to `demo/src/mock/types.ts`. Find the `Employee` interface and add the `departmentId` field. Then append all new interfaces after the existing ones:

```typescript
// Add to Employee interface:
departmentId: string

// New interfaces — add at the bottom of the file:

export interface Department {
  id: string
  name: string
  parentDepartmentId: string | null
  headEmployeeId: string | null
  headCount: number
}

export interface Team {
  id: string
  name: string
  departmentId: string
  teamLeadId: string | null
  memberIds: string[]
  description?: string
}

export type ScopeType = 'department' | 'people' | 'role'

export interface HierarchyScopeException {
  id: string
  tenantId: string
  grantedToEmployeeId: string
  scopeType: ScopeType
  scopeId: string
  appliesTo: string | null  // null = all features
  grantedByEmployeeId: string
  createdAt: string
  expiresAt: string | null
}

export interface PermissionDelegationScope {
  id: string
  tenantId: string
  delegatedToEmployeeId: string
  moduleScope: string[]
  delegatedByEmployeeId: string
  createdAt: string
  expiresAt: string | null
}

export type CreatorTier = 'root' | 'parent' | 'leaf' | 'non-head'
```

- [ ] **Step 3: Run the TypeScript compiler to check for errors**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -30
```

Expected: errors only about `departmentId` missing on existing employee objects (will fix in Task 2). No syntax errors.

- [ ] **Step 4: Commit**

```bash
git add demo/src/mock/types.ts
git commit -m "feat(demo): add Department, Team, HierarchyScopeException types"
```

---

## Task 2: Update mock data — org and employees

**Files:**
- Modify: `demo/src/mock/data/org.ts`
- Modify: `demo/src/mock/data/employees.ts`

- [ ] **Step 1: Read both files**

Open `demo/src/mock/data/org.ts` and `demo/src/mock/data/employees.ts`.

- [ ] **Step 2: Rewrite org.ts with hierarchy + bypass data**

Replace the entire contents of `demo/src/mock/data/org.ts` with:

```typescript
import type { Department, Team, HierarchyScopeException } from '../types'

export const departments: Department[] = [
  // Root — Sarah (e1) is head, no parent
  { id: 'd0', name: 'NEXUS Technologies', parentDepartmentId: null, headEmployeeId: 'e1', headCount: 12 },
  // Mid-level parents under root
  { id: 'd1', name: 'Engineering', parentDepartmentId: 'd0', headEmployeeId: 'e2', headCount: 6 },
  { id: 'd2', name: 'HR', parentDepartmentId: 'd0', headEmployeeId: 'e4', headCount: 2 },
  { id: 'd3', name: 'Finance', parentDepartmentId: 'd0', headEmployeeId: 'e5', headCount: 1 },
  { id: 'd4', name: 'Marketing', parentDepartmentId: 'd0', headEmployeeId: 'e7', headCount: 1 },
  // Leaf departments under Engineering — James (e2) heads Engineering which has children
  { id: 'd1a', name: 'Platform Engineering', parentDepartmentId: 'd1', headEmployeeId: 'e3', headCount: 3 },
  { id: 'd1b', name: 'Mobile Engineering', parentDepartmentId: 'd1', headEmployeeId: 'e6', headCount: 2 },
]

export const teams: Team[] = [
  { id: 'tm1', name: 'Platform', departmentId: 'd1a', teamLeadId: 'e3', memberIds: ['e1', 'e2', 'e3'] },
  { id: 'tm2', name: 'Mobile', departmentId: 'd1b', teamLeadId: 'e6', memberIds: ['e6'] },
  { id: 'tm3', name: 'Backend', departmentId: 'd1', teamLeadId: 'e8', memberIds: ['e8'] },
]

// Bypass grants:
// James (e2, Engineering parent head) can add HR dept employees to calendar events
// This does NOT apply to teams (appliesTo = 'calendar' only)
export const hierarchyScopeExceptions: HierarchyScopeException[] = [
  {
    id: 'hse1',
    tenantId: 't1',
    grantedToEmployeeId: 'e2',
    scopeType: 'department',
    scopeId: 'd2',
    appliesTo: 'calendar',
    grantedByEmployeeId: 'e1',
    createdAt: '2026-04-01',
    expiresAt: null,
  },
  // Priya (e5, Finance head — leaf dept) can add Vikram (e8) to calendar events individually
  {
    id: 'hse2',
    tenantId: 't1',
    grantedToEmployeeId: 'e5',
    scopeType: 'people',
    scopeId: 'e8',
    appliesTo: 'calendar',
    grantedByEmployeeId: 'e1',
    createdAt: '2026-04-05',
    expiresAt: null,
  },
]
```

- [ ] **Step 3: Update employees.ts — add departmentId to every employee**

Open `demo/src/mock/data/employees.ts`. Add `departmentId` to each employee object. Here is the mapping:

```typescript
// Add these departmentId fields to the matching employees:
// e1 — Sarah Lim: departmentId: 'd0'     (heads root dept NEXUS Technologies)
// e2 — James Rajan: departmentId: 'd1'   (heads Engineering, mid-level parent)
// e3 — Aisha Noor: departmentId: 'd1a'   (heads Platform Engineering, leaf)
// e4 — Ravi Kumar: departmentId: 'd2'    (heads HR, mid-level)
// e5 — Priya Devi: departmentId: 'd3'    (heads Finance, mid-level — but Finance has no children so leaf in practice)
// e6 — Hafiz Azman: departmentId: 'd1b'  (heads Mobile Engineering, leaf)
// e7 — Nurul Ain: departmentId: 'd4'     (heads Marketing, mid-level)
// e8 — Vikram Singh: departmentId: 'd1'  (member of Engineering, no heading)
// e9 and beyond: use 'd1' or appropriate existing dept id
```

For example, the e1 entry becomes:
```typescript
{ id: 'e1', tenantId: 't1', name: 'Sarah Lim', ..., departmentId: 'd0' },
```

Add `departmentId` to every employee object in the array.

- [ ] **Step 4: Run TypeScript check**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors (all `departmentId` fields now present).

- [ ] **Step 5: Commit**

```bash
git add demo/src/mock/data/org.ts demo/src/mock/data/employees.ts
git commit -m "feat(demo): restructure departments with parent-child hierarchy and add bypass mock data"
```

---

## Task 3: Create hierarchy scope utility

**Files:**
- Create: `demo/src/mock/utils/hierarchyScope.ts`

- [ ] **Step 1: Create the utils directory if it doesn't exist**

```bash
mkdir -p demo/src/mock/utils
```

- [ ] **Step 2: Write hierarchyScope.ts**

Create `demo/src/mock/utils/hierarchyScope.ts`:

```typescript
import { employees } from '../data/employees'
import { departments, teams, hierarchyScopeExceptions } from '../data/org'
import type { CreatorTier } from '../types'

// Returns all employee IDs below employeeId in the managerId chain (recursive)
export function resolveSubordinates(employeeId: string): Set<string> {
  const result = new Set<string>()
  const queue = [employeeId]
  while (queue.length > 0) {
    const current = queue.shift()!
    const directs = employees.filter(e => e.managerId === current)
    for (const d of directs) {
      result.add(d.id)
      queue.push(d.id)
    }
  }
  return result
}

// Returns employee IDs from active bypass grants for employeeId
// featureContext: if provided, matches applies_to IS NULL or applies_to = featureContext
//                if null, matches applies_to IS NULL only
export function resolveBypassIds(
  employeeId: string,
  featureContext: string | null = null
): Set<string> {
  const now = new Date()
  const matchingGrants = hierarchyScopeExceptions.filter(hse => {
    if (hse.grantedToEmployeeId !== employeeId) return false
    if (hse.expiresAt && new Date(hse.expiresAt) < now) return false
    if (featureContext !== null) {
      return hse.appliesTo === null || hse.appliesTo === featureContext
    }
    return hse.appliesTo === null
  })

  const result = new Set<string>()
  for (const grant of matchingGrants) {
    if (grant.scopeType === 'people') {
      result.add(grant.scopeId)
    } else if (grant.scopeType === 'department') {
      employees
        .filter(e => e.departmentId === grant.scopeId)
        .forEach(e => result.add(e.id))
    }
    // role scope_type omitted from demo for simplicity
  }
  return result
}

// Returns all departments accessible for dept selection by employeeId
// Root head: all depts; Parent head: dept + descendants; Leaf/non-head: own dept only
export function getAccessibleDepartments(employeeId: string): typeof departments {
  const tier = resolveCreatorTier(employeeId)
  const emp = employees.find(e => e.id === employeeId)
  if (!emp) return []

  if (tier === 'root') return departments

  if (tier === 'parent') {
    const headedDept = departments.find(
      d => d.headEmployeeId === employeeId && d.parentDepartmentId !== null && hasChildren(d.id)
    )
    if (!headedDept) return []
    return getDeptAndDescendants(headedDept.id)
  }

  // leaf / non-head — own department only
  const ownDept = departments.find(d => d.id === emp.departmentId)
  return ownDept ? [ownDept] : []
}

// Returns the accessible member pool for team creation
// For leaf/non-head: subordinates filtered to same dept + bypassIds
// For root/parent: all subordinates + bypassIds
export function resolveTeamMemberPool(employeeId: string): {
  members: typeof employees
  bypassMemberIds: Set<string>
} {
  const tier = resolveCreatorTier(employeeId)
  const emp = employees.find(e => e.id === employeeId)
  const subordinates = resolveSubordinates(employeeId)
  const bypassIds = resolveBypassIds(employeeId, 'teams')

  let basePool: typeof employees
  if (tier === 'leaf' || tier === 'non-head') {
    basePool = employees.filter(
      e => subordinates.has(e.id) && e.departmentId === emp?.departmentId
    )
  } else {
    basePool = employees.filter(e => subordinates.has(e.id))
  }

  const bypassMembers = employees.filter(e => bypassIds.has(e.id))
  const allMembers = [...basePool, ...bypassMembers.filter(b => !basePool.find(m => m.id === b.id))]

  return { members: allMembers, bypassMemberIds: bypassIds }
}

// Returns the accessible participant pool for calendar events
export function resolveCalendarParticipantPool(employeeId: string): {
  participants: typeof employees
  bypassParticipantIds: Set<string>
} {
  const subordinates = resolveSubordinates(employeeId)
  const bypassIds = resolveBypassIds(employeeId, 'calendar')

  const basePool = employees.filter(e => subordinates.has(e.id))
  const bypassParticipants = employees.filter(e => bypassIds.has(e.id))
  const allParticipants = [
    ...basePool,
    ...bypassParticipants.filter(b => !basePool.find(m => m.id === b.id)),
  ]

  return { participants: allParticipants, bypassParticipantIds: bypassIds }
}

// Determines the creator tier for an employee
export function resolveCreatorTier(employeeId: string): CreatorTier {
  const headedDepts = departments.filter(d => d.headEmployeeId === employeeId)
  if (headedDepts.length === 0) return 'non-head'

  // Check root first
  if (headedDepts.some(d => d.parentDepartmentId === null)) return 'root'

  // Check parent (heads a dept that has children)
  if (headedDepts.some(d => hasChildren(d.id))) return 'parent'

  return 'leaf'
}

function hasChildren(deptId: string): boolean {
  return departments.some(d => d.parentDepartmentId === deptId)
}

function getDeptAndDescendants(deptId: string): typeof departments {
  const result: typeof departments = []
  const queue = [deptId]
  while (queue.length > 0) {
    const current = queue.shift()!
    const dept = departments.find(d => d.id === current)
    if (dept) {
      result.push(dept)
      departments
        .filter(d => d.parentDepartmentId === current)
        .forEach(d => queue.push(d.id))
    }
  }
  return result
}
```

- [ ] **Step 3: Run TypeScript check**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add demo/src/mock/utils/hierarchyScope.ts
git commit -m "feat(demo): add hierarchy scope utility with tier resolution and bypass grant support"
```

---

## Task 4: Add Create Team modal to OrgPage

**Files:**
- Modify: `demo/src/modules/org/OrgPage.tsx`

- [ ] **Step 1: Read OrgPage.tsx**

Open `demo/src/modules/org/OrgPage.tsx`. Find the Teams tab section (`{tab === 'teams' && ...}`).

- [ ] **Step 2: Add imports at the top of OrgPage.tsx**

Add these imports after the existing imports:

```typescript
import { useState } from 'react'
import { Plus, X, Lock } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import {
  resolveCreatorTier,
  getAccessibleDepartments,
  resolveTeamMemberPool,
} from '../../mock/utils/hierarchyScope'
import { employees } from '../../mock/data/employees'
import type { Team } from '../../mock/types'
```

- [ ] **Step 3: Add CreateTeamModal component**

Add this component above the `OrgPage` function (before `export function OrgPage`):

```typescript
function CreateTeamModal({
  onClose,
  onSave,
}: {
  onClose: () => void
  onSave: (team: Team) => void
}) {
  const { user } = useAuthStore()
  const creatorId = user?.id ?? 'e2'

  const tier = resolveCreatorTier(creatorId)
  const accessibleDepts = getAccessibleDepartments(creatorId)
  const { members, bypassMemberIds } = resolveTeamMemberPool(creatorId)

  const creatorEmp = employees.find(e => e.id === creatorId)
  const defaultDeptId = accessibleDepts[0]?.id ?? creatorEmp?.departmentId ?? ''

  const [name, setName] = useState('')
  const [deptId, setDeptId] = useState(defaultDeptId)
  const [leadId, setLeadId] = useState('')
  const [selectedMembers, setSelectedMembers] = useState<string[]>([])

  const canPickDept = tier === 'root' || tier === 'parent'

  function toggleMember(id: string) {
    setSelectedMembers(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    )
  }

  function handleSave() {
    if (!name.trim()) return
    onSave({
      id: `tm${Date.now()}`,
      name: name.trim(),
      departmentId: deptId,
      teamLeadId: leadId || null,
      memberIds: selectedMembers,
    })
    onClose()
  }

  const input = 'w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.09] text-white text-sm font-geist outline-none focus:border-violet-500/50'
  const label = 'block text-white/40 text-xs font-outfit uppercase tracking-wider mb-1.5'

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={onClose} />
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="w-full max-w-md bg-[#13121c] border border-white/[0.09] rounded-2xl shadow-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-white font-outfit font-semibold text-base">Create Team</h2>
            <button onClick={onClose} className="text-white/40 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Team Name */}
          <div>
            <label className={label}>Team Name</label>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. Frontend Guild"
              className={input}
            />
          </div>

          {/* Department */}
          <div>
            <label className={label}>Department</label>
            {canPickDept ? (
              <select
                value={deptId}
                onChange={e => setDeptId(e.target.value)}
                className={input}
              >
                {accessibleDepts.map(d => (
                  <option key={d.id} value={d.id} className="bg-[#13121c]">
                    {d.name}
                  </option>
                ))}
              </select>
            ) : (
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                <Lock className="w-3.5 h-3.5 text-white/25" />
                <span className="text-white/50 text-sm font-geist">
                  {accessibleDepts[0]?.name ?? '—'}
                </span>
              </div>
            )}
            {!canPickDept && (
              <p className="text-white/25 text-xs mt-1.5 font-geist">
                Department locked to your scope
              </p>
            )}
          </div>

          {/* Team Lead */}
          <div>
            <label className={label}>Team Lead</label>
            <select value={leadId} onChange={e => setLeadId(e.target.value)} className={input}>
              <option value="" className="bg-[#13121c]">— No lead —</option>
              {members.map(m => (
                <option key={m.id} value={m.id} className="bg-[#13121c]">
                  {m.name}
                  {bypassMemberIds.has(m.id) ? ' (Bypass)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Members */}
          <div>
            <label className={label}>Members</label>
            <div className="max-h-36 overflow-y-auto space-y-1 pr-1">
              {members.map(m => {
                const isBypass = bypassMemberIds.has(m.id)
                const checked = selectedMembers.includes(m.id)
                return (
                  <label
                    key={m.id}
                    className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-white/[0.03] cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleMember(m.id)}
                      className="accent-violet-500"
                    />
                    <img src={m.avatar} alt={m.name} className="w-5 h-5 rounded-full" />
                    <span className="text-white/70 text-sm font-geist flex-1">{m.name}</span>
                    {isBypass && (
                      <span className="text-[10px] font-outfit font-medium px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20">
                        Bypass
                      </span>
                    )}
                  </label>
                )
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 rounded-lg border border-white/[0.09] text-white/60 text-sm font-outfit hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!name.trim()}
              className="flex-1 px-4 py-2 rounded-lg bg-violet-600 text-white text-sm font-outfit font-medium hover:bg-violet-500 transition-colors disabled:opacity-40"
            >
              Create Team
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
```

- [ ] **Step 4: Wire up state and button in OrgPage**

Inside `export function OrgPage()`, add:

```typescript
const [teams, setTeams] = useState<Team[]>(initialTeams)
const [showCreateTeam, setShowCreateTeam] = useState(false)
```

And import `teams as initialTeams` instead of `teams` directly from org data:

```typescript
import { departments, teams as initialTeams, hierarchyScopeExceptions } from '../../mock/data/org'
```

- [ ] **Step 5: Add Create Team button in the Teams tab header**

Find the `{tab === 'teams' && (` section. Add a header row before the grid:

```typescript
{tab === 'teams' && (
  <div className="space-y-4">
    <div className="flex items-center justify-between">
      <h2 className="text-white/60 text-sm font-outfit">Teams</h2>
      <button
        onClick={() => setShowCreateTeam(true)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-600/80 hover:bg-violet-600 text-white text-xs font-outfit font-medium transition-colors"
      >
        <Plus className="w-3.5 h-3.5" />
        Create Team
      </button>
    </div>
    <div className="grid grid-cols-3 gap-4">
      {/* existing teams.map(...) */}
    </div>
    {showCreateTeam && (
      <CreateTeamModal
        onClose={() => setShowCreateTeam(false)}
        onSave={team => setTeams(prev => [...prev, team])}
      />
    )}
  </div>
)}
```

- [ ] **Step 6: Start the dev server and verify**

```bash
cd demo && npm run dev
```

Open `http://localhost:5173`. Navigate to Organization → Teams tab.

Verify:
- "Create Team" button is visible
- Clicking it opens the modal
- Login as James (e2): department picker shows Engineering + Platform Engineering + Mobile Engineering (parent head tier)
- Login as Aisha (e3): department is locked to "Platform Engineering" (leaf head tier)
- Login as Sarah (e1): all departments shown (root head tier)
- Members list shows "Bypass" badge for bypass-granted employees
- Saving adds the team to the list

- [ ] **Step 7: Commit**

```bash
git add demo/src/modules/org/OrgPage.tsx
git commit -m "feat(demo): add hierarchy-aware Create Team modal to OrgPage"
```

---

## Task 5: Add Security tab with Bypass Grants to EmployeeProfile

**Files:**
- Modify: `demo/src/modules/people/employees/EmployeeProfile.tsx`

- [ ] **Step 1: Read EmployeeProfile.tsx**

Open `demo/src/modules/people/employees/EmployeeProfile.tsx`. Find the tab definitions array (the array containing `overview`, `leave`, etc.) and the `renderTab` function.

- [ ] **Step 2: Add imports**

Add to the existing imports:

```typescript
import { ShieldCheck, Plus, X, Trash2 } from 'lucide-react'
import { hierarchyScopeExceptions, departments } from '../../../mock/data/org'
import { employees as allEmployees } from '../../../mock/data/employees'
import type { HierarchyScopeException, ScopeType } from '../../../mock/types'
import {
  resolveCreatorTier,
  getAccessibleDepartments,
} from '../../../mock/utils/hierarchyScope'
// NOTE: useState is already imported at the top of EmployeeProfile.tsx — do NOT add a duplicate import
```

- [ ] **Step 3: Add Security tab to the tabs array**

Find the `moreTabs` or main tabs array in the component. Add the Security tab entry:

```typescript
{ id: 'security', label: 'Security', Icon: ShieldCheck }
```

Add it to whichever array the other tabs live in (check the file — it uses a `moreTabs` array for overflow tabs).

- [ ] **Step 4: Add renderTab case for 'security'**

Inside `renderTab()`, add a new case:

```typescript
case 'security':
  return <SecurityTab employeeId={emp.id} />
```

- [ ] **Step 5: Add SecurityTab component**

Add this component above `EmployeeProfile` in the file:

```typescript
function AddBypassGrantModal({
  targetEmployeeId,
  grantorId,
  onClose,
  onSave,
}: {
  targetEmployeeId: string
  grantorId: string
  onClose: () => void
  onSave: (grant: HierarchyScopeException) => void
}) {
  const accessibleDepts = getAccessibleDepartments(grantorId)
  const tier = resolveCreatorTier(grantorId)
  const isRootAdmin = tier === 'root'

  const [scopeType, setScopeType] = useState<ScopeType>('department')
  const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
  const [appliesTo, setAppliesTo] = useState<string>('calendar')

  const featureOptions = ['calendar', 'teams', 'attendance']

  function handleSave() {
    onSave({
      id: `hse-${Date.now()}`,
      tenantId: 't1',
      grantedToEmployeeId: targetEmployeeId,
      scopeType,
      scopeId,
      appliesTo: appliesTo === 'all' ? null : appliesTo,
      grantedByEmployeeId: grantorId,
      createdAt: new Date().toISOString().split('T')[0],
      expiresAt: null,
    })
    onClose()
  }

  const input = 'w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.09] text-white text-sm font-geist outline-none focus:border-violet-500/50'
  const label = 'block text-white/40 text-xs font-outfit uppercase tracking-wider mb-1.5'

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={onClose} />
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="w-full max-w-sm bg-[#13121c] border border-white/[0.09] rounded-2xl shadow-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-white font-outfit font-semibold text-sm">Add Bypass Grant</h3>
            <button onClick={onClose} className="text-white/40 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div>
            <label className={label}>Scope Type</label>
            <select
              value={scopeType}
              onChange={e => setScopeType(e.target.value as ScopeType)}
              className={input}
            >
              <option value="department" className="bg-[#13121c]">Department</option>
              <option value="people" className="bg-[#13121c]">Person</option>
              <option value="role" className="bg-[#13121c]">Role</option>
            </select>
          </div>

          {scopeType === 'department' && (
            <div>
              <label className={label}>Department</label>
              <select value={scopeId} onChange={e => setScopeId(e.target.value)} className={input}>
                {accessibleDepts.map(d => (
                  <option key={d.id} value={d.id} className="bg-[#13121c]">{d.name}</option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className={label}>Applies To</label>
            <select value={appliesTo} onChange={e => setAppliesTo(e.target.value)} className={input}>
              {isRootAdmin && (
                <option value="all" className="bg-[#13121c]">All Features</option>
              )}
              {featureOptions.map(f => (
                <option key={f} value={f} className="bg-[#13121c]">
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </option>
              ))}
            </select>
            {!isRootAdmin && (
              <p className="text-white/25 text-xs mt-1.5 font-geist">
                "All Features" restricted to root administrators
              </p>
            )}
          </div>

          <div className="flex gap-2 pt-1">
            <button onClick={onClose} className="flex-1 px-3 py-2 rounded-lg border border-white/[0.09] text-white/60 text-sm font-outfit hover:text-white transition-colors">
              Cancel
            </button>
            <button onClick={handleSave} className="flex-1 px-3 py-2 rounded-lg bg-violet-600 text-white text-sm font-outfit font-medium hover:bg-violet-500 transition-colors">
              Save Grant
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

function SecurityTab({ employeeId }: { employeeId: string }) {
  const { user } = useAuthStore()
  const grantorId = user?.id ?? 'e1'

  const [grants, setGrants] = useState<HierarchyScopeException[]>(
    () => hierarchyScopeExceptions.filter(h => h.grantedToEmployeeId === employeeId)
  )
  const [showAdd, setShowAdd] = useState(false)

  function removeGrant(id: string) {
    setGrants(prev => prev.filter(g => g.id !== id))
  }

  function getScopeLabel(grant: HierarchyScopeException): string {
    if (grant.scopeType === 'department') {
      return departments.find(d => d.id === grant.scopeId)?.name ?? grant.scopeId
    }
    if (grant.scopeType === 'people') {
      return allEmployees.find(e => e.id === grant.scopeId)?.name ?? grant.scopeId
    }
    return grant.scopeId
  }

  return (
    <div className="space-y-4">
      {/* Effective Permissions — simplified mock */}
      <GlassCard>
        <p className="text-white/30 text-xs font-outfit uppercase tracking-wider mb-3">Effective Permissions</p>
        <div className="flex flex-wrap gap-1.5">
          {['employees:read', 'calendar:write', 'org:manage', 'attendance:read'].map(p => (
            <span key={p} className="text-[11px] font-geist px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20">
              {p}
            </span>
          ))}
        </div>
      </GlassCard>

      {/* Bypass Grants */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <p className="text-white/30 text-xs font-outfit uppercase tracking-wider">Bypass Grants</p>
          <button
            onClick={() => setShowAdd(true)}
            className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 font-outfit transition-colors"
          >
            <Plus className="w-3 h-3" />
            Add Grant
          </button>
        </div>

        {grants.length === 0 ? (
          <p className="text-white/25 text-sm font-geist">No bypass grants configured.</p>
        ) : (
          <div className="space-y-2">
            {grants.map(grant => (
              <div
                key={grant.id}
                className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.06]"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-outfit font-medium text-white/70 capitalize">
                      {grant.scopeType}:
                    </span>
                    <span className="text-xs font-geist text-white/50">
                      {getScopeLabel(grant)}
                    </span>
                  </div>
                  <span className="text-[11px] font-geist text-white/30">
                    Applies to: {grant.appliesTo ?? 'All Features'}
                  </span>
                </div>
                <button
                  onClick={() => removeGrant(grant.id)}
                  className="text-white/20 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </GlassCard>

      {showAdd && (
        <AddBypassGrantModal
          targetEmployeeId={employeeId}
          grantorId={grantorId}
          onClose={() => setShowAdd(false)}
          onSave={grant => {
            setGrants(prev => [...prev, grant])
            setShowAdd(false)
          }}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 6: Start dev server and verify**

```bash
cd demo && npm run dev
```

Navigate to People → any employee → Security tab.

Verify:
- Security tab appears in the tab list
- Effective Permissions shows mock permissions
- Bypass Grants section shows existing grants (e.g., James e2 has HR dept bypass for calendar)
- "Add Grant" opens the modal
- Scope type selector changes the scope picker
- "All Features" only visible when logged in as root admin (e1)
- Delete button removes a grant
- Saved grant appears in the list

- [ ] **Step 7: Commit**

```bash
git add demo/src/modules/people/employees/EmployeeProfile.tsx
git commit -m "feat(demo): add Security tab with Bypass Grants section to employee profile"
```

---

## Task 6: Update calendar event individual participant picker

**Files:**
- Modify: `demo/src/modules/calendar/CalendarPage.tsx`

- [ ] **Step 1: Read CalendarPage.tsx**

Open `demo/src/modules/calendar/CalendarPage.tsx`. Find `CreateEventModal` and the individual audience section (the `audienceType === 'individual'` block currently showing a plain text input).

- [ ] **Step 2: Add imports to CalendarPage.tsx**

Add after existing imports:

```typescript
import { employees } from '../../mock/data/employees'
import { resolveCalendarParticipantPool } from '../../mock/utils/hierarchyScope'
import { useAuthStore } from '../../store/authStore'
```

- [ ] **Step 3: Update CreateEventModal to use participant pool**

Inside `CreateEventModal`, add at the top of the function body:

```typescript
const { user } = useAuthStore()
const creatorId = user?.id ?? 'e2'
const { participants, bypassParticipantIds } = resolveCalendarParticipantPool(creatorId)
const [participantSearch, setParticipantSearch] = useState('')

const filteredParticipants = participants.filter(p =>
  p.name.toLowerCase().includes(participantSearch.toLowerCase())
)
```

- [ ] **Step 4: Replace the individual audience input**

Find this block in `CreateEventModal`:

```typescript
{audienceType === 'individual' && (
  <input value={audienceLabel} onChange={e => setAudienceLabel(e.target.value)}
    placeholder="Search employee…" className={input + ' mt-2'} />
)}
```

Replace it with:

```typescript
{audienceType === 'individual' && (
  <div className="mt-2 space-y-1">
    <input
      value={participantSearch}
      onChange={e => setParticipantSearch(e.target.value)}
      placeholder="Search employee…"
      className={input}
    />
    {participantSearch.trim() && (
      <div className="max-h-40 overflow-y-auto rounded-lg border border-white/[0.09] bg-[#13121c] divide-y divide-white/[0.05]">
        {filteredParticipants.length === 0 ? (
          <div className="px-3 py-2 text-white/30 text-xs font-geist">No employees found</div>
        ) : (
          filteredParticipants.map(p => {
            const isBypass = bypassParticipantIds.has(p.id)
            return (
              <button
                key={p.id}
                onClick={() => {
                  setAudienceLabel(p.name)
                  setParticipantSearch('')
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-white/[0.04] transition-colors text-left"
              >
                <img src={p.avatar} alt={p.name} className="w-6 h-6 rounded-full shrink-0" />
                <span className="text-white/70 text-sm font-geist flex-1">{p.name}</span>
                {isBypass && (
                  <span className="text-[10px] font-outfit font-medium px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 shrink-0">
                    Bypass
                  </span>
                )}
              </button>
            )
          })
        )}
      </div>
    )}
    {audienceLabel && (
      <div className="flex items-center gap-2 px-2 py-1">
        <span className="text-white/50 text-xs font-geist">Selected:</span>
        <span className="text-white/70 text-xs font-geist">{audienceLabel}</span>
      </div>
    )}
  </div>
)}
```

- [ ] **Step 5: Start dev server and verify**

```bash
cd demo && npm run dev
```

Navigate to Calendar → click any day → Create Event.

Verify:
- Audience = Individual: shows search input instead of plain text
- Typing a name filters the employee list
- Employees below the current user (managerId chain) appear normally
- HR employees appear for James (e2) with an amber "Bypass" badge (because hse1 grants him HR dept for calendar)
- Clicking an employee sets audienceLabel and clears search
- Audience = Department/Team/Tenant: participant picker not shown (unchanged)

- [ ] **Step 6: Commit**

```bash
git add demo/src/modules/calendar/CalendarPage.tsx
git commit -m "feat(demo): replace calendar individual audience text input with bypass-aware employee picker"
```
