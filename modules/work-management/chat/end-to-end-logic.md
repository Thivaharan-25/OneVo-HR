# Chat & Messaging — End-to-End Logic

**Module:** WorkSync
**Feature:** Chat & Messaging

---

## Send Message

```
POST /api/v1/channels/{id}/messages
  body: { content, content_type, parent_message_id?, sync_to_teams? }
  → [RequirePermission("chat:write")]
  → SendMessageHandler
    → 1. Verify user is channel_member
    → 2. Validate: content not empty, content_type in enum
    → 3. If parent_message_id: verify parent is in same channel,
         verify parent has no parent (one level of threading only)
    → 4. INSERT messages row
    → 5. Publish MessageSentEvent:
         → SignalR IChannelHub pushes to all channel members
         → ChatAI detection (if premium_ai flag — see Chat AI module)
         → Notifications for @mentions
    → Return Result<MessageDto>
  → 201 Created
```

## Create Direct Message Channel

## Microsoft Teams Sync

When a channel has an active `channel_teams_links` row, message sync is delegated to [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]. The base chat send flow still saves the ONEVO message first; Teams delivery runs after `MessageSentEvent` so Teams outages do not block ONEVO chat.

```
MessageSentEvent
  -> TeamsOutboundMessageSyncHandler
    -> 1. Check channel Teams link
    -> 2. Check sender has linked Teams account
    -> 3. Send message through Microsoft Graph
    -> 4. Store teams_message_sync_state
    -> 5. Update message sync_status

Teams Graph webhook/delta notification
  -> TeamsMessageWebhookHandler
    -> 1. Resolve Teams channel/chat to ONEVO channel
    -> 2. Deduplicate by external_message_id
    -> 3. Insert inbound ONEVO message
    -> 4. Push SignalR update
```

```
POST /api/v1/workspaces/{wsId}/dms
  body: { other_user_id }
  → CreateDMHandler
    → 1. Verify both users are workspace members
    → 2. Check existing DM channel:
         SELECT c.id FROM channels c
         JOIN channel_members cm1 ON cm1.channel_id = c.id AND cm1.user_id = caller
         JOIN channel_members cm2 ON cm2.channel_id = c.id AND cm2.user_id = other_user
         WHERE c.channel_type = 'direct'
         If found: return existing channel (idempotent)
    → 3. BEGIN TRANSACTION
         a. INSERT channels (channel_type = "direct")
         b. INSERT channel_members for caller (role = "owner")
         c. INSERT channel_members for other_user (role = "member")
    → 4. COMMIT
    → Return Result<ChannelDto>
```

## Unread Count

```
GET /api/v1/channels/{id}/messages
  → Returns messages + caller's unread count:
    unread_count = SELECT COUNT(*) FROM messages
      WHERE channel_id = ?
        AND created_at > (SELECT last_read_at FROM channel_members
                          WHERE channel_id = ? AND user_id = ?)
        AND is_deleted = false

PATCH /api/v1/channels/{id}/read
  → UPDATE channel_members SET last_read_at = now()
    WHERE channel_id = ? AND user_id = ?
```

## Soft Delete Message

```
DELETE /api/v1/channels/{id}/messages/{msgId}
  → SoftDeleteMessageHandler
    → 1. Verify caller is sender OR channel owner/workspace admin
    → 2. UPDATE messages:
             is_deleted = true
             deleted_at = now()
         DO NOT clear content (compliance — content retained)
    → 3. SignalR: push deletion event to channel
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Send to channel not a member of | 403 | Not a channel member |
| Thread reply to a thread reply | 422 | Cannot nest thread replies |
| DM to non-workspace member | 422 | User is not in this workspace |
| Edit another user's message | 403 | Cannot edit other users' messages |
| Teams channel linked but sender has no Teams account | 202 | Message saved locally; sync_status = not_linked |
| Duplicate Teams inbound message | 200 | Ignored by idempotency |

### Edge Cases

- Message content after soft-delete: API returns `[Message deleted]` placeholder in content field for rendering, but DB retains original content.
- IDE sidebar polling: `GET /api/v1/channels/{id}/messages?after={last_message_id}` used as SignalR fallback for VS Code extension.
- Teams sync failures do not block ONEVO chat. The message stays visible with `sync_status = failed` and can be retried.

## Related

- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync Logic]]
- [[modules/work-management/chat/overview|Chat Overview]]
- [[modules/work-management/chat-ai/overview|Chat AI]] — AI detection on messages
- [[modules/work-management/chat/testing|Chat Testing]]
