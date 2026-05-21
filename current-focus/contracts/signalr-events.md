# Contract: SignalR Real-Time Events

**Backend owners:** DEV2 Task 5 (notifications hub), DEV3 Tasks 3-4 (WorkSync chat, Semantic Kernel assistant, IDEHub chat/tag), DEV4 Tasks 3 and 5 (agent/exception)
**Consumers:** DEV6 Task 4 (agent-status), DEV7 Task 3 (chat + assistant), DEV8 Tasks 2-3 (IDE)
**Canonical source:** `ONEVO.Api/Hubs/`

---

## Hub: `workforce-live`

```ts
// Agent status push - consumed by DEV6 Task 4
event "agent:status" {
  agent_id: string
  employee_id: string
  state: "online" | "degraded" | "offline" | "failed"
  last_heartbeat_at: string
}

// Exception alert - consumed by DEV6 Task 3
event "exception:alert" {
  alert_id: string
  employee_id: string
  rule_type: string
  severity: "low" | "medium" | "high" | "critical"
  raised_at: string
}
```

## Hub: `notifications-{userId}`

```ts
// In-app notification push - consumed by DEV6, DEV7, DEV8
event "notification:created" {
  notification_id: string
  title: string
  body: string
  unread_count: number
  created_at: string
}
```

## Hub: `worksync-chat`

```ts
// Chat message - consumed by DEV7 Task 3 and DEV8 Task 2
event "chat:message" {
  channel_id: string
  message_id: string
  sender_id: string | null
  sender_type: "user" | "assistant" | "system" | "external"
  content: string
  content_type: "text" | "markdown" | "system" | "ai_answer" | "ai_action_card"
  sent_at: string
  external_source: "microsoft_teams" | null
  sync_status: "not_applicable" | "pending" | "synced" | "failed" | "skipped" | "not_linked"
}

// Typing indicator - consumed by DEV7 Task 3
event "chat:typing" {
  channel_id: string
  user_id: string
  is_typing: boolean
}

// AI action pending - created by Semantic Kernel / Chat AI for reversible actions
event "ai:action_pending" {
  job_id: string
  channel_id: string
  source_message_id: string
  action_type: "auto_create_task" | "auto_create_reminder" | "auto_update_status" | "auto_create_calendar_event"
  action_description: string
  undo_expires_at: string
  created_entity_type: string | null
}

// AI action final state - emitted after undo, finalization, or failure
event "ai:action_finalized" {
  job_id: string
  channel_id: string
  source_message_id: string
  status: "finalized" | "undone" | "failed"
  undone: boolean
  created_entity_type: string | null
  created_entity_id: string | null
  error: string | null
}

// Microsoft Teams sync status changed for an existing ONEVO message
event "chat:sync_status" {
  channel_id: string
  message_id: string
  external_source: "microsoft_teams"
  sync_status: "pending" | "synced" | "failed" | "skipped" | "not_linked"
  last_error: string | null
}
```

## Hub: `IDEHub` (VS Code extension only)

```ts
// Tag execution result - consumed by DEV8 Task 3
event "tag:executed" {
  execution_id: string
  tag_action: string
  status: "success" | "denied" | "error"
  result_summary: string
  undo_available: boolean
  undo_expires_at: string | null
}

// Task update - consumed by DEV8 Task 2
event "task:updated" {
  task_id: string
  changes: Partial<TaskDto>   // shape from worksync-core.md
}

// IDE receives chat messages either by joining worksync-chat groups or through an IDE bridge event with the same payload shape.
event "chat:message" {
  channel_id: string
  message_id: string
  sender_id: string | null
  sender_type: "user" | "assistant" | "system" | "external"
  content: string
  sent_at: string
}

// Typing indicator - IDE bridge shape mirrors worksync-chat.
event "chat:typing" {
  channel_id: string
  user_id: string
  is_typing: boolean
}
```

## Notes

- Customer web hub connections authenticate with the same HttpOnly cookie-backed web session as REST.
- `IDEHub` may use the IDE-specific tenant JWT flow; that token is stored in IDE secure storage and is rejected at the admin boundary.
- `exception:alert` also dispatches `notification:created` to the manager's `notifications-{userId}` hub
- Client subscribes to `notifications-{userId}` using the `user_id` from `GET /api/v1/auth/me/permissions`
- `worksync-chat` is the canonical web chat hub. IDE may consume the same event payloads through IDEHub or by joining the same channel groups with an IDE token.
- `ai:action_pending` and `ai:action_finalized` are required for the Semantic Kernel assistant and Chat AI undo workflow.

