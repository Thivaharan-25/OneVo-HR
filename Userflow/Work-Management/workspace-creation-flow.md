# Workspace Creation

**Area:** WorkSync Workspace Creation  
**Trigger:** User creates a workspace for a reporting team, explicit team, or manually invited group  
**Required Permission:** `workspaces:create`; member management requires `workspaces:manage`

---

## Purpose

A workspace is a regular collaboration area for a group. It can hold members, chat, workspace-level resources, and links to projects. A workspace is not the same as a project, and it is not the source of truth for company reporting hierarchy.

Workspace members can come from:

| Source | Meaning | Stored as Org Team? |
|:-------|:--------|:--------------------|
| My Reporting Team | Employees below the creator in position hierarchy | No |
| Existing Explicit Team | Stored cross-functional or reusable Org Structure team | Yes |
| Manual Invite | Selected employees filtered by allowed pool or invite approval | No |

---

## Preconditions

- Employee records exist and have active user links for workspace access.
- Position hierarchy exists if the user wants to use "My Reporting Team".
- User has `workspaces:create`.
- User's active legal entity context is resolved before workspace creation.

---

## Flow Steps

### Step 1: Open Create Workspace

- **UI:** WorkSync -> Workspaces -> Create Workspace
- **Backend:** Checks module entitlement and `workspaces:create`.
- **Context:** Active legal entity is shown as read-only context.

### Step 2: Choose Member Source

User selects one source:

1. **My Reporting Team**
   - Backend resolves employees under the creator from `employee_hierarchy_closure`.
   - No `teams` row is created.
   - This is the default for a manager or team lead creating a workspace for their own people.

2. **Existing Explicit Team**
   - User selects a stored Org Structure team they are allowed to manage.
   - Workspace can optionally sync the team through `workspace_team_links`.

3. **Manual Invite**
   - User searches employees.
   - Search results are filtered by hierarchy, legal-entity authority, bypass grants, or approved invite state.
   - Outside-scope employees require a participation request instead of direct add.

### Step 3: Assign Workspace Roles

- **UI:** User assigns local workspace roles: Admin/Lead, Member, or Viewer.
- **Rule:** These are local workspace roles. They do not grant tenant-wide HR, payroll, security, billing, or project visibility.
- **Validation:** User cannot assign a role they are not allowed to grant.

### Step 4: Save Workspace

- **DB:** `workspaces`, `workspace_roles`, `workspace_members`.
- **If source is My Reporting Team:** only `workspace_members` are inserted; no duplicate stored team is created.
- **If source is Existing Explicit Team and sync is enabled:** `workspace_team_links` is created.

### Step 5: Add Outside Member Later

- **UI:** Workspace Settings -> Members -> Invite.
- Search defaults to the user's allowed pool.
- If the selected employee is outside the allowed pool, ONEVO creates a participation request.
- Target manager, workspace owner, legal-entity approver, or configured resolver approves/rejects.
- On approval, ONEVO adds the employee as a workspace member.

---

## Project Link From Workspace

When a workspace authority holder creates a project from a workspace:

1. User clicks Create Project from workspace.
2. System checks `projects:create` plus local workspace authority.
3. Project owning legal entity is set from active legal entity context.
4. Creator becomes project admin.
5. Workspace is auto-linked through `project_workspaces`.

When a project outside this workspace requests participation:

1. Workspace authority holder receives a participation request.
2. Request shows project purpose, requesting legal entity, requested members/data visibility, and expected responsibility.
3. Approver accepts, rejects, or limits the request.
4. Approved workspace becomes active in `project_workspaces`.

---

## Visibility Rules

- Workspace Admin/Lead sees workspace progress, members, tasks, blockers, and project links for this workspace.
- Workspace Member sees workspace resources and their own/project-visible work.
- Workspace Viewer sees read-only workspace content allowed by workspace policy.
- Being a reporting manager over an employee does not grant control over that employee inside another manager's workspace.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| User lacks `workspaces:create` | Blocked | "You do not have permission to create workspaces" |
| Reporting hierarchy missing | My Reporting Team unavailable | "Reporting hierarchy is not ready" |
| Selected employee outside allowed pool | Direct add blocked; request flow offered | "Request participation from this employee's owner" |
| Existing explicit team not manageable by user | Blocked | "You cannot use this team as a workspace source" |
| User tries to create duplicate stored team for reporting branch | Warning | "Use My Reporting Team instead of storing a duplicate team" |

---

## Related

- [[modules/work-management/foundation/overview|WorkSync Foundation]]
- [[modules/org-structure/teams/overview|Org Structure Teams]]
- [[modules/org-structure/positions/overview|Positions]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
