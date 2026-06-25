
**Module:** WorkSync

---

## Purpose

Defines how WorkSync Chat mirrors user messages, assistant messages, and case-conversation discussion with Microsoft Teams after a workspace/channel or workflow case conversation has been linked to a Teams Team/channel or Teams chat.


For Agentic Chat, Microsoft Teams is an input/output channel. Inbound Teams messages are normalized into ONEVO messages first, then the Semantic Kernel assistant may process them only after the Teams sender maps to a ONEVO user and ONEVO permissions are resolved.

---


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
         e. Send Graph message
         f. Store external_message_id in teams_message_sync_state
         g. Update messages.sync_status = "synced"
    -> 5. SignalR pushes ONEVO message with sync badge
```


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
         f. If sender is mapped and assistant is enabled, invoke Semantic Kernel assistant
```


```text
Workflow delivery router creates or updates case conversation
       2. Send summary message with request/alert details
       3. Include secure ONEVO link for approve/reject/resolve actions
       5. Keep workflow state changes in ONEVO only
```


```text
Time Off request from Nimal Perera
Dates: May 10-12
Status: Waiting for approval

Reply here to discuss.
Open ONEVO to approve or reject:
[Open Request]
```

## Edit Sync

```
ONEVO edit:
  -> Update local message
  -> If external_source is null and channel linked:
       Update sync_status

  -> Graph delta detects modified message
  -> Update ONEVO message content
  -> Set is_edited = true, edited_at = Graph modifiedDateTime
```

## Delete Sync

```
ONEVO delete:
  -> Soft delete local message

  -> Graph delta/webhook detects delete
  -> Soft delete local message
  -> Preserve last known content for compliance/legal hold
```

## Attachments

```
ONEVO attachment outbound:
  -> Upload/share through Graph

  -> Import metadata and permitted file copy/link
  -> Create message_attachments row
  -> Do not import blocked file types
```

## Idempotency


```
UNIQUE(tenant_id, external_source, external_message_id)
```


## Error Scenarios

| Scenario | Handling |
|:---------|:---------|
| Graph send fails | Mark sync_status = `failed`, queue retry |
| Inbound sender not mapped | Import as external participant or skip per tenant policy |
| Attachment too large | Import message, mark attachment sync failed |
| Message already imported | No-op idempotent success |

---

## Related

- [[modules/work-management/chat/overview|Chat Overview]]
- [[modules/work-management/chat/end-to-end-logic|Chat Logic]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
