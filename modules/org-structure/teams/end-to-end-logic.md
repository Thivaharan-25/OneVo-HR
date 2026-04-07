# Teams — End-to-End Logic

**Module:** Org Structure
**Feature:** Teams

---

## Create Team

### Flow

```
POST /api/v1/org/teams
  -> TeamController.Create(CreateTeamCommand)
    -> [RequirePermission("org:write")]
    -> TeamService.CreateAsync(command, ct)
      -> 1. Validate: name unique within department
      -> 2. Validate department_id exists
      -> 3. Validate team_lead_id is an active employee
      -> 4. INSERT into teams
      -> Return Result.Success(teamDto)
```

## Assign Members

### Flow

```
POST /api/v1/org/teams/{id}/members
  -> TeamController.AddMember(id, AddMemberCommand)
    -> [RequirePermission("org:write")]
    -> TeamService.AddMemberAsync(teamId, employeeId, ct)
      -> 1. Validate employee exists and is active
      -> 2. Check employee not already in team
      -> 3. INSERT into team_members
      -> Return Result.Success()

```

## Related

- [[teams|Overview]]
- [[departments]]
- [[job-hierarchy]]
- [[event-catalog]]
- [[error-handling]]
