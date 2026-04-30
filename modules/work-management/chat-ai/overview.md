# Chat AI

**Module:** WorkSync
**Feature:** Chat AI
**Namespace:** `WorkSync.ChatAI`
**Owner:** DEV7
**Tables:** 3

---

## Purpose

AI-assisted chat that detects user intent from messages and automatically creates ONEVO entities (tasks, reminders, etc.) with a 10-second undo window. Activated only for tenants with the `premium_ai` feature flag. The `ai_action_jobs` table is the **universal undo state machine** — shared with the IDE Tag Engine (which uses a 30s window).

---

## Database Tables

### `premium_ai_detections`
Records each AI intent detection from a message. Key columns: `message_id`, `channel_id`, `workspace_id`, `tenant_id`, `detected_intent` (`create_task`, `set_reminder`, `schedule_meeting`, etc.), `confidence_score`, `raw_message_excerpt`, `processed_at`, `ai_action_job_id` (FK → ai_action_jobs, nullable).

### `ai_action_jobs`
Universal undo state machine. Used by Chat AI (10s window) AND IDE Tag Engine (30s window). Key columns:
- `status` — `pending`, `finalized`, `undone`, `failed`
- `entity_type`, `action_type` — what to create/do
- `action_params` — JSONB: params for entity creation
- `undo_expires_at` — Chat AI: `now() + 10s`; IDE tags: `now() + 30s`
- `undone_at` — set when user clicks Undo
- `finalized_at` — set by Hangfire when window expires
- `tag_execution_id` (FK → ide_tag_executions, nullable) — null for Chat AI actions
- `workspace_id`, `tenant_id`, `created_by_id`

Hangfire scans: `WHERE status = 'pending' AND undo_expires_at < now()` every 5 seconds.

### `chat_reminder_items`
Two-way sync bridge. Key columns: `reminder_id` (FK → reminders), `message_id` (FK → messages), `user_id`, `sync_direction` (`chat_to_reminder`, `reminder_to_chat`).

---

## Key Business Rules

1. Chat AI only activates when tenant has `premium_ai` feature flag — check before processing any message.
2. AI detection flow: message received → AI detects intent → `premium_ai_detections` row → `ai_action_jobs` row (status = pending, undo_expires_at = now() + 10s).
3. During undo window: `ai:action_pending` SignalR event fires; user sees countdown toast.
4. Undo: set `ai_action_jobs.status = undone`, `undone_at = now()`. No entity created.
5. Window expires: Hangfire finalizes — creates the entity from `action_params`, sets `status = finalized`.
6. `ai_action_jobs.tag_execution_id` is **null** for Chat AI (only set for IDE tag actions).
7. Hangfire job processing is idempotent: check `status = pending` before acting; skip if already finalized/undone.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AiIntentDetectedEvent` | AI detects intent | Creates ai_action_jobs row |
| `AiActionFinalizedEvent` | Hangfire finalizes | Creates entity, notifies user via SignalR `ai:action_finalized` |
| `AiActionUndoneEvent` | User clicks Undo | Marks job undone, fires `ai:action_finalized` (undone=true) |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/ai-actions` | `chat:read` | List pending AI actions |
| DELETE | `/api/v1/ai-actions/{id}/undo` | `chat:write` | Undo pending action |

---

## Undo State Machine

```
pending ──(Hangfire: undo_expires_at < now())──► finalized
pending ──(user clicks Undo)──────────────────► undone
pending/finalized ──(Hangfire error)──────────► failed
```

---

## Related

- [[modules/work-management/chat/overview|Chat]] — messages feed AI detection
- [[modules/work-management/my-space/overview|My Space]] — chat_reminder_items
- [[modules/ide-extension/overview|IDE Extension]] — shares ai_action_jobs (30s window)
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 2]]
