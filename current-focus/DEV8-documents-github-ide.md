# Task: Documents + Wiki + GitHub Integration + IDE Context Engine + Agent Entitlement

**Assignee:** Dev 8
**Pillar:** Pillar 3 — WorkSync + IDE Extension
**Priority:** Critical
**Dependencies:** DEV1 Infrastructure (file_assets, documents base table), DEV5 Projects, DEV6 Tasks, DEV4 Agent Gateway (agent_install_entitlements, registered_agents)

---

## Task 1: Documents (WorkSync Scope) + Wiki + Task-Document Links

**Module:** `ONEVO.Modules.WorkSync.Collaboration`
**Tables:** `documents` (extend existing), `document_versions`, `document_approvals`, `wiki_pages`, `task_documents`
**Depends on:** DEV1 Infrastructure (documents base table + file_assets), DEV6 Tasks

### Acceptance Criteria

- [ ] Extend `documents` table: add `workspace_id → workspaces nullable`, `project_id → projects nullable`, `document_scope` (company/legal_entity/employee/workspace/project), `locked_at timestamptz nullable`, `locked_by → users nullable`, `approved_version_id → document_versions nullable`. Update `status` enum to include `approved` (full set: draft/in_review/approved/published/archived).
- [ ] `document_versions` table: id, document_id → documents, version_number int, content_snapshot text (or storage key), created_by → users, created_at
- [ ] `document_approvals` table: id, document_id → documents, requested_by → users, approver_id → users, status (pending/approved/rejected), comment text nullable, decided_at nullable
- [ ] `wiki_pages` table: id, project_id → projects, parent_page_id → wiki_pages nullable, title, content text, author_id → users, version_number int, created_at, updated_at
- [ ] `task_documents` table: id, task_id → tasks, document_id → documents, linked_by → users, linked_at. UNIQUE (task_id, document_id)
- [ ] When a document approval is approved: set `documents.status = approved`, `locked_at = now()`, `locked_by = approver_id`, `approved_version_id = latest version id`. Locked documents cannot be edited until unlocked by an admin.
- [ ] `POST /api/v1/documents/{id}/versions` — save new version (creates `document_versions` row)
- [ ] `POST /api/v1/documents/{id}/approval-requests` — request approval (requires document in in_review status)
- [ ] `PUT /api/v1/documents/approvals/{id}` — approve or reject (requires `documents:approve` permission)
- [ ] `POST /api/v1/tasks/{id}/documents` — link document to task
- [ ] `GET /api/v1/tasks/{id}/documents` — list documents linked to a task
- [ ] `GET /api/v1/projects/{id}/wiki` — wiki page tree
- [ ] `PUT /api/v1/wiki/{id}` — update wiki page (auto-increments `version_number`, snapshots previous version in a separate `wiki_page_versions` table — optional Phase 1 if time allows)
- [ ] Domain event: `DocumentApprovedEvent` → Notifications (notify document owner)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 12 Documents, Section 35 WMS Collaboration
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
- [[modules/work-management/collaboration|WMS Collaboration spec]]

---

## Task 2: GitHub/GitLab Integration

**Module:** `ONEVO.Modules.WorkSync.Integrations`
**Tables:** `repositories`, `task_repository_links`, `code_activity_events`
**Depends on:** DEV5 Projects (project_id FK), DEV6 Tasks

### Acceptance Criteria

- [ ] `repositories` table: id, workspace_id → workspaces, provider (github/gitlab/bitbucket), full_name varchar(255), url varchar(500), default_branch varchar(100), auth_provider_id → auth_providers nullable (OAuth connection), webhook_secret varchar(255) nullable, is_active boolean, created_at
- [ ] `task_repository_links` table: id, task_id → tasks, repository_id → repositories, linked_by → users, linked_at. UNIQUE (task_id, repository_id)
- [ ] `code_activity_events` table: id, user_id → users, tenant_id → tenants, repository_id → repositories nullable, event_type (commit/push/pr_opened/pr_merged/pr_closed/branch_created/review_submitted/ci_started/ci_completed), branch_name varchar nullable, task_id → tasks nullable, event_metadata jsonb, occurred_at, source (ide_extension/github_webhook/gitlab_webhook)
- [ ] GitHub OAuth flow: `GET /api/v1/integrations/github/connect` → redirect to GitHub OAuth. On callback → store in `auth_providers` table + create `integration_connections` row.
- [ ] `POST /api/v1/tasks/{id}/repositories` — link repo to task (requires GitHub connected)
- [ ] `GET /api/v1/tasks/{id}/repositories` — list linked repos with recent activity
- [ ] Webhook endpoint: `POST /api/v1/webhooks/github` — validate HMAC signature via webhook_secret → parse event type → create `code_activity_events` row → extract task refs from commit messages/PR descriptions → auto-link to tasks
- [ ] Task ref detection in commit messages: patterns `#TASK-123`, `closes #TASK-123`, `fixes #TASK-123` → auto-populate `code_activity_events.task_id`
- [ ] `GET /api/v1/workspaces/{id}/code-activity` — paginated code activity feed filtered by workspace repos
- [ ] Branch naming convention warning: if branch name doesn't match `{task-id}-{slug}` pattern, log a warning in `code_activity_events.event_metadata`

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 38 WMS Integration & API
- [[database/schemas/wms-integrations|WMS Integrations Schema]]
- [[OneVo_WorkSync_final|WorkSync Spec]] — Section 4.4 GitHub Repository Linking, 5.5 IDE Extension Monitoring

---

## Task 3: Commit Records + PR Records + CI Pipeline + Automation Rules

**Module:** `ONEVO.Modules.WorkSync.Integrations` (same)
**Tables:** `commit_records`, `pull_request_records`, `ci_pipeline_runs`, `task_automation_rules`
**Depends on:** Task 2 (repositories, code_activity_events)

### Acceptance Criteria

- [ ] `commit_records` table: id, repository_id → repositories, sha varchar(40) UNIQUE, author_user_id → users nullable, message text, task_ids uuid[] (array of extracted task IDs), committed_at, pushed_at nullable
- [ ] `pull_request_records` table: id, repository_id → repositories, external_pr_id varchar(50), title varchar(500), url varchar(500), status (open/merged/closed), author_user_id → users nullable, task_ids uuid[], opened_at, merged_at nullable, closed_at nullable
- [ ] `ci_pipeline_runs` table: id, repository_id → repositories, external_run_id varchar(100), branch_name varchar(255), status (pending/running/success/failed/cancelled), task_ids uuid[], started_at, finished_at nullable
- [ ] `task_automation_rules` table: id, workspace_id → workspaces, rule_name varchar(100), trigger_type (commit_pushed/pr_opened/pr_merged/branch_created/ci_success/ci_failed), condition_json jsonb, action_type (update_task_status/assign_task/add_label/log_time/post_chat_message), action_params jsonb, is_active boolean, created_by → users, created_at
- [ ] Webhook handler (from Task 2) processes: push → creates `commit_records`; PR event → creates/updates `pull_request_records`; CI event → creates/updates `ci_pipeline_runs`
- [ ] Automation rule engine (Hangfire): after each webhook event, evaluate active `task_automation_rules` for the workspace. If trigger matches condition, execute action. Example: `pr_merged` → find linked tasks → set status to `done`.
- [ ] `POST /api/v1/workspaces/{id}/automation-rules` — create rule
- [ ] `GET /api/v1/tasks/{id}/code-activity` — all commits, PRs, CI runs linked to this task
- [ ] CI status shown on task: latest `ci_pipeline_runs.status` for branches linked to the task

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 38 WMS Integration & API
- [[database/schemas/wms-integrations|WMS Integrations Schema]]

---

## Task 4: IDE Extension Context Engine (Week 5)

**Module:** `ONEVO.Modules.IDEExtension` (backend) + VS Code Extension (TypeScript)
**Tables:** `ide_extension_installs`, `ide_sessions`, `ide_context_links`
**Depends on:** DEV7 Task 4 (IDE Extension Core — sessions, auth), DEV2 (repositories linked to tasks)

### Acceptance Criteria — Backend

- [ ] `ide_context_links` table: id, user_id → users, tenant_id → tenants, repository_url varchar(500), branch_name varchar(255), file_path varchar(1000) nullable, entity_type (task/project/sprint/document), entity_id uuid, link_type (branch/commit/file/pr), created_at, created_by → users
- [ ] `GET /api/v1/ide/context/branch?branch={name}&repo={url}` — return linked tasks and sprint for this branch. Looks up `task_repository_links` and `commit_records.task_ids` for the repo + branch.
- [ ] `GET /api/v1/ide/context/file?path={filePath}&repo={url}` — return tasks referencing this file path (via `code_activity_events.event_metadata` or `ide_context_links`)
- [ ] `POST /api/v1/ide/context/links` — create a context link (user manually links branch/file to task)
- [ ] `GET /api/v1/ide/tasks/assigned` — tasks assigned to current user in active workspace, ordered by sprint then priority. Used by tasks sidebar panel.
- [ ] `POST /api/v1/ide/time/start` — start a time tracking session linked to a task (creates a `time_logs` row with `logged_minutes = 0`, sets a server-side start_time in Redis)
- [ ] `POST /api/v1/ide/time/stop` — stop time tracking, calculate elapsed, update `time_logs.logged_minutes`

### Acceptance Criteria — VS Code Extension

- [ ] On branch switch (git event): call `GET /api/v1/ide/context/branch?branch=...` → if linked tasks found, show status bar notification "Task: TASK-456 — Fix OAuth redirect" with quick actions (View, Log Time)
- [ ] On file open: call `GET /api/v1/ide/context/file?path=...` → if related tasks found, show CodeLens above first function in file: "Related: TASK-456" → click to open task detail webview
- [ ] Time tracker in status bar: show "⏱ 00:23:14 — TASK-456". Click → stop/pause quick-pick.
- [ ] Task detail webview: `onevo.task.open` command → opens a VS Code WebView panel rendering the full task detail (title, description, status, assignees, comments, linked repos, CI status)
- [ ] When creating a new Git branch, suggest branch name format: `{TASK-ID}-{slug}` based on current task context

### Backend References
- [[modules/ide-extension/overview|IDE Extension spec]]
- [[database/schemas/ide-extension|IDE Extension Schema]]

---

## Task 5: IDE Extension Agent Entitlement Flow (Week 6)

**Module:** `ONEVO.Modules.IDEExtension` (entitlement) + `ONEVO.Modules.AgentGateway` (install jobs)
**Tables:** `agent_install_entitlements`, `agent_install_jobs` (owned by DEV4 Agent Gateway — DEV8 consumes)
**Depends on:** DEV4 Shared Platform + Agent Gateway (agent_install_entitlements, agent_install_jobs tables must exist), DEV7 Task 4 (IDE extension installs, sessions)

### Acceptance Criteria — Backend

- [ ] `GET /api/v1/ide/entitlements` — return `{ has_monitoring_entitlement: bool, has_worksync: bool, monitoring_agent_installed: bool, workspace_id: uuid? }`. Checks `agent_install_entitlements` for user/tenant. Checks `registered_agents` for existing install.
- [ ] `POST /api/v1/ide/agent-install/request` — create `agent_install_jobs` record for this user. Body: `{ device_fingerprint: string, install_trigger: "ide_extension" }`. Returns `{ job_id, installer_download_url, installer_hash }`. Only allowed if `has_monitoring_entitlement = true` (backend validates — never trust client claim).
- [ ] `GET /api/v1/ide/agent-install/status/{jobId}` — return current `agent_install_jobs.status` (pending/provisioned/installed/failed). Polled by extension.
- [ ] `PUT /api/v1/ide/agent-install/{jobId}/installed` — called by the agent installer after successful install to transition status to `installed` and register the device via Agent Gateway's normal registration flow.
- [ ] Audit log: every entitlement check and install request is logged in `audit_logs` with full context.

### Acceptance Criteria — VS Code Extension

- [ ] On extension connect (after auth): call `GET /api/v1/ide/entitlements`
- [ ] If `has_monitoring_entitlement = true` AND `monitoring_agent_installed = false` → show VS Code information message: "Desktop monitoring is available for your account. Set it up now?" with buttons [Set Up] [Not Now] [Don't Ask Again]
- [ ] If "Not Now": dismiss, re-prompt next session
- [ ] If "Don't Ask Again": store flag in VS Code globalState, never prompt again
- [ ] If "Set Up": call `POST /api/v1/ide/agent-install/request`. Show progress notification "Downloading OneVo desktop agent...". Download installer from returned URL. Verify SHA-256 hash before executing.
- [ ] Execute installer as a detached process (not inline). Show "Installation in progress — check your taskbar"
- [ ] Poll `GET /api/v1/ide/agent-install/status/{jobId}` every 5 seconds (max 3 minutes). On `installed`: show "Desktop monitoring active" success notification. On `failed`: show error with support link.
- [ ] If `has_monitoring_entitlement = false`: never prompt, never install. No silent background check.
- [ ] Extension NEVER bypasses the backend entitlement check. Entitlement is checked server-side on every install request.

### Backend References
- [[modules/agent-gateway/overview|Agent Gateway spec]]
- [[modules/ide-extension/overview|IDE Extension spec]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[Userflow/Work-Management/ide-extension-agent-install|IDE Agent Install Flow]]

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workspaces/[id]/
├── docs/
│   ├── page.tsx                   # Document list (workspace/project scope)
│   └── [docId]/
│       ├── page.tsx               # Document editor + approval toolbar
│       └── history/page.tsx       # Version history
├── wiki/
│   ├── page.tsx                   # Wiki home (page tree sidebar + content area)
│   └── [pageId]/
│       ├── page.tsx               # Wiki page view
│       └── edit/page.tsx          # Wiki page editor
├── integrations/
│   ├── page.tsx                   # Integration list (GitHub, GitLab, Slack, etc.)
│   └── github/
│       └── page.tsx               # GitHub settings: connected repos, webhook status
└── automation/
    └── page.tsx                   # Automation rules list + rule builder
```

### Key Userflows
- [[Userflow/Work-Management/document-approval|Document Approval Flow]]
- [[Userflow/Work-Management/github-integration|GitHub Integration]]
- [[Userflow/Work-Management/automation-rules|Automation Rules]]
- [[Userflow/Work-Management/ide-extension-agent-install|IDE Agent Install Flow]]
