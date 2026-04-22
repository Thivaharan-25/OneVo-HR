# Bypass Grant Multi-Select Person Picker

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `AddBypassGrantModal` so the "Person" scope type supports selecting multiple employees at once, each saved as a separate `hierarchy_scope_exceptions` row.

**Architecture:** Two tasks. Task 1 is all demo code in `EmployeeProfile.tsx` — adds `selectedIds: string[]` state, chip pills UI, and loops `onSave` over each selected ID. Task 2 documents the batch path in the KB. Task 2 is fully independent of Task 1.

**Tech Stack:** React 18, TypeScript, Tailwind CSS. `X` icon already imported via lucide-react. `HierarchyScopeException` type from `demo/src/mock/types.ts`.

---

## Known Constraints

- Multi-select **only applies to `scopeType === 'people'`**. Department stays a single-select `<select>`. Role stays unimplemented. Do not unify `scopeId` and `selectedIds` — keep `scopeId: string` for department, add `selectedIds: string[]` for people.
- `onSave` prop type changes from `(grant: HierarchyScopeException) => void` to `(grants: HierarchyScopeException[]) => void`. The call site in `SecurityTab` must be updated to spread.
- Clicking a person in the dropdown adds them to `selectedIds` and clears `personSearch`. Selected persons are **excluded from the dropdown** (not shown again once selected). Chips have an ✕ button to deselect.
- `canSave` for people scope: `selectedIds.length > 0`. For all other scope types: `scopeId.trim() !== ''`.

---

## File Map

| File | Change Type | Purpose |
|---|---|---|
| `demo/src/modules/people/employees/EmployeeProfile.tsx` | Modify | Multi-select state, chip UI, updated handleSave and onSave types |
| `modules/auth/authorization/end-to-end-logic.md` | Modify | Document batch grant creation path |

---

## Task 1: Multi-select in AddBypassGrantModal

**Files:**
- Modify: `demo/src/modules/people/employees/EmployeeProfile.tsx`

- [ ] **Step 1: Add `selectedIds` state**

Find (line ~114):
```typescript
  const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
  const [appliesTo, setAppliesTo] = useState<string>('calendar')
  const [personSearch, setPersonSearch] = useState('')
```

Replace with:
```typescript
  const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [appliesTo, setAppliesTo] = useState<string>('calendar')
  const [personSearch, setPersonSearch] = useState('')
```

- [ ] **Step 2: Exclude selected persons from dropdown results**

Find (line ~122):
```typescript
  const filteredPersons = accessibleEmployees.filter(e =>
    e.name.toLowerCase().includes(personSearch.toLowerCase())
  )
```

Replace with:
```typescript
  const filteredPersons = accessibleEmployees.filter(e =>
    e.name.toLowerCase().includes(personSearch.toLowerCase()) &&
    !selectedIds.includes(e.id)
  )
```

- [ ] **Step 3: Reset `selectedIds` on scope type change**

Find (line ~126):
```typescript
  function handleScopeTypeChange(next: ScopeType) {
    setScopeType(next)
    setPersonSearch('')
    if (next === 'department') {
      setScopeId(accessibleDepts[0]?.id ?? '')
    } else {
      setScopeId('')
    }
  }
```

Replace with:
```typescript
  function handleScopeTypeChange(next: ScopeType) {
    setScopeType(next)
    setPersonSearch('')
    setSelectedIds([])
    if (next === 'department') {
      setScopeId(accessibleDepts[0]?.id ?? '')
    } else {
      setScopeId('')
    }
  }
```

- [ ] **Step 4: Update `canSave`**

Find (line ~136):
```typescript
  const canSave = scopeId.trim() !== ''
```

Replace with:
```typescript
  const canSave = scopeType === 'people' ? selectedIds.length > 0 : scopeId.trim() !== ''
```

- [ ] **Step 5: Update `handleSave` to loop over `selectedIds` for people scope**

Find (line ~140):
```typescript
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
```

Replace with:
```typescript
  function handleSave() {
    const now = Date.now()
    const base = {
      tenantId: 't1' as const,
      grantedToEmployeeId: targetEmployeeId,
      scopeType,
      appliesTo: appliesTo === 'all' ? null : appliesTo,
      grantedByEmployeeId: grantorId,
      createdAt: new Date().toISOString().split('T')[0],
      expiresAt: null,
    }
    if (scopeType === 'people') {
      onSave(selectedIds.map((id, i) => ({ ...base, id: `hse-${now}-${i}`, scopeId: id })))
    } else {
      onSave([{ ...base, id: `hse-${now}`, scopeId }])
    }
    onClose()
  }
```

- [ ] **Step 6: Change `onSave` prop type**

Find (line ~108):
```typescript
  onSave: (grant: HierarchyScopeException) => void
```

Replace with:
```typescript
  onSave: (grants: HierarchyScopeException[]) => void
```

- [ ] **Step 7: Replace the person picker JSX with chip pills + multi-select**

Find the entire `{scopeType === 'people' && (...)}` block (lines ~194–238):
```typescript
          {scopeType === 'people' && (
            <div>
              <label className={labelCls}>Person</label>
              <input
                value={personSearch}
                onChange={e => {
                  setPersonSearch(e.target.value)
                  setScopeId('')
                }}
                placeholder="Search employee…"
                className={inputCls}
              />
              {personSearch.trim() && (
                <div className="mt-1 max-h-36 overflow-y-auto rounded-lg border border-white/[0.09] bg-[#0e0d18] divide-y divide-white/[0.05]">
                  {filteredPersons.length === 0 ? (
                    <div className="px-3 py-2 text-white/30 text-xs font-geist">No employees found</div>
                  ) : (
                    filteredPersons.map(p => (
                      <button
                        key={p.id}
                        onClick={() => {
                          setScopeId(p.id)
                          setPersonSearch('')
                        }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-white/[0.04] transition-colors text-left"
                      >
                        <img src={p.avatar} alt={p.name} className="w-5 h-5 rounded-full shrink-0" />
                        <span className="text-white/70 text-sm font-geist flex-1">{p.name}</span>
                        {bypassEmpIds.has(p.id) && (
                          <span className="text-[10px] font-outfit px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 shrink-0">
                            Bypass
                          </span>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
              {scopeId && !personSearch.trim() && (
                <p className="text-white/40 text-xs mt-1.5 font-geist">
                  Selected: {accessibleEmployees.find(e => e.id === scopeId)?.name ?? scopeId}
                </p>
              )}
            </div>
          )}
```

Replace with:
```typescript
          {scopeType === 'people' && (
            <div>
              <label className={labelCls}>Person</label>
              {selectedIds.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {selectedIds.map(id => {
                    const emp = accessibleEmployees.find(e => e.id === id)
                    return (
                      <span key={id} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-violet-500/15 border border-violet-500/25 text-violet-300 text-xs font-geist">
                        {emp?.name ?? id}
                        <button
                          onClick={() => setSelectedIds(prev => prev.filter(x => x !== id))}
                          className="text-violet-400 hover:text-white transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    )
                  })}
                </div>
              )}
              <input
                value={personSearch}
                onChange={e => setPersonSearch(e.target.value)}
                placeholder="Search employee…"
                className={inputCls}
              />
              {personSearch.trim() && (
                <div className="mt-1 max-h-36 overflow-y-auto rounded-lg border border-white/[0.09] bg-[#0e0d18] divide-y divide-white/[0.05]">
                  {filteredPersons.length === 0 ? (
                    <div className="px-3 py-2 text-white/30 text-xs font-geist">No employees found</div>
                  ) : (
                    filteredPersons.map(p => (
                      <button
                        key={p.id}
                        onClick={() => {
                          setSelectedIds(prev => [...prev, p.id])
                          setPersonSearch('')
                        }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-white/[0.04] transition-colors text-left"
                      >
                        <img src={p.avatar} alt={p.name} className="w-5 h-5 rounded-full shrink-0" />
                        <span className="text-white/70 text-sm font-geist flex-1">{p.name}</span>
                        {bypassEmpIds.has(p.id) && (
                          <span className="text-[10px] font-outfit px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 shrink-0">
                            Bypass
                          </span>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          )}
```

- [ ] **Step 8: Update the `onSave` call site in `SecurityTab`**

Find (line ~364):
```typescript
          onSave={grant => {
            setGrants(prev => [...prev, grant])
            setShowAdd(false)
          }}
```

Replace with:
```typescript
          onSave={grants => {
            setGrants(prev => [...prev, ...grants])
            setShowAdd(false)
          }}
```

- [ ] **Step 9: Run TypeScript check**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -20
```

Expected: no output (no errors).

- [ ] **Step 10: Verify manually in browser**

```bash
cd demo && npm run dev
```

Open `http://localhost:5173`. Navigate to People → any employee → Security tab → Add Grant → Scope Type: Person.

Verify:
- Search and select first employee → chip appears, search clears, that employee no longer appears in dropdown
- Search and select a second employee → two chips shown, Save button enabled
- Click ✕ on a chip → employee removed from chips and reappears in dropdown search results
- Save → both employees appear as separate rows in the grants list with correct names
- Switch Scope Type away and back → chips are cleared

Regression: Department scope → single select still works, Save enabled immediately.

- [ ] **Step 11: Commit**

```bash
cd demo && git add src/modules/people/employees/EmployeeProfile.tsx && git commit -m "feat(demo): multi-select person picker in AddBypassGrantModal with chip pills"
```

---

## Task 2: Update end-to-end-logic.md for batch path

**Files:**
- Modify: `modules/auth/authorization/end-to-end-logic.md`

- [ ] **Step 1: Read the current file**

Open `modules/auth/authorization/end-to-end-logic.md`. Locate `BypassGrantService.CreateAsync`.

- [ ] **Step 2: Add batch path note after the CreateAsync block**

Find the line immediately after the `-> 7. Audit log entry` line in the CreateAsync block:

```
    -> 7. Audit log entry
```

Replace with:
```
    -> 7. Audit log entry

NOTE (batch path): When the UI saves a "Person" scope grant for multiple selected employees,
it calls POST /api/v1/employees/{employeeId}/bypass-grants once per selected person — each
with a distinct dto.scopeId. The backend processes each call independently through
BypassGrantService.CreateAsync. There is no batch endpoint; atomicity is UI-side only.
If a partial failure occurs mid-batch, already-inserted rows are NOT rolled back.
A future BatchCreateAsync could wrap the loop in a transaction if needed.
```

- [ ] **Step 3: Verify**

Confirm the NOTE paragraph is present immediately after step 7, mentions "once per selected person", and documents the no-rollback caveat.

- [ ] **Step 4: Commit**

```bash
git add modules/auth/authorization/end-to-end-logic.md && git commit -m "docs: document batch path for multi-select person bypass grants in BypassGrantService"
```
