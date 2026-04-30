# Task: Chat + Chat AI + My Space + Reminders + IDE Extension

**Assignee:** Dev 7
**Pillar:** Pillar 3 — WorkSync + IDE Extension
**Priority:** Critical (Chat) / High (AI + IDE)
**Dependencies:** DEV5 WorkSync Foundation (workspace_id FK), DEV1 Infrastructure (file_assets for attachments), DEV2 Auth (JWT for IDE extension auth)

---

## Task 1: Chat

**Module:** `ONEVO.Modules.WorkSync.Chat`
**Tables:** `channels`, `channel_members`, `messages`, `message_reactions`, `message_attachments`, `message_pins`
**Depends on:** DEV5 Task 1 (workspaces)

### Acceptance Criteria

- [ ] `channels` table: id, workspace_id → workspaces, name, description, channel_type (public/private/direct), created_by → users, is_archived boolean, created_at
- [ ] `channel_members` table: id, channel_id → channels, user_id → users, role (admin/member), last_read_at timestamptz nullable, joined_at. UNIQUE (channel_id, user_id)
- [ ] `messages` table: id, channel_id → channels, user_id → users, content text, parent_message_id → messages nullable (threads), is_edited boolean, edited_at nullable, is_deleted boolean, deleted_at nullable, created_at
- [ ] `message_reactions` table: id, message_id → messages, user_id → users, emoji varchar(10). UNIQUE (message_id, user_id, emoji)
- [ ] `message_attachments` table: id, message_id → messages, file_asset_id → file_assets
- [ ] `message_pins` table: id, channel_id → channels, message_id → messages, pinned_by → users, pinned_at
- [ ] SignalR hub: `ChatHub` — clients join channel groups, receive real-time messages, reactions, typing indicators
- [ ] `POST /api/v1/channels/{id}/messages` — send message (triggers SignalR broadcast to channel group)
- [ ] `PUT /api/v1/channels/{id}/messages/{msgId}` — edit message (mark is_edited, update content)
- [ ] `DELETE /api/v1/channels/{id}/messages/{msgId}` — soft-delete (mark is_deleted, clear content)
- [ ] `POST /api/v1/channels/{id}/messages/{msgId}/reactions` — react with emoji
- [ ] `POST /api/v1/channels/{id}/messages/{msgId}/pin` — pin message
- [ ] `GET /api/v1/channels/{id}/messages` — paginated messages (cursor-based, newest first)
- [ ] `GET /api/v1/workspaces/{id}/channels` — list channels user is member of
- [ ] Typing indicator: SignalR client sends typing event → server broadcasts to channel (TTL 5 seconds)
- [ ] Unread count: tracked via `channel_members.last_read_at` vs latest message created_at
- [ ] DM channels: channel_type = direct, exactly 2 members, name auto-generated
- [ ] `POST /api/v1/workspaces/{id}/channels/{id}/members` — add member to channel (workspace admin or channel admin)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 33 WMS Chat
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[modules/work-management/chat|WMS Chat spec]]

---

## Task 2: Chat AI

**Module:** `ONEVO.Modules.WorkSync.ChatAI`
**Tables:** `premium_ai_detections`, `ai_action_jobs`, `chat_reminder_items`
**Depends on:** Task 1 (messages)

### Acceptance Criteria

- [ ] `premium_ai_detections` table: id, message_id → messages, channel_id → channels, detected_intent (task/report/issue/other), confidence_score numeric(5,4), auto_created boolean, created_entity_type varchar nullable, created_entity_id uuid nullable, detected_at
- [ ] `ai_action_jobs` table: id, detection_id → premium_ai_detections nullable, tag_execution_id → ide_tag_executions nullable, user_id → users, tenant_id → tenants, action_type (auto_create_task/auto_update_status/auto_create_reminder), action_params jsonb, status (pending/finalized/undone/failed), created_entity_type varchar nullable, created_entity_id uuid nullable, undo_expires_at timestamptz nullable, undone_at timestamptz nullable, finalized_at timestamptz nullable, created_at
- [ ] `chat_reminder_items` table: id, channel_id → channels, task_id → tasks nullable, user_id → users, title, status (pending/done/snoozed), reminder_at timestamptz nullable, created_at
- [ ] Premium AI message analysis: after each message save, if tenant has `premium_ai` feature flag enabled, run AI intent detection (async via Hangfire). Do not block message delivery.
- [ ] If intent = task AND confidence > 0.85 AND auto_created = false yet → create `ai_action_jobs` record with status = pending, `undo_expires_at = created_at + 10 seconds`
- [ ] Hangfire job (10-second delay): if `ai_action_jobs.status = pending` AND `undo_expires_at` passed → create task from `action_params`, set `status = finalized`, `created_entity_id = new task id`
- [ ] SignalR: when `ai_action_jobs` is created, push `ai:action_pending` event to message sender with countdown. When finalized, push `ai:action_finalized`. When undone, push `ai:action_undone`.
- [ ] `DELETE /api/v1/ai-action-jobs/{id}` — undo (only if status=pending AND undo_expires_at not passed). Sets status=undone, undone_at=now
- [ ] Chat reminder sync: when task status changes, update linked `chat_reminder_items.status`
- [ ] Two-way sync: if user changes `chat_reminder_items.status` to done → update linked task status

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 34 WMS Chat AI
- [[database/schemas/wms-chat|WMS Chat Schema]]

---

## Task 3: My Space + Reminders

**Module:** `ONEVO.Modules.WorkSync.MySpace`
**Tables:** `personal_boards`, `personal_board_columns`, `todos`, `reminders`, `saved_views`
**Depends on:** DEV5 Task 1 (workspaces), DEV6 Task 1 (tasks, for task-linked todos)

### Acceptance Criteria

- [ ] `personal_boards` table: id, user_id → users, workspace_id → workspaces, name, created_at
- [ ] `personal_board_columns` table: id, personal_board_id → personal_boards, name, position int, color varchar(20)
- [ ] `todos` table: id, user_id → users, workspace_id → workspaces nullable, title, description text nullable, task_id → tasks nullable (link to WorkSync task), status (pending/done), due_date date nullable, position int, created_at
- [ ] `reminders` table: id, user_id → users, workspace_id → workspaces nullable, entity_type (task/meeting/custom), entity_id uuid nullable, title, remind_at timestamptz, is_sent boolean, created_at
- [ ] Personal board columns are user-specific — no WIP limits, free drag
- [ ] `GET /api/v1/my/board` — personal board with columns and todo cards
- [ ] `POST /api/v1/my/todos` — create personal todo
- [ ] `PUT /api/v1/my/board/columns/{colId}/todos/{todoId}/position` — drag todo
- [ ] `POST /api/v1/my/reminders` — set reminder
- [ ] Hangfire job: scan `reminders` where `remind_at <= now AND is_sent = false` every minute → push notification via Notifications module, mark is_sent = true
- [ ] When a WorkSync task is assigned to a user, auto-create a `todos` row with `task_id` linked
- [ ] My Space view shows: own assigned tasks from WorkSync + personal todos, combined and sorted by due_date

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 29 WMS My Space, Section 36 WMS Reminders
- [[modules/work-management/my-space|WMS My Space spec]]

---

## Task 4: IDE Extension Core (Week 5)

**Module:** `ONEVO.Modules.IDEExtension` (backend) + VS Code Extension (TypeScript)
**Tables:** `ide_extension_installs`, `ide_sessions`
**Depends on:** DEV2 Auth (JWT), DEV7 Chat (channels, messages), DEV6 Tasks (tasks), DEV2 Notifications

### Acceptance Criteria — Backend

- [ ] `ide_extension_installs` table: id, user_id → users, tenant_id → tenants, workspace_id → workspaces nullable, editor_type (vscode/jetbrains), editor_version varchar, extension_version varchar, device_fingerprint varchar(255), installed_at, last_active_at, is_active boolean
- [ ] `ide_sessions` table: id, install_id → ide_extension_installs, user_id → users, tenant_id → tenants, workspace_id → workspaces nullable, active_project_id → projects nullable, started_at, ended_at nullable
- [ ] `POST /api/v1/ide/register` — register extension install, return install_id. Auth: bearer JWT.
- [ ] `GET /api/v1/ide/entitlements` — return `{ has_monitoring_entitlement: bool, has_worksync: bool, workspace_id: uuid }`. Used by extension on startup.
- [ ] `POST /api/v1/ide/sessions` — start session, return session_id
- [ ] `PUT /api/v1/ide/sessions/{id}/end` — end session
- [ ] SignalR hub: `IDEHub` — IDE extension connects with session_id. Receives task updates for tasks the user is assigned to, new chat messages in joined channels, notifications
- [ ] `PUT /api/v1/ide/sessions/{id}/context` — update active project/branch context: `{ project_id?, branch_name? }`

### Acceptance Criteria — VS Code Extension (TypeScript)

- [ ] Extension activates on VS Code start if workspace has `.onevo` config file OR user is signed in
- [ ] Auth flow: `onevo.login` command → open browser to `https://{tenant}.onevo.app/ide-auth?code_challenge=...` → OAuth PKCE → store JWT + refresh token in VS Code SecretStorage (not plaintext)
- [ ] WebSocket: connect to `wss://{tenant}.onevo.app/hubs/ide?access_token={jwt}` via SignalR JS client
- [ ] Sidebar: contribute `onevo` viewContainer with three views:
  - `onevo.chat` — Chat panel (channel list + message feed + input box)
  - `onevo.tasks` — Tasks panel (assigned tasks + quick status toggle)
  - `onevo.notifications` — Notifications panel (bell feed)
- [ ] Chat panel: render messages with markdown, show reactions, send new message via `POST /api/v1/channels/{id}/messages`
- [ ] Tasks panel: list tasks assigned to current user in active workspace, grouped by status. Click task → open webview with full task detail.
- [ ] Status bar item: shows active workspace name + active sprint (if any). Click → workspace switcher quick-pick.
- [ ] Token refresh: background timer refreshes access token 60 seconds before expiry via `POST /api/v1/auth/refresh`

### Backend References
- [[modules/ide-extension/overview|IDE Extension spec]]
- [[database/schemas/ide-extension|IDE Extension Schema]]

---

## Task 5: IDE Extension Tag Engine (Week 6)

**Module:** `ONEVO.Modules.IDEExtension` (tag execution backend) + VS Code Extension tag parser
**Tables:** `ide_tag_executions`
**Depends on:** Task 4 (IDE sessions), DEV6 Tasks + Sprints, DEV7 Chat, DEV5 OKR/Time

### Acceptance Criteria — Backend

- [ ] `ide_tag_executions` table: id, user_id → users, tenant_id → tenants, session_id → ide_sessions nullable, raw_tag_input text, parsed_entity varchar(50), parsed_action varchar(50), resolved_params jsonb, permission_check_result (allowed/denied), execution_status (pending/success/failed/undone), created_entity_type varchar nullable, created_entity_id uuid nullable, undo_expires_at timestamptz nullable, undone_at timestamptz nullable, executed_at
- [ ] `POST /api/v1/ide/tags/execute` — parse and execute a tag. Body: `{ raw: "@task:new ...", session_id: uuid, context: { branch, file_path } }`. Returns `{ execution_id, status, result, undo_expires_at? }`
- [ ] Tag router: parses `@entity:action params` and routes to the corresponding existing API endpoint. Permission check uses the same RBAC as the web frontend — no separate permission logic.
- [ ] Supported entities and actions:
  - `task`: new, status, assign, link, move, view
  - `sprint`: add, move, start, complete, view
  - `time`: log, stop, view
  - `chat`: send, pin, remind
  - `doc`: view, create, link
  - `leave`: request, view, cancel
  - `board`: move, view
  - `notify`: send
  - `okr`: checkin, view
  - `review`: request, approve, reject
- [ ] Reversible actions (new, log, send) set `undo_expires_at = executed_at + 30 seconds`
- [ ] `DELETE /api/v1/ide/tags/executions/{id}` — undo (if reversible and within window). Calls the corresponding delete/patch on the created entity.
- [ ] All executions audit-logged even if denied (`permission_check_result = denied`)
- [ ] SignalR: push tag execution result back to IDE session immediately (success/denied/error + undo window)

### Acceptance Criteria — VS Code Extension

- [ ] Tag input: in the Chat panel input box, detect `@` prefix → show autocomplete dropdown with entity types
- [ ] After entity selected, show action autocomplete (`@task:` → `new`, `status`, `assign`, `move`, `link`, `view`)
- [ ] After action selected, show parameter hints inline (e.g. `@task:new "title" #sprint:current @assign:user #priority:high`)
- [ ] Autocomplete sources: tasks, sprints, projects, users — fetched from backend and cached for 60 seconds
- [ ] On Enter: send raw tag to `POST /api/v1/ide/tags/execute`. Show spinner.
- [ ] On success: show inline result card (green) with entity link. If undo_expires_at: show countdown + Undo button.
- [ ] On Undo click: call `DELETE /api/v1/ide/tags/executions/{id}`. Show "Undone" confirmation.
- [ ] On denied: show red error card with the permission that was missing.
- [ ] Code comment detection (opt-in): if `.onevo` config has `scan_comments: true`, detect `// @onevo:task ...` patterns in active editor. On save, offer to execute detected tags.
- [ ] Commit message template (optional): inject `@onevo:task:close #TASK-XXX` into commit message template when user is on a branch with a linked task

### Backend References
- [[modules/ide-extension/overview|IDE Extension spec]]
- [[Userflow/Work-Management/ide-extension-tag-flow|IDE Tag Flow]]

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workspaces/[id]/
├── chat/
│   ├── layout.tsx                 # Chat layout: channel list sidebar + message area
│   ├── [channelId]/
│   │   └── page.tsx               # Channel message feed + composer
│   └── dm/
│       └── [userId]/page.tsx      # DM conversation
├── my-space/
│   ├── page.tsx                   # My Space: personal board + todo list + reminders
│   └── reminders/page.tsx         # Reminder management
```

### IDE Extension Views (TypeScript — not Next.js)
```
src/
├── panels/
│   ├── ChatPanel.ts               # Chat sidebar panel
│   ├── TasksPanel.ts              # Tasks sidebar panel
│   └── NotificationsPanel.ts      # Notifications sidebar panel
├── tag-engine/
│   ├── TagParser.ts               # @entity:action syntax parser
│   ├── TagExecutor.ts             # Calls backend, handles result/undo
│   └── AutoComplete.ts            # Autocomplete provider
├── context/
│   ├── BranchContextDetector.ts   # Reads git branch → finds linked task
│   └── FileContextDetector.ts     # Active file → related tasks
├── auth/
│   └── AuthService.ts             # PKCE OAuth, token storage, refresh
└── signalr/
    └── IDEHubClient.ts            # SignalR connection manager
```

### Key Userflows
- [[Userflow/Work-Management/chat-flow|Chat Flow]]
- [[Userflow/Work-Management/chat-ai-flow|Chat AI + Undo Flow]]
- [[Userflow/Work-Management/my-space-flow|My Space Flow]]
- [[Userflow/Work-Management/ide-extension-auth|IDE Extension Auth]]
- [[Userflow/Work-Management/ide-extension-tag-flow|IDE Tag Flow]]
