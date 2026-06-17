# Teams

**Module:** Org Structure
**Feature:** Teams

---

## Purpose

Teams are tenant-scoped explicit work groups made from employees. A stored team is used only when the group is not simply the current reporting hierarchy, or when the customer wants a reusable named group that can be linked to a workspace.

Do not create a stored `teams` row for every reporting manager. A reporting manager's people are a **virtual reporting team** resolved from `employee_hierarchy_closure`, which is derived from position hierarchy. The UI may show "My Reporting Team" as a selectable source when creating a workspace, but that source is calculated from positions and is not persisted in `teams` or `team_members`.

A team does not own or require a department. Department context for reporting is derived from the current departments of the employees inside the team. A user with `org:manage` can create explicit teams, but the employees they can add depend on hierarchy scope, explicit bypass grants, and tenant permissions. See [[modules/auth/authorization/end-to-end-logic|Authorization - Hierarchy Scoping]] for bypass resolution.

Use stored teams for stable or cross-functional groups such as "Payroll Implementation Group" or "HR Operations Reviewers". Use the virtual reporting team for "people under this manager/team lead".

## Database Tables

### `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | Unique within tenant |
| `description` | `text` | nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

Team leadership is derived from `team_member_roles -> team_roles`. Do not store `team_lead_id`; it creates a second source of truth that can contradict team role assignment.

### `team_members`
Join table: `team_id`, `employee_id`, `joined_at`, `left_at`. PK: `(team_id, employee_id)`. Current membership is `left_at IS NULL`; historical membership remains available for reporting and audit.

### `team_roles`, `team_member_roles`, `team_role_permissions`

Team roles represent scoped authority inside one explicit stored team. They are configured from Roles & Permissions under Team Roles, not from team creation. Team creation and team editing only assign existing team roles to team members.

Allowed standard team roles:

- Admin / Lead
- Member
- Viewer / Reviewer

Team roles can carry scoped work-context permissions used by WorkSync when the team is linked to a workspace. They are separate from tenant security roles stored in `roles`.

Rules:

- Team role permissions apply only inside the linked team/work area.
- Team role permissions must not grant tenant-wide HR, payroll, security, or system administration authority.
- A user in multiple teams receives the union of their scoped team-role permissions inside each linked workspace where they have active workspace access.
- Project managers, tech leads, reviewers, or observers who are not in the explicit stored team should be added directly as workspace members or project members with Admin, Member, or Viewer access instead of being forced into that team.
- Team creation UI must show only team roles. It must not show security roles.
- Team lead behavior must come from the assigned team role permissions/capabilities, not from a `teams.team_lead_id` shortcut.
- A user's reporting authority over an employee must not leak into unrelated workspaces or projects. Hierarchy can be used to choose eligible members for a workspace the user manages, but actions inside a workspace/project require the relevant workspace or project context role.

## Member Pool Resolution

On `POST /api/v1/org/teams`, the service resolves the creator's allowed employee pool before validating the request:

```
TeamService.ResolveMemberPoolAsync(creatorEmployeeId)
  -> Query hierarchy/reporting scope for creator
  -> Add explicit hierarchy bypass grants for featureContext = "teams"
  -> If creator has organization-scope org/team management permission, allow all active tenant employees
  -> Return eligible employee ids
```

**Member pool:**

| Source | Meaning |
|:-------|:--------|
| Hierarchy scope | Employees inside the creator's allowed reporting/hierarchy scope |
| Bypass grants | Employees explicitly allowed through `hierarchy_scope_exceptions` for `featureContext = "teams"` |
| Organization scope | All active tenant employees when the creator has organization-wide org/team management permission |

`IHierarchyScope.GetSubordinateIdsAsync(featureContext: "teams")` provides hierarchy and bypass sets. Department is not a team ownership boundary; department reporting can be computed from `team_members -> employees.department_id`.

## Workspace Creation Source Rules

When a user creates a WorkSync workspace, the workspace member source can be:

| Source | Stored in `teams`? | Meaning |
|:-------|:-------------------|:--------|
| My Reporting Team | No | Employees under the creator in the current position hierarchy. Recomputed each time from `employee_hierarchy_closure`. |
| Existing Explicit Team | Yes | A named stored team from `teams`/`team_members`, usually cross-functional or reusable. |
| Manual Invite | No | Employee search filtered by hierarchy, bypass grants, workspace/project invite approval, or organization-wide authority. |

If the source is "My Reporting Team", the workspace stores only `workspace_members`; it does not create a matching `teams` row. If a reporting change happens later, existing workspace membership does not silently change unless the workspace uses an explicit sync policy. This prevents reporting history and workspace collaboration history from becoming the same thing.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/teams` | `org:manage` | List teams visible to creator by tenant permission/scope |
| POST | `/api/v1/org/teams` | `org:manage` | Create tenant-scoped team and assign team roles only; validates members against member pool + bypass grants |
| PUT | `/api/v1/org/teams/{id}` | `org:manage` | Update team |
| DELETE | `/api/v1/org/teams/{id}` | `org:manage` | Deactivate team |
| GET | `/api/v1/org/teams/{id}/members` | `org:manage` | List team members with assigned team roles |
| POST | `/api/v1/org/teams/{id}/members` | `org:manage` | Add member and assign team role; validated against member pool |
| PUT | `/api/v1/org/teams/{id}/members/{employeeId}/roles` | `org:manage` | Replace this member's team roles; accepts `team_roles` only |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/auth/authorization/end-to-end-logic|Authorization]] - IHierarchyScope, bypass resolution
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
