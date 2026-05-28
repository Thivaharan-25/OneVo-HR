# Chat AI - End-to-End Logic

**Module:** WorkSync
**Feature:** ONEVO Semantic Kernel Assistant / Chat AI

---

## Assistant Detection And Tool Flow

```text
Message received
  -> POST /api/v1/channels/{id}/messages
     or TeamsMessageImportedEvent
     or IDE chat message
  -> Message saved by Chat module
  -> MessageSentEvent published
  -> SemanticKernelChatOrchestrator
      -> 1. Load trusted context:
             tenant_id, user_id, employee_id, workspace_id, channel_id,
             source, timezone, enabled modules, effective permissions
      -> 2. Check tenant has Agentic Chat / premium_ai
             If not: skip assistant processing
      -> 3. Register only allowed Kernel Functions
             Example: no tasks:write -> do not register WorkSync.CreateTask
      -> 4. Invoke Semantic Kernel with message + minimal context
      -> 5. Kernel returns one of:
             a. read-only answer
             b. clarification question
             c. tool call
             d. low-confidence/no action
      -> 6. For read-only answer:
             INSERT assistant message with sender_type = assistant
             Fire chat:message
      -> 7. For reversible tool call:
             INSERT premium_ai_detections
             INSERT ai_action_jobs:
               status = pending
               source = onevo_chat | microsoft_teams | ide_tag
               source_message_id = message id
               channel_id = channel id
               action_type = detected action
               action_params = normalized JSON
               undo_expires_at = now() + 10s
               tag_execution_id = null for chat-originated actions
             Fire ai:action_pending
      -> 8. For non-reversible or high-risk action:
             Ask for explicit confirmation instead of executing
```

## Example Kernel Input

```json
{
  "tenant_id": "tenant-uuid",
  "user_id": "user-uuid",
  "employee_id": "employee-uuid",
  "source": "onevo_chat",
  "channel_id": "channel-uuid",
  "workspace_id": "workspace-uuid",
  "message": {
    "id": "msg-uuid",
    "content": "Create a task to review payroll before Friday"
  },
  "permissions": ["chat:write", "tasks:write"],
  "active_modules": ["work_management", "core_hr"],
  "active_features": ["work_management.tasks", "chat_ai.agentic_chat", "core_hr.employee_profiles"],
  "timezone": "Asia/Colombo"
}
```

## Example Semantic Kernel Tool Call

```json
{
  "tool": "WorkSync.CreateTask",
  "arguments": {
    "workspace_id": "workspace-uuid",
    "title": "Review payroll",
    "due_date": "2026-05-22",
    "source_message_id": "msg-uuid"
  }
}
```

## Pending Action Payload

```json
{
  "id": "job-uuid",
  "detection_id": "detection-uuid",
  "user_id": "user-uuid",
  "tenant_id": "tenant-uuid",
  "channel_id": "channel-uuid",
  "source_message_id": "msg-uuid",
  "source": "onevo_chat",
  "action_type": "auto_create_task",
  "action_params": {
    "workspace_id": "workspace-uuid",
    "title": "Review payroll",
    "due_date": "2026-05-22",
    "source_message_id": "msg-uuid"
  },
  "status": "pending",
  "undo_expires_at": "2026-05-20T10:30:10Z"
}
```

## SignalR Pending Event

```json
{
  "job_id": "job-uuid",
  "channel_id": "channel-uuid",
  "source_message_id": "msg-uuid",
  "action_type": "auto_create_task",
  "action_description": "Create task: Review payroll",
  "undo_expires_at": "2026-05-20T10:30:10Z",
  "created_entity_type": "task"
}
```

## Undo Window - User Cancels

```text
DELETE /api/v1/ai-actions/{jobId}/undo
  -> [Authenticated - must be job creator or allowed channel actor]
  -> UndoAiActionHandler
    -> 1. Load ai_action_jobs
    -> 2. Verify status = pending
    -> 3. Verify undo_expires_at > now()
         If expired: return 409 UNDO_WINDOW_EXPIRED
    -> 4. UPDATE ai_action_jobs:
           status = undone
           undone_at = now()
    -> 5. If tag_execution_id is not null:
           UPDATE ide_tag_executions.status = undone
    -> 6. Fire SignalR ai:action_finalized:
           { job_id, status: "undone", undone: true }
    -> Return 200
```

## Hangfire Finalization

```text
FinalizeAiActionsJob (every 5s)
  -> SELECT ai_action_jobs
     WHERE status = 'pending' AND undo_expires_at < now()
  -> For each row:
     -> 1. Acquire distributed lock on job_id
     -> 2. Re-check status = pending
     -> 3. Execute action through application command:
            auto_create_task -> CreateTaskCommand
            auto_create_reminder -> CreateReminderCommand
            auto_update_status -> UpdateTaskStatusCommand
            auto_create_calendar_event -> CreateCalendarEventCommand
     -> 4. UPDATE ai_action_jobs:
            status = finalized
            finalized_at = now()
            created_entity_type = "task"
            created_entity_id = new entity id
     -> 5. Fire SignalR ai:action_finalized
     -> 6. Insert assistant message/card if needed
  -> On exception:
     -> UPDATE ai_action_jobs.status = failed
     -> Log error with job_id
     -> Fire ai:action_finalized with status = failed
```

## Microsoft Teams-Originated Messages

```text
Graph webhook/delta notification
  -> TeamsMessageWebhookHandler
  -> Resolve channel_teams_links
  -> Map Teams sender to ONEVO user
  -> INSERT messages with:
       external_source = microsoft_teams
       external_message_id = Graph message id
       sender_type = user when mapped, external when tenant policy allows unmapped import
  -> Publish TeamsMessageImportedEvent / MessageSentEvent
  -> SemanticKernelChatOrchestrator handles it exactly like ONEVO chat
```

Rules:

- Unmapped Teams senders cannot execute assistant tools.
- Teams-originated high-risk actions should ask for confirmation in ONEVO unless tenant policy explicitly allows Teams-originated auto-actions.
- Assistant replies may sync back to Teams only when `channel_teams_links.sync_direction` allows outbound sync.

## Error Scenarios

| Scenario | HTTP / State | Handling |
|---|---|---|
| Tenant has no Agentic Chat entitlement | none | Assistant skipped; normal chat only |
| User lacks permission for selected tool | assistant answer | "You do not have permission..." |
| Low confidence | assistant answer | Ask clarification; no action job |
| Undo after window expired | 409 | "This action has already been applied" |
| Undo non-existent job | 404 | "Action not found" |
| Undo already-finalized job | 409 | "Action already finalized" |
| Entity creation fails | failed | Job status failed, SignalR failure event, safe retry only |
| Teams sender unmapped | skipped | Import discussion only; no assistant tool execution |

## Idempotency

Hangfire may process a job more than once if a node crashes mid-execution. Guard with a distributed lock on `job_id`. The second execution must find `status != pending` and skip.

## Related

- [[modules/work-management/chat-ai/overview|Chat AI Overview]]
- [[modules/shared-platform/chatbot-api-integration|Semantic Kernel Assistant Integration]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
- [[modules/ide-extension/overview|IDE Extension]]
- [[modules/work-management/chat-ai/testing|Chat AI Testing]]
