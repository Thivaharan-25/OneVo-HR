# Chat AI Flow (Phase 2)

**Phase:** Phase 2. Not part of Phase 1 implementation scope.

**Area:** Work -> Chat (Phase 2)  
**Trigger:** Deferred Phase 2 only. Phase 1 Work must not expose Chat AI, IDE chat assistance, or Teams-synced assistant actions.
**Required Permission(s):** `chat:read`, `chat:write`  
**Related Permissions:** Feature flag `premium_ai`

---

## Preconditions

- Tenant has WorkSync Chat enabled -> [[Userflow/Chat/chat-overview|Chat Overview]]
- Tenant has Agentic Chat / `premium_ai` enabled
- User has access to the workspace/channel
- For Microsoft Teams messages, the Teams sender is mapped to a ONEVO user

## Flow Steps

### Step 1: User Sends Message
- **UI:** User posts a message in a channel or DM
- **Backend:** Chat message is persisted normally before AI processing

### Step 2: AI Detects Intent
- **Backend:** ONEVO Semantic Kernel assistant checks tenant feature flag, module entitlements, and user permissions before registering callable tools
- **DB:** `premium_ai_detections`
- **Examples:** answer HR/work status questions, create task, set reminder, schedule meeting

### Step 3: Pending AI Action Is Created
- **Backend:** Creates `ai_action_jobs` with `status = pending`
- **Rule:** Chat AI uses a 10-second undo window
- **SignalR:** Sends `ai:action_pending`

### Step 4: User Reviews Countdown Toast
- **UI:** Toast or inline action shows what will be created
- **User Action:** User can click Undo before the countdown expires

### Step 5A: User Clicks Undo
- **API:** `DELETE /api/v1/ai-actions/{id}/undo`
- **DB:** `ai_action_jobs.status = undone`
- **Result:** No downstream entity is created

### Step 5B: Window Expires
- **System:** Hangfire finalizes the pending action
- **DB:** `ai_action_jobs.status = finalized`
- **Result:** Entity is created from `action_params`
- **SignalR:** Sends `ai:action_finalized`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Premium AI disabled | Assistant does not process message | Normal chat only |
| Low confidence intent | No action job created | No automation prompt |
| Undo window expired | Undo request rejected | "This action has already been applied" |
| Entity creation fails | Job moves to failed | Failure notification with retry if supported |

## Events Triggered

- `AiIntentDetectedEvent`
- `AiActionFinalizedEvent`
- `AiActionUndoneEvent`

## Related Flows

- [[Userflow/Chat/chat-overview|Chat Overview]]
- [[Userflow/Work-Management/my-space-flow|My Space]]
- [[Userflow/IDE-Extension/tag-engine-flow|Tag Engine Flow]]

## Module References

- [[modules/work-management/chat-ai/overview|Chat AI]]
- [[modules/work-management/chat/overview|Chat]]
