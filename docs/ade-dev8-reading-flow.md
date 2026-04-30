# ADE Reading Flow: Dev 8 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 8. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 8's
5 tasks across Documents/Wiki, GitHub Integration, CI/CD Automation, IDE Context Engine,
and IDE Agent Entitlement.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ADE-START-HERE.md                   ← Platform overview, all 3 pillars, IDE Extension
2. current-focus/README.md             ← Task assignment table: Dev 8 has 5 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | Module | Key Tables |
|:-------|:-------|:-----------|
| 1 | Documents + Wiki + Task Docs | documents (extended), document_versions, document_approvals, wiki_pages, task_documents |
| 2 | GitHub Integration | repositories, task_repository_links, code_activity_events, commit_records, pull_request_records |
| 3 | CI/CD + Automation Rules | ci_pipeline_runs, task_automation_rules |
| 4 | IDE Context Engine (Week 5) | ide_context_links, context detection logic |
| 5 | IDE Agent Entitlement (Week 6) | agent_install_entitlements, agent_install_jobs |

**Hard dependency:** DEV5 Task 1 (workspaces) + DEV5 Task 2 (projects) must be complete. DEV6 Task 1 (tasks) must be done before `task_documents` links work. DEV1 Agent Gateway must be done before Task 5.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**Key concepts DEV8 must absorb:**

- `documents` is a **shared table** — HR Documents module owns `employee_id`/`legal_entity_id` scope; WorkSync Collaboration owns `workspace_id`/`project_id` scope. Do not drop existing HR columns.
- Document approval triggers a lock: `documents.status = approved`, `locked_at`, `locked_by`, `approved_version_id` all set atomically
- Only admins can unlock an approved document
- GitHub webhook events and IDE extension events both write to `code_activity_events` (unified stream)
- IDE context engine detects active branch → maps to task via `ide_context_links` and `task_repository_links`
- Agent entitlement is always server-side: never allow silent install, always check `agent_install_entitlements`

---

## Phase 2: Task 1 — Documents + Wiki + Task Documents

**Task file:** `current-focus/DEV8-documents-github-ide.md` (Task 1 section)

**Schema files to read:**
```
database/schemas/wms-collaboration.md      ← documents (extended), document_versions, document_approvals, wiki_pages, task_documents
database/schemas/documents.md             ← Original HR Documents schema (do not break existing columns)
```

**Key invariants:**
- `documents.status` enum extended: draft / in_review / **approved** / published / archived
- When `document_approvals` status → approved: set `documents.status = approved`, `locked_at = now()`, `locked_by = approver_id`, `approved_version_id = latest version id` — all in one transaction
- Approved documents: only admins can edit (unlock first, then edit, re-approval required)
- `document_versions.version_number` auto-increments per document (not global)
- `wiki_pages.parent_page_id` self-FK — unlimited nesting depth; enforce no cycles
- `task_documents` is for document-editor links only — file attachments use the existing `attachments` table

---

## Phase 3: Task 2 — GitHub Integration

**Task file:** `current-focus/DEV8-documents-github-ide.md` (Task 2 section)

**Schema files to read:**
```
database/schemas/wms-integrations.md       ← repositories, task_repository_links, code_activity_events, commit_records, pull_request_records
```

**Key invariants:**
- Webhook events validated via HMAC using `repositories.webhook_secret`
- `code_activity_events.source` distinguishes webhook vs IDE extension origin
- Task auto-detection from commit message: parse `[TASK-123]` or `#123` patterns → populate `commit_records.task_ids uuid[]`
- `task_repository_links` is the explicit user-created link (different from auto-detected commit references)
- PR merge → `code_activity_events` with `event_type = pr_merged` → can trigger automation rules (Task 3)

---

## Phase 4: Task 3 — CI/CD + Automation Rules

**Task file:** `current-focus/DEV8-documents-github-ide.md` (Task 3 section)

**Schema files to read:**
```
database/schemas/wms-integrations.md       ← ci_pipeline_runs, task_automation_rules
```

**Key invariants:**
- `task_automation_rules` evaluated by Hangfire after each webhook event
- Query: `WHERE workspace_id = ? AND is_active = true AND trigger_type = ?` (index covers this)
- `condition_json` evaluated against event payload: `branch_pattern` glob match, `repo_id` exact match
- `action_type` execution: `update_task_status` → update matching tasks; `post_chat_message` → write to channel
- Rule evaluation is idempotent — same event processed twice should not duplicate actions
- Log all rule evaluations in `audit_logs` with rule_id and action taken

---

## Phase 5: Task 4 — IDE Context Engine (Week 5)

**Task file:** `current-focus/DEV8-documents-github-ide.md` (Task 4 section)

**Schema files to read:**
```
database/schemas/ide-extension.md          ← ide_context_links (branch→task detection)
database/schemas/wms-integrations.md       ← repositories, task_repository_links
modules/ide-extension/overview.md          ← Context Engine section, .onevo config file format
```

**Key invariants:**
- Context detection priority: (1) explicit `ide_context_links` user-created link, (2) `task_repository_links` from repo management, (3) branch name pattern matching
- Index `(repository_url, branch_name)` is the primary lookup — must be present
- `.onevo` config file: per-repo YAML/JSON; controls `scan_comments`, `commit_template`, `branch_naming`, `time_tracking`
- When branch context detected: fire `context:detected` SignalR IDEHub event
- `ide_sessions.active_project_id` updated when context changes (branch switch in editor)

---

## Phase 6: Task 5 — IDE Agent Entitlement (Week 6)

**Task file:** `current-focus/DEV8-documents-github-ide.md` (Task 5 section)

**Schema files to read:**
```
database/schemas/agent-gateway.md          ← agent_install_entitlements, agent_install_jobs, registered_agents
database/schemas/ide-extension.md          ← ide_extension_installs (install_id referenced by agent_install_jobs)
modules/ide-extension/overview.md          ← Agent Entitlement section
```

**Key invariants:**
- Server-side check on every install request: query `agent_install_entitlements` for tenant — if no row or `is_active = false`, reject with 403
- Never silent install: user must explicitly approve in VS Code extension UI after seeing disclosure
- On approval: create `agent_install_jobs` row with `status = pending` — Hangfire picks it up and runs the install flow
- `agent_install_jobs.install_id` → `ide_extension_installs.id` — links the job to the specific IDE install that requested it
- After install: `registered_agents` row created by existing Agent Gateway flow (DEV1 built this)
- Entitlement is tenant-level — if the tenant has it, any user in that tenant can approve
