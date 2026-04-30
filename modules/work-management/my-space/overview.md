# My Space & Reminders

**Module:** WorkSync
**Feature:** My Space & Reminders
**Namespace:** `WorkSync.MySpace`
**Owner:** DEV7
**Tables:** 4

---

## Purpose

My Space is the personal area for each user within WorkSync. It provides personal boards (not linked to a project), a to-do/reminder system, and saved views. Reminders have two-way sync with tasks via `chat_reminder_items`.

---

## Database Tables

### `boards` (personal variant)
Personal boards share the `boards` table with project boards. Key differentiator: `boards.project_id = null` AND `boards.user_id = {userId}`.

All standard board columns apply (`board_columns`, `board_task_positions`) — personal boards follow the same drag-and-drop mechanics.

### `reminders`
Key columns: `user_id`, `tenant_id`, `title`, `description`, `due_at`, `is_completed`, `completed_at`, `linked_task_id` (FK → tasks, nullable), `linked_chat_message_id` (FK → messages, nullable), `recurrence_rule` (nullable — RFC 5545 RRULE).

Reminders are **user-scoped, not workspace-scoped**.

### `chat_reminder_items`
Two-way sync bridge between chat messages and reminders. Key columns: `reminder_id`, `message_id`, `user_id`, `sync_direction` (`chat_to_reminder`, `reminder_to_chat`).

When `tasks.status → done`: linked reminder → `is_completed = true` (via domain event).
When reminder → `is_completed = true`: linked task status updates (via command).

### `saved_views`
User's personal saved filter combinations. Key columns: `user_id`, `workspace_id`, `name`, `entity_type` (`tasks`, `sprints`, `projects`), `filter_json`, `sort_json`, `is_pinned`.

Workspace-scoped saved views can optionally be shared via `saved_view_shares` (Analytics module).

---

## Key Business Rules

1. Personal boards: `project_id = null`, `user_id` set — never workspace-scoped directly.
2. Only one active reminder per linked task per user — duplicate check at application layer.
3. `chat_reminder_items` two-way sync: status change in either direction propagates to the other.
4. Reminders are personal — no tenant-wide or workspace-wide visibility.
5. Active timer (time_logs): only one timer per user with `ended_at = null` — enforced at application layer.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ReminderDueEvent` | Hangfire: due_at reached | Push notification to user |
| `TaskCompletedEvent` | tasks.status → done | Marks linked reminder complete |
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

- [[modules/work-management/chat-ai/overview|Chat AI]] — chat_reminder_items source
- [[modules/work-management/planning/overview|Planning]] — board mechanics shared
- [[modules/work-management/analytics/overview|Analytics]] — saved_view_shares
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 3]]
