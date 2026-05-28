# Semantic Kernel Assistant Integration

**Module:** Shared Platform + WorkSync Chat AI
**Phase:** 1
**Purpose:** Build ONEVO's first-party Semantic Kernel assistant inside the ONEVO backend so HR Management, Workforce Intelligence, and WorkSync actions use the same tenant context, RBAC, module entitlements, audit trail, and undo workflow.

> [!IMPORTANT]
> ONEVO owns this assistant. It is not an external WMS chatbot and it must not bypass ONEVO application services. Semantic Kernel is the orchestration layer that chooses permission-checked ONEVO functions; the functions execute through existing CQRS handlers or application service interfaces.

---

## Architecture

```text
ONEVO Web Chat / IDE Chat / Microsoft Teams linked channel
    -> Chat message saved in WorkSync Chat
    -> MessageSentEvent or TeamsMessageImportedEvent
    -> SemanticKernelChatOrchestrator
    -> Kernel plugins expose ONEVO functions
    -> Function permission/module filter runs before execution
    -> Application service / CQRS handler executes
    -> Query answer or ai_action_jobs pending action
    -> Assistant message + SignalR update
    -> Optional Microsoft Teams outbound sync
```

The assistant is a backend capability. Browser JavaScript never receives provider keys, Semantic Kernel credentials, or user JWTs.

---

## Runtime Boundaries

| Boundary | Rule |
|---|---|
| Tenant context | Resolved from the authenticated web/IDE/Teams-mapped ONEVO user, never from AI text. |
| Permissions | Every tool call checks the same effective permissions used by REST endpoints. |
| Module entitlements | Tools are disabled when the tenant lacks the module or add-on. |
| Data access | Kernel functions call application-layer services/CQRS handlers, not DbContext directly. |
| Actions | Reversible creates/updates go through `ai_action_jobs` and the server-enforced undo window. |
| Audit | Store assistant runs, tool calls, permission denials, and finalized actions with user and tenant context. |
| PII | Do not send unnecessary HR, payroll, identity, or monitoring data to the model. Send only the minimal context required for the requested function. |

---

## Entry Points

### ONEVO Web Chat

```text
POST /api/v1/channels/{channelId}/messages
  -> save user message
  -> publish MessageSentEvent
  -> SemanticKernelChatOrchestrator handles the message when assistant is enabled
  -> assistant answer or pending action appears in the same channel
```

### IDE Chat

```text
IDEHub chat message
  -> save message into the linked ONEVO channel or IDE chat thread
  -> use same orchestrator and same permission checks
  -> IDE receives chat:message and ai:* events
```

### Microsoft Teams Linked Channel

```text
Graph webhook/delta
  -> TeamsMessageWebhookHandler
  -> map Teams sender to ONEVO user
  -> insert ONEVO message with external_source = "microsoft_teams"
  -> invoke SemanticKernelChatOrchestrator if assistant is enabled for the channel
  -> assistant reply can sync back to Teams when policy allows
```

Teams messages are discussion by default. Official state changes still execute only through ONEVO application commands after user mapping and permission checks.

---

## Kernel Plugin Model

Use typed in-process Kernel Functions for Phase 1. OpenAPI import is allowed later for internal reuse, but the first build should keep function boundaries explicit so permission filtering, module entitlement checks, and undo behavior are predictable.

### HR Plugin

| Function | Required permission | Result |
|---|---|---|
| `GetEmployeeProfile` | `employees:read` (access policy scopes results to allowed employees) | Returns scoped employee summary. |
| `GetLeaveBalance` | `leave:read` or own employee context | Returns leave balance. |
| `CreateLeaveRequest` | `leave:write` | Creates leave request through Leave module. |
| `ApproveLeaveRequest` | `leave:approve` | Approves through workflow API. |
| `GetAttendanceStatus` | `attendance:read` (access policy scopes results to allowed employees) | Returns presence/activity summary. |
| `ListExceptionAlerts` | `monitoring:alerts:read` | Returns visible exception alerts. |

### WorkSync Plugin

| Function | Required permission | Result |
|---|---|---|
| `CreateTask` | `tasks:write` | Creates pending `ai_action_jobs` before task creation. |
| `UpdateTaskStatus` | `tasks:write` | Creates pending action or direct update depending on reversibility. |
| `ListMyTasks` | `tasks:read` | Returns assigned tasks. |
| `CreateReminder` | `chat:write` | Creates pending reminder action. |
| `PostChatMessage` | `chat:write` | Posts assistant/system message. |

### Calendar Plugin

| Function | Required permission | Result |
|---|---|---|
| `CreateCalendarEvent` | `calendar:write` | Creates pending calendar action when triggered from chat. |
| `FindAvailability` | `calendar:read` | Returns availability summary. |

### Exception Plugin

| Function | Required permission | Result |
|---|---|---|
| `GetActiveAlerts` | `monitoring:alerts:read` | Returns alert cards. |
| `AcknowledgeAlert` | `monitoring:alerts:resolve` | Acknowledges through Exception Engine. |
| `RequestCaptureForAlert` | `agent:command` | Creates remote capture command through Agent Gateway. |

---

## Orchestration Payloads

### Kernel Input Context

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
    "content": "Create a task to review payroll before Friday",
    "created_at": "2026-05-20T10:30:00Z"
  },
  "permissions": ["chat:write", "tasks:write"],
  "active_modules": ["work_management", "chat_ai", "core_hr"],
  "active_features": ["work_management.tasks", "chat_ai.agentic_chat", "core_hr.employee_profiles"],
  "locale": "en-LK",
  "timezone": "Asia/Colombo"
}
```

### Tool Call Selected By Semantic Kernel

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

### Permission Denial Result

```json
{
  "status": "denied",
  "reason": "missing_permission",
  "missing_permission": "tasks:write",
  "user_message": "You do not have permission to create tasks."
}
```

### Pending Action Result

```json
{
  "status": "pending_action",
  "job_id": "job-uuid",
  "action_type": "auto_create_task",
  "action_description": "Create task: Review payroll",
  "undo_expires_at": "2026-05-20T10:30:10Z"
}
```

---

## Data Processing Flow

1. Save the original user/Teams/IDE message before AI processing.
2. Build `KernelInputContext` from trusted server-side context.
3. Register only the tools allowed by the user's permissions and tenant modules.
4. Invoke Semantic Kernel with a system instruction that requires tool use for product data/actions and forbids guessing.
5. For read-only queries, execute the tool and write an assistant message with summarized results plus metadata.
6. For reversible actions, create `ai_action_jobs` with `status = pending` and send `ai:action_pending`.
7. If the user clicks Undo, mark the job `undone`.
8. If the undo window expires, Hangfire finalizes the job by executing the stored `action_params`.
9. Send `ai:action_finalized`.
10. If the source channel is Teams-linked and policy allows assistant sync, send the assistant response to Microsoft Teams.

---

## User Experience

| Outcome | UI behavior |
|---|---|
| Read-only answer | Assistant message in the chat thread with concise answer and source links when available. |
| Low confidence | Assistant asks a clarification question; no action job is created. |
| Permission denied | Assistant says the user lacks permission; no stack trace or raw 403 is shown. |
| Pending action | Inline AI action card with countdown and Undo button. |
| Finalized action | Chat shows created entity link, e.g. "Task created: Review payroll". |
| Failed action | Chat shows failure card with retry only if the action is safe to retry. |
| Teams-originated action | Prefer confirmation in ONEVO unless the tenant explicitly allows Teams-originated auto-actions. |

---

## Microsoft Teams Sync Rules

The assistant runs on normalized ONEVO messages. Teams is an input/output channel, not a separate authority.

| Direction | Rule |
|---|---|
| ONEVO -> Teams | Assistant replies and normal chat messages may sync when `channel_teams_links.status = active` and policy allows outbound sync. |
| Teams -> ONEVO | Teams messages are imported, deduplicated by Graph message id, mapped to a ONEVO user, then processed by the same assistant flow. |
| Workflow actions | Teams discussion does not change workflow state unless the message maps to a ONEVO user and the assistant executes a permission-checked ONEVO command. |
| Audit | Store the source as `microsoft_teams` and the external message id on imported messages and tool runs. |

---

## Required Storage

Use existing Chat AI tables for action state:

- `premium_ai_detections`
- `ai_action_jobs`
- `chat_reminder_items`

The Chat message schema must also support assistant/system messages and metadata. Minimum required fields are documented in [[database/schemas/wms-chat|WMS Chat Schema]].

Implementation should add assistant-run audit storage if existing audit logs cannot answer:

- who asked
- what source channel/message triggered the run
- which tool was selected
- which permissions were checked
- whether the tool executed, was denied, failed, or became a pending action
- model/provider token usage if available

---

## Related

- [[modules/work-management/chat/overview|Chat]]
- [[modules/work-management/chat-ai/overview|Chat AI]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[current-focus/contracts/signalr-events|SignalR Events]]
- [[AI_CONTEXT/rules|Rules]]
