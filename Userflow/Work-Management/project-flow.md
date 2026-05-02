# Project Management

**Area:** Workforce -> Projects (`/workforce/projects`)
**Trigger:** User clicks "Projects" in the Workforce panel
**Required Permission:** `projects:read` (view); `projects:write` (create/edit)

## Purpose

Projects are the top-level containers for all work in the WMS. Each project holds tasks, epics, milestones, sprints, and members. Projects are scoped to the current legal entity.

Project members are employee-backed in Phase 1. The system stores both `user_id` and `employee_id` so project access can follow HR status, offboarding, department/team reporting, and legal-entity scope.

## Key Entities

| Entity | Role |
|---|---|
| `PROJECT` | Top-level container: name, status, dates |
| `PROJECT_MEMBER` | Employee-backed user-to-project link with role (owner / member / viewer) |
| `EPIC` | Groups of related tasks within a project |
| `MILESTONE` | Target deliverable with a due date |
| `PROJECT_SETTING` | Timezone, working days, default priority |
| `CHANGE_REQUEST` | Formal request to change project scope or timeline |

## Flow Steps

### View All Projects

1. User opens Workforce -> Projects.
2. System loads all projects in the current legal entity scope, filtered by active membership.
3. Projects display as a list or grid: name, status badge, member count, open task count, due date.
4. User can filter by status or search by name.

### Create Project

1. User clicks "+ Create" in the Workforce panel header.
2. System opens a create form: name, description, start date, end date, default priority, working days.
3. User submits; system creates `PROJECT` plus project settings.
4. Creator is automatically added as `PROJECT_MEMBER` with role `Owner`, including both `user_id` and `employee_id`.
5. System redirects to the new project detail page.

### Project Detail (`/workforce/projects/[id]`)

1. User clicks a project card.
2. System loads: project overview, epics, milestones, recent activity, member list.
3. Sub-routes available from within project detail:
   - `/workforce/projects/[id]/board`: Kanban or list view of all tasks.
   - `/workforce/projects/[id]/sprints`: sprint planning and management.
   - `/workforce/projects/[id]/roadmap`: timeline view of epics and milestones.

### Add Project Member

1. From project detail, user clicks "Add Member" (requires `projects:write`).
2. User searches for an employee scoped to the same legal entity/workspace.
3. User selects a role: owner, member, or viewer.
4. System validates the employee is active and already belongs to the workspace.
5. System creates a `PROJECT_MEMBER` record with both `user_id` and `employee_id`.

### Submit Change Request

1. User clicks "Request Change" on project detail.
2. User fills the change form: type, description, impact.
3. System creates a `CHANGE_REQUEST` with status `pending`.
4. Project owners receive an Inbox notification to approve or reject.
5. Outcome is logged in the change request history.

## Connection Points

| Connects to | How |
|---|---|
| Workforce -> Presence | The employee's current task from this project shows on their presence card |
| Workforce -> My Work | My Work shows tasks from all projects where I am an active member |
| Workforce -> Planner | Project sprints and roadmap are accessible from the Planner item |
| Workforce -> Timesheets | Time is logged against tasks within this project |
| People -> Employees | Project members are ONEVO employees; profile link on the member list |
| Org Structure -> Teams | HR teams can sync into workspace membership through `workspace_hr_team_links` |
| Inbox | Change request approvals and project notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
