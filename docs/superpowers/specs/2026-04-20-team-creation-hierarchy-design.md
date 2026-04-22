# Team Creation Hierarchy Scoping + Bypass Grant System — Design Spec

**Date:** 2026-04-20  
**Branch:** feature/luminous-depth  
**Status:** Approved — ready for implementation planning

---

## Problem

The current team creation flow (`org:manage`) allows any permission holder to select any department and add any employee with no hierarchy awareness. The system also has no mechanism for granting controlled exceptions to hierarchy scope — meaning a manager cannot invite a specific person outside their reporting chain to a calendar event, team, or any other hierarchy-scoped operation.

---

## Goals

1. Scope team creation by the creator's position in the department hierarchy
2. Introduce a `hierarchy_scope_exceptions` table that expands `IHierarchyScope` results with explicit bypass grants
3. Allow permission granters to delegate `roles:manage` with a module whitelist (ceiling rule enforced)
4. Expose bypass grant configuration in the existing Security tab on employee profiles
5. Update calendar event participant picking to respect bypass grants
6. All changes flow through `IHierarchyScope` — no per-flow rewrites needed for existing flows

---

## Database

### New table: `hierarchy_scope_exceptions`

```sql
id                      uuid          PK
tenant_id               uuid          FK → tenants
granted_to_employee_id  uuid          FK → employees
scope_type              varchar(20)   CHECK IN ('department', 'people', 'role')
scope_id                uuid          FK → departments / employees / roles (always required)
applies_to              varchar(50)   nullable — null = all features (root admin only)
granted_by_employee_id  uuid          FK → employees
created_at              timestamptz
expires_at              timestamptz   nullable
```

**`scope_type` resolution at runtime:**

| `scope_type` | `scope_id` points to | Resolved as |
|---|---|---|
| `department` | `departments.id` | All active employees in that dept |
| `people` | `employees.id` | That specific employee |
| `role` | `roles.id` | All employees with that role |

**`applies_to` rules:**
- `null` → bypass applies to every feature using `IHierarchyScope` — only root admins can create this
- `'calendar'` → only applies when feature context is `calendar`
- `'teams'` → only applies when feature context is `teams`
- Any future feature opts in by passing its context string to `IHierarchyScope`

---

### New table: `permission_delegation_scopes`

```sql
id                        uuid          PK
tenant_id                 uuid          FK → tenants
delegated_to_employee_id  uuid          FK → employees
module_scope              text[]        e.g. ['calendar', 'hr', 'attendance']
delegated_by_employee_id  uuid          FK → employees
created_at                timestamptz
expires_at                timestamptz   nullable
```

**Ceiling rule:** `module_scope` must be a strict subset of the granter's own `module_scope`. Root admins (no `permission_delegation_scopes` record) can grant any modules.

**Option C combined scope:** The same `module_scope` list automatically governs which `applies_to` values the delegated granter can use when creating bypass grants — no separate bypass config needed.

---

## `IHierarchyScope` Changes

`GetSubordinateIdsAsync()` returns a **split result**:

```
{
  subordinateIds: Set<Guid>   // from reports_to_id recursive CTE (unchanged)
  bypassIds:      Set<Guid>   // resolved from hierarchy_scope_exceptions
}
```

**Signature:**
```
GetSubordinateIdsAsync(currentUserId, featureContext = null, ct)
```

**Bypass resolution logic:**

When `featureContext` is provided:
```sql
WHERE tenant_id = @tenantId
  AND granted_to_employee_id = @currentUserId
  AND (applies_to IS NULL OR applies_to = @featureContext)
  AND (expires_at IS NULL OR expires_at > NOW())
```

When `featureContext` is not provided (null):
```sql
WHERE tenant_id = @tenantId
  AND granted_to_employee_id = @currentUserId
  AND applies_to IS NULL
  AND (expires_at IS NULL OR expires_at > NOW())
```

The two branches must be kept separate — `applies_to = NULL` is always false in SQL and must never be used as a comparison.

Then for each matched record, expand `scope_id` into employee IDs based on `scope_type`.

**Caller behaviour:**
- Flows passing `featureContext` → match `applies_to IS NULL OR applies_to = context`
- Flows passing no context → match `applies_to IS NULL` only (broad bypasses only — safe default)
- `bypassIds` is **always included in full** regardless of additional filters applied by the calling feature

---

## Team Creation — Hierarchy Scoping

### Creator tier resolution

On form load, query `departments` where `head_employee_id = currentEmployeeId`:

| Tier | Condition | Dept selector | Member pool |
|---|---|---|---|
| **Root head** | Heads a dept where `parent_department_id IS NULL` | All active depts in tenant | `subordinateIds + bypassIds` |
| **Parent head** | Heads a dept with child depts (not root) | Their dept + all descendants (recursive CTE) | `subordinateIds + bypassIds` |
| **Leaf / non-head** | Heads only leaf dept, or no dept | Auto-locked to `employee.department_id`, no picker | `subordinateIds` filtered to same dept + `bypassIds` always included |

**Rules:**
- Employee heads multiple departments → tier = highest (root beats parent beats leaf)
- Super Admin → bypasses all tiers, sees all depts and all employees
- Team lead must come from the same resolved member pool
- `featureContext = 'teams'` passed to `IHierarchyScope`

### Error messages

| Scenario | Message |
|---|---|
| Leaf head tries dept picker | Prevented at UI — picker not rendered |
| Member outside pool via API | `"You can only add employees within your hierarchy scope"` |
| Team lead outside pool | `"Team lead must be within your accessible employee pool"` |

---

## Permission Assignment — New Paths

### Path C: Grant hierarchy bypass to an employee

Location: Employee profile → Security tab → new **"Bypass Grants"** section (below existing Override Permissions panel).

**Steps:**
1. Click **"Add Bypass Grant"**
2. Select `scope_type`: Department / Person / Role
3. Select `scope_id` from searchable picker (dept tree / employee search / role list)
4. Select `applies_to`: dropdown
   - Root admin sees: `All Features` + individual feature list
   - Delegated granter sees: only features within their `module_scope` (no "All Features")
5. Optionally set `expires_at`
6. Save → inserts into `hierarchy_scope_exceptions`

**Ceiling rule on scope picker:** Only shows targets the granter themselves can access.

---

### Path D: Delegate `roles:manage` with module scope

Triggered when granting `roles:manage` via role assignment or per-employee override.

**Steps:**
1. Module checklist appears — only modules within granter's own `module_scope` shown (ceiling rule)
2. Granter selects which modules recipient can manage
3. Save → inserts `user_permission_overrides` record + `permission_delegation_scopes` record atomically
4. Combined scope (Option C): selected modules automatically govern bypass grant scope — no extra step

**Error messages:**

| Scenario | Message |
|---|---|
| Granting module outside own scope | Checkbox disabled: `"You can only delegate modules within your own scope"` |
| Bypass target outside own scope | Picker filters silently |
| Creating null bypass as delegated granter | `"All Features bypass can only be granted by root administrators"` |

---

## Calendar Event Creation — Updated

`featureContext = 'calendar'` passed to `IHierarchyScope`.

**Step 3 (Add Participants) change:**

Participant search returns:
- `subordinateIds` from normal hierarchy (unchanged)
- `bypassIds` appended — people covered by a bypass grant with `applies_to IS NULL OR applies_to = 'calendar'`

**Visual distinction:** Bypass-granted participants show a **"Bypass"** badge in the picker so the creator knows they are outside normal scope.

**Updated Audience Rules table addition:**

| Audience | Who can select |
|---|---|
| Individual | `calendar:write` + `employees:read` scoped to that person **or covered by active bypass grant** |

No new error states — if someone appears in the picker, they are accessible.

---

## Files to Change — Knowledge Base

| File | Change |
|---|---|
| `Userflow/Org-Structure/team-creation.md` | Full rewrite — tier logic, dept selector rules, member pool rules |
| `Userflow/Auth-Access/permission-assignment.md` | Add Path C (bypass grant) and Path D (module delegation) |
| `Userflow/Calendar/calendar-event-creation.md` | Update Step 3 and Audience Rules table |
| `modules/auth/authorization/end-to-end-logic.md` | Update Hierarchy Scoping section — split result, featureContext param, bypass resolution |
| `modules/org-structure/overview.md` | Add `hierarchy_scope_exceptions` and `permission_delegation_scopes` tables |
| `modules/org-structure/teams/overview.md` | Update API logic, tier resolution, member pool |

---

## Files to Change — Demo

| Screen | Change |
|---|---|
| Team creation screen | Dept selector respects tier, member picker filtered by pool, bypass-granted shown |
| Permission assignment → Security tab | New Bypass Grants section (Path C UI) + Delegation Scope panel (Path D UI) |
| Calendar event participant picker | Bypass badge on out-of-hierarchy participants |

---

## What Does Not Change

- All other flows using `IHierarchyScope` (attendance, shifts, payroll, performance, etc.) — they pass no `featureContext` and receive only broad (`applies_to IS NULL`) bypasses automatically
- No existing userflow or module file needs updating outside the list above
- Permission resolution order (`role + grants - revokes`) is unchanged
- Super Admin bypass is unchanged
