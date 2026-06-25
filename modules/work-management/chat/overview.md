# Chat & Messaging

**Phase:** Phase 2. Not part of Phase 1 implementation scope.

**Module:** WorkSync
**Feature:** Chat & Messaging
**Namespace:** `WorkSync.Chat`
**Owner:** DEV7
**Tables:** 8

---

## Purpose

Phase 2 real-time messaging within workspaces. Supports public channels, private channels, direct messages, system-created case conversations, assistant messages, and Microsoft Teams-linked channels. Messages are delivered via the WorkSync chat SignalR hub with polling fallback for the VS Code IDE sidebar.

When a workspace/channel is linked to Microsoft Teams, this module can mirror messages with Teams through the [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]. Teams sync is optional per tenant and per workspace/channel.

The ONEVO Semantic Kernel assistant runs on normalized chat messages after they are saved. Assistant answers are stored as `messages.sender_type = assistant`; reversible assistant actions use `ai_action_jobs`.

---

## Database Tables

### `channels`
Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `channel_type` (`public`, `private`, `direct`), `created_by_id`, `is_archived`.

Teams-linked channels use `channel_teams_links`; do not store Graph IDs directly on `channels`.

DM channels: `channel_type = direct` with exactly 2 members - enforced at application layer.

Case conversations use a private channel-like conversation linked to one workflow item, approval, alert, request, or case. They are not normal DMs because the assigned person can invite other employees and every decision action must be audited by the source workflow.

### `channel_members`
Key columns: `channel_id`, `user_id`, `role` (`owner`, `member`), `joined_at`, `last_read_at` (drives unread count), `notification_preference` (`all`, `mentions`, `none`).

### `messages`
Key columns: `channel_id`, `user_id` nullable, `sender_type` (`user`, `assistant`, `system`, `external`), `content`, `content_type` (`text`, `markdown`, `system`, `ai_answer`, `ai_action_card`), `metadata_json`, `parent_message_id`, `is_edited`, `edited_at`, `is_deleted` (soft delete; content NOT wiped for compliance), `deleted_at`.


### `message_reactions`
Key columns: `message_id`, `user_id`, `emoji`, `created_at`.

### `message_attachments`
Key columns: `message_id`, `file_asset_id` (FK -> file_assets), `file_name`, `file_size_bytes`, `mime_type`.

### `message_pins`
Key columns: `channel_id`, `message_id`, `pinned_by_id`, `pinned_at`.

---

## Key Business Rules

1. DM channels: `channel_type = direct`, exactly 2 members - enforced at application layer (not DB constraint).
2. Messages are soft-deleted: `is_deleted = true`, content retained for compliance. Never wipe content.
3. `channel_members.last_read_at` is the source of truth for unread count: `SELECT COUNT(*) WHERE created_at > last_read_at AND is_deleted = false`.
4. Thread replies: `parent_message_id` self-FK; only 1 level of threading (replies cannot have replies).
5. SignalR: the WorkSync chat hub publishes the canonical `chat:message`, `chat:typing`, `ai:*`, and `chat:sync_status` events; VS Code IDE sidebar consumes the same payload shape and can poll `/api/v1/channels/{id}/messages` as fallback.
6. Message edit: updates `content`, sets `is_edited = true`, `edited_at = now()`. Edit history not stored (not Phase 1).
7. Microsoft Teams sync is optional. If a channel is not linked, messages remain ONEVO-only.
10. Case conversations are private, system-created conversations for workflow items. Official actions such as approve, reject, acknowledge, dismiss, escalate, request information, and resolve are delegated to the workflow/case APIs and audited there.
11. Microsoft Teams mirrors case conversation discussion only. Teams messages must not change workflow state through buttons, bot commands, or text parsing.
13. Microsoft Teams-originated messages can trigger the assistant only after the Teams sender is mapped to a ONEVO user and normal ONEVO permissions are resolved.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `MessageSentEvent` | Message created | SignalR push, Chat AI detection (if premium) |
| `DirectMessageReceivedEvent` | DM received | Push notification to recipient |
| `ChannelMentionEvent` | `@username` in message | Push notification to mentioned user |
| `CaseConversationMessageSentEvent` | Message posted in case conversation | Phase 2 workflow automation trigger and SignalR push |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/channels` | `chat:read` | List channels user can see |
| POST | `/api/v1/workspaces/{wsId}/channels` | `chat:write` | Create channel |
| GET | `/api/v1/channels/{id}/messages` | `chat:read` | List messages (paginated) |
| POST | `/api/v1/channels/{id}/messages` | `chat:write` | Send message |
| PATCH | `/api/v1/channels/{id}/messages/{msgId}` | `chat:write` | Edit message |
| DELETE | `/api/v1/channels/{id}/messages/{msgId}` | `chat:write` | Soft-delete message |
| POST | `/api/v1/channels/{id}/messages/{msgId}/reactions` | `chat:write` | Add reaction |
| POST | `/api/v1/channels/{id}/messages/{msgId}/pin` | `chat:manage` | Pin message |
| POST | `/api/v1/workspaces/{wsId}/dms` | `chat:write` | Create/get DM channel |

---

## Related

- [[modules/shared-platform/workflow-engine/overview|Workflow Engine and Automation Center (Phase 2)]] - Case conversations and action cards
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]] - Graph account linking, webhooks, and delta sync

- [[modules/work-management/chat-ai/overview|Chat AI]] - AI intent detection on messages
- [[modules/ide-extension/overview|IDE Extension]] - Chat sidebar panel
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 1]]
