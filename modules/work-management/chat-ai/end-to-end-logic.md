# Chat AI — End-to-End Logic

**Module:** WorkSync
**Feature:** Chat AI

---

## AI Intent Detection Flow

```
Message received (POST /api/v1/channels/{id}/messages)
  → Message saved (Chat module)
  → MessageSentEvent published
  → ChatAIDetectionHandler (INotificationHandler<MessageSentEvent>)
      → 1. Check tenant has "premium_ai" feature flag
             If not: SKIP — no detection
      → 2. Send message content to AI service (Claude API)
             Prompt: detect intent + extract params
      → 3. AI returns: { intent, confidence, params }
      → 4. If confidence < threshold (0.8): SKIP
      → 5. INSERT premium_ai_detections row
      → 6. INSERT ai_action_jobs row:
             status = pending
             entity_type = detected entity (e.g. "Task")
             action_type = detected action (e.g. "create")
             action_params = extracted params JSON
             undo_expires_at = now() + 10s   ← Chat AI: 10s window
             tag_execution_id = null          ← null for Chat AI
      → 7. Fire SignalR event: ai:action_pending
             payload: { job_id, action_description, expires_at, channel_id }
```

## Undo Window — User Cancels

```
DELETE /api/v1/ai-actions/{jobId}/undo
  → [Authenticated — must be job creator]
  → UndoAiActionHandler
    → 1. Load ai_action_jobs, verify status = "pending"
    → 2. Verify undo_expires_at > now() (window still open)
         If expired: return 409 UNDO_WINDOW_EXPIRED
    → 3. UPDATE ai_action_jobs:
             status = "undone"
             undone_at = now()
    → 4. If tag_execution_id is not null:
             UPDATE ide_tag_executions.status = "undone"
    → 5. Fire SignalR: ai:action_finalized
             payload: { job_id, undone: true }
    → Toast dismissed: "Action cancelled"
    → Return 200
```

## Hangfire Finalization (Every 5 Seconds)

```
FinalizeAiActionsJob (Hangfire recurring — every 5s)
  → SELECT * FROM ai_action_jobs
      WHERE status = 'pending' AND undo_expires_at < now()
  → For each row:
      → 1. Begin distributed lock on job_id (prevent double-processing)
      → 2. Re-check status = 'pending' inside lock (optimistic check)
      → 3. Execute action from action_params:
             "create_task" → INSERT tasks (using action_params)
             "set_reminder" → INSERT reminders
             "schedule_meeting" → INSERT calendar_events
      → 4. UPDATE ai_action_jobs:
             status = "finalized"
             finalized_at = now()
      → 5. If tag_execution_id is not null:
             UPDATE ide_tag_executions.status = "completed"
      → 6. Fire SignalR: ai:action_finalized
             payload: { job_id, undone: false, entity_id: new entity id }
      → 7. Release lock
  → On exception:
      → UPDATE ai_action_jobs.status = "failed"
      → Log error with job_id
```

## IDE Tag Undo (30s Window — Same State Machine)

```
Same ai_action_jobs table, different undo window:
  → undo_expires_at = now() + 30s (IDE Tag Engine sets this)
  → tag_execution_id set (links to ide_tag_executions)
  → All other logic identical to Chat AI flow above
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Undo after window expired | 409 | Undo window has expired |
| Undo non-existent job | 404 | Action not found |
| Undo already-finalized job | 409 | Action already finalized |
| Tenant has no premium_ai flag | — | Detection silently skipped (no 403) |
| Finalization: entity creation fails | — | status = failed, error logged |

### Idempotency

Hangfire may process a job more than once if a node crashes mid-execution. Guard: distributed lock on `job_id`. Second execution finds `status != pending` and skips.

## Related

- [[modules/work-management/chat-ai/overview|Chat AI Overview]]
- [[modules/ide-extension/overview|IDE Extension]] — IDE tag uses same ai_action_jobs table
- [[modules/work-management/chat-ai/testing|Chat AI Testing]]
