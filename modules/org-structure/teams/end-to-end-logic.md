# Teams - End-to-End Logic

**Module:** Org Structure
**Feature:** Teams

---

## Create Team

### Flow

```
POST /api/v1/org/teams
  -> TeamController.Create(CreateTeamCommand)
    -> [RequirePermission("org:manage")]
      -> TeamService.CreateAsync(command, ct)
      -> 1. Resolve creator's allowed employee member pool
      -> 2. Validate team name unique within tenant
      -> 3. Validate each submitted member is active and inside member pool
      -> 4. Validate submitted team_role_ids reference team roles only
      -> 5. Reject any role id that belongs to security roles (`roles`) instead of team roles (`team_roles`)
      -> 6. INSERT into teams
      -> 7. INSERT into team_members for each submitted member
      -> 8. INSERT into team_member_roles for each submitted member
      -> Return Result.Success(teamDto)
```

### Validation Rules

- Team creation must assign only `team_roles`: `Admin / Lead`, `Member`, or `Viewer / Reviewer`.
- Team creation must not assign tenant security `roles` or direct `role_permissions`.
- Every submitted member must be an active employee inside the resolved member pool.
- Bypass-granted employees are allowed only when resolved by `hierarchy_scope_exceptions` for `featureContext = "teams"`.
- Team has no `department_id`. Department reporting is derived from `team_members -> employees.department_id`.
- Team has no `team_lead_id`. Lead/admin behavior is derived from `team_member_roles -> team_roles -> team_role_permissions`.

## Assign Members

### Flow

```
POST /api/v1/org/teams/{id}/members
  -> TeamController.AddMember(id, AddMemberCommand)
    -> [RequirePermission("org:manage")]
    -> TeamService.AddMemberAsync(teamId, employeeId, teamRoleId, ct)
      -> 1. Resolve creator's allowed employee member pool
      -> 2. Validate team exists in tenant
      -> 3. Validate employee exists, is active, and is inside member pool
      -> 4. Validate teamRoleId references `team_roles`
      -> 5. Reject security role ids from `roles`
      -> 6. Check employee not already active in team
      -> 7. INSERT into team_members
      -> 8. INSERT into team_member_roles
      -> Return Result.Success()

```

## Replace Member Team Roles

### Flow

```
PUT /api/v1/org/teams/{id}/members/{employeeId}/roles
  -> TeamController.ReplaceMemberRoles(id, employeeId, command)
    -> [RequirePermission("org:manage")]
    -> TeamService.ReplaceMemberRolesAsync(teamId, employeeId, teamRoleIds, ct)
      -> 1. Validate team and employee membership exist
      -> 2. Validate all submitted role ids reference `team_roles`
      -> 3. Reject security role ids from `roles`
      -> 4. Close removed team_member_roles by setting effective_to
      -> 5. Insert newly assigned team_member_roles with effective_from
      -> Return Result.Success()
```

## Related

- [[modules/org-structure/teams/overview|Overview]]
- [[modules/org-structure/departments/overview|Departments]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
