# Chat AI

**Module:** WorkSync
**Feature:** Chat AI / ONEVO Semantic Kernel Assistant
**Namespace:** `WorkSync.ChatAI`
**Owner:** DEV3 backend, DEV7/DEV8 clients
**Tables:** 3 core tables plus assistant audit storage if required

---

## Purpose

Chat AI is ONEVO's first-party Semantic Kernel assistant for Chat, IDE, and Microsoft Teams-linked channels. It can answer permission-scoped HR/WorkSync questions and create undoable actions such as tasks, reminders, task status updates, and calendar events.

It activates only when the tenant has the Agentic Chat / `premium_ai` entitlement. It must use the same tenant context, permissions, module entitlements, and audit rules as normal ONEVO APIs.

The `ai_action_jobs` table is the universal undo state machine shared by Chat AI and the IDE Tag Engine.

---

## Database Tables

### `premium_ai_detections`

Records each detected assistant intent from a message. Key columns:

- `message_id`, `channel_id`, `workspace_id`, `tenant_id`
- `detected_intent` such as `create_task`, `set_reminder`, `schedule_meeting`, `answer_hr_question`
- `confidence_score`
- `source` such as `semantic_kernel`, `heuristic`, `manual`
- `raw_message_excerpt`, `processed_at`
- `ai_action_job_id` nullable FK to `ai_action_jobs`

### `ai_action_jobs`

Universal undo state machine. Used by Phase 1 Chat AI with a 10 second undo window and Phase 2 IDE tags with a 30 second undo window. Key columns:

- `status` - `pending`, `finalized`, `undone`, `failed`
- `source` - Phase 1: `onevo_chat`, `microsoft_teams`, `system`; Phase 2 adds `ide_tag`
- `source_message_id`, `channel_id`
- `entity_type`, `action_type`
- `action_params` JSONB used by finalization
- `undo_expires_at`
- `undone_at`, `finalized_at`
- `tag_execution_id` nullable Phase 2 FK to IDE tag execution
- `workspace_id`, `tenant_id`, `created_by_id`

Hangfire scans `status = 'pending' AND undo_expires_at < now()` every 5 seconds.

### `chat_reminder_items`

Two-way sync bridge between chat reminders and task/reminder state. Key columns: `reminder_id`, `message_id`, `user_id`, `sync_direction`.

---

## Key Business Rules

1. Chat AI only activates when the tenant has Agentic Chat / `premium_ai`.
2. Semantic Kernel functions are registered only after filtering by tenant modules and effective user permissions.
3. The assistant may answer read-only questions directly, but product actions must execute through ONEVO application services or CQRS handlers.
4. Reversible actions from chat create `ai_action_jobs` first; the entity is created only after the undo window expires.
5. During the undo window, `ai:action_pending` fires and the user sees an inline action card or toast.
6. Undo sets `status = undone`, sets `undone_at`, and creates no downstream entity.
7. Hangfire finalization creates the entity from `action_params`, then sets `status = finalized`.
8. Teams-originated messages use the same pipeline only after the Teams sender maps to a ONEVO user. Unmapped Teams senders cannot execute assistant tools.
9. Assistant answers are saved as chat messages with `sender_type = assistant`.
10. Hangfire job processing is idempotent: re-check `status = pending` inside a lock before acting.

---

## Domain Events

| Event | Published When | Consumers |
|---|---|---|
| `AiIntentDetectedEvent` | Semantic Kernel detects a tool/action intent | Creates detection/action state |
| `AiActionFinalizedEvent` | Hangfire finalizes an action | Creates entity, sends `ai:action_finalized` |
| `AiActionUndoneEvent` | User clicks Undo | Marks job undone, sends `ai:action_finalized` with `undone=true` |
| `AssistantMessageCreatedEvent` | Assistant answers or asks clarification | Saves assistant message and sends `chat:message` |

---

## API Endpoints

| Method | Route | Permission | Description |
|---|---|---|
| GET | `/api/v1/workspaces/{wsId}/ai-actions` | `chat:read` | List pending AI actions |
| DELETE | `/api/v1/ai-actions/{id}/undo` | `chat:write` | Undo pending action |
| POST | `/api/v1/channels/{id}/assistant/runs` | `chat:write` | Explicitly invoke assistant for a message/channel |

---

## User Outcome

| Result | User sees |
|---|---|
| Read-only answer | Assistant message in the chat thread with concise answer. |
| Low confidence | Clarifying assistant question. |
| Permission denied | Plain no-permission message. |
| Pending action | AI action card with countdown and Undo. |
| Finalized action | Created entity card/link in chat. |
| Failed action | Failure card with retry only when safe. |

---

## Related

- [[modules/shared-platform/chatbot-api-integration|Semantic Kernel Assistant Integration]]
- [[Userflow/Work-Management/chat-ai-flow|Chat AI Flow]]
- [[modules/work-management/chat/overview|Chat]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
- [[modules/work-management/my-space/overview|My Space]]
- [[modules/ide-extension/overview|IDE Extension]]
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[current-focus/contracts/signalr-events|SignalR Events]]
