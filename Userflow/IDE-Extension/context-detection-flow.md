# User Flow: IDE Context Detection (Branch -> Task)

**Module:** IDE Extension - Context Engine (Week 5)
**Pillar:** WorkSync (Pillar 3)
**Phase:** Phase 1
**Owner:** Dev 8 (IDE Context Engine)

---

## Overview

When a developer switches branches in VS Code, the context engine automatically detects which ONEVO task (and project) is related to that branch. This powers `@task:current` resolution in the tag engine and auto-starts time tracking if configured.

---

## Detection Priority (Highest -> Lowest)

| Priority | Source | Description |
|:---------|:-------|:------------|
| 1 | `ide_context_links` | Explicit user-created link: developer manually mapped this branch to a task in VS Code |
| 2 | `task_repository_links` | Repo management link: PM/developer linked a task to a repo via WorkSync UI |
| 3 | Branch name pattern | Branch name contains task ID: `feature/TASK-123-fix-login` or `TASK-123` |

---

## Flow 1: Branch Switch Detected

```
Developer switches branch in VS Code
        |
        v
Extension: onDidChangeBranch event fires
  payload: { branch_name, repo_url }
        |
        v
POST /api/v1/ide/context/detect
  body: { install_id, branch_name, repo_url }
        |
        v
Server: Context Detection (Priority 1 - Explicit Link)
  SELECT * FROM ide_context_links
  WHERE repository_url = ? AND branch_name = ?
        |
        |- Row found ----------------------------------> Context resolved (go to Flow 3)
        |
        \- No row
                |
                v
        Server: Context Detection (Priority 2 - Task Repository Link)
          repositories.id <- WHERE clone_url = repo_url
          task_repository_links <- WHERE repository_id = repos.id
          tasks <- active tasks in that repo
                |
                |- Single match ----------------------> Context resolved (go to Flow 3)
                |
                |- Multiple matches
                |       v
                |   Return list to extension
                |   Extension shows "Which task?" picker
                |   Developer selects -> Flow 2 (save explicit link)
                |
                \- No match
                        |
                        v
                Server: Context Detection (Priority 3 - Branch Name Pattern)
                  Extract task ID from branch_name:
                    TASK-\d+ or #\d+ patterns
                  Lookup tasks WHERE short_id matches
                        |
                        |- Match found ---------------> Context resolved (go to Flow 3)
                        |
                        \- No match
                                |
                                v
                        Context = null
                        ide_sessions.active_project_id unchanged
                        Extension shows: "No task context detected"
                        @task:current resolves to null
```

---

## Flow 2: Developer Creates Explicit Context Link

```
Developer right-clicks branch in VS Code -> "Link to ONEVO Task"
        |
        v
Extension shows task picker (searches tasks in active workspace)
        |
        v
Developer selects task
        |
        v
POST /api/v1/ide/context/links
  body: { install_id, repository_url, branch_name, task_id }
        |
        v
ide_context_links row upserted:
  - repository_url, branch_name, task_id
  - workspace_id, project_id
  - created_by_id
  Index: (repository_url, branch_name) - primary lookup

(Future branch switches on this branch -> Priority 1 instant match)
        |
        v
Flow 3: Context Resolved
```

---

## Flow 3: Context Resolved - Update Session & Notify IDE

```
Context resolved: task_id known
        |
        v
Server: Update active session
  ide_sessions.active_project_id = task.project_id
  (workspace context already set from install)
        |
        v
SignalR IDEHub event fired: context:detected
  payload: {
    task_id, task_title, task_status,
    project_id, project_name,
    sprint_id (if assigned),
    branch_name
  }
        |
        v
Extension receives context:detected event:
  - Sidebar Tasks Panel: highlights active task
  - Time Tracker Panel: shows "Start tracking [task_title]?"
  - Status bar: shows "@task:current = TASK-123"
        |
        v
If .onevo config has time_tracking: auto
        |
        |- No active timer for user
        |       v
        |   POST /api/v1/time/start (auto-start)
        |   time_logs row created with task_id
        |
        \- Active timer already running
                v
            Show "Switch timer to [task_title]?" prompt
```

---

## Flow 4: Workspace / Project Scoping

```
Context detection always respects workspace scope:
        |
        v
ide_sessions carries workspace_id (set at auth time from IDE auth claims)
        |
        v
All context lookups filter by:
  - tenant_id (from JWT)
  - workspace_id (from session or X-Workspace-Id header)
        |
        v
task lookup: must belong to workspace's projects
repository lookup: must be linked to workspace
```

---

## Key Invariants

| Rule | Enforcement |
|:-----|:------------|
| Index `(repository_url, branch_name)` on ide_context_links | Migration - covering index for primary lookup |
| Priority 1 always wins over branch pattern | Explicit > inferred |
| Multiple matches from Priority 2 -> user must choose | Never auto-pick ambiguous context |
| context:detected fires every branch switch (even null result) | Extension handles null gracefully |
| ide_sessions.active_project_id updated on every context change | Server updates before firing SignalR |
| Workspace scope enforced on all context queries | Global query filter |

---

## Tables Involved

- `ide_context_links` - explicit branch->task links (Priority 1)
- `task_repository_links` - task-to-repo links from WorkSync UI (Priority 2)
- `repositories` - repo metadata (clone_url for matching)
- `ide_sessions` - active_project_id updated on context change
- `tasks` - task lookup for branch pattern match (Priority 3)

---

## Related

- [[Userflow/IDE-Extension/ide-install-flow|IDE Install & Auth Flow]]
- [[Userflow/IDE-Extension/tag-engine-flow|Tag Engine Flow]] - uses @task:current from context
- [[modules/ide-extension/overview|IDE Extension Module Overview]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[database/schemas/wms-integrations|WMS Integrations Schema]] - repositories, task_repository_links
- [[current-focus/DEV8-documents-github-ide|DEV8 Task 4]] - IDE Context Engine implementation

