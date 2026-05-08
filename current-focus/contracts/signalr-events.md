# Contract: SignalR Real-Time Events

**Backend owners:** DEV2 Task 5 (notifications hub), DEV3 Tasks 3-4 (IDEHub chat/tag), DEV4 Tasks 3 and 5 (agent/exception)  
**Consumers:** DEV6 Task 4 (agent-status), DEV7 Task 3 (chat), DEV8 Tasks 2-3 (IDE)  
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

// Chat message - consumed by DEV7 Task 3 and DEV8 Task 2
event "chat:message" {
  channel_id: string
  message_id: string
  sender_id: string
  content: string
  sent_at: string
}

// Typing indicator - consumed by DEV7 Task 3
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

