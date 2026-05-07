# Chat & Messaging

**Module:** WorkSync
**Feature:** Chat & Messaging
**Namespace:** `WorkSync.Chat`
**Owner:** DEV7
**Tables:** 8

---

## Purpose

Real-time messaging within workspaces. Supports public channels, private channels, direct messages, and system-created case conversations. Messages are delivered via SignalR `IChannelHub` with polling fallback for the VS Code IDE sidebar.

When a workspace/channel is linked to Microsoft Teams, this module can mirror messages with Teams through the [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]. Teams sync is optional per tenant and per workspace/channel.

---

## Database Tables

### `channels`
Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `channel_type` (`public`, `private`, `direct`), `created_by_id`, `is_archived`.

Teams-linked channels use `channel_teams_links`; do not store Graph IDs directly on `channels`.

DM channels: `channel_type = direct` with exactly 2 members — enforced at application layer.

Case conversations use a private channel-like conversation linked to one workflow item, approval, alert, request, or case. They are not normal DMs because the assigned person can invite other employees and every decision action must be audited by the source workflow.

### `channel_members`
Key columns: `channel_id`, `user_id`, `role` (`owner`, `member`), `joined_at`, `last_read_at` (drives unread count), `notification_preference` (`all`, `mentions`, `none`).

### `messages`
Key columns: `channel_id`, `sender_id`, `content`, `content_type` (`text`, `markdown`, `system`), `parent_message_id` (FK → messages, nullable — thread reply), `is_edited`, `edited_at`, `is_deleted` (soft delete — content NOT wiped for compliance), `deleted_at`.

Teams-synced messages include external sync metadata in the schema: `external_source`, `external_message_id`, `sync_direction`, and `sync_status`.

### `message_reactions`
Key columns: `message_id`, `user_id`, `emoji`, `created_at`.

### `message_attachments`
Key columns: `message_id`, `file_asset_id` (FK → file_assets), `file_name`, `file_size_bytes`, `mime_type`.

### `message_pins`
Key columns: `channel_id`, `message_id`, `pinned_by_id`, `pinned_at`.

---

## Key Business Rules

1. DM channels: `channel_type = direct`, exactly 2 members — enforced at application layer (not DB constraint).
2. Messages are soft-deleted: `is_deleted = true`, content retained for compliance. Never wipe content.
3. `channel_members.last_read_at` is the source of truth for unread count: `SELECT COUNT(*) WHERE created_at > last_read_at AND is_deleted = false`.
4. Thread replies: `parent_message_id` self-FK; only 1 level of threading (replies cannot have replies).
5. SignalR: `IChannelHub` for real-time delivery; VS Code IDE sidebar polls `/api/v1/channels/{id}/messages` as fallback.
6. Message edit: updates `content`, sets `is_edited = true`, `edited_at = now()`. Edit history not stored (not Phase 1).
7. Microsoft Teams sync is optional. If a channel is not linked, messages remain ONEVO-only.
8. Teams inbound messages must be idempotent by external message id. Duplicate Graph webhook deliveries must not create duplicate ONEVO messages.
9. Teams outbound messages require the sender to have a linked Teams account and ONEVO `chat:write`.
10. Case conversations are private, system-created conversations for workflow items. Official actions such as approve, reject, acknowledge, dismiss, escalate, request information, and resolve are delegated to the workflow/case APIs and audited there.
11. Microsoft Teams mirrors case conversation discussion only. Teams messages must not change workflow state through buttons, bot commands, or text parsing.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `MessageSentEvent` | Message created | SignalR push, Chat AI detection (if premium) |
| `DirectMessageReceivedEvent` | DM received | Push notification to recipient |
| `ChannelMentionEvent` | `@username` in message | Push notification to mentioned user |
| `CaseConversationMessageSentEvent` | Message posted in case conversation | Workflow automation trigger, SignalR push |

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
| GET | `/api/v1/channels/{id}/teams-link` | `chat:read` | Get Teams link/sync state for channel |
| POST | `/api/v1/channels/{id}/teams-link` | `chat:manage` | Link channel to a Teams channel/chat |
| DELETE | `/api/v1/channels/{id}/teams-link` | `chat:manage` | Disconnect Teams sync for channel |

---

## Related

- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]] - Two-way Teams message sync
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine and Automation Center]] - Case conversations and action cards
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]] - Graph account linking, webhooks, and delta sync

- [[modules/work-management/chat-ai/overview|Chat AI]] — AI intent detection on messages
- [[modules/ide-extension/overview|IDE Extension]] — Chat sidebar panel
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 1]]
