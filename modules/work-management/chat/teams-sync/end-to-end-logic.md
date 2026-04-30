# Teams Chat Sync - End-to-End Logic

**Module:** WorkSync
**Feature:** Teams Chat Sync

---

## Purpose

Defines how WorkSync Chat mirrors messages with Microsoft Teams after a workspace/channel has been linked to a Teams Team/channel or Teams chat.

---

## Send ONEVO Message To Teams

```
POST /api/v1/channels/{id}/messages
  body: { content, content_type, parent_message_id?, sync_to_teams = true }
  -> SendMessageHandler
    -> 1. Verify caller is ONEVO channel member
    -> 2. Save messages row with sync_direction = "outbound"
    -> 3. Publish MessageSentEvent
    -> 4. TeamsOutboundMessageSyncHandler:
         a. Load channel_teams_links for channel_id
         b. Verify link status = active
         c. Verify sender has linked Teams account
         d. Transform markdown to Teams-supported format
         e. Send Graph message
         f. Store external_message_id in teams_message_sync_state
         g. Update messages.sync_status = "synced"
    -> 5. SignalR pushes ONEVO message with sync badge
```

## Pull Teams Message Into ONEVO

```
Graph change notification
  -> TeamsMessageWebhookHandler
    -> 1. Validate notification
    -> 2. Resolve Team/channel/chat to ONEVO channel using channel_teams_links
    -> 3. Fetch new/changed messages via Graph delta
    -> 4. For each message:
         a. Skip if teams_message_sync_state already has external_message_id
         b. Map sender by teams_user_id/email
         c. INSERT messages:
              external_source = "microsoft_teams"
              external_message_id = Graph message id
              sync_direction = "inbound"
              sync_status = "synced"
         d. Store attachments via file pipeline if allowed
         e. Push SignalR `message:created`
```

## Edit Sync

```
ONEVO edit:
  -> Update local message
  -> If external_source is null and channel linked:
       PATCH Teams message via Graph
       Update sync_status

Teams edit:
  -> Graph delta detects modified message
  -> Update ONEVO message content
  -> Set is_edited = true, edited_at = Graph modifiedDateTime
```

## Delete Sync

```
ONEVO delete:
  -> Soft delete local message
  -> If outbound-synced and policy allows Teams delete:
       DELETE/PATCH Teams message through Graph if supported

Teams delete:
  -> Graph delta/webhook detects delete
  -> Soft delete local message
  -> Preserve last known content for compliance/legal hold
```

## Attachments

```
ONEVO attachment outbound:
  -> Verify file access and Teams file policy
  -> Upload/share through Graph
  -> Create Teams message with attachment reference

Teams attachment inbound:
  -> Import metadata and permitted file copy/link
  -> Create message_attachments row
  -> Do not import blocked file types
```

## Idempotency

Every synced Teams message must have exactly one ONEVO message:

```
UNIQUE(tenant_id, external_source, external_message_id)
```

Outbound sync must also record the local `message_id` before retrying so a Graph timeout does not create duplicate Teams messages without detection.

## Error Scenarios

| Scenario | Handling |
|:---------|:---------|
| Channel not linked to Teams | Save ONEVO message only |
| Sender has no Teams account | Save ONEVO message and mark sync_status = `not_linked` |
| Graph send fails | Mark sync_status = `failed`, queue retry |
| Inbound sender not mapped | Import as external participant or skip per tenant policy |
| Attachment too large | Import message, mark attachment sync failed |
| Message already imported | No-op idempotent success |

---

## Related

- [[modules/work-management/chat/overview|Chat Overview]]
- [[modules/work-management/chat/end-to-end-logic|Chat Logic]]
- [[modules/work-management/chat/teams-sync/testing|Teams Chat Sync Testing]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
