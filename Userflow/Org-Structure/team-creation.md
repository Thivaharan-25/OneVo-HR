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
