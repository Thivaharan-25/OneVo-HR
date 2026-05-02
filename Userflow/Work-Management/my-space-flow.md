# My Space

**Area:** WorkSync -> My Space  
**Trigger:** User opens personal work area  
**Required Permission(s):** Authenticated WorkSync user

---

## Purpose

My Space is the user's personal WorkSync area for assigned work, personal boards, reminders, and saved views. It is user-scoped, not workspace-wide.

## Flow Steps

### Step 1: Open My Space
- **UI:** WorkSync -> My Space
- **API:** `GET /api/v1/me/boards`, `GET /api/v1/me/reminders`, `GET /api/v1/me/saved-views`
- **UI:** Shows personal board columns, reminders, pinned saved views, and assigned work shortcuts

### Step 2: Create Personal Board
- **UI:** User clicks New Board
- **API:** `POST /api/v1/me/boards`
- **Backend:** Creates a board with `project_id = null` and `user_id = current user`

### Step 3: Create Reminder
- **UI:** User adds reminder title, due date, recurrence, and optional linked task/message
- **API:** `POST /api/v1/me/reminders`
- **Backend:** Ensures only one active reminder exists per linked task per user

### Step 4: Reminder Becomes Due
- **System:** Hangfire detects due reminder
- **Event:** `ReminderDueEvent`
- **UI:** User receives in-app notification

### Step 5: Complete Reminder
- **API:** `PATCH /api/v1/me/reminders/{id}/complete`
- **Backend:** Marks reminder completed and updates linked task when applicable

### Step 6: Save View
- **UI:** User configures filters on task/project/sprint list and saves the view
- **API:** `POST /api/v1/me/saved-views`
- **Result:** View appears in My Space and can be pinned

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate linked reminder | Create is blocked | "A reminder already exists for this task" |
| Linked task inaccessible | Link rejected | "You do not have access to this task" |
| Recurrence invalid | Validation fails | "Check the recurrence rule" |

## Events Triggered

- `ReminderDueEvent`
- `ReminderCompletedEvent`
- `TaskCompletedEvent` consumed to complete linked reminders

## Related Flows

- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/chat-ai-flow|Chat AI Flow]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/work-management/my-space/overview|My Space & Reminders]]
- [[modules/work-management/tasks/overview|Task Management]]
