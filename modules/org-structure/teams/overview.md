# Teams

**Module:** Org Structure
**Feature:** Teams

---

## Purpose

Teams are tenant-scoped work groups made from employees. A team does not own or require a department. Department context for reporting is derived from the current departments of the employees inside the team. A user with `org:manage` can create teams, but the employees they can add depend on hierarchy scope, explicit bypass grants, and tenant permissions. See [[modules/auth/authorization/end-to-end-logic|Authorization - Hierarchy Scoping]] for bypass resolution.

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

Team roles represent scoped authority inside one HR team. They are configured from Roles & Permissions under Team Roles, not from team creation. Team creation and team editing only assign existing team roles to team members.

Allowed standard team roles:

- Admin / Lead
- Member
- Viewer / Reviewer

Team roles can carry scoped work-context permissions used by WorkSync when the team is linked to a workspace. They are separate from tenant security roles stored in `roles`.

Rules:

- Team role permissions apply only inside the linked team/work area.
- Team role permissions must not grant tenant-wide HR, payroll, security, or system administration authority.
- A user in multiple teams receives the union of their scoped team-role permissions inside each linked workspace where they have active workspace access.
- Project managers, tech leads, reviewers, or observers who are not in the HR team should be added directly as workspace members or project members with Admin, Member, or Viewer access instead of being forced into the HR team.
- Team creation UI must show only team roles. It must not show security roles.
- Team lead behavior must come from the assigned team role permissions/capabilities, not from a `teams.team_lead_id` shortcut.

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
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]

