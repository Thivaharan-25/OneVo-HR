# Planning — End-to-End Logic

**Module:** WorkSync
**Feature:** Planning (Sprints, Boards, Roadmaps)

---

## Activate Sprint

```
PATCH /api/v1/sprints/{id}/activate
  → [RequirePermission("sprints:manage")]
  → ActivateSprintHandler
    → 1. Verify sprint status = "planning"
    → 2. Check no other sprint in project has status = "active"
         If found: return 409 ACTIVE_SPRINT_EXISTS
    → 3. Verify start_date and end_date are set
    → 4. Update sprints.status = "active"
    → 5. Publish SprintActivatedEvent
         → SignalR IDEHub fires "sprint:updated" to connected IDE clients
    → Return Result<SprintDto>
```

## Add Task to Sprint

```
POST /api/v1/sprints/{id}/backlog
  → AddToSprintHandler
    → 1. Verify sprint is in "planning" or "active" status
    → 2. Verify task belongs to same project as sprint
    → 3. Check task not already in sprint (sprint_backlog_items WHERE removed_at IS NULL)
    → 4. INSERT sprint_backlog_items (sprint_id, task_id, added_at, added_by_id)
    → 5. UPDATE tasks.sprint_id = sprint_id (denorm convenience field)
    → Return 201
```

## Complete Sprint

```
PATCH /api/v1/sprints/{id}/complete
  → [RequirePermission("sprints:manage")]
  → CompleteSprintHandler
    → 1. Verify sprint status = "active"
    → 2. BEGIN TRANSACTION
         a. Mark sprint: status = "completed", completed_at = now()
         b. For all incomplete tasks in sprint:
            sprint_backlog_items.removed_at = now()
            tasks.sprint_id = null
         c. Generate sprint_reports row (summary stats)
    → 3. COMMIT
    → 4. Publish SprintCompletedEvent
    → Return Result<SprintReportDto>
```

## Nightly Burndown Snapshot (Hangfire)

```
Hangfire: SprintDailySnapshotJob — runs at 00:05 UTC daily
  → For each active sprint across all tenants:
      → Count tasks in sprint_backlog_items (removed_at IS NULL)
      → Sum story_points: total / completed / remaining
      → Sum added/removed today (events since yesterday's snapshot)
      → INSERT sprint_daily_snapshots row
         (sprint_id, snapshot_date=today, total, completed, remaining, added, removed)
  → No duplicate: UPSERT on (sprint_id, snapshot_date)
```

## Board Card Move (Full Flow)

```
PATCH /api/v1/boards/{boardId}/tasks/{taskId}/move
  body: { targetColumnId, afterTaskId? }
  → MoveCardHandler
    → 1. Load target board_column
    → 2. WIP limit check (see Tasks end-to-end-logic)
    → 3. Calculate new position:
         If afterTaskId provided: position = (afterTask.position + nextTask.position) / 2
         If null: position = last position + 1000
    → 4. BEGIN TRANSACTION
         a. UPDATE tasks.status = column.status_key
         b. UPSERT board_task_positions SET column_id=?, position=?
            WHERE board_id=? AND task_id=?
    → 5. COMMIT
    → 6. Publish BoardCardMovedEvent (triggers TaskStatusChangedEvent)
```

## Roadmap Item Creation

```
POST /api/v1/workspaces/{wsId}/roadmaps/{rmId}/items
  body: { entity_type, entity_id, start_date, end_date, color }
  → AddRoadmapItemHandler
    → 1. Validate entity_type in (Epic, Milestone, Sprint)
    → 2. Verify entity_id exists in correct table
    → 3. Verify entity belongs to a project in same workspace
    → 4. INSERT roadmap_items
    → Return 201
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Activate with existing active sprint | 409 | Project already has an active sprint |
| Sprint missing dates | 422 | start_date and end_date required |
| Task already in sprint | 409 | Task is already in this sprint |
| WIP limit exceeded on move | 422 | Column WIP limit reached |
| Invalid roadmap entity_type | 422 | entity_type must be Epic, Milestone, or Sprint |

### Edge Cases

- Sprint burndown gap days (no snapshot written for completed/planning sprints): handled by chart rendering logic (fill gap with last known value).
- Position float collision (2 cards at same position): detected and auto-resolved by reindexing on next load.
- Completing a sprint with zero tasks: allowed — generates report with 0 points.

## Related

- [[modules/work-management/planning/overview|Planning Overview]]
- [[modules/work-management/tasks/end-to-end-logic|Tasks Logic]] — status transitions
- [[modules/work-management/planning/testing|Planning Testing]]
