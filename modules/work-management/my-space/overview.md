# My Space & Reminders

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**Module:** WorkSync
**Feature:** My Space & Reminders
**Namespace:** `WorkSync.MySpace`
**Owner:** DEV7
**Tables:** 4

---

## Purpose

My Space is a Phase 2 personal area for each user within Work. It provides personal boards (not linked to a project), a to-do/reminder system, and saved views. All personal boards, reminder automation, and saved views in this module are Phase 2 unless explicitly reactivated later.

---

## Database Tables

### `boards` (personal variant)
Personal boards share the `boards` table with project boards. Key differentiator: `boards.project_id = null` AND `boards.user_id = {userId}`.

All standard board columns apply (`board_columns`, `board_task_positions`) - personal boards follow the same drag-and-drop mechanics.

### `reminders`
Key columns: `user_id`, `tenant_id`, `title`, `description`, `due_at`, `is_completed`, `completed_at`, `linked_task_id` (FK -> tasks, nullable), `linked_chat_message_id` (FK -> messages, nullable), `recurrence_rule` (nullable - RFC 5545 RRULE).

Reminders are **user-scoped, not workspace-scoped**.

### `saved_views`
User's personal saved filter combinations. Key columns: `user_id`, `workspace_id`, `name`, `entity_type` (`tasks`, `sprints`, `projects`), `filter_json`, `sort_json`, `is_pinned`.

Workspace-scoped saved views can optionally be shared via `saved_view_shares` (Analytics module).

---

## Key Business Rules

1. Personal boards: `project_id = null`, `user_id` set - never workspace-scoped directly.
2. Only one active reminder per linked task per user - duplicate check at application layer.
3. Task-linked reminder sync uses `reminders.linked_task_id`; status change in either direction propagates to the other.
4. Reminders are personal - no tenant-wide or workspace-wide visibility.
5. Active timer (time_logs): only one timer per user with `ended_at = null` - enforced at application layer.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ReminderDueEvent` | Hangfire: due_at reached | Push notification to user |
| `TaskCompletedEvent` | tasks.status -> done | Marks linked reminder complete |
| `ReminderCompletedEvent` | reminder marked done | Updates linked task status |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/me/boards` | authenticated | List personal boards |
| POST | `/api/v1/me/boards` | authenticated | Create personal board |
| GET | `/api/v1/me/reminders` | authenticated | List reminders |
| POST | `/api/v1/me/reminders` | authenticated | Create reminder |
| PATCH | `/api/v1/me/reminders/{id}/complete` | authenticated | Mark reminder done |
| GET | `/api/v1/me/saved-views` | authenticated | List saved views |
| POST | `/api/v1/me/saved-views` | authenticated | Save a view |

---

## Related

- [[Userflow/Work-Management/my-space-flow|My Space]] - personal work area user flow

- [[modules/work-management/planning/overview|Planning]] - board mechanics shared
- [[modules/work-management/analytics/overview|Analytics]] - saved_view_shares
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 3]]
