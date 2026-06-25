# Module: IDE Extension

**Namespace:** `ONEVO.Modules.IDEExtension`
**Phase:** 2
**Pillar:** Cross-Pillar (WorkSync + HR + Monitoring)
**Owner:** Dev 7 (core + tag engine) + Dev 8 (context engine + agent entitlement)
**Tables:** 5 (`ide_extension_installs`, `ide_sessions`, `ide_tag_executions`, `ide_context_links`, `ide_chat_threads`)
**Client:** VS Code Extension (TypeScript).

---

## Purpose

The IDE Extension turns every developer's editor into a full OneVo terminal. It provides:

1. **Embedded Chat Sidebar** - full WorkSync chat (channels + DMs) inside VS Code, with the same real-time experience as the web frontend
2. **Tag Engine** - `@entity:action params` syntax lets users trigger any OneVo action they have permission for, without leaving the editor. Tasks, sprints, time logs, chat messages, Time Off requests, document links, code reviews - all accessible via tags.
3. **Context Engine** - automatic linking of Git branches and files to WorkSync tasks. Time tracking integrates with the active branch context.
4. **Entitlement-Gated Agent Provisioning** - if the user's tenant has a monitoring entitlement, the extension offers to provision the desktop monitoring agent. Never silent, never without server-side entitlement validation.

The extension is a **client** of the same backend APIs used by the web frontend. It has no separate database, no separate auth, and no separate permission model. Every action goes through the backend.

---

## Dependencies

**Depends on:**
- `Infrastructure` - `tenants`, `users` (auth context)
- `Auth` - JWT authentication, refresh token rotation
- `WorkSync.Foundation` - `workspaces`, `workspace_members`
- `WorkSync.Chat` - `channels`, `messages` (chat sidebar)
- `WorkSync.Tasks` - `tasks`, `task_assignments` (tasks panel)
- `WorkSync.ChatAI` - `ai_action_jobs` (tag-triggered creates share the same undo state machine)
- `WorkSync.Integrations` - `repositories`, `task_repository_links` (branch->task context)
- `AgentGateway` - `agent_install_entitlements`, `agent_install_jobs`, `registered_agents`
- `Notifications` - notification feed in IDE sidebar

**Consumed by:**
- `WorkSync.ChatAI` - `ide_tag_executions.tag_execution_id` FK in `ai_action_jobs`
- `ActivityMonitoring` - `ide_sessions` provides IDE coding-context for activity attribution (future Phase 2)

---

## Database Tables

### `ide_extension_installs` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces, nullable |
| `editor_type` | varchar(20) | vscode / jetbrains |
| `editor_version` | varchar(50) | |
| `extension_version` | varchar(20) | |
| `device_fingerprint` | varchar(255) | OS + hardware hash (not PII) |
| `installed_at` | timestamptz | |
| `last_active_at` | timestamptz | |
| `is_active` | boolean | |

---

### `ide_sessions` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `install_id` | uuid | FK -> ide_extension_installs |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces, nullable |
| `active_project_id` | uuid | FK -> projects, nullable - updated on branch switch |
| `started_at` | timestamptz | |
| `ended_at` | timestamptz | nullable |

---

### `ide_tag_executions` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `session_id` | uuid | FK -> ide_sessions, nullable |
| `raw_tag_input` | text | The exact string the user typed |
| `parsed_entity` | varchar(50) | task / sprint / time / chat / time_off / doc / board / okr / review / notify |
| `parsed_action` | varchar(50) | new / status / assign / log / send / request / view / move / link |
| `resolved_params` | jsonb | Parsed parameters after autocomplete resolution |
| `permission_check_result` | varchar(20) | allowed / denied |
| `execution_status` | varchar(20) | pending / success / failed / undone |
| `created_entity_type` | varchar(50) | nullable - task / time_log / message / etc |
| `created_entity_id` | uuid | nullable |
| `undo_expires_at` | timestamptz | nullable - set for reversible actions |
| `undone_at` | timestamptz | nullable |
| `executed_at` | timestamptz | |

**Index:** `(user_id, executed_at DESC)`, `(session_id)`

---

### `ide_context_links` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK -> users |
| `tenant_id` | uuid | FK -> tenants |
| `repository_url` | varchar(500) | Full clone URL |
| `branch_name` | varchar(255) | |
| `file_path` | varchar(1000) | nullable - for file-level links |
| `entity_type` | varchar(30) | task / project / sprint / document |
| `entity_id` | uuid | |
| `link_type` | varchar(30) | branch / commit / file / pr |
| `created_at` | timestamptz | |
| `created_by` | uuid | FK -> users |

**Index:** `(repository_url, branch_name)`, `(tenant_id, entity_type, entity_id)`

---

### `ide_chat_threads` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `channel_id` | uuid | FK -> channels |
| `user_id` | uuid | FK -> users |
| `ide_session_id` | uuid | FK -> ide_sessions, nullable |
| `context_task_id` | uuid | FK -> tasks, nullable |
| `context_file_path` | varchar(1000) | nullable |
| `last_message_at` | timestamptz | |

---

## Public Interface

```csharp
public interface IIDEExtensionService
{
    Task<IDEInstallResult> RegisterInstallAsync(RegisterIDEInstallCommand cmd);
    Task<IDEEntitlementsDto> GetEntitlementsAsync(Guid userId, Guid tenantId);
    Task<TagExecutionResult> ExecuteTagAsync(ExecuteTagCommand cmd);
    Task UndoTagExecutionAsync(Guid executionId, Guid userId);
    Task<IDEContextDto> GetBranchContextAsync(string repositoryUrl, string branchName, Guid userId);
    Task<AgentInstallJobDto> RequestAgentInstallAsync(RequestAgentInstallCommand cmd);
}
```

---

## Tag Engine

### Tag Syntax

```
@{entity}:{action} {positional-args} #{named-param}:{value} @{user-mention}
```

### Supported Entities and Actions

| Entity | Actions | Example |
|:-------|:--------|:--------|
| `task` | `new`, `status`, `assign`, `link`, `move`, `view`, `comment` | `@task:new "Fix bug" #sprint:current @assign:sarah` |
| `sprint` | `add`, `move`, `start`, `complete`, `view` | `@sprint:add #TASK-456 to:next` |
| `time` | `log`, `start`, `stop`, `view` | `@time:log 2h #TASK-456 "Auth refactor"` |
| `chat` | `send`, `pin`, `remind`, `thread` | `@chat:send #dev-backend "PR ready"` |
| `doc` | `view`, `create`, `link`, `approve` | `@doc:link #TASK-456 to:"API Guidelines"` |
| `time_off` | `request`, `view`, `cancel` | `@time-off:request 2026-05-05 2026-05-07 "Conference"` |
| `board` | `move`, `view` | `@board:move #TASK-456 column:"In Review"` |
| `okr` | `checkin`, `view` | `@okr:checkin #KR-12 value:75` |
| `review` | `request`, `approve`, `reject` | `@review:request #TASK-456 @reviewer:john` |
| `notify` | `send` | `@notify:send @sarah "Sprint planning in 15 min"` |
| `project` | `view`, `members` | `@project:view #PROJ-1` |

### Permission Model

The tag engine calls the **same backend API endpoints** as the web frontend. It does not have a separate permission system. The backend validates `RequirePermission` attributes on each endpoint exactly as it does for web requests.

If the user does not have permission:
- Backend returns 403
- Tag engine logs `permission_check_result = denied` in `ide_tag_executions`
- Extension shows red inline error: "You don't have `{permission}` - contact your workspace admin"

### Undo Window

Actions that create entities have an `undo_expires_at` (default 30 seconds for tag-triggered, 10 seconds for AI auto-create). During the window:
- Extension shows a countdown toast with [Undo] button
- SignalR pushes real-time state (pending -> finalized/undone)
- Clicking Undo calls `DELETE /api/v1/ide/tags/executions/{id}`
- Backend calls the appropriate reverse operation (soft-delete task, delete time_log, etc.)

### Context Variables

These are automatically resolved from current editor context if not provided explicitly:

| Param | Auto-source |
|:------|:------------|
| `#sprint:current` | Active sprint in `active_project_id` from current session |
| `@assign:me` | Authenticated user |
| `#repo:current` | Current repository URL from git remote |
| `#branch:current` | Current git branch |
| `#task:current` | Task linked to current branch via `ide_context_links` |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/ide/register` | authenticated | Register extension install |
| GET | `/api/v1/ide/entitlements` | authenticated | Get monitoring + WorkSync entitlements |
| POST | `/api/v1/ide/sessions` | authenticated | Start IDE session |
| PUT | `/api/v1/ide/sessions/{id}/end` | authenticated | End session |
| PUT | `/api/v1/ide/sessions/{id}/context` | authenticated | Update active project/branch |
| POST | `/api/v1/ide/tags/execute` | authenticated | Execute tag action |
| DELETE | `/api/v1/ide/tags/executions/{id}` | authenticated | Undo tag execution |
| GET | `/api/v1/ide/context/branch` | authenticated | Get tasks linked to branch |
| GET | `/api/v1/ide/context/file` | authenticated | Get tasks linked to file |
| POST | `/api/v1/ide/context/links` | authenticated | Create context link |
| GET | `/api/v1/ide/tasks/assigned` | `tasks:read` | Tasks assigned to current user |
| POST | `/api/v1/ide/time/start` | `time_logs:write` | Start time tracking |
| POST | `/api/v1/ide/time/stop` | `time_logs:write` | Stop + log time |
| POST | `/api/v1/ide/agent-install/request` | authenticated | Request agent install (entitlement checked server-side) |
| GET | `/api/v1/ide/agent-install/status/{id}` | authenticated | Poll install job status |
| PUT | `/api/v1/ide/agent-install/{id}/installed` | authenticated | Mark agent installed (called by installer) |

---

## SignalR Hub: `IDEHub`

**Connection:** `wss://{tenantSlug}.onevo.com/hubs/ide?access_token={jwt}`

IDE extension connects with a JWT and session_id. Hub groups:
- `user:{userId}` - personal notifications
- `workspace:{workspaceId}` - workspace-level events
- `channel:{channelId}` - subscribed when user opens a channel in chat panel

### Events pushed to extension

| Event | Trigger | Payload |
|:------|:--------|:--------|
| `chat:message` | New message in joined channel | `{ channel_id, message }` |
| `chat:typing` | User typing in channel | `{ channel_id, user_id }` |
| `task:updated` | Task status/assignment changed | `{ task_id, changes }` |
| `notification:new` | New notification for user | `{ notification }` |
| `ai:action_pending` | AI auto-create job created | `{ job_id, action_type, undo_expires_at }` |
| `ai:action_finalized` | Undo window expired | `{ job_id, created_entity_id }` |
| `ai:action_undone` | User clicked undo | `{ job_id }` |
| `tag:executed` | Tag execution result | `{ execution_id, status, result, undo_expires_at? }` |

---

## VS Code Extension Architecture

```
src/
+-- extension.ts               # Activate/deactivate, register commands, contribute viewContainers
+-- auth/
|   +-- AuthService.ts         # PKCE OAuth flow, token storage (VS Code SecretStorage)
|   +-- TokenRefresher.ts      # Background refresh 60s before expiry
+-- signalr/
|   +-- IDEHubClient.ts        # SignalR JS client, reconnect logic, group subscriptions
+-- panels/
|   +-- ChatPanel.ts           # TreeDataProvider for channel list + WebviewPanel for message feed
|   +-- TasksPanel.ts          # TreeDataProvider for assigned tasks (grouped by sprint/status)
|   +-- NotificationsPanel.ts  # TreeDataProvider for notification feed
+-- tag-engine/
|   +-- TagParser.ts           # Lexer + parser for @entity:action syntax
|   +-- TagExecutor.ts         # Calls POST /api/v1/ide/tags/execute, handles undo
|   +-- AutoCompleteProvider.ts # VS Code CompletionItemProvider - entity/action/param hints
|   +-- CommentScanner.ts      # Opt-in: detect @onevo: tags in code comments on file save
+-- context/
|   +-- BranchDetector.ts      # Reads git HEAD ref, calls GET /api/v1/ide/context/branch
|   +-- FileContextDetector.ts # Active editor path -> GET /api/v1/ide/context/file
|   +-- TimeTracker.ts         # Status bar timer, start/stop calls, branch-linked tracking
+-- webviews/
|   +-- TaskDetailWebview.ts   # Full task detail in WebviewPanel
|   +-- ChatWebview.ts         # Rich chat message renderer (markdown, reactions, files)
+-- agent-install/
|   +-- AgentInstaller.ts      # Entitlement check, download, hash verify, execute installer
+-- api/
|   +-- OneVoApiClient.ts      # Typed HTTP client wrapping all backend endpoints
+-- config/
    +-- WorkspaceConfig.ts     # Reads .onevo config file (scan_comments, workspace_id override)
```

---

## `.onevo` Configuration File

Optional file at repo root. Controls extension behavior per repository:

```json
{
  "workspace_id": "uuid",
  "scan_comments": false,
  "commit_template": true,
  "branch_naming": "{task-id}-{slug}",
  "time_tracking": "auto"
}
```

- `scan_comments`: if true, extension scans `// @onevo:task ...` comments on file save and offers to execute
- `commit_template`: if true, inject task reference into git commit message template
- `branch_naming`: warn when branch name doesn't match pattern
- `time_tracking`: `auto` starts timer when branch with linked task is checked out; `manual` requires explicit start

---

## Key Business Rules

1. **Permission is always checked server-side.** The extension client never decides if a tag action is allowed. Backend returns 403 if unauthorized.
2. **Agent install requires explicit user consent.** The extension NEVER installs the monitoring agent silently. It always shows a prompt and requires the user to click "Set Up". The entitlement is validated server-side on every install request.
3. **Undo window is server-enforced.** The undo window timestamp is set by the backend. The client shows the countdown as a UI convenience only - the backend rejects undo calls after `undo_expires_at`.
4. **Tag executions are audit-logged even when denied.** Every `@entity:action` attempt creates an `ide_tag_executions` row regardless of the permission check result.
5. **Context resolution is best-effort.** If `GET /api/v1/ide/context/branch` finds no linked task, the extension operates without context - no error shown to user.

---

## Related

- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task Pack]] - chat sidebar, tag engine
- [[current-focus/DEV8-documents-github-ide|DEV8 Task Pack]] - context engine, agent entitlement
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[modules/agent-gateway/overview|Agent Gateway]] - registered_agents, install jobs
- [[modules/work-management/chat|WMS Chat]] - channels, messages
- [[Userflow/IDE-Extension/ide-install-flow|IDE Extension Install + Auth Flow]]
- [[Userflow/IDE-Extension/tag-engine-flow|IDE Tag Engine Flow]]
- [[Userflow/IDE-Extension/context-detection-flow|IDE Context Detection Flow]]
- [[Userflow/IDE-Extension/agent-install-flow|IDE Agent Install Flow]]
