# ADE Reading Flow: Dev 7 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 7. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 7's
5 tasks across Chat, Chat AI, My Space/Reminders, IDE Extension Core, and IDE Tag Engine.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ADE-START-HERE.md                   ← Platform overview, tag technology spec, IDE Extension
2. current-focus/README.md             ← Task assignment table: Dev 7 has 5 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | Module | Key Tables |
|:-------|:-------|:-----------|
| 1 | Chat & Messaging | channels, channel_members, messages, reactions, pins |
| 2 | Chat AI | premium_ai_detections, ai_action_jobs (undo state machine) |
| 3 | My Space + Reminders | personal boards, reminders |
| 4 | IDE Extension Core (Week 5) | ide_extension_installs, ide_sessions, sidebar panels |
| 5 | IDE Tag Engine (Week 6) | ide_tag_executions, @entity:action parser |

**Hard dependency:** DEV5 Task 1 (workspaces) must be complete. DEV8 Task 1 (documents) must be done before IDE tag `@doc:*` commands work end-to-end.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**Key concepts DEV7 must absorb:**

- `ai_action_jobs` is the **universal undo state machine** — used by both Chat AI (10s window) and IDE tags (30s window)
- Hangfire scans `status = pending AND undo_expires_at < now()` every 5 seconds to finalize
- Permission checks for IDE tags are always **server-side** — never trust client validation
- SignalR IDEHub events: `task:updated`, `chat:message`, `tag:executed`, `ai:action_pending`, `ai:action_finalized`
- VS Code extension uses PKCE OAuth; JWT stored in SecretStorage
- `ide_tag_executions.id` referenced by `ai_action_jobs.tag_execution_id` — they share the undo lifecycle

---

## Phase 2: Task 1 — Chat & Messaging

**Task file:** `current-focus/DEV7-chat-ai-reminders.md` (Task 1 section)

**Schema files to read:**
```
database/schemas/wms-chat.md               ← channels, channel_members, messages, message_reactions, message_attachments, message_pins
```

**Module overview:**
```
modules/ide-extension/overview.md          ← IDE sidebar chat spec (read the Chat Sidebar Panel section)
```

**Key invariants:**
- DM channels: `channel_type = direct` — exactly 2 members, enforced at application layer
- Messages are soft-deleted: `is_deleted = true`, content NOT wiped (compliance)
- `channel_members.last_read_at` drives unread count calculation
- Thread replies: `messages.parent_message_id` self-FK
- SignalR: `IChannelHub` for real-time delivery; fallback to polling for IDE sidebar

---

## Phase 3: Task 2 — Chat AI

**Task file:** `current-focus/DEV7-chat-ai-reminders.md` (Task 2 section)

**Schema files to read:**
```
database/schemas/wms-chat.md               ← premium_ai_detections, ai_action_jobs
```

**Key invariants:**
- Chat AI only activates when tenant has `premium_ai` feature flag
- Flow: message received → AI detects intent → `premium_ai_detections` row created → `ai_action_jobs` row created with `status = pending`, `undo_expires_at = now() + 10s`
- During undo window: `ai:action_pending` SignalR event fires; user sees countdown toast
- If user clicks Undo: set `ai_action_jobs.status = undone`, `undone_at = now()`
- If window expires: Hangfire finalizes — creates the entity from `action_params`, sets `status = finalized`
- `ai_action_jobs.tag_execution_id` is null for Chat AI (only set for IDE tags)

---

## Phase 4: Task 3 — My Space + Reminders

**Task file:** `current-focus/DEV7-chat-ai-reminders.md` (Task 3 section)

**Schema files to read:**
```
onevo-unified-entity-map.md                ← Section 29 (WMS — My Space), Section 36 (WMS — Reminders)
database/schemas/wms-chat.md               ← chat_reminder_items (two-way chat↔task sync)
```

**Key invariants:**
- Personal boards: `boards.project_id = null`, `boards.user_id` — no workspace project scope
- `chat_reminder_items` two-way sync: when `tasks.status → done`, linked reminder → done (domain event); when reminder → done, linked task status updates (command)
- Reminders are user-scoped, not workspace-scoped

---

## Phase 5: Task 4 — IDE Extension Core (Week 5)

**Task file:** `current-focus/DEV7-chat-ai-reminders.md` (Task 4 section)

**Schema files to read:**
```
database/schemas/ide-extension.md          ← ide_extension_installs, ide_sessions, ide_context_links, ide_chat_threads
modules/ide-extension/overview.md          ← Full spec: sidebar panels, IIDEExtensionService, SignalR IDEHub, PKCE OAuth
```

**Key invariants:**
- PKCE OAuth: IDE extension authenticates via browser-opened auth flow; JWT stored in VS Code SecretStorage
- `ide_extension_installs.device_fingerprint` = OS + hardware hash, not PII, used for dedup only
- `ide_sessions.ended_at = null` means session still open (extension activated but not yet deactivated)
- SignalR IDEHub events to implement: `task:updated`, `chat:message`, `sprint:updated`, `context:detected`
- Sidebar panels: Tasks Panel, Chat Panel, Time Tracker — all read from existing WorkSync APIs

---

## Phase 6: Task 5 — IDE Tag Engine (Week 6)

**Task file:** `current-focus/DEV7-chat-ai-reminders.md` (Task 5 section)

**Schema files to read:**
```
database/schemas/ide-extension.md          ← ide_tag_executions (full schema with undo fields)
modules/ide-extension/overview.md          ← Tag syntax spec: @entity:action params
database/schemas/wms-chat.md               ← ai_action_jobs (shared undo state machine)
```

**Tag syntax reference:**
```
@task:new "Fix login bug" #sprint:current @alice due:tomorrow
@time:log 2h @task:current
@leave:request type:annual start:2026-05-01 end:2026-05-05
@chat:send #general "Deployed v1.2"
@sprint:status
```

**Key invariants:**
- Parser validates syntax → resolve params → server-side permission check → execute or deny
- Permission check uses BOTH workspace role AND HR RBAC permissions (cross-pillar check)
- Reversible actions: set `ide_tag_executions.undo_expires_at = now() + 30s`, create `ai_action_jobs` row
- Undo window is 30 seconds (vs 10s for Chat AI)
- `tag_execution_id` on `ai_action_jobs` links the two records — undo either table, the other follows
- `ai:action_pending` SignalR event triggers IDE toast with countdown; `ai:action_finalized` clears it
- Context variables resolved before execution: `#sprint:current`, `@task:current`, `@repo:current`
