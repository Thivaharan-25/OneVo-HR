# Team Creation

**Area:** Org Structure
**Trigger:** User with `org:manage` creates a team (user action)
**Required Permission(s):** `org:manage`
**Related Permissions:** `employees:read` (to search members; team lead is derived from team-role assignment), `roles:manage` only if the user also configures team-role permission sets from Roles & Permissions

---

## Preconditions

- Employee records exist.
- Employee reporting lines are available for scoped creators. If reporting lines are missing, only unrestricted org admins can create teams until hierarchy data is complete.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Member Pool

The set of employees a creator can add as members and assign team roles is resolved from permission scope, hierarchy scope, and bypass grants.

| Source | Member pool |
|:-------|:------------|
| Organization-scope org/team admin | All active employees in tenant |
| Scoped manager/lead | Employees inside resolved hierarchy/reporting scope |
| Bypass grant | Explicit employees allowed through `hierarchy_scope_exceptions` for `featureContext = 'teams'` |

Department is not selected on the team. If reporting needs department context, the backend derives it from the current departments of employees in `team_members`.

## Flow Steps

### Step 1: Navigate to Teams
- **UI:** Sidebar -> Organization -> Teams -> click "Create Team"
- **API:** `GET /api/v1/org/teams`
- **Backend:** Resolves whether creator can create teams and prepares member-pool search rules

### Step 2: Define Team
- **UI:** Enter team name and optional description
- **Validation:** Name unique within tenant

### Step 3: Add Members And Assign Team Roles
- **UI:** Search employee from resolved member pool -> add employee -> select a Team Role from the team-role picker
- **Allowed Team Roles:** `Admin / Lead`, `Member`, `Viewer / Reviewer`
- **Backend:** Creates `team_members` rows and assigns selected `team_member_roles` rows. Team creation must not assign tenant security roles or direct `role_permissions`.
- **Leadership Rule:** Team lead/admin behavior is derived from the employee's assigned team role and team-role permissions. The team record must not store `team_lead_id`.

### Step 4: Confirm Members
- **UI:** Search employees from resolved member pool -> add to team -> select a Team Role for each member
  - Bypass-granted employees show a "Bypass" badge indicating they are outside normal hierarchy scope
- **API:** `POST /api/v1/org/teams`
- **DB:** `teams`, `team_members`, `team_member_roles` - records created
- **Validation:** Team creation shows only `team_roles`. It must not show or accept security-role records from `roles`.

### Step 5: Confirmation
- **UI:** Team visible in team list. Department reporting, if shown, is derived from the team's current members.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate name in tenant | Validation fails | "Team name already exists" |
| Team lead not in member pool | `403 Forbidden` | "Team lead must be within your accessible employee pool" |
| Member not in member pool (API) | `403 Forbidden` | "You can only add employees within your allowed scope" |
| Security role submitted as team role | `400 Bad Request` | "Select a team role for this team member" |
| Unknown team role | `400 Bad Request` | "Team role is not available" |
| No reporting-line data for scoped creator | Team creation blocked | "No eligible employees found in your hierarchy" |

## Events Triggered

- `TeamCreated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - security roles, team-role permission sets, and bypass grants configured here
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

## Module References

- [[modules/org-structure/teams/overview|Teams]] - member pool and team-role assignment logic
- [[modules/auth/authorization/end-to-end-logic|Authorization]] - IHierarchyScope, bypass resolution
- [[modules/org-structure/overview|Org Structure]]

