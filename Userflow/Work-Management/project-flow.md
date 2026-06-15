# Project Management

**Area:** Workforce -> Projects (`/workforce/projects`)
**Trigger:** User clicks "Projects" in the Workforce panel
**Required Permission:** `projects:read` (view); `projects:write` (create/edit)

## Purpose

Projects are the top-level containers for all work in the WMS. Each project holds tasks, epics, milestones, sprints, and members. Projects are tenant-local by default and scoped to the current company tenant.

Project members are employee-backed in Phase 1. The system stores both `user_id` and `employee_id` so project access can follow HR status, offboarding, department/team reporting, and company tenant scope.

Projects can involve multiple team workspaces. Linked workspaces provide team context, member suggestions, task grouping, and reporting, but they do not automatically expose the project to every member of those workspaces. Project visibility comes from `PROJECT_MEMBER`.

The project's owning legal entity is auto-selected from the active legal entity context. Users with access to multiple legal entities select the context before creating the project; the form does not ask normal users to manually choose an owner entity.

## Key Entities

| Entity | Role |
|---|---|
| `PROJECT` | Top-level container: name, status, dates |
| `PROJECT_WORKSPACE` | Link between a project and an involved team workspace; context only, not access |
| `PROJECT_MEMBER` | Employee-backed user-to-project link with local access level (admin / member / viewer) |
| `EPIC` | Groups of related tasks within a project |
| `MILESTONE` | Target deliverable with a due date |
| `PROJECT_SETTING` | Timezone, working days, default priority |
| `CHANGE_REQUEST` | Formal request to change project scope or timeline |
| `WORKSPACE_PARTICIPATION_REQUEST` | Request for another workspace/legal entity to join a project |

## Flow Steps

### View All Projects

1. User opens Workforce -> Projects.
2. System loads all projects in the current company tenant scope, filtered by active membership.
3. Projects display as a list or grid: name, status badge, member count, open task count, due date.
4. User can filter by status or search by name.

### Create Project

1. User clicks "+ Create" in the Workforce panel header.
2. System reads the active legal entity context and shows it as read-only context, not as a free-form owner field.
3. System opens a create form: name, description, start date, end date, default priority, working days.
4. User submits; system creates `PROJECT` plus project settings with `owning_legal_entity_id` from the active context.
5. Creator is automatically added as `PROJECT_MEMBER` with local access level `admin`, including both `user_id` and `employee_id`.
6. User can link one or more workspaces to the project for context.
7. System redirects to the new project detail page.

### Link Workspace To Project

1. Project admin opens Project -> Workspaces -> Add Workspace.
2. UI shows:
   - Workspaces the user can manage directly.
   - Workspaces already participating.
   - Request another workspace.
3. If the selected workspace is managed by the user, ONEVO creates an active `PROJECT_WORKSPACE` link immediately.
4. If the workspace is outside the user's managed context or legal entity, ONEVO creates a pending participation request.
5. Target workspace/legal-entity approver receives an Inbox action card with project purpose, requested workspace, requested members or data visibility, and requested role.
6. Approver approves, rejects, or limits the request.
7. On approval, ONEVO activates the `PROJECT_WORKSPACE` link.

### Add Project Members From Workspace

1. Project admin opens Project -> Members -> Add Member.
2. UI offers approved linked workspaces as source pools.
3. User selects members and local project access level: admin, member, or viewer.
4. System validates each selected employee is active and the workspace participation is active.
5. System creates `PROJECT_MEMBER` rows.
6. Workspace membership alone remains insufficient for project visibility unless the member is explicitly added or a project policy selects them.

### Project Detail (`/workforce/projects/[id]`)

1. User clicks a project card.
2. System loads: project overview, epics, milestones, recent activity, member list.
3. Sub-routes available from within project detail:
   - `/workforce/projects/[id]/board`: Kanban or list view of all tasks.
   - `/workforce/projects/[id]/sprints`: sprint planning and management.
   - `/workforce/projects/[id]/roadmap`: timeline view of epics and milestones.

### Add Project Member

1. From project detail, user clicks "Add Member" (requires `projects:write`).
2. User searches for an active employee in the same company tenant. Search results are filtered by project authority, linked workspace source pools, legal-entity context, and approved invite state.
3. User selects a local access level: admin, member, or viewer.
4. System validates the employee is active and belongs to the tenant.
5. System creates a `PROJECT_MEMBER` record with both `user_id` and `employee_id`.

### Cross-Company Project Participation

Cross-company projects are not created by switching an in-tenant operating scope. They require an active company connection plus an explicit project/workspace data-sharing scope. Members from a connected company may be represented through a controlled projection or invite flow, while source-of-truth employee records remain inside their own tenant.

### Multi-Legal-Entity Project Journey

1. Project admin creates the project in the active legal entity context.
2. Admin links a workspace from their own legal entity.
3. Admin clicks Request Workspace and selects a workspace or legal entity outside their authority.
4. ONEVO sends a participation request to the target workspace/legal-entity approver.
5. Target approver reviews:
   - project purpose
   - requested participation
   - requested members or source pool
   - data visibility level
   - expected task responsibility
6. If approved, ONEVO activates the workspace link and allows selected members to be added as project members.
7. Tasks can now be assigned to that responsible workspace.
8. Progress and health roll up by responsible workspace and legal entity.

### Project Dashboard Visibility

When a user opens a project dashboard:

1. System checks `projects:read` and project membership or approved scoped grant.
2. System determines viewer context:
   - full project administration
   - legal entity contribution
   - workspace contribution
   - reporting-manager/team contribution
   - project member
   - viewer/stakeholder
3. Dashboard cards are filtered:
   - Full project administration sees overall health, all workspaces, all legal entities, all risks, all blockers, and all pending approvals.
   - Legal entity context sees only that entity's contribution.
   - Workspace context sees only that workspace's tasks, progress, blockers, members, and milestones.
   - Reporting manager context sees only their reports' contribution inside project/workspace contexts they can access.
   - Project member sees own tasks, watched tasks, blockers they raised, assigned milestones, and published announcements.
   - Viewer sees published summary only.

### Submit Change Request

1. User clicks "Request Change" on project detail.
2. User fills the change form: type, description, impact.
3. System creates a `CHANGE_REQUEST` with status `pending`.
4. Project admins receive an Inbox notification to approve or reject.
5. Outcome is logged in the change request history.

## Connection Points

| Connects to | How |
|---|---|
| Workforce -> Presence | The employee's current task from this project shows on their presence card |
| Workforce -> My Work | My Work shows tasks from all projects where I am an active member |
| Workforce -> Planner | Project sprints and roadmap are accessible from the Planner item |
| Workforce -> Timesheets | Time is logged against tasks within this project |
| People -> Employees | Project members are ONEVO employees; profile link on the member list |
| Org Structure -> Teams | Explicit stored teams can sync into workspace membership through `workspace_team_links`; project membership remains explicit through `PROJECT_MEMBER` |
| Inbox | Change request approvals and project notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
