# User Flow: IDE Context Detection (Branch â†’ Task)

**Module:** IDE Extension â€” Context Engine (Week 5)
**Pillar:** WorkSync (Pillar 3)
**Phase:** Phase 1
**Owner:** Dev 8 (IDE Context Engine)

---

## Overview

When a developer switches branches in VS Code, the context engine automatically detects which ONEVO task (and project) is related to that branch. This powers `@task:current` resolution in the tag engine and auto-starts time tracking if configured.

---

## Detection Priority (Highest â†’ Lowest)

| Priority | Source | Description |
|:---------|:-------|:------------|
| 1 | `ide_context_links` | Explicit user-created link: developer manually mapped this branch to a task in VS Code |
| 2 | `task_repository_links` | Repo management link: PM/developer linked a task to a repo via WorkSync UI |
| 3 | Branch name pattern | Branch name contains task ID: `feature/TASK-123-fix-login` or `TASK-123` |

---

## Flow 1: Branch Switch Detected

```
Developer switches branch in VS Code
        â”‚
        â–¼
Extension: onDidChangeBranch event fires
  payload: { branch_name, repo_url }
        â”‚
        â–¼
POST /api/v1/ide/context/detect
  body: { install_id, branch_name, repo_url }
        â”‚
        â–¼
Server: Context Detection (Priority 1 â€” Explicit Link)
  SELECT * FROM ide_context_links
  WHERE repository_url = ? AND branch_name = ?
        â”‚
        â”œâ”€ Row found â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Context resolved (go to Flow 3)
        â”‚
        â””â”€ No row
                â”‚
                â–¼
        Server: Context Detection (Priority 2 â€” Task Repository Link)
          repositories.id â† WHERE clone_url = repo_url
          task_repository_links â† WHERE repository_id = repos.id
          tasks â† active tasks in that repo
                â”‚
                â”œâ”€ Single match â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Context resolved (go to Flow 3)
                â”‚
                â”œâ”€ Multiple matches
                â”‚       â–¼
                â”‚   Return list to extension
                â”‚   Extension shows "Which task?" picker
                â”‚   Developer selects â†’ Flow 2 (save explicit link)
                â”‚
                â””â”€ No match
                        â”‚
                        â–¼
                Server: Context Detection (Priority 3 â€” Branch Name Pattern)
                  Extract task ID from branch_name:
                    TASK-\d+ or #\d+ patterns
                  Lookup tasks WHERE short_id matches
                        â”‚
                        â”œâ”€ Match found â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Context resolved (go to Flow 3)
                        â”‚
                        â””â”€ No match
                                â”‚
                                â–¼
                        Context = null
                        ide_sessions.active_project_id unchanged
                        Extension shows: "No task context detected"
                        @task:current resolves to null
```

---

## Flow 2: Developer Creates Explicit Context Link

```
Developer right-clicks branch in VS Code â†’ "Link to ONEVO Task"
        â”‚
        â–¼
Extension shows task picker (searches tasks in active workspace)
        â”‚
        â–¼
Developer selects task
        â”‚
        â–¼
POST /api/v1/ide/context/links
  body: { install_id, repository_url, branch_name, task_id }
        â”‚
        â–¼
ide_context_links row upserted:
  - repository_url, branch_name, task_id
  - workspace_id, project_id
  - created_by_id
  Index: (repository_url, branch_name) â€” primary lookup

(Future branch switches on this branch â†’ Priority 1 instant match)
        â”‚
        â–¼
Flow 3: Context Resolved
```

---

## Flow 3: Context Resolved â€” Update Session & Notify IDE

```
Context resolved: task_id known
        â”‚
        â–¼
Server: Update active session
  ide_sessions.active_project_id = task.project_id
  (workspace context already set from install)
        â”‚
        â–¼
SignalR IDEHub event fired: context:detected
  payload: {
    task_id, task_title, task_status,
    project_id, project_name,
    sprint_id (if assigned),
    branch_name
  }
        â”‚
        â–¼
Extension receives context:detected event:
  - Sidebar Tasks Panel: highlights active task
  - Time Tracker Panel: shows "Start tracking [task_title]?"
  - Status bar: shows "@task:current = TASK-123"
        â”‚
        â–¼
If .onevo config has time_tracking: auto
        â”‚
        â”œâ”€ No active timer for user
        â”‚       â–¼
        â”‚   POST /api/v1/time/start (auto-start)
        â”‚   time_logs row created with task_id
        â”‚
        â””â”€ Active timer already running
                â–¼
            Show "Switch timer to [task_title]?" prompt
```

---

## Flow 4: Workspace / Project Scoping

```
Context detection always respects workspace scope:
        â”‚
        â–¼
ide_sessions carries workspace_id (set at auth time from IDE auth claims)
        â”‚
        â–¼
All context lookups filter by:
  - tenant_id (from JWT)
  - workspace_id (from session or X-Workspace-Id header)
        â”‚
        â–¼
task lookup: must belong to workspace's projects
repository lookup: must be linked to workspace
```

---

## Key Invariants

| Rule | Enforcement |
|:-----|:------------|
| Index `(repository_url, branch_name)` on ide_context_links | Migration â€” covering index for primary lookup |
| Priority 1 always wins over branch pattern | Explicit > inferred |
| Multiple matches from Priority 2 â†’ user must choose | Never auto-pick ambiguous context |
| context:detected fires every branch switch (even null result) | Extension handles null gracefully |
| ide_sessions.active_project_id updated on every context change | Server updates before firing SignalR |
| Workspace scope enforced on all context queries | Global query filter |

---

## Tables Involved

- `ide_context_links` â€” explicit branchâ†’task links (Priority 1)
- `task_repository_links` â€” task-to-repo links from WorkSync UI (Priority 2)
- `repositories` â€” repo metadata (clone_url for matching)
- `ide_sessions` â€” active_project_id updated on context change
- `tasks` â€” task lookup for branch pattern match (Priority 3)

---

## Related

- [[Userflow/IDE-Extension/ide-install-flow|IDE Install & Auth Flow]]
- [[Userflow/IDE-Extension/tag-engine-flow|Tag Engine Flow]] â€” uses @task:current from context
- [[modules/ide-extension/overview|IDE Extension Module Overview]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[database/schemas/wms-integrations|WMS Integrations Schema]] â€” repositories, task_repository_links
- [[current-focus/DEV8-documents-github-ide|DEV8 Task 4]] â€” IDE Context Engine implementation

