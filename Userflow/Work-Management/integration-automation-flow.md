# Work Integration Automation (Phase 2)

**Area:** Work -> Integrations  
**Phase:** Phase 2 - deferred  
**Phase 1 Status:** Not active in current Phase 1 Work implementation. Preserve as future repository automation design reference.  
**Trigger:** Future workspace/project admin connects a code repository or configures automation  
**Required Permission(s):** `integrations:read`, `integrations:manage`  
**Related Permissions:** `tasks:write`

---

## Phase 2 Boundary

Phase 1 Work must not expose repository automation rules, GitHub/GitLab automation configuration, or workspace automation screens. Phase 1 Work focuses on projects, work items, basic membership, simple settings, worklogs, and simple docs/pages where retained.

## Flow Steps - Phase 2

### Step 1: Open Workspace Integrations
- **UI:** Work -> Project/Workspace Settings -> Integrations (Phase 2)
- **API:** `GET /api/v1/workspaces/{wsId}/repositories`
- **UI:** Shows connected repositories, webhook health, and automation rules

### Step 2: Connect Repository
- **API:** `POST /api/v1/workspaces/{wsId}/repositories`
- **Backend:** Stores repository metadata and webhook secret
- **Security:** Webhooks must validate HMAC before processing

### Step 3: Link Task to Repository
- **UI:** Task detail -> Repository links
- **API:** `POST /api/v1/tasks/{id}/repository-links`
- **Result:** Explicit link is visible on the task

### Step 4: Receive Code Event
- **API:** `POST /api/v1/webhooks/github/{repoId}`
- **Backend:** Validates HMAC, writes `code_activity_events`, parses commits/PRs, and detects task references

### Step 5: Evaluate Automation Rules - Phase 2
- **System:** Rule evaluator checks active rules for the event type
- **Examples:** move task after PR merge, post chat message on CI failure, assign task after push
- **Audit:** Rule action and idempotency key are recorded

### Step 6: Manage Rules - Phase 2
- **API:** `GET /api/v1/workspaces/{wsId}/automation-rules`, `POST /api/v1/workspaces/{wsId}/automation-rules`
- **UI:** Admin creates, edits, disables, or tests rules

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid webhook signature | Webhook rejected | Integration health warning |
| Repository already connected | Save rejected | Duplicate repository message |
| Task reference not found | Event stored without task link | Unlinked event indicator |
| Rule action fails | Rule result logged as failed | Rule failure notification |
| Provider unavailable | Sync pauses/retries | Provider outage status |

## Events Triggered

- `WebhookReceivedEvent`
- `PullRequestMergedEvent`
- `CIPipelineFailedEvent`

## Related Flows

- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/IDE-Extension/context-detection-flow|Context Detection Flow]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/work-management/integrations/overview|Integration & API]]
- [[modules/ide-extension/overview|IDE Extension]]
- [[database/schemas/wms-integrations|WMS Integrations Schema]]
