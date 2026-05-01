# Project Management — End-to-End Logic

**Module:** WorkSync
**Feature:** Project Management

---

## Create Project

```
POST /api/v1/workspaces/{wsId}/projects
  → [RequirePermission("projects:create")]
  → CreateProjectHandler
    → 1. Verify user is workspace member
    → 2. Validate: name required, identifier unique within workspace
         (identifier: 2-6 uppercase letters, e.g. "TASK", "BUG")
    → 3. Create Project entity (status = "active")
    → 4. Add creator as Owner in project_members
    → 5. Publish ProjectCreatedEvent
    → Return Result<ProjectDto>
  → 201 Created
```

## Archive Project

```
PATCH /api/v1/projects/{id}/archive
  → [RequirePermission("projects:write") + must be Owner or Workspace Admin]
  → ArchiveProjectHandler
    → 1. Verify project status != "archived"
    → 2. Check active sprint: if sprint status = "active" → return 422
         "Complete active sprint before archiving project"
    → 3. UPDATE projects.status = "archived"
    → 4. Publish ProjectArchivedEvent
         → Close open sprints (set status = "completed"), notify members
    → Return Result<ProjectDto>
```

## Manage Project Members

```
POST /api/v1/projects/{id}/members
  → [RequirePermission("projects:write")]
  → AddProjectMemberHandler
    → 1. Verify user is a workspace member (must join workspace first)
    → 2. Verify user not already a project member
    → 3. INSERT project_members (role = "Member" default)
    → Return 201

DELETE /api/v1/projects/{id}/members/{userId}
  → 1. Cannot remove the Owner unless transferring ownership first
  → 2. DELETE project_members row
```

## Transfer Project Ownership

```
PATCH /api/v1/projects/{id}/owner
  body: { new_owner_id }
  → TransferOwnershipHandler
    → 1. Verify caller is current Owner OR Workspace Admin
    → 2. BEGIN TRANSACTION
         a. UPDATE project_members SET role = "Admin"
               WHERE project_id = ? AND user_id = current_owner (demote)
         b. UPDATE project_members SET role = "Owner"
               WHERE project_id = ? AND user_id = new_owner_id
    → 3. COMMIT
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Identifier not unique | 409 | Project identifier already in use |
| Archive with active sprint | 422 | Complete active sprint first |
| Add non-workspace member | 422 | User must be a workspace member |
| Remove Owner without transfer | 422 | Transfer ownership before removing |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/testing|Projects Testing]]
