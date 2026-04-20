# Team Creation Hierarchy — Knowledge Base Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update all userflow and module docs to reflect hierarchy-scoped team creation, the bypass grant system, and the permission delegation ceiling rule.

**Architecture:** Six targeted file rewrites. Each file is independent — tasks can be done in any order. No new files created. All changes derive directly from the approved spec at `docs/superpowers/specs/2026-04-20-team-creation-hierarchy-design.md`.

**Tech Stack:** Markdown, Obsidian wiki-links (`[[path|label]]`), existing ONEVO doc conventions.

---

## File Map

| File | Change Type |
|---|---|
| `Userflow/Org-Structure/team-creation.md` | Full rewrite |
| `Userflow/Auth-Access/permission-assignment.md` | Add Path C and Path D sections |
| `Userflow/Calendar/calendar-event-creation.md` | Update Step 3 and Audience Rules table |
| `modules/auth/authorization/end-to-end-logic.md` | Update Hierarchy Scoping section |
| `modules/org-structure/overview.md` | Add two new DB tables |
| `modules/org-structure/teams/overview.md` | Update API logic and member pool |

---

## Task 1: Rewrite team-creation.md

**Files:**
- Modify: `Userflow/Org-Structure/team-creation.md`

- [ ] **Step 1: Read the current file**

Open `Userflow/Org-Structure/team-creation.md` and note the current structure. You are replacing it entirely.

- [ ] **Step 2: Write the new file**

Replace the entire file with:

```markdown
# Team Creation

**Area:** Org Structure  
**Trigger:** User with `org:manage` creates a team (user action)  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to search members and team lead)

---

## Preconditions

- At least one department exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Creator Tier Resolution

On form load the system determines the creator's **tier** by querying `departments` where `head_employee_id = currentEmployeeId`:

| Tier | Condition | Effect on form |
|:-----|:----------|:---------------|
| **Root head** | Heads a dept where `parent_department_id IS NULL` | Full dept picker (all active depts in tenant) |
| **Parent head** | Heads a dept that has child depts (not root) | Dept picker scoped to their dept + all descendants |
| **Leaf / non-head** | Heads only a leaf dept, or heads no dept | Dept auto-locked to their own `department_id` — no picker shown |

If an employee heads multiple departments, their tier is the highest (root > parent > leaf).

Super Admin bypasses all tier logic — sees all departments and all employees.

## Member Pool

The set of employees a creator can add as members or team lead:

| Tier | Member pool |
|:-----|:------------|
| Root head | `subordinateIds` (full hierarchy below them) + `bypassIds` |
| Parent head | `subordinateIds` + `bypassIds` |
| Leaf / non-head | `subordinateIds` filtered to same `department_id` as creator, **plus** `bypassIds` always included in full |

`bypassIds` are resolved from `hierarchy_scope_exceptions` for the current user with `featureContext = 'teams'`. See [[modules/auth/authorization/end-to-end-logic|Authorization — Hierarchy Scoping]].

## Flow Steps

### Step 1: Navigate to Teams
- **UI:** Sidebar → Organization → Teams → click "Create Team"
- **API:** `GET /api/v1/org/teams`
- **Backend:** Resolves creator tier before returning form config

### Step 2: Define Team
- **UI:** Enter team name
  - Root/Parent head: department picker shown — select from accessible departments
  - Leaf/Non-head: department field shows their department name (read-only, no picker)
- **Validation:** Name unique within the selected department

### Step 3: Assign Team Lead
- **UI:** Search employee from resolved member pool → select as team lead
- **Backend:** Team lead gains `*:read-team` scope for this team's members

### Step 4: Add Members
- **UI:** Search employees from resolved member pool → add to team
  - Bypass-granted employees show a "Bypass" badge indicating they are outside normal hierarchy scope
- **API:** `POST /api/v1/org/teams`
- **DB:** `teams`, `team_members` — records created

### Step 5: Confirmation
- **UI:** Team visible in department view → team lead can see team dashboard

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate name in department | Validation fails | "Team name already exists in this department" |
| Team lead not in member pool | `403 Forbidden` | "Team lead must be within your accessible employee pool" |
| Member not in member pool (API) | `403 Forbidden` | "You can only add employees within your hierarchy scope" |
| Leaf head dept picker attempted | Prevented at UI | Dept field rendered as read-only label |

## Events Triggered

- `TeamCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — bypass grants configured here
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

## Module References

- [[modules/org-structure/teams/overview|Teams]] — tier resolution, member pool logic
- [[modules/auth/authorization/end-to-end-logic|Authorization]] — IHierarchyScope, bypass resolution
- [[modules/org-structure/overview|Org Structure]]
```

- [ ] **Step 3: Verify the file reads correctly**

Open the file and confirm:
- Tier table is present with three rows (Root head, Parent head, Leaf/non-head)
- Member pool table references `bypassIds` and `featureContext = 'teams'`
- Step 2 describes conditional dept picker
- Step 4 mentions the Bypass badge
- All wiki-links use `[[path|label]]` format

- [ ] **Step 4: Commit**

```bash
git add Userflow/Org-Structure/team-creation.md
git commit -m "docs: rewrite team-creation userflow with hierarchy tier scoping"
```

---

## Task 2: Add Path C and Path D to permission-assignment.md

**Files:**
- Modify: `Userflow/Auth-Access/permission-assignment.md`

- [ ] **Step 1: Read the current file**

Open `Userflow/Auth-Access/permission-assignment.md`. Note that it currently has Path A (role permissions) and Path B (per-employee override). You are appending Path C and Path D after Path B.

- [ ] **Step 2: Append Path C after the Path B section**

Find the line `### Path B: Per-Employee Permission Override` and locate the end of that section (just before `## Permission Resolution Order`). Insert the following between Path B and Permission Resolution Order:

```markdown
### Path C: Grant Hierarchy Bypass to an Employee

#### Step C1: Navigate to Employee Security Tab
- **UI:** Employees > search employee > click profile > Security tab > scroll to **"Bypass Grants"** section (below Override Permissions panel)
- **API:** `GET /api/v1/employees/{employeeId}/bypass-grants`
- **Backend:** `BypassGrantService.GetByEmployeeAsync()` → [[modules/auth/authorization/end-to-end-logic|Authorization]]
- **Validation:** Permission check for `roles:manage`. Granter must have an active `permission_delegation_scopes` record or be a root admin.
- **DB:** `hierarchy_scope_exceptions`, `permission_delegation_scopes`

#### Step C2: Add a Bypass Grant
- **UI:** Click **"Add Bypass Grant"**. A panel appears with three fields:
  1. **Scope Type** — dropdown: `Department` / `Person` / `Role`
  2. **Scope Target** — searchable picker:
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employees
     - Role: role list
  3. **Applies To** — dropdown:
     - Root admin sees: `All Features` + individual feature names (e.g., `Calendar`, `Teams`)
     - Delegated granter sees: only features within their own `module_scope` — no "All Features" option
  4. **Expires At** — optional date picker
- **Validation:** Scope target must be within the granter's own accessible scope (ceiling rule). Delegated granters cannot set `Applies To = All Features`.
- **DB:** None (client-side selection)

#### Step C3: Save Bypass Grant
- **UI:** Click "Save Grant"
- **API:** `POST /api/v1/employees/{employeeId}/bypass-grants`
  ```json
  {
    "scopeType": "department",
    "scopeId": "uuid",
    "appliesTo": "calendar"
  }
  ```
- **Backend:** `BypassGrantService.CreateAsync()`
  1. Validate granter's scope (ceiling rule): target must be in granter's accessible scope
  2. Validate `appliesTo`: if granter is delegated, check `permission_delegation_scopes.module_scope`
  3. Insert `hierarchy_scope_exceptions` record
  4. Audit log entry
- **DB:** `hierarchy_scope_exceptions`, `audit_logs`

#### Step C4: Confirmation
- **UI:** Toast: "Bypass grant saved. [Employee] can now include [target] in [applies_to] operations."
- Bypass Grants section refreshes showing the new grant with scope type, target name, applies to, and expiry

---

### Path D: Delegate `roles:manage` with Module Scope

Triggered automatically when granting `roles:manage` to an employee via role assignment or per-employee override (Path A or Path B).

#### Step D1: Module Scope Panel Appears
- **UI:** After selecting the `roles:manage` permission in the permission browser, a **"Delegation Scope"** panel appears below automatically.
  - Module checklist is shown — one checkbox per module
  - Root admin sees all modules
  - Delegated granter sees only modules within their own `module_scope` (ceiling rule — cannot delegate beyond own scope)
- **Validation:** At least one module must be selected before save is enabled.
- **DB:** None (client-side)

#### Step D2: Save Delegation
- **UI:** Included in the existing "Save Changes" or "Save Overrides" action — no separate save step
- **API:** Existing permission save endpoints (`PUT /api/v1/roles/{roleId}/permissions` or `PUT /api/v1/employees/{employeeId}/permission-overrides`) receive an additional `delegationScope` field:
  ```json
  {
    "permissionIds": ["roles-manage-uuid"],
    "delegationScope": {
      "moduleScope": ["calendar", "hr"]
    }
  }
  ```
- **Backend:** After saving the permission, atomically insert `permission_delegation_scopes` record
  - Ceiling check: `moduleScope` must be subset of granter's own `module_scope`
  - If granter is root admin (no `permission_delegation_scopes` record), any modules are allowed
- **DB:** `user_permission_overrides` or `role_permissions` (existing) + `permission_delegation_scopes` (new)

#### Step D3: Combined Scope Effect
- The saved `module_scope` automatically governs two things:
  1. Which modules the recipient can manage permissions for
  2. Which `applies_to` values they can use when creating bypass grants (Path C)
- No separate configuration needed — one setting covers both.

#### Step D4: Confirmation
- **UI:** Toast: "Permissions updated. [Employee] can now manage permissions for: Calendar, HR."

---
```

- [ ] **Step 3: Add new error scenarios to the Error Scenarios table**

Find the `## Error Scenarios` section and append these rows:

```markdown
| Bypass grant target outside granter's scope | Scope picker filters silently | Picker only shows accessible targets |
| Delegated granter sets `All Features` bypass | Save blocked | "All Features bypass can only be granted by root administrators" |
| Delegation scope exceeds granter's own scope | Save blocked | "You can only delegate modules within your own scope" |
```

- [ ] **Step 4: Add new events to Events Triggered section**

Find `## Events Triggered` and append:

```markdown
- `BypassGrantCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]]
- `PermissionDelegationScopeCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]]
```

- [ ] **Step 5: Verify the file**

Confirm:
- Path C section exists with steps C1–C4
- Path D section exists with steps D1–D4
- `Applies To` dropdown rules are documented (root admin vs delegated granter)
- Ceiling rule is mentioned in both paths
- New error rows added to the table

- [ ] **Step 6: Commit**

```bash
git add Userflow/Auth-Access/permission-assignment.md
git commit -m "docs: add Path C (bypass grant) and Path D (module delegation) to permission assignment"
```

---

## Task 3: Update calendar-event-creation.md

**Files:**
- Modify: `Userflow/Calendar/calendar-event-creation.md`

- [ ] **Step 1: Read the current file**

Open `Userflow/Calendar/calendar-event-creation.md`. Locate Step 3 (Add Participants) and the Audience Rules section.

- [ ] **Step 2: Replace Step 3**

Find the section `### Step 3: Add Participants` and replace it with:

```markdown
### Step 3: Add Participants *(individual audience only)*
- **UI:** Employee search picker — returns employees from two pools:
  1. **Hierarchy subordinates** — employees below the creator in the `reports_to_id` chain
  2. **Bypass-granted** — employees covered by an active `hierarchy_scope_exceptions` record for this user with `applies_to IS NULL OR applies_to = 'calendar'`
  
  Bypass-granted employees are shown with a **"Bypass"** badge in the search results so the creator knows they are outside normal hierarchy scope.
- **Backend:** `CalendarService.SearchParticipantsAsync()` calls `IHierarchyScope.GetSubordinateIdsAsync(featureContext: "calendar")` → [[modules/auth/authorization/end-to-end-logic|Authorization]]
- Skipped when audience is Tenant / Department / Team (participants resolved server-side)
- **DB:** `calendar_events`, `calendar_event_participants`
```

- [ ] **Step 3: Update the Audience Rules table**

Find the `## Audience Rules` section. Replace the `Individual` row:

Old row:
```
| **Individual** | Any user with `calendar:write` + `employees:read` scoped to that person |
```

New row:
```
| **Individual** | Any user with `calendar:write` + `employees:read` scoped to that person **or covered by an active bypass grant (`applies_to = 'calendar'` or `applies_to IS NULL`)** |
```

- [ ] **Step 4: Update the Error Scenarios table**

Find the `## Error Scenarios` section. The existing row `"Selected department outside hierarchy"` is fine. Add this row:

```markdown
| Participant added via API without bypass grant | `403 Forbidden` | "You do not have access to add this participant" |
```

- [ ] **Step 5: Verify**

Confirm:
- Step 3 mentions both subordinates and bypass-granted pools
- Step 3 mentions the "Bypass" badge
- `featureContext = 'calendar'` is referenced
- Audience Rules Individual row updated

- [ ] **Step 6: Commit**

```bash
git add Userflow/Calendar/calendar-event-creation.md
git commit -m "docs: update calendar event creation with bypass-aware participant picker"
```

---

## Task 4: Update modules/auth/authorization/end-to-end-logic.md

**Files:**
- Modify: `modules/auth/authorization/end-to-end-logic.md`

- [ ] **Step 1: Read the current file**

Open `modules/auth/authorization/end-to-end-logic.md`. Locate the section `## Hierarchy Scoping (Data Filtering)`.

- [ ] **Step 2: Replace the Hierarchy Scoping section**

Find `## Hierarchy Scoping (Data Filtering)` and replace its `### Flow` subsection with:

```markdown
### Flow

```
Any endpoint returning employee-related data
  -> Controller calls service with IHierarchyScope and optional featureContext
    -> HierarchyScopeService.GetSubordinateIdsAsync(currentUserId, featureContext?, ct)
      -> Returns HierarchyScopeResult { subordinateIds: Set<Guid>, bypassIds: Set<Guid> }

      SUBORDINATE RESOLUTION (unchanged):
      -> 1. If current user is Super Admin -> subordinateIds = ALL employee IDs
      -> 2. Otherwise: recursive CTE on reports_to_id
           WITH RECURSIVE subordinates AS (
             SELECT id FROM employees WHERE reports_to_id = @currentEmployeeId
             UNION ALL
             SELECT e.id FROM employees e
             INNER JOIN subordinates s ON e.reports_to_id = s.id
           )
           SELECT id FROM subordinates
      -> 3. Cache in Redis (key: `hierarchy:{tenantId}:{userId}`, TTL: 5 min)

      BYPASS RESOLUTION (new):
      -> 4. If featureContext IS PROVIDED:
           SELECT * FROM hierarchy_scope_exceptions
           WHERE tenant_id = @tenantId
             AND granted_to_employee_id = @currentUserId
             AND (applies_to IS NULL OR applies_to = @featureContext)
             AND (expires_at IS NULL OR expires_at > NOW())
         If featureContext IS NULL:
           SELECT * FROM hierarchy_scope_exceptions
           WHERE tenant_id = @tenantId
             AND granted_to_employee_id = @currentUserId
             AND applies_to IS NULL
             AND (expires_at IS NULL OR expires_at > NOW())
         NOTE: applies_to = NULL comparison is always false in SQL —
               the two branches MUST remain separate.
      -> 5. For each exception record, expand scope_id into employee IDs:
           - scope_type = 'department': SELECT id FROM employees WHERE department_id = scope_id
           - scope_type = 'people':     { scope_id }
           - scope_type = 'role':       SELECT employee_id FROM user_roles WHERE role_id = scope_id

      CALLER CONTRACT:
      -> Services apply WHERE employee_id IN (@subordinateIds) to base queries
      -> bypassIds are ALWAYS appended after any additional filters
         (e.g. team creation dept filter applies to subordinateIds only, not bypassIds)
      -> Flows NOT passing featureContext only receive applies_to IS NULL bypasses (safe default)
```
```

- [ ] **Step 3: Add new section for Bypass Grant Management**

After the Hierarchy Scoping section, add:

```markdown
## Bypass Grant Management

### Create Bypass Grant
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

### Permission Delegation Scope
```
Created atomically when roles:manage is granted (Path A or Path B in permission assignment)
  -> PermissionDelegationService.CreateAsync(grantorId, recipientId, moduleScope[])
    -> 1. Resolve granter's own module_scope (from permission_delegation_scopes)
           If no record: granter is root admin, any modules allowed
    -> 2. Verify moduleScope is strict subset of granter's own module_scope
    -> 3. Insert permission_delegation_scopes record
    -> 4. Audit log entry
```
```

- [ ] **Step 4: Verify**

Confirm:
- The flow shows two branches for featureContext provided vs null
- SQL NOTE about `applies_to = NULL` is present
- scope_type expansion for all three types is shown
- Bypass Grant Management section is added
- Ceiling rule is mentioned

- [ ] **Step 5: Commit**

```bash
git add modules/auth/authorization/end-to-end-logic.md
git commit -m "docs: update authorization hierarchy scoping with bypass resolution and split result"
```

---

## Task 5: Update modules/org-structure/overview.md

**Files:**
- Modify: `modules/org-structure/overview.md`

- [ ] **Step 1: Read the current file**

Open `modules/org-structure/overview.md`. Locate the `## Database Tables` section. You will add two new table definitions.

- [ ] **Step 2: Add `hierarchy_scope_exceptions` table definition**

After the last existing table entry (whichever is last), append:

```markdown
### `hierarchy_scope_exceptions`

Cross-feature bypass grants that expand `IHierarchyScope` results for a specific employee.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `granted_to_employee_id` | `uuid` | FK → employees — who receives the bypass |
| `scope_type` | `varchar(20)` | `department` \| `people` \| `role` |
| `scope_id` | `uuid` | FK → departments / employees / roles depending on `scope_type` — always required |
| `applies_to` | `varchar(50)` | nullable — `null` = all features (root admin only); e.g. `'calendar'`, `'teams'` |
| `granted_by_employee_id` | `uuid` | FK → employees — audit trail |
| `created_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | nullable |

Resolved by `IHierarchyScope.GetSubordinateIdsAsync()` — bypass targets are appended to `bypassIds` in the result. See [[modules/auth/authorization/end-to-end-logic|Authorization — Hierarchy Scoping]].
```

- [ ] **Step 3: Add `permission_delegation_scopes` table definition**

Immediately after the `hierarchy_scope_exceptions` section, append:

```markdown
### `permission_delegation_scopes`

Records the module whitelist for employees who were granted `roles:manage` via delegation (not as base role).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `delegated_to_employee_id` | `uuid` | FK → employees |
| `module_scope` | `text[]` | Modules this person can manage permissions and bypass grants for |
| `delegated_by_employee_id` | `uuid` | FK → employees — audit trail |
| `created_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | nullable |

**Ceiling rule:** `module_scope` must be a strict subset of the granter's own `module_scope`. Employees with `roles:manage` from their base role (no `permission_delegation_scopes` record) are treated as root admins with unrestricted scope.
```

- [ ] **Step 4: Update the Database Tables count in the section header**

Find `## Database Tables (8)` (or whatever number is there) and increment it by 2.

- [ ] **Step 5: Verify**

Confirm both new tables are present with all columns listed and the ceiling rule note is included.

- [ ] **Step 6: Commit**

```bash
git add modules/org-structure/overview.md
git commit -m "docs: add hierarchy_scope_exceptions and permission_delegation_scopes tables to org structure"
```

---

## Task 6: Update modules/org-structure/teams/overview.md

**Files:**
- Modify: `modules/org-structure/teams/overview.md`

- [ ] **Step 1: Read the current file**

Open `modules/org-structure/teams/overview.md`. Note the current Purpose, Database Tables, and API Endpoints sections.

- [ ] **Step 2: Update Purpose section**

Replace the existing Purpose section content with:

```markdown
## Purpose

Teams live within departments. A user with `org:manage` can create teams, but the departments they can assign and the employees they can add depend on their position in the department hierarchy (creator tier). See [[modules/auth/authorization/end-to-end-logic|Authorization — Hierarchy Scoping]] for bypass resolution.
```

- [ ] **Step 3: Update the `teams` table entry**

Find the `teams` table definition and ensure it matches the production schema. Replace with:

```markdown
### `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Unique within department |
| `department_id` | `uuid` | FK → departments |
| `team_lead_id` | `uuid` | FK → employees (nullable) |
| `description` | `text` | nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
```

- [ ] **Step 4: Add Creator Tier Resolution section**

After the Database Tables section, insert:

```markdown
## Creator Tier Resolution

On `POST /api/v1/org/teams`, the service resolves the creator's tier before validating the request:

```
TeamService.ResolveCreatorTierAsync(creatorEmployeeId)
  -> Query: departments WHERE head_employee_id = @creatorId
  -> For each headed department:
       - parentDepartmentId IS NULL → ROOT tier → break
       - Has child departments → PARENT tier
       - No children → LEAF tier
  -> If no departments headed → NON-HEAD tier (same restrictions as LEAF)
  -> If multiple headed → use highest tier
```

**Accessible departments by tier:**

| Tier | Accessible departments |
|:-----|:----------------------|
| Root | All active departments in tenant |
| Parent | Their department + all descendants (recursive CTE on `parent_department_id`) |
| Leaf / Non-head | Only their own `department_id` |

**Member pool by tier:**

| Tier | `subordinateIds` filter | `bypassIds` |
|:-----|:------------------------|:------------|
| Root / Parent | No extra filter | Always included |
| Leaf / Non-head | AND `department_id = creator.department_id` | Always included regardless of dept filter |

`IHierarchyScope.GetSubordinateIdsAsync(featureContext: "teams")` provides both sets.
```

- [ ] **Step 5: Update API Endpoints section**

Find the `## API Endpoints` section and ensure the POST endpoint documents the new validation:

```markdown
## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/teams` | `org:manage` | List teams (scoped to creator's accessible departments) |
| POST | `/api/v1/org/teams` | `org:manage` | Create team — validates dept and members against creator tier + bypass grants |
| PUT | `/api/v1/org/teams/{id}` | `org:manage` | Update team |
| DELETE | `/api/v1/org/teams/{id}` | `org:manage` | Deactivate team |
| GET | `/api/v1/org/teams/{id}/members` | `org:manage` | List team members |
| POST | `/api/v1/org/teams/{id}/members` | `org:manage` | Add member — validated against member pool |
```

- [ ] **Step 6: Verify**

Confirm:
- Creator tier resolution flow is present
- Tier table shows all four tiers with accessible dept rules
- Member pool table shows bypass logic
- `featureContext = 'teams'` is mentioned
- API endpoint table updated

- [ ] **Step 7: Commit**

```bash
git add modules/org-structure/teams/overview.md
git commit -m "docs: update teams module with creator tier resolution and hierarchy-aware member pool"
```
