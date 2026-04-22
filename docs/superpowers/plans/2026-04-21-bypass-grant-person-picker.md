# Bypass Grant Person Picker Fix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the "Person" scope type in `AddBypassGrantModal` so the granter can search and select a specific employee from within their accessible scope, and prevent saving with an empty or invalid `scopeId`.

**Architecture:** Four independent tasks. Tasks 1–2 are demo code (Task 2 depends on Task 1). Tasks 3–4 are knowledge base doc updates (fully independent). All four can be read in any order; Task 2 must execute after Task 1.

**Tech Stack:** React 18, TypeScript, Tailwind CSS (demo). Markdown/Obsidian wiki-links (knowledge base). All demo files in `demo/src/`. All KB files in `Userflow/` and `modules/`.

---

## Known Conflicts

Before touching any file, read these — they describe intentional design differences that look like bugs but aren't:

1. **`resolveTeamMemberPool` dept filter ≠ bypass grant person picker scope.** Team creation for leaf/non-head granters filters subordinates to `departmentId === creator.departmentId`. The bypass grant person picker must NOT apply this filter. The ceiling rule for bypass grants is raw subordinate chain (managerId recursion) + null-context bypasses only. Do not reuse `resolveTeamMemberPool` for the person picker.

2. **`resolveBypassIds(grantorId, null)` not `'teams'` or `'calendar'`.** The person picker should include the granter's own subordinates AND employees they have access to via broad (applies_to IS NULL) bypasses. Feature-specific bypasses (calendar, teams) are excluded from this pool intentionally — a granter cannot re-delegate access they only have via a feature-scoped bypass.

3. **Single `scopeId` state init is wrong.** Currently `useState(accessibleDepts[0]?.id ?? '')` always starts as a dept ID. After this fix, `scopeId` must reset to `''` whenever `scopeType` changes away from `'department'`, and reset to `accessibleDepts[0]?.id` only when switching back to `'department'`.

4. **Role scope type has no picker** — intentionally left incomplete in this plan. The save guard added in Task 2 will block saving with `scopeType='role'` and empty `scopeId` (correct behaviour).

---

## File Map

| File | Change Type | Purpose |
|---|---|---|
| `demo/src/mock/utils/hierarchyScope.ts` | Modify | Add `resolveAccessibleEmployeesForBypassGrant()` |
| `demo/src/modules/people/employees/EmployeeProfile.tsx` | Modify | Fix `AddBypassGrantModal` — scopeId reset, person picker, save guard |
| `Userflow/Auth-Access/permission-assignment.md` | Modify | Step C2: document Person picker scope rules and required selection |
| `modules/auth/authorization/end-to-end-logic.md` | Modify | `BypassGrantService.CreateAsync`: add scope_id validation step |

---

## Task 1: Add `resolveAccessibleEmployeesForBypassGrant` to hierarchyScope.ts

**Files:**
- Modify: `demo/src/mock/utils/hierarchyScope.ts`

- [ ] **Step 1: Read the current file**

Open `demo/src/mock/utils/hierarchyScope.ts`. Note the existing exports: `resolveSubordinates`, `resolveBypassIds`, `getAccessibleDepartments`, `resolveTeamMemberPool`, `resolveCalendarParticipantPool`, `resolveCreatorTier`.

- [ ] **Step 2: Add the new function after `resolveCalendarParticipantPool`**

Insert the following immediately after the closing brace of `resolveCalendarParticipantPool` and before the `resolveCreatorTier` function:

```typescript
// Returns the accessible employee pool for the "Person" scope type in bypass grant creation.
// Includes all subordinates (full managerId chain, no dept filter) + employees reachable
// via broad (applies_to IS NULL) bypasses. Feature-scoped bypasses excluded intentionally.
export function resolveAccessibleEmployeesForBypassGrant(employeeId: string): {
  accessible: typeof employees
  bypassEmployeeIds: Set<string>
} {
  const subordinates = resolveSubordinates(employeeId)
  const broadBypassIds = resolveBypassIds(employeeId, null)

  const basePool = employees.filter(e => subordinates.has(e.id))
  const bypassPool = employees.filter(e => broadBypassIds.has(e.id))
  const accessible = [
    ...basePool,
    ...bypassPool.filter(b => !basePool.find(m => m.id === b.id)),
  ]

  return { accessible, bypassEmployeeIds: broadBypassIds }
}
```

- [ ] **Step 3: Run TypeScript check**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -20
```

Expected: no output (no errors).

- [ ] **Step 4: Commit**

```bash
cd demo && git add src/mock/utils/hierarchyScope.ts && git commit -m "feat(demo): add resolveAccessibleEmployeesForBypassGrant utility"
```

---

## Task 2: Fix AddBypassGrantModal in EmployeeProfile.tsx

**Files:**
- Modify: `demo/src/modules/people/employees/EmployeeProfile.tsx`

This task depends on Task 1 being complete.

- [ ] **Step 1: Read `AddBypassGrantModal` in the file**

Open `demo/src/modules/people/employees/EmployeeProfile.tsx`. Locate the `AddBypassGrantModal` function. Note the current state declarations and the conditional rendering blocks.

Current state (problematic):
```typescript
const [scopeType, setScopeType] = useState<ScopeType>('department')
const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
```

- [ ] **Step 2: Add the new import**

Find the line that imports from `../../../mock/utils/hierarchyScope`:

```typescript
import {
  resolveCreatorTier,
  getAccessibleDepartments,
} from '../../../mock/utils/hierarchyScope'
```

Replace it with:

```typescript
import {
  resolveCreatorTier,
  getAccessibleDepartments,
  resolveAccessibleEmployeesForBypassGrant,
} from '../../../mock/utils/hierarchyScope'
```

- [ ] **Step 3: Replace AddBypassGrantModal state and logic**

Find the entire `AddBypassGrantModal` function body up to and including the `return` statement. Replace the state declarations and pre-return logic with:

Find this block (inside `AddBypassGrantModal`):
```typescript
  const [scopeType, setScopeType] = useState<ScopeType>('department')
  const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
  const [appliesTo, setAppliesTo] = useState<string>('calendar')
```

Replace with:
```typescript
  const [scopeType, setScopeType] = useState<ScopeType>('department')
  const [scopeId, setScopeId] = useState(accessibleDepts[0]?.id ?? '')
  const [appliesTo, setAppliesTo] = useState<string>('calendar')
  const [personSearch, setPersonSearch] = useState('')

  const { accessible: accessibleEmployees, bypassEmployeeIds: bypassEmpIds } =
    resolveAccessibleEmployeesForBypassGrant(grantorId)

  const filteredPersons = accessibleEmployees.filter(e =>
    e.name.toLowerCase().includes(personSearch.toLowerCase())
  )

  function handleScopeTypeChange(next: ScopeType) {
    setScopeType(next)
    setPersonSearch('')
    if (next === 'department') {
      setScopeId(accessibleDepts[0]?.id ?? '')
    } else {
      setScopeId('')
    }
  }

  const canSave = scopeId.trim() !== ''
```

- [ ] **Step 4: Wire up scopeType change handler**

Find the scopeType `<select>` element:

```typescript
            <select
              value={scopeType}
              onChange={e => setScopeType(e.target.value as ScopeType)}
              className={inputCls}
            >
```

Replace `onChange` with:

```typescript
            <select
              value={scopeType}
              onChange={e => handleScopeTypeChange(e.target.value as ScopeType)}
              className={inputCls}
            >
```

- [ ] **Step 5: Add Person picker after the department picker block**

Find this block (the department picker conditional):

```typescript
          {scopeType === 'department' && (
            <div>
              <label className={labelCls}>Department</label>
              <select value={scopeId} onChange={e => setScopeId(e.target.value)} className={inputCls}>
                {accessibleDepts.map(d => (
                  <option key={d.id} value={d.id} className="bg-[#13121c]">{d.name}</option>
                ))}
              </select>
            </div>
          )}
```

Replace with:

```typescript
          {scopeType === 'department' && (
            <div>
              <label className={labelCls}>Department</label>
              <select value={scopeId} onChange={e => setScopeId(e.target.value)} className={inputCls}>
                {accessibleDepts.map(d => (
                  <option key={d.id} value={d.id} className="bg-[#13121c]">{d.name}</option>
                ))}
              </select>
            </div>
          )}

          {scopeType === 'people' && (
            <div>
              <label className={labelCls}>Person</label>
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
                          setScopeId(p.id)
                          setPersonSearch(p.name)
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

- [ ] **Step 6: Guard the Save button with `canSave`**

Find the Save Grant button:

```typescript
            <button onClick={handleSave} className="flex-1 px-3 py-2 rounded-lg bg-violet-600 text-white text-sm font-outfit font-medium hover:bg-violet-500 transition-colors">
              Save Grant
            </button>
```

Replace with:

```typescript
            <button
              onClick={handleSave}
              disabled={!canSave}
              className="flex-1 px-3 py-2 rounded-lg bg-violet-600 text-white text-sm font-outfit font-medium hover:bg-violet-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Save Grant
            </button>
```

- [ ] **Step 7: Run TypeScript check**

```bash
cd demo && npx tsc --noEmit 2>&1 | head -20
```

Expected: no output (no errors).

- [ ] **Step 8: Verify manually in browser**

```bash
cd demo && npm run dev
```

Open `http://localhost:5173`. Navigate to People → any employee → Security tab → Add Grant.

Verify the following scenarios:

**Person picker:**
- Switch Scope Type to "Person"
- `scopeId` resets — Save button is disabled (greyed out)
- Typing a name filters the list
- Clicking an employee sets their name in the search box, saves their ID as scopeId, enables Save
- Employees accessible via broad bypass show "Bypass" badge
- Save → grant appears in the list with correct employee name label

**Department picker (regression check):**
- Switch Scope Type to "Department" — dept dropdown shows immediately, Save is enabled
- Switch back to "Person" — dept selection is cleared, Save disabled again

**Root admin (Sarah e1) vs delegated granter (James e2):**
- Login as Sarah (e1): "All Features" option visible in Applies To
- Login as James (e2): "All Features" not shown

- [ ] **Step 9: Commit**

```bash
cd demo && git add src/modules/people/employees/EmployeeProfile.tsx && git commit -m "feat(demo): fix AddBypassGrantModal person picker with accessible employee search and save guard"
```

---

## Task 3: Update Userflow/Auth-Access/permission-assignment.md

**Files:**
- Modify: `Userflow/Auth-Access/permission-assignment.md`

- [ ] **Step 1: Read the current file**

Open `Userflow/Auth-Access/permission-assignment.md`. Locate Step C2 "Add a Bypass Grant". Find the "Scope Target" bullet under the fields list.

- [ ] **Step 2: Replace the Scope Target bullet in Step C2**

Find:
```markdown
  2. **Scope Target** — searchable picker:
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employees
     - Role: role list
```

Replace with:
```markdown
  2. **Scope Target** — searchable picker (required — Save is blocked until a target is selected):
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employee pool — all employees below the granter in the `reports_to_id` chain **plus** employees reachable via the granter's own broad (`applies_to IS NULL`) bypass grants. Feature-scoped bypasses (e.g. `applies_to = 'calendar'`) are excluded from this pool — a granter cannot re-delegate access they only have via a feature-specific bypass.
     - Role: role list (picker not yet implemented in v1 — blocked at save until implemented)
```

- [ ] **Step 3: Add a note below the field list about required selection**

Find the line immediately after the Expires At field (before the Validation line):

```markdown
- **Validation:** Scope target must be within the granter's own accessible scope (ceiling rule). Delegated granters cannot set `Applies To = All Features`.
```

Replace with:
```markdown
- **Validation:**
  - Scope target is required — the Save button is disabled until a valid target is selected for the chosen scope type.
  - Scope target must be within the granter's own accessible scope (ceiling rule).
  - Delegated granters cannot set `Applies To = All Features`.
  - For Person scope: selected employee must be in granter's subordinate chain or reachable via a broad (`applies_to IS NULL`) bypass grant. Feature-scoped bypasses do not extend the Person picker pool.
```

- [ ] **Step 4: Verify**

Confirm:
- "required" and save-guard language is present in Step C2
- Person pool description mentions `reports_to_id` chain + null-context bypasses
- Feature-scoped bypass exclusion is documented

- [ ] **Step 5: Commit**

```bash
git add Userflow/Auth-Access/permission-assignment.md && git commit -m "docs: clarify bypass grant Person picker scope rules and required selection in Step C2"
```

---

## Task 4: Update modules/auth/authorization/end-to-end-logic.md

**Files:**
- Modify: `modules/auth/authorization/end-to-end-logic.md`

- [ ] **Step 1: Read the current file**

Open `modules/auth/authorization/end-to-end-logic.md`. Locate the `## Bypass Grant Management` section and the `### Create Bypass Grant` flow block.

- [ ] **Step 2: Update the Create Bypass Grant flow**

Find:
```
POST /api/v1/employees/{employeeId}/bypass-grants
  -> Requires roles:manage
  -> BypassGrantService.CreateAsync(grantorId, targetEmployeeId, dto)
    -> 1. Resolve granter's accessible scope via IHierarchyScope
    -> 2. Verify dto.scopeId is within granter's accessible scope (ceiling rule)
    -> 3. If granter has permission_delegation_scopes record:
           - Verify dto.appliesTo is within module_scope
           - Block dto.appliesTo = null (All Features) for delegated granters
    -> 4. Insert hierarchy_scope_exceptions record
    -> 5. Invalidate bypass cache for targetEmployeeId
    -> 6. Audit log entry
```

Replace with:
```
POST /api/v1/employees/{employeeId}/bypass-grants
  -> Requires roles:manage
  -> BypassGrantService.CreateAsync(grantorId, targetEmployeeId, dto)
    -> 1. Validate dto.scopeId is not null/empty — return 422 if missing
    -> 2. Validate dto.scopeId references an existing entity matching dto.scopeType:
           - scope_type = 'department': SELECT 1 FROM departments WHERE id = dto.scopeId
           - scope_type = 'people':     SELECT 1 FROM employees WHERE id = dto.scopeId
           - scope_type = 'role':       SELECT 1 FROM roles WHERE id = dto.scopeId
           Return 422 if entity not found
    -> 3. Resolve granter's accessible scope via IHierarchyScope (featureContext = null)
           For 'people' scope: verify dto.scopeId is within subordinateIds OR broadBypassIds
           For 'department' scope: verify granter can access that dept (tier check)
           For 'role' scope: verify granter is root admin or has that role in accessible scope
           Return 403 if outside accessible scope (ceiling rule)
    -> 4. If granter has permission_delegation_scopes record:
           - Verify dto.appliesTo is within module_scope
           - Block dto.appliesTo = null (All Features) for delegated granters
    -> 5. Insert hierarchy_scope_exceptions record
    -> 6. Invalidate bypass cache for targetEmployeeId
    -> 7. Audit log entry

NOTE: For 'people' scope, the accessible pool uses featureContext = null (broad bypasses only).
A granter who has calendar-scoped access to an employee cannot re-delegate that access
as a bypass grant — they can only grant from their own null-context or subordinate scope.
```

- [ ] **Step 3: Verify**

Confirm:
- Step 1 validates non-empty scopeId
- Step 2 validates entity existence per scope_type
- Step 3 documents the 'people' pool uses `featureContext = null`
- NOTE about feature-scoped bypass exclusion is present

- [ ] **Step 4: Commit**

```bash
git add modules/auth/authorization/end-to-end-logic.md && git commit -m "docs: add scope_id validation and people scope ceiling rule to BypassGrantService.CreateAsync"
```
