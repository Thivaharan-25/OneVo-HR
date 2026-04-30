# Task Management — End-to-End Logic

**Module:** WorkSync
**Feature:** Task Management

---

## Create Task

```
POST /api/v1/projects/{id}/tasks
  → [RequirePermission("tasks:write")]
  → FluentValidation: title required, status in enum, project_id valid
  → CreateTaskHandler
    → 1. Verify project exists and user is project member
    → 2. Generate short_id: project.identifier + NEXTVAL(project_task_sequence)
         e.g. "TASK-124"
    → 3. Validate parent_task_id if provided (must be in same project)
    → 4. Validate epic_id if provided (must be in same project)
    → 5. Create Task entity (status = "todo" default)
    → 6. Create TaskAssignment rows for each assignee_id
    → 7. Publish TaskCreatedEvent
    → Return Result<TaskDto>
  → 201 Created
```

## Update Task Status

```
PATCH /api/v1/tasks/{id}/status
  → [RequirePermission("tasks:write")]
  → UpdateTaskStatusHandler
    → 1. Load task, verify workspace + tenant scope
    → 2. Validate status transition (server-side state machine):
         Allowed: todo→in_progress, in_progress→in_review, in_review→done,
                  any→cancelled, done→todo (re-open)
         Blocked: cannot go done→in_progress directly
    → 3. If transitioning to "done" AND project has approval flow:
         Check task_approvals: must have an approved row
         If not: return 422 APPROVAL_REQUIRED
    → 4. Update tasks.status
    → 5. Publish TaskStatusChangedEvent (consumed by sprint burndown, reminders)
    → 6. If status = "done": also check for linked reminder (chat_reminder_items)
         → if found: mark reminder complete
    → Return Result<TaskDto>
```

## Move Card on Board

```
PATCH /api/v1/boards/{id}/tasks/{taskId}/move
  → [RequirePermission("tasks:write")]
  → MoveCardHandler
    → 1. Load board_column by target column_id
    → 2. Check WIP limit: if wip_limit is set:
         COUNT tasks in target column WHERE status = column.status_key
         If count >= wip_limit: return 422 WIP_LIMIT_EXCEEDED
    → 3. BEGIN TRANSACTION
         a. UPDATE tasks.status = column.status_key
         b. UPSERT board_task_positions (board_id, column_id, task_id, position)
         c. Publish TaskStatusChangedEvent
    → 4. COMMIT
    → Return Result<BoardTaskPositionDto>
```

## Task Approval Flow

```
POST /api/v1/tasks/{id}/approvals  (submit for approval)
  → CreateTaskApprovalHandler
    → 1. Verify project has approval_flow enabled
    → 2. Task must be in "in_review" status
    → 3. Create task_approvals row (status = pending)
    → 4. Notify approver via Notifications module
    → Return 201

PATCH /api/v1/tasks/{id}/approvals/{approvalId}/approve
  → ApproveTaskHandler
    → 1. Verify caller is the designated approver_id
    → 2. Update task_approvals.status = approved, decided_at = now()
    → 3. Update tasks.status = "done" (skips normal transition check)
    → 4. Publish TaskApprovedEvent → TaskCompletedEvent
```

## Custom Field Values

```
PATCH /api/v1/tasks/{id}/custom-fields
  → UpdateCustomFieldValuesHandler
    → 1. Load custom_field definitions for project
    → 2. For each value in request:
         a. Validate field_type matches value type (text/number/date/select)
         b. For select type: validate value is in options_json
         c. If field is_required and value is null: return 422
    → 3. UPSERT custom_field_values (task_id, custom_field_id, typed value column)
    → Return Result<TaskDto> with custom fields populated
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Invalid status transition | 422 | Invalid status transition: {from} → {to} |
| Approval required before done | 422 | Task requires approval before completion |
| WIP limit exceeded | 422 | Column WIP limit reached ({n}/{wip_limit}) |
| short_id collision (race) | 409 | Retry — sequence gap; regenerate |
| Custom field required but null | 422 | Field '{name}' is required |

### Edge Cases

- Subtask status change does not cascade to parent — parent status must be updated manually.
- Archived tasks: `is_archived = true` — excluded from board view but not deleted. Queries must filter `WHERE is_archived = false` (global filter handles this).
- Sprint task removal: removing from sprint sets `sprint_backlog_items.removed_at = now()` but does NOT reset `tasks.sprint_id` automatically.

## Related

- [[modules/work-management/tasks/overview|Tasks Overview]]
- [[modules/work-management/planning/end-to-end-logic|Planning Logic]] — board mechanics detail
- [[modules/work-management/tasks/testing|Tasks Testing]]
