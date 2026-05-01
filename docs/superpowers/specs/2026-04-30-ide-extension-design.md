# IDE Extension — Full Design Spec
**Date:** 2026-04-30  
**Author:** Brainstorming session  
**Status:** Approved — ready for implementation plan  
**Implements:** DEV9 build pack  

---

## 1. What This Is

The OneVo IDE Extension is a VS Code extension that turns every developer's editor into a full OneVo terminal. It gives developers access to the entire ONEVO platform without leaving their editor — chat, tasks, sprints, time logging, HR actions, and more.

This spec covers:
- The `@` tag picker — a searchable, permission-filtered action launcher in chat
- Full WMS tag engine — all Work Management actions via `@entity:action` syntax
- HR automation tags — gated by tenant `active_modules`, filtered by user permissions
- NLP via Semantic Kernel — natural language maps to tag actions with confirmation
- Chat integration — same channels/messages as the web app, real-time via SignalR
- Context engine — branch→task linking, file context, time tracking
- Agent entitlement — monitoring agent install flow

**Reference:** `modules/ide-extension/overview.md` — module spec (architecture, DB tables, API endpoints, SignalR hub). This doc is the ADE build plan — it tells the ADE what to build, in what order, with what acceptance criteria.

---

## 2. Tenant Module Check — How It Works

The extension calls `GET /api/v1/ide/entitlements` on startup. The backend derives entitlements from:
- `feature_access_grants.module` — active modules per tenant
- `subscription_plans.features_json` — plan-level gates
- User's `permissions` (tenant-level RBAC) and `workspace_roles` (WMS-level RBAC)

**Extended `IDEEntitlementsDto`:**
```json
{
  "active_modules": ["hr_management", "worksync", "workforce_intelligence"],
  "permitted_tag_actions": ["task:new", "task:view", "task:status", "task:assign", "task:comment", "task:link", "task:move", "sprint:add", "sprint:start", "time:log", "time:start", "time:stop", "leave:request", "leave:view", "leave:cancel", "clockin", "break:start", "break:end", "clockout"],
  "has_monitoring_entitlement": true,
  "workspace_id": "uuid",
  "user_role": "developer"
}
```

**Rules:**
- `active_modules` is resolved server-side — the client never guesses
- The `@` picker is built entirely from `permitted_tag_actions[]` — only actions in this list are shown
- HR section in picker is shown only when `active_modules.includes("hr_management")`
- `permitted_tag_actions[]` is re-fetched on reconnect and cached for the session
- Backend still validates every action on execute (403 if permission changed)

---

## 3. The `@` Tag Picker

### How It Appears

A small `@` button sits in the chat message composer. Clicking it opens a **searchable dropdown picker** above the composer. The picker is grouped by category.

### Picker Structure

```
┌─────────────────────────────────┐
│ 🔍 Search actions or describe…  │
├─────────────────────────────────┤
│ HR AUTOMATION        [tenant]   │  ← only if active_modules includes hr_management
│   🟢 @clockin        start shift (instant)
│   ☕ @break:start    take a break (instant)
│   🔴 @break:end      end break (instant)
│   🔴 @clockout       end shift (instant)
│   📋 @leave:request  apply leave → form
│   📋 @leave:view     view balance
│   📋 @leave:cancel   cancel request → picker
│   💰 @payslip:view   view payslip
│   🗓 @overtime:request → form
│   📊 @timesheet:view
│   📤 @timesheet:submit
│   📅 @shift:view     today/week schedule
│   🏖 @calendar:view  holidays + events
├─────────────────────────────────┤
│ TASKS                           │
│   ✅ @task:new       create task → form
│   👁 @task:view      view task detail
│   🔄 @task:status    update status → picker
│   👤 @task:assign    assign to member → picker
│   💬 @task:comment   add comment → input
│   🔗 @task:link      link branch/doc
│   ➡ @task:move      move to sprint/board
├─────────────────────────────────┤
│ SPRINT                          │
│   ➕ @sprint:add     add task to sprint
│   🚀 @sprint:start   start sprint
│   ✅ @sprint:complete complete sprint
│   👁 @sprint:view    view sprint
├─────────────────────────────────┤
│ TIME                            │
│   ⏱ @time:log       log hours → form
│   ▶️ @time:start     start timer (instant)
│   ⏹ @time:stop      stop + log (instant)
│   👁 @time:view      view time logs
├─────────────────────────────────┤
│ MORE                            │
│   📊 @board:move     move task to column
│   🎯 @okr:checkin    OKR progress update
│   📄 @doc:link       link doc to task
│   📄 @doc:create     create document
│   👁 @review:request request code review
│   🔔 @notify:send    send notification
│   🏗 @project:view   view project
└─────────────────────────────────┘
```

### Picker Behaviour

- Picker is fully searchable — typing filters across all categories
- Typing `@` in the message input also opens the picker (native to the composer)
- Only actions present in `permitted_tag_actions[]` are rendered
- Categories with zero permitted actions are hidden entirely
- Clicking an action either:
  - **Fires instantly** (clockin, break:start, break:end, clockout, time:start, time:stop)
  - **Opens a mini form** inline above the composer (leave:request, task:new, time:log, overtime:request, timesheet:submit)
  - **Inserts the tag** into the message input for the user to complete (all others)

---

## 4. Mini Forms

Mini forms appear inline above the composer when an action requires parameters.

### `@leave:request` Form
Fields: Leave Type (select from tenant leave types), From date, To date, Reason (optional)  
Shows: Remaining balance for selected leave type  
Submit → bot confirmation card in chat → routes to approval workflow

### `@task:new` Form
Fields: Title, Description (optional), Assignee (optional), Sprint (optional, defaults to current), Priority  
Submit → task created → bot card in chat with task link + undo countdown (30s)

### `@time:log` Form
Fields: Hours, Task (defaults to `#task:current` from branch), Description  
Submit → time log created → bot card in chat + undo countdown (30s)

### `@overtime:request` Form
Fields: Date, Hours, Reason  
Submit → routes to manager approval workflow

### `@timesheet:submit` Form
Shows: Current period timesheet summary  
Confirm → submits for approval

### Instant-fire actions (no form)
`@clockin`, `@break:start`, `@break:end`, `@clockout`, `@time:start`, `@time:stop`  
Fire immediately → bot confirmation card appears in chat channel

---

## 5. NLP via Semantic Kernel

### Overview

Every message typed in chat goes through a Semantic Kernel intent detection pipeline **before** sending. If SK detects an actionable intent above the confidence threshold (0.8), a confirmation card appears.

### Flow

```
User types: "log 2 hours on the login bug"
                    ↓
SK pipeline (WorkSync.ChatAI module)
  → Intent: time:log
  → Params: hours=2, task=TASK-123 (resolved from #task:current via branch context)
  → Confidence: 0.92 → above threshold
                    ↓
Confirmation card appears in chat:
  ┌─────────────────────────────────┐
  │ 🧠 OneVo AI detected action     │
  │ @time:log 2h · Fix login bug    │
  │ Sprint 12 · TASK-123            │
  │ [✅ Confirm] [✏️ Edit] [✕ Dismiss] │
  └─────────────────────────────────┘
                    ↓
Confirm → POST /api/v1/ide/tags/execute
Edit    → opens pre-filled mini form
Dismiss → message sends as plain chat text
```

### HR NLP Examples

| User types | SK maps to | Behaviour |
|---|---|---|
| "I want to take leave next week" | `@leave:request` | Opens mini form pre-filled with next week's dates |
| "log me out" / "I'm done for today" | `@clockout` | Instant fire after confirm |
| "I need a break" | `@break:start` | Instant fire after confirm |
| "submit my timesheet" | `@timesheet:submit` | Opens timesheet summary form |
| "request overtime for yesterday" | `@overtime:request` | Opens form pre-filled with yesterday's date |

### Rules
- SK runs **server-side** in `WorkSync.ChatAI` — same module handling `#task` AI detection
- Confidence < 0.8 → message sends as plain text, no card shown
- SK only maps to actions in the user's `permitted_tag_actions[]` — no permission bypass
- SK context: user's active branch, linked task, workspace, tenant modules — all passed to SK pipeline
- All SK-resolved actions execute via the same `POST /api/v1/ide/tags/execute` endpoint

---

## 6. Chat Integration

The chat sidebar in VS Code is the **same chat** as the web app. Same channels, same messages, same real-time. The backend is a single source of truth.

### Architecture

```
Web App Chat (Manager/HR/Lead)          VS Code Chat (Developer)
         │                                        │
         │        HTTPS + SignalR                 │
         └──────────────┬─────────────────────────┘
                        │
              ONEVO Backend (WorkSync.Chat)
              • Channel store
              • Message store
              • SignalR IDEHub
                        │
              Git Activity (W13 Integrations)
              • GitHub webhooks → bot messages
              • Branch/commit events → chat cards
```

### Panels

1. **Chat Panel** — `ChatPanel.ts` + `ChatWebview.ts`
   - Left sidebar: channel list (TreeDataProvider), unread badges
   - Main area: message feed (WebviewPanel) with markdown rendering, reactions, file previews
   - Composer: message input + `@` button + file attach

2. **Tasks Panel** — `TasksPanel.ts`
   - Assigned tasks grouped by sprint/status
   - Click → `TaskDetailWebview.ts`

3. **Notifications Panel** — `NotificationsPanel.ts`
   - Notification feed with unread badges
   - Status bar badge count

### Real-time Events (SignalR `IDEHub`)

| Event | What happens in extension |
|---|---|
| `chat:message` | Appends message to chat feed instantly |
| `task:updated` | Updates task in Tasks panel |
| `notification:new` | Prepends to Notifications panel, updates status bar badge |
| `tag:executed` | Shows bot confirmation card in chat |
| `ai:action_pending` | Shows undo countdown toast |
| `ai:action_finalized` | Dismisses undo toast |
| `ai:action_undone` | Shows "Action undone" in chat |

### Git Activity → Chat (automatic bot messages)

Handled by `W13 WorkSync.Integrations` via GitHub webhooks. Bot messages appear in the relevant task channel automatically:
- Branch created → `🌿 Arun created branch: feature/task-123-fix`
- Commit → `🔨 Committed: "Fix JWT validation"`
- PR opened → `🔀 PR #42 opened by Arun → [Review PR]`
- CI passed → `✅ CI Passed — PR #42`
- CI failed → `❌ CI Failed — PR #42 · [View Logs]`
- PR merged → `🎉 PR #42 merged → Task → Done`
- Branch naming mismatch → `⚠️ Branch mismatch: expected feature/task-123-*`

---

## 7. Context Engine

`BranchDetector.ts` — reads git HEAD ref on branch switch → calls `GET /api/v1/ide/context/branch` → links branch to task via `ide_context_links` table → sets `active_project_id` in session.

`FileContextDetector.ts` — active editor path → `GET /api/v1/ide/context/file` → surfaces linked tasks for the file.

`TimeTracker.ts` — status bar timer. If `.onevo` has `time_tracking: "auto"`, starts automatically when checking out a branch that has a linked task. Manual start/stop via `@time:start` / `@time:stop` tags.

Context variables auto-resolved in tag params:
- `#task:current` → task linked to current branch
- `#sprint:current` → active sprint in `active_project_id`
- `#repo:current` → git remote URL
- `@assign:me` → authenticated user

---

## 8. Agent Entitlement Flow

Only triggered when `has_monitoring_entitlement: true` in entitlements response.

The IDE extension login does not replace TrayApp enrollment. IDE login creates a user/editor session; TrayApp enrollment creates the Windows device session and receives a separate device credential from Agent Gateway. If the browser SSO session is already active, the TrayApp step may only require confirmation, but the extension JWT must never be reused as the agent credential.

1. Extension shows a non-intrusive prompt: "Your organisation uses productivity monitoring. Set up the OneVo agent?"
2. User clicks "Set Up" → `POST /api/v1/ide/agent-install/request`
3. Backend validates entitlement server-side, creates `agent_install_jobs` record
4. `AgentInstaller.ts` downloads agent binary, verifies SHA256 hash, executes installer
5. Extension polls `GET /api/v1/ide/agent-install/status/{id}` until complete
6. On completion calls `PUT /api/v1/ide/agent-install/{id}/installed`
7. **Never silent** — user must explicitly click "Set Up"

---

## 9. DEV9 — Build Tasks for ADE

### Task 1: Foundation
**Week 1**

**Backend:**
- [ ] Extend `GET /api/v1/ide/entitlements` → return `active_modules[]` and `permitted_tag_actions[]` derived from `feature_access_grants` + `subscription_plans.features_json` + user permissions
- [ ] `POST /api/v1/ide/register` — register install, upsert `ide_extension_installs`
- [ ] `POST /api/v1/ide/sessions` / `PUT /api/v1/ide/sessions/{id}/end` — session lifecycle
- [ ] `IDEHub` SignalR hub — connect with JWT, join `user:{userId}` and `workspace:{workspaceId}` groups

**VS Code Extension:**
- [ ] Scaffold extension with `yo code` — TypeScript, ES2022, webpack bundler
- [ ] `AuthService.ts` — PKCE OAuth flow, token storage in `VS Code SecretStorage`
- [ ] `TokenRefresher.ts` — background refresh 60s before expiry
- [ ] `IDEHubClient.ts` — SignalR JS client, reconnect logic, group subscriptions
- [ ] `WorkspaceConfig.ts` — read `.onevo` config file from repo root
- [ ] `OneVoApiClient.ts` — typed HTTP client for all backend endpoints
- [ ] On activate: check token → auto-login or show login WebView → call `/ide/register` → call `/ide/entitlements` → cache result → start session
- [ ] `extension.ts` — register all viewContainers, commands, contribute activity bar icon

**Acceptance Criteria:**
- Extension activates silently if token exists — no login prompt shown
- Extension shows login WebView if no token, completes PKCE flow, stores token
- `permitted_tag_actions[]` and `active_modules[]` cached in memory for the session
- SignalR connects within 500ms of activation
- Total startup time < 1.5 seconds

---

### Task 2: Chat Panel
**Week 2**

**Backend:**
- [ ] `GET /api/v1/chat/channels` — return channels the user is a member of (name, type, unread_count, last_message)
- [ ] `GET /api/v1/chat/messages?channel_id=X&limit=50` — paginated messages with sender, avatar, content, time, read_receipts
- [ ] `POST /api/v1/chat/messages` — send message, returns message_id + sent status
- [ ] `PATCH /api/v1/chat/messages/{id}/read` — mark read
- [ ] `IDEHub` — push `chat:message` event to `channel:{channelId}` group on new message

**VS Code Extension:**
- [ ] `ChatPanel.ts` — `TreeDataProvider` for channel list with unread badges
- [ ] `ChatWebview.ts` — WebviewPanel for message feed: markdown rendering, sender avatars, timestamps, read receipts, reactions
- [ ] Message composer with `@` button and file attach icon
- [ ] On channel click → load messages → mark channel as read
- [ ] `chat:message` SignalR event → append message to feed instantly (< 100ms)
- [ ] Typing indicator via `chat:typing` outbound SignalR event

**Acceptance Criteria:**
- Channel list loads on sidebar open
- Messages load on channel click
- New message from anyone appears in < 100ms via SignalR — no refresh needed
- Sending a message from VS Code appears in the web app chat instantly
- Unread badge on channel decrements when channel is opened

---

### Task 3: `@` Tag Picker + Full WMS Tag Engine
**Week 3**

**Backend:**
- [ ] `POST /api/v1/ide/tags/execute` — parse `raw_tag_input`, permission check, execute action, return `tag:executed` SignalR event with undo window
- [ ] `DELETE /api/v1/ide/tags/executions/{id}` — undo within `undo_expires_at`
- [ ] Log every execution (including denied) in `ide_tag_executions` table
- [ ] All WMS tag actions route through existing module endpoints — no duplicate logic

**VS Code Extension:**
- [ ] `TagParser.ts` — lexer + parser for `@entity:action params #named:value @mention` syntax
- [ ] `TagExecutor.ts` — calls `POST /api/v1/ide/tags/execute`, handles undo countdown toast (30s)
- [ ] `AutoCompleteProvider.ts` — `VS Code CompletionItemProvider`: typing `@` shows picker, filters as user types
- [ ] `CommentScanner.ts` — opt-in (`.onevo` `scan_comments: true`): detect `// @onevo:entity:action` in code comments on file save, offer to execute
- [ ] `@` button in composer opens picker WebView — groups: HR AUTOMATION (gated), TASKS, SPRINT, TIME, MORE
- [ ] Picker built from `permitted_tag_actions[]` — missing actions = hidden categories
- [ ] Instant-fire actions execute without form; form actions open mini form; tag-insert actions put text in composer
- [ ] `tag:executed` SignalR event → bot card appears in chat with action result + undo button
- [ ] Undo toast: countdown timer, [Undo] button, calls `DELETE /api/v1/ide/tags/executions/{id}`

**WMS Tags Supported:**
`@task:new`, `@task:view`, `@task:status`, `@task:assign`, `@task:comment`, `@task:link`, `@task:move`, `@sprint:add`, `@sprint:start`, `@sprint:complete`, `@sprint:view`, `@time:log`, `@time:start`, `@time:stop`, `@time:view`, `@board:move`, `@board:view`, `@okr:checkin`, `@okr:view`, `@doc:link`, `@doc:create`, `@doc:view`, `@review:request`, `@review:approve`, `@review:reject`, `@notify:send`, `@project:view`, `@project:members`, `@chat:send`, `@chat:pin`, `@chat:remind`

**Acceptance Criteria:**
- Typing `@` in composer opens picker; typing filters results
- Every tag in `permitted_tag_actions[]` appears in picker; others are absent
- Instant-fire tag executes and bot card appears in chat within 200ms
- Undo window works — clicking Undo within 30s reverses the action
- Denied actions show inline red error: "You don't have `{permission}`"
- Every execution (allowed or denied) creates `ide_tag_executions` row

---

### Task 4: HR Automation
**Week 4**

**Backend:**
- [ ] HR tag actions route through existing module endpoints:
  - `@clockin` → `POST /api/v1/workforce/sessions/start` (WorkforcePresence)
  - `@break:start` → `POST /api/v1/workforce/breaks/start`
  - `@break:end` → `PATCH /api/v1/workforce/breaks/{id}/end`
  - `@clockout` → `POST /api/v1/workforce/sessions/end`
  - `@overtime:request` → `POST /api/v1/workforce/overtime/request`
  - `@leave:request` → `POST /api/v1/leave/requests`
  - `@leave:view` → `GET /api/v1/leave/balance/me`
  - `@leave:cancel` → `DELETE /api/v1/leave/requests/{id}`
  - `@payslip:view` → `GET /api/v1/payroll/payslips/latest`
  - `@timesheet:view` → `GET /api/v1/timesheets/current`
  - `@timesheet:submit` → `POST /api/v1/timesheets/submit`
  - `@shift:view` → `GET /api/v1/presence/shifts/me`
  - `@calendar:view` → `GET /api/v1/calendar/events?scope=company`
- [ ] All HR tag actions are included in `permitted_tag_actions[]` only if user has the relevant HR permission

**VS Code Extension:**
- [ ] On entitlements load: if `active_modules.includes("hr_management")` → show HR AUTOMATION section in picker
- [ ] If HR not in `active_modules` → HR section hidden entirely, no hint shown
- [ ] Instant-fire HR tags: `@clockin`, `@break:start`, `@break:end`, `@clockout` — execute immediately, bot card in chat
- [ ] Mini form for `@leave:request`: Leave Type (from `GET /api/v1/leave/types`), From, To, Reason. Shows balance.
- [ ] Mini form for `@overtime:request`: Date, Hours, Reason
- [ ] Mini form for `@timesheet:submit`: Shows period summary, confirm to submit
- [ ] View tags (`@leave:view`, `@payslip:view`, `@timesheet:view`, `@shift:view`, `@calendar:view`) → open detail in WebviewPanel

**Acceptance Criteria:**
- HR section visible in picker when `active_modules` includes `hr_management`; absent otherwise
- HR section absent for tenants without HR — no empty group shown
- `@clockin` fires and bot card shows in chat: "Arun clocked in at 09:02 AM"
- `@leave:request` form shows remaining balance for selected leave type
- Submitting leave request creates approval workflow, bot card shows in chat: "Leave request submitted · Pending approval"
- HR actions not in `permitted_tag_actions[]` are not shown in picker

---

### Task 5: NLP via Semantic Kernel
**Week 5**

**Backend (`WorkSync.ChatAI` module):**
- [ ] Add SK intent detection pipeline — runs on every `POST /api/v1/chat/messages` before message is stored
- [ ] SK receives: message text + user context (permitted_tag_actions[], active_modules[], branch context, active task)
- [ ] SK maps intent to tag action if confidence ≥ 0.8
- [ ] If intent detected: do not store message yet — return `ai.suggestion` event via SignalR with parsed action + params
- [ ] If intent not detected (confidence < 0.8): store message normally, return message to chat
- [ ] SK only maps to actions in `permitted_tag_actions[]` — cannot suggest actions user cannot do
- [ ] On Confirm: call `POST /api/v1/ide/tags/execute` with resolved params; store message as chat record
- [ ] On Dismiss: store message as plain chat text
- [ ] On Edit: return parsed params to client → client opens pre-filled mini form

**VS Code Extension:**
- [ ] `ai.suggestion` SignalR event → show confirmation card in chat feed: action name, parsed params, [Confirm] [Edit] [Dismiss]
- [ ] [Confirm] → call confirm endpoint, bot card replaces suggestion card
- [ ] [Edit] → open pre-filled mini form (same form as manual tag)
- [ ] [Dismiss] → suggestion card removed, message stored as plain text

**HR NLP Mappings:**
- "clock in" / "start work" / "I'm in" → `@clockin`
- "take a break" / "going for lunch" → `@break:start`
- "back from break" → `@break:end`
- "clock out" / "done for today" / "logging off" → `@clockout`
- "take leave" / "apply for leave" / "I need {N} days off" → `@leave:request`
- "submit timesheet" → `@timesheet:submit`
- "request overtime" → `@overtime:request`

**Acceptance Criteria:**
- "log 2 hours on the login bug" → suggestion card with `@time:log 2h TASK-123` within 500ms
- "I want to take leave next week" → suggestion card → Edit opens leave form pre-filled with next week dates
- Low-confidence message (< 0.8) sends as normal chat with no card
- SK cannot suggest actions not in `permitted_tag_actions[]`
- Confirm → action executes, bot card in chat

---

### Task 6: Context Engine
**Week 6**

**Backend:**
- [ ] `GET /api/v1/ide/context/branch?repo={url}&branch={name}` — return linked tasks from `ide_context_links`
- [ ] `GET /api/v1/ide/context/file?repo={url}&path={path}` — return linked tasks for file
- [ ] `POST /api/v1/ide/context/links` — create branch/file→task link
- [ ] `PUT /api/v1/ide/sessions/{id}/context` — update `active_project_id` in session on branch switch
- [ ] `POST /api/v1/ide/time/start` / `POST /api/v1/ide/time/stop` — branch-linked time tracking

**VS Code Extension:**
- [ ] `BranchDetector.ts` — watch `git HEAD` via VS Code git extension API; on branch change → call `/ide/context/branch` → update `#task:current` context variable
- [ ] `FileContextDetector.ts` — watch `onDidChangeActiveTextEditor` → call `/ide/context/file` → surface linked task in status bar tooltip
- [ ] `TimeTracker.ts` — status bar timer. If `.onevo` `time_tracking: "auto"` → auto-start timer when branch with linked task is checked out. Manual start/stop via `@time:start`/`@time:stop` tags.
- [ ] Branch naming check: if `.onevo` `branch_naming` is set → warn in chat if current branch doesn't match pattern
- [ ] Commit message template: if `.onevo` `commit_template: true` → inject `[TASK-123]` into git commit message template

**Acceptance Criteria:**
- Checking out `feature/task-123-fix` → `#task:current` resolves to TASK-123 within 1 second
- `@time:log` with no explicit task → auto-fills TASK-123 from context
- Auto time tracking starts when branch with linked task is checked out (if `time_tracking: auto`)
- Branch naming mismatch → warning bot card appears in chat channel
- File context surfaces linked task in status bar

---

### Task 7: Agent Entitlement
**Week 7**

**Backend:**
- [ ] `GET /api/v1/ide/entitlements` → `has_monitoring_entitlement: true` when `agent_install_entitlements` record exists for tenant
- [ ] `POST /api/v1/ide/agent-install/request` — validate entitlement server-side, create `agent_install_jobs` record, return job ID + download URL + SHA256 hash
- [ ] `GET /api/v1/ide/agent-install/status/{id}` — return job status (pending/downloading/installing/installed/failed)
- [ ] `PUT /api/v1/ide/agent-install/{id}/installed` — mark installed (called by installer on success)

**VS Code Extension:**
- [ ] `AgentInstaller.ts` — entitlement check, non-intrusive prompt ("Set Up" / "Not Now" / "Never ask again")
- [ ] Download agent binary to temp dir, verify SHA256 hash matches response
- [ ] Execute installer with user consent — never silent
- [ ] Poll `GET /api/v1/ide/agent-install/status/{id}` until `installed` or `failed`
- [ ] On success → show "OneVo monitoring agent installed" notification
- [ ] On failure → show error + link to manual install docs

**Acceptance Criteria:**
- Prompt never appears if `has_monitoring_entitlement: false`
- User must click "Set Up" — no background install
- Download fails SHA256 check → abort and show error
- Install completes → backend job status = `installed`
- "Never ask again" suppresses future prompts permanently

---

## 10. Backend Additions Summary

| Change | Module | Notes |
|---|---|---|
| Extend `IDEEntitlementsDto` | IDEExtension | Add `active_modules[]`, `permitted_tag_actions[]` |
| SK intent pipeline | WorkSync.ChatAI | On every message send, before storage |
| HR tag routing | IDEExtension tag executor | Routes to WorkforcePresence + Leave endpoints |
| `GET /api/v1/leave/types` | Leave | Return tenant leave types for form dropdown |
| `GET /api/v1/leave/balance/me` | Leave | Return balance per type for user |

---

## 11. VS Code Extension File Structure

```
src/
├── extension.ts                    # Activate/deactivate, register commands, viewContainers
├── auth/
│   ├── AuthService.ts              # PKCE OAuth, SecretStorage token management
│   └── TokenRefresher.ts           # Background refresh 60s before expiry
├── signalr/
│   └── IDEHubClient.ts             # SignalR client, reconnect, group subscriptions
├── panels/
│   ├── ChatPanel.ts                # TreeDataProvider for channel list
│   ├── TasksPanel.ts               # TreeDataProvider for assigned tasks
│   └── NotificationsPanel.ts       # TreeDataProvider for notifications
├── tag-engine/
│   ├── TagParser.ts                # Lexer + parser for @entity:action syntax
│   ├── TagExecutor.ts              # POST /api/v1/ide/tags/execute + undo handling
│   ├── TagPickerWebview.ts         # @ picker UI — grouped, searchable, permission-filtered
│   ├── AutoCompleteProvider.ts     # VS Code CompletionItemProvider
│   └── CommentScanner.ts           # Opt-in: detect @onevo: tags in code comments
├── hr/
│   ├── HrTagHandler.ts             # Routes HR tags to correct endpoints
│   ├── LeaveFormWebview.ts         # @leave:request mini form
│   ├── OvertimeFormWebview.ts      # @overtime:request mini form
│   └── TimesheetWebview.ts         # @timesheet:view / submit WebView
├── nlp/
│   └── NlpSuggestionHandler.ts     # Handles ai.suggestion SignalR events, confirmation card
├── context/
│   ├── BranchDetector.ts           # Git HEAD watcher → branch context
│   ├── FileContextDetector.ts      # Active editor → file context
│   └── TimeTracker.ts              # Status bar timer, auto-start/stop
├── webviews/
│   ├── ChatWebview.ts              # Rich chat renderer (markdown, reactions, files)
│   ├── TaskDetailWebview.ts        # Full task detail
│   └── MiniFormWebview.ts          # Reusable mini form host
├── agent-install/
│   └── AgentInstaller.ts           # Entitlement check, download, hash verify, install
├── api/
│   └── OneVoApiClient.ts           # Typed HTTP client for all endpoints
└── config/
    └── WorkspaceConfig.ts          # Reads .onevo config file
```

---

## 12. Key Business Rules (ADE Must Follow)

1. **Permission is always server-side.** `permitted_tag_actions[]` tells the client what to show. Backend validates on every execute. 403 = inline error in extension.
2. **HR section only when `active_modules` includes `hr_management`.** No HR UI for non-HR tenants — not even a hint.
3. **Instant-fire HR actions have no undo window.** Clock-in/out/break fire immediately. No countdown. This is intentional — they reflect real-world time events.
4. **SK confidence threshold is 0.8.** Below threshold = plain chat message, no suggestion card shown.
5. **Agent install is never silent.** Always requires explicit user action. Entitlement is validated server-side on every install request.
6. **Undo window is server-enforced.** Backend rejects undo after `undo_expires_at`. Client countdown is UI convenience only.
7. **Every tag execution is audit-logged.** `ide_tag_executions` row created for every attempt, allowed or denied.
8. **JetBrains plugin is Phase 2.** All backend APIs are editor-agnostic. Phase 1 ships VS Code only.
9. **Extension reads code context, not code content.** Branch name, file path, git remote — not keystrokes, file content, or terminal commands.

---

*OneVo IDE Extension — Design Spec v1.0 · 2026-04-30*
