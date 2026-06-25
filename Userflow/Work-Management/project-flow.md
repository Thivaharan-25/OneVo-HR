# Project Management

**Area:** Work -> Projects (`/work/projects`)
**Trigger:** User clicks "Projects" in the Work panel
**Required Permission:** `projects:read` (view); `projects:write` (create/edit)

## Purpose

Projects are the top-level containers for Phase 1 Work. Each project belongs to one workspace and holds work items, documents, members, settings, worklogs, and simple project views: Kanban, List, and Calendar. Phase 2 may add sprints, roadmaps, advanced dependency management, and advanced planning. Projects are tenant-local by default and scoped to the current company tenant.



The project's owning legal entity is auto-selected from the active legal entity context. Users with access to multiple legal entities select the context before creating the project; the form does not ask normal users to manually choose an owner entity.

## Key Entities

| Entity | Role |
|---|---|
| `PROJECT` | Top-level container: name, status, dates |
| `WORKSPACE` | Phase 1 collaboration container; a tenant can create multiple workspaces |
| `PROJECT_MEMBER` | Employee-backed user-to-project link with local access level (admin / member / viewer) |
| `PROJECT_MEMBER_INVITATION` | Direct invite from project/workspace admin to an employee/member; recipient accepts or declines |
| `PROJECT_LINK_INVITATION` | Simple invite from one project admin to another project admin to create a project-link record |
| `PROJECT_LINK` | Accepted simple relationship between two projects; not an advanced dependency platform |
| `EPIC` | Groups of related tasks within a project |
| `MILESTONE` | Target deliverable with a due date |
| `PROJECT_SETTING` | Timezone, working days, default priority |
| `CHANGE_REQUEST` | Formal request to change project scope or timeline |

## Flow Steps

### View All Projects

1. User opens Work -> Projects.
2. System loads all projects in the current company tenant scope, filtered by active membership.
3. Projects display as a list or grid: name, status badge, member count, open task count, due date.
4. User can filter by status or search by name.

### Create Project

1. User clicks "+ Create" in the Work panel header.
2. System reads the active legal entity context and selected workspace context. Both are shown as read-only context, not as free-form owner fields.
3. System opens a create form: name, description, start date, end date, default priority, working days.
4. User submits; system creates `PROJECT` plus project settings with `owning_legal_entity_id` from the active context and `workspace_id` from the selected workspace.
5. Creator is automatically added as `PROJECT_MEMBER` with local access level `admin`, including both `user_id` and `employee_id`.
6. The project opens with Kanban, List, and Calendar views for its work items.
7. System redirects to the new project detail page.

### Add Project Members

1. Project admin opens Project -> Members -> Invite Member.
2. User searches active employees/members in the current tenant and permitted company context.
3. User selects a local project access level: admin, member, or viewer.
4. System validates each selected employee is active and belongs to the tenant.
5. System creates a `PROJECT_MEMBER_INVITATION` for each selected recipient.
6. The selected member receives an Inbox action and accepts or declines.
7. On acceptance, ONEVO creates the `PROJECT_MEMBER` row.
8. Workspace membership alone is not project visibility. Project visibility comes from accepted project membership or a scoped project permission.

### Link Projects

1. Project admin opens Project -> Links -> Invite Project Link.
2. User selects another project visible to them or enters the target project/admin according to the allowed UI.
3. ONEVO sends a `PROJECT_LINK_INVITATION` to the selected target project admin.
4. Target project admin accepts or declines.
5. On acceptance, ONEVO creates a simple `PROJECT_LINK` record.
6. Phase 1 project links are informational/simple relationship records. Advanced project-linking, dependency management, cross-workspace source pools, and project-to-project governance platforms are Phase 2.

### Project Detail (`/work/projects/[id]`)

1. User clicks a project card.
2. System loads: project overview, epics, milestones, recent activity, member list.
3. Sub-routes available from within project detail:
   - `/work/projects/[id]/items`: Kanban, List, and Calendar views of project work items.
   - `/work/projects/[id]/sprints`: sprint planning and management (Phase 2).
   - `/work/projects/[id]/roadmap`: timeline view of epics and milestones (Phase 2).

### Add Project Member

1. From project detail, user clicks "Add Member" (requires `projects:write`).
2. User searches for an active employee in the same company tenant. Search results are filtered by project authority and active company context.
3. User selects a local access level: admin, member, or viewer.
4. System validates the employee is active and belongs to the tenant.
5. System creates a project member invitation. The employee/member must accept before becoming an active project member.

### Cross-Company Project Participation

Cross-company projects are not created by switching an in-tenant operating scope. They require an active company connection plus an explicit project/workspace data-sharing scope. Members from a connected company may be represented through a controlled projection or invite flow, while source-of-truth employee records remain inside their own tenant.

### Multi-Company Project Rule

Project creation happens inside the currently selected Company context. If an admin needs a project for a different Company, they switch Company in the topbar first and must hold the required project permission in that Company. Phase 1 does not expose a free-form Company/legal-entity picker inside the create project form.

Simple project-link invitations may connect two projects when both sides' project admins accept. This does not move employee source-of-truth records, create workspace source pools, or grant cross-company employee visibility.

### Project Dashboard Visibility

When a user opens a project dashboard:

1. System checks `projects:read` and project membership or approved scoped grant.
2. System determines viewer context:
   - full project administration
   - project member
   - viewer/stakeholder
3. Dashboard cards are filtered:
   - Full project administration sees overall health, members, risks, blockers, and pending project actions.
   - Reporting manager context sees only their reports' contribution where project membership or project authority allows it.
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
| Monitoring -> Live Status | The employee's current task from this project may show on their presence card when enabled |
| Work -> Work Items | Work Items shows tasks from all projects where I am an active member |
| Work -> Planner (Phase 2) | Project sprints and roadmap are deferred Phase 2 planning surfaces |
| Work -> Worklogs | Time is logged against tasks within this project |
| People -> Employees | Project members are ONEVO employees; profile link on the member list |
| Inbox | Project member invitations, project-link invitations, change request approvals, and project notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
