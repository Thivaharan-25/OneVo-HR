# Contract: WorkSync Core (Workspaces + Projects + Tasks)

**Backend owner:** DEV3 Tasks 1-2  
**Consumers:** DEV7 Tasks 1-2, DEV8 Tasks 2-4  
**Canonical source:** `ONEVO.Application/Features/WorkSync/`

---

## GET `/api/v1/workspaces`

```ts
interface WorkspaceDto {
  id: string
  name: string
  slug: string
  member_count: number
  your_role: string
}
```

## GET `/api/v1/projects` (cursor paginated)

```ts
interface ProjectDto {
  id: string
  name: string
  status: "active" | "on_hold" | "completed" | "archived"
  owner: { id: string; full_name: string }
  member_count: number
  open_task_count: number
  created_at: string
}
```

## GET `/api/v1/projects/{id}/tasks` (cursor paginated)

```ts
interface TaskDto {
  id: string
  title: string
  status: string
  priority: "none" | "low" | "medium" | "high" | "urgent"
  assignees: Array<{
    user_id: string
    employee_id: string
    full_name: string
    avatar_url: string | null
    availability_status: "available" | "on_leave" | "unavailable" | null
    availability_warning: string | null
  }>
  due_date: string | null
  sprint_id: string | null
  labels: string[]
  created_at: string
}
```

## GET `/api/v1/ide/tasks/assigned` -> `TaskDto[]`

Tasks assigned to the authenticated user; used by DEV8 Tasks panel.

## Notes

- `availability_status` and `availability_warning` are set server-side by the Time Off + Calendar check at assignment time
- `availability_status: null` means no check has run yet (pre-existing assignments before the feature)
- Workspace membership requires an active employee record in Phase 1
- Tenant-scoped; workspace APIs enforce membership before returning project data

