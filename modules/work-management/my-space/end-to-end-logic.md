# My Space & Reminders — End-to-End Logic

**Module:** WorkSync
**Feature:** My Space & Reminders

---

## Create Reminder

```
POST /api/v1/me/reminders
  body: { title, due_at, linked_task_id?, recurrence_rule? }
  → CreateReminderHandler
    → 1. If linked_task_id: verify task exists and user has access
    → 2. If linked_task_id: check no existing reminder for same user + task
         If exists: return 409 DUPLICATE_REMINDER
    → 3. INSERT reminders (is_completed = false)
    → 4. If linked_task_id: INSERT chat_reminder_items
             (sync_direction = "reminder_to_chat")
    → Schedule Hangfire: ReminderDueJob(reminder_id, due_at)
    → Return Result<ReminderDto>
  → 201 Created
```

## Two-Way Sync: Task Completed → Reminder Done

```
TaskCompletedEvent (domain event from TaskStatusChangedEvent)
  → ReminderSyncHandler (INotificationHandler<TaskCompletedEvent>)
    → 1. SELECT reminder_id FROM chat_reminder_items
             WHERE linked entity = task_id (via reminder.linked_task_id)
    → 2. If found: UPDATE reminders.is_completed = true, completed_at = now()
    → (No command needed — domain event driven)
```

## Two-Way Sync: Reminder Done → Task Updated

```
PATCH /api/v1/me/reminders/{id}/complete
  → CompleteReminderHandler
    → 1. UPDATE reminders.is_completed = true, completed_at = now()
    → 2. If reminder.linked_task_id is not null:
         Send UpdateTaskStatusCommand (status = "done")
         (Uses same status validation as normal task status update)
    → Return Result<ReminderDto>
```

## Personal Board

```
POST /api/v1/me/boards
  body: { name }
  → CreatePersonalBoardHandler
    → 1. INSERT boards (project_id = null, user_id = caller)
    → 2. Seed default columns: "To Do", "In Progress", "Done"
         (status_key maps to tasks.status equivalents)
    → Return Result<BoardDto>
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Duplicate reminder for same task | 409 | Reminder already linked to this task |
| Complete already-completed reminder | 409 | Reminder already completed |
| Task update from reminder fails status check | 422 | Propagated from task validation |

## Related

- [[modules/work-management/my-space/overview|My Space Overview]]
- [[modules/work-management/tasks/end-to-end-logic|Task Logic]] — status change validation
- [[modules/work-management/my-space/testing|My Space Testing]]
