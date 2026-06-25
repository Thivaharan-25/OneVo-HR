# User Flow: IDE Tag Engine (@entity:action)

**Module:** IDE Extension - Tag Engine (Week 6)
**Pillar:** Cross-Pillar (HR + Work (Phase 2 IDE context))
**Phase:** Phase 2 - deferred
**Owner:** Dev 7 (IDE Tag Engine)

---

## Overview

The tag engine lets developers trigger ONEVO actions directly from code comments or the VS Code command palette using `@entity:action` syntax. Every action is permission-checked server-side, and reversible actions have a 30-second undo window.

---

## Tag Syntax

```
@task:new "Fix login bug" #sprint:current @alice due:tomorrow
@task:update #current status:in-progress
@time:log 2h @task:current
@time:start @task:current
@time-off:request type:annual start:2026-05-01 end:2026-05-05
@chat:send #general "Deployed v1.2"
@sprint:status
@doc:link @task:current doc:123
@board:move @task:current column:in-review
@okr:update kr:456 progress:75
@notify:send @alice @bob "PR ready for review"
```

**Entities:** `task`, `sprint`, `time`, `time_off`, `chat`, `doc`, `board`, `okr`, `notify`, `review`

**Context variables** (resolved before execution):
- `@task:current` -> active task from `ide_context_links` or branch detection
- `#sprint:current` -> active sprint for current project
- `@repo:current` -> repository linked to current workspace

---

## Flow 1: Tag Execution (Happy Path)

```
Developer types @tag:action in comment or command palette
        |
        v
Extension sends POST /api/v1/ide/tags/execute
  payload: { raw_tag, install_id, context: { branch, repo_url, active_task_id } }
        |
        v
Server: Tag Parser
  1. Tokenise raw_tag string
  2. Validate syntax - unknown entity/action -> 400 Bad Request
  3. Resolve context variables
     (@task:current -> look up ide_context_links or branch pattern)
     (#sprint:current -> query active sprint for project)
        |
        +- Parse/resolve error
        |       v
        |   400 returned with structured error
        |   Extension shows inline error in VS Code
        |   STOP
        |
        +- Parsed successfully
                |
                v
        Server: Permission Check (ALWAYS server-side)
        Check BOTH:
          - workspace_member role (Admin/Member/Viewer)
          - HR RBAC permissions (e.g. time_off:request for @time-off:request)
                |
                +- Permission denied
                |       v
                |   403 returned
                |   Extension shows "You don't have permission for @{entity}:{action}"
                |   STOP
                |
                +- Permission granted
                        |
                        v
                ide_tag_executions row created:
                  - parsed_entity, parsed_action, resolved_params_json
                  - executed_by_id, install_id
                  - status = pending
                  - is_reversible = true/false
                        |
                        +- Not reversible ---> Execute immediately
                        |                    Update status = completed
                        |                    Return success to extension
                        |
                        +- Reversible action (30s undo window)
                                |
                                v
                        Flow 2: Undo Window
```

---

## Flow 2: Reversible Action - 30s Undo Window

```
Reversible action detected (e.g. @task:new, @chat:send)
        |
        v
ide_tag_executions:
  - undo_expires_at = now() + 30s
  - undo_snapshot_json = current state before change

ai_action_jobs row created (universal undo state machine):
  - status = pending
  - undo_expires_at = now() + 30s
  - entity_type, action_type, action_params
  - tag_execution_id FK -> ide_tag_executions.id
        |
        v
SignalR IDEHub event fired: ai:action_pending
  payload: { tag_execution_id, action_description, expires_at }
        |
        v
VS Code shows countdown toast:
  "@task:new 'Fix login bug' will execute in 30s [Undo]"
        |
        +- User clicks Undo (within 30s)
        |       |
        |       v
        |   POST /api/v1/ide/tags/{executionId}/undo
        |   ai_action_jobs.status = undone
        |   ai_action_jobs.undone_at = now()
        |   ide_tag_executions.status = undone
        |   SignalR: ai:action_finalized (undone=true)
        |   Toast dismissed - "Action cancelled"
        |
        +- Timer expires (Hangfire polls every 5s)
                |
                v
        Hangfire: WHERE status = pending AND undo_expires_at < now()
                |
                v
        Execute action from action_params
        (create entity, post message, update status, etc.)
                |
                v
        ai_action_jobs.status = finalized
        ide_tag_executions.status = completed
        SignalR: ai:action_finalized (undone=false)
        Toast: "Action completed"
```

---

## Flow 3: Tag in Code Comment (Passive Scanning)

```
Developer saves file with @tag comments (e.g. // @time:log 2h)
        |
        v
Extension scans active document (if scan_comments enabled in .onevo config)
        |
        v
Detected tags shown in VS Code panel: "Pending tags"
        |
        v
Developer reviews - clicks "Execute" per tag
        |
        v
Same as Flow 1 from POST /api/v1/ide/tags/execute
```

---

## .onevo Config File (Per-Repo)

Stored at repo root as `.onevo` (YAML or JSON). Controls extension behaviour for that repository.

```yaml
scan_comments: true          # scan code comments for @tags
commit_template: "[{task_id}] {message}"   # auto-prefix commits
branch_naming: "feature/{task_id}-{slug}"  # branch name suggestion
time_tracking: auto          # auto-start timer when context detected
```

---

## Key Invariants

| Rule | Enforcement |
|:-----|:------------|
| Permission check always server-side | Never validate client-side only |
| Cross-pillar check: workspace role AND HR RBAC | Both must pass |
| Reversible action undo window = 30s (vs Chat AI = 10s) | Server sets undo_expires_at |
| tag_execution_id links ide_tag_executions <-> ai_action_jobs | Undo either table, the other follows |
| Hangfire scans every 5s for expired pending jobs | Background service |
| Context variables resolved before permission check | Parser resolves first |
| Idempotency: duplicate execute request returns existing execution | Check by idempotency key |

---

## Tables Involved

- `ide_tag_executions` - one row per tag fired (parsed, status, undo fields)
- `ai_action_jobs` - universal undo state machine (shared with Chat AI)
- `ide_context_links` - provides `@task:current` resolution
- `ide_sessions` - active session context
- `ide_extension_installs` - install_id for execution attribution

---

## Related

- [[Userflow/IDE-Extension/ide-install-flow|IDE Install & Auth Flow]]
- [[Userflow/IDE-Extension/context-detection-flow|Context Detection Flow]]
- [[modules/ide-extension/overview|IDE Extension Module Overview]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[database/schemas/wms-chat|Chat AI - ai_action_jobs schema]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 5]] - IDE Tag Engine implementation
