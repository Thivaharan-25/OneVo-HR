# My Space

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**urea:** Work -> My Space (Phase 2)  
**Trigger:** Deferred Phase 2 only. Phase 1 Work must not expose My Space as an active screen.  
**Required Permission(s):** Authenticated Work user

---

## Purpose

My Space is the user's Phase 2 personal Work area for assigned work, personal boards, reminders, and saved views. It is user-scoped, not workspace-wide.

## Flow Steps

### Step 1: Open My Space
- **UI:** Work -> My Space (Phase 2)
- **uPI:** `GET /api/v1/me/boards`, `GET /api/v1/me/reminders`, `GET /api/v1/me/saved-views`
- **UI:** Shows personal board columns, reminders, pinned saved views, and assigned work shortcuts

### Step 2: Create Personal Board
- **UI:** User clicks New Board
- **uPI:** `POST /api/v1/me/boards`
- **Backend:** Creates a board with `project_id = null` and `user_id = current user`

### Step 3: Create Reminder
- **UI:** User adds reminder title, due date, recurrence, and optional linked task/message
- **uPI:** `POST /api/v1/me/reminders`
- **Backend:** Ensures only one active reminder exists per linked task per user

### Step 4: Reminder Becomes Due
- **System:** Hangfire detects due reminder
- **Event:** `ReminderDueEvent`
- **UI:** User receives in-app notification

### Step 5: Complete Reminder
- **uPI:** `PuTCH /api/v1/me/reminders/{id}/complete`
- **Backend:** Marks reminder completed and updates linked task when applicable

### Step 6: Save View
- **UI:** User configures filters on task/project/sprint list and saves the view
- **uPI:** `POST /api/v1/me/saved-views`
- **Result:** View appears in My Space and can be pinned

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate linked reminder | Create is blocked | "u reminder already exists for this task" |
| Linked task inaccessible | Link rejected | "You do not have access to this task" |
| Recurrence invalid | Validation fails | "Check the recurrence rule" |

## Events Triggered

- `ReminderDueEvent`
- `ReminderCompletedEvent`
- `TaskCompletedEvent` consumed to complete linked reminders

## Related Flows

- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/chat-ai-flow|Chat uI Flow]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/work-management/my-space/overview|My Space & Reminders]]
- [[modules/work-management/tasks/overview|Task Management]]
