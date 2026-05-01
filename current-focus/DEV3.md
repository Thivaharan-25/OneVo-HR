# DEV3: Backend WorkSync + IDE APIs

**Track:** Backend
**Primary ownership:** WorkSync backend, projects, tasks, boards, planning, OKR, time, resources, chat, Chat AI, collaboration, integrations, analytics, IDE backend APIs, tag execution
**Current Unfinished Task:** Task 1 - WorkSync foundation
**Blocked By:** DEV1 tenant/auth foundation

---

## ADE Instructions

When Dev 3 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Keep WorkSync inside the main backend and database.

---

## Task 1: WorkSync Foundation + Projects + Resources

**Goal:** create workspace, membership, role, and project foundation for WorkSync.

### Acceptance Criteria

- [ ] Workspaces table and APIs exist.
- [ ] Workspace members and roles exist.
- [ ] Workspace role permissions can be resolved for a user.
- [ ] Projects can be created, listed, updated, archived, and assigned members.
- [ ] Project members, epics, milestones, versions, and repository links are represented.
- [ ] Resource plans, resource allocations, capacity snapshots, and resource rates needed for planning are represented where in scope.
- [ ] Workspace provisioning can be triggered from tenant module activation.
- [ ] Workspace APIs are tenant-scoped.
- [ ] Tests cover workspace membership, role permissions, project CRUD, and tenant isolation.

### References

- [[modules/work-management/foundation/overview|Work Management Foundation]]
- [[modules/work-management/projects/overview|Projects]]
- [[modules/work-management/resources/overview|Resources]]
- [[Userflow/Work-Management/wm-overview|Work Management Overview]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]

### Verification

```bash
dotnet test ONEVO.sln --filter WorkSync
```

---

## Task 2: Tasks + Boards + Planning + OKR + Time

**Goal:** implement task, board, sprint, and roadmap APIs consumed by web app and IDE extension.

### Acceptance Criteria

- [ ] Task create/list/detail/update APIs exist.
- [ ] Task assignments, comments, checklists, labels, and status transitions exist.
- [ ] Boards, columns, and task positions exist.
- [ ] Sprint planning APIs exist for backlog, sprint assignment, start, complete, and burndown snapshots.
- [ ] Roadmap APIs exist.
- [ ] OKR APIs exist for objectives, key results, check-ins, and progress updates.
- [ ] Time management APIs exist for time logs, timers, timesheets, and current period summary.
- [ ] WorkSync time can provide daily logged minutes to the Discrepancy Engine.
- [ ] `GET /api/v1/ide/tasks/assigned` returns tasks for the authenticated developer.
- [ ] Tests cover task lifecycle, board moves, sprint assignment, and IDE assigned-task feed.

### References

- [[modules/work-management/tasks/overview|Tasks]]
- [[modules/work-management/planning/overview|Planning]]
- [[modules/work-management/okr/overview|OKR]]
- [[modules/work-management/time/overview|Time]]
- [[Userflow/Work-Management/task-flow|Task Flow]]
- [[Userflow/Work-Management/planning-flow|Planning Flow]]

### Verification

```bash
dotnet test ONEVO.sln --filter Tasks
dotnet test ONEVO.sln --filter Planning
dotnet test ONEVO.sln --filter OKR
dotnet test ONEVO.sln --filter Time
```

---

## Task 3: Chat + Chat AI

**Goal:** implement WorkSync chat and action suggestion pipeline used by web and IDE.

### Acceptance Criteria

- [ ] Channels, channel members, messages, reactions, and attachments exist.
- [ ] Chat APIs support channel list, message page, send message, and mark read.
- [ ] SignalR publishes `chat:message`, `chat:typing`, and unread update events.
- [ ] AI action job flow supports pending, finalized, and undone states.
- [ ] Chat AI can detect task/action intents and produce undoable action jobs.
- [ ] Chat AI suggestions are filtered by backend permissions and active modules.
- [ ] Undo window is server-enforced.
- [ ] Tests cover message send, realtime event contract, and undo state transitions.

### References

- [[modules/work-management/chat/overview|Chat]]
- [[modules/work-management/chat-ai/overview|Chat AI]]
- [[Userflow/Chat/chat-overview|Chat Overview]]

### Verification

```bash
dotnet test ONEVO.sln --filter Chat
dotnet test ONEVO.sln --filter AiAction
```

---

## Task 4: IDE Backend APIs + Tag Execution

**Goal:** provide backend source of truth for the VS Code extension.

### Acceptance Criteria

- [ ] `POST /api/v1/ide/register` upserts extension install.
- [ ] `POST /api/v1/ide/sessions` starts an IDE session.
- [ ] `PUT /api/v1/ide/sessions/{id}/end` ends an IDE session.
- [ ] `GET /api/v1/ide/entitlements` returns active modules, permitted tag actions, workspace ID, and monitoring entitlement.
- [ ] `POST /api/v1/ide/tags/execute` parses, authorizes, executes, and logs every tag attempt.
- [ ] `DELETE /api/v1/ide/tags/executions/{id}` supports undo when allowed.
- [ ] `GET /api/v1/ide/context/branch` resolves branch-linked tasks.
- [ ] `GET /api/v1/ide/context/file` resolves file-linked tasks.
- [ ] SignalR `IDEHub` sends tag result, task update, chat, and notification events.
- [ ] Tests cover allowed action, denied action, audit row, undo, and entitlement filtering.

### References

- [[modules/ide-extension/overview|IDE Extension Spec]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[backend/real-time|Real-Time Architecture]]

### Verification

```bash
dotnet test ONEVO.sln --filter IDE
```

---

## Task 5: WorkSync Collaboration + Integrations + Analytics

**Goal:** build documents/wiki, Git/code integration, automation, and WorkSync analytics APIs.

### Acceptance Criteria

- [ ] Documents and document versions support workspace/project scope.
- [ ] Document approvals use the Shared Platform workflow engine.
- [ ] Wiki pages support tree structure and versioning.
- [ ] Task-document links exist and enforce uniqueness.
- [ ] Repository records, task repository links, and code activity events exist.
- [ ] GitHub webhook endpoint validates signatures and extracts task refs from commits and PRs.
- [ ] Commit records, pull request records, CI pipeline runs, and task automation rules exist.
- [ ] Automation rules can update task status, assign, add labels, log time, or post chat messages after code events.
- [ ] WorkSync analytics exposes sprint reports, dashboard widgets, saved views, and task throughput/capacity data.
- [ ] Tests cover document version, document approval workflow, wiki update, repo link, webhook signature, task ref extraction, PR/CI record update, automation rule execution, and analytics query.

### References

- [[modules/work-management/collaboration/overview|Collaboration]]
- [[modules/work-management/integrations/overview|Integrations]]
- [[modules/work-management/analytics/overview|Analytics]]
- [[Userflow/Documents/document-versioning|Document Versioning]]
- [[Userflow/Documents/document-upload|Document Upload]]
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
- [[database/schemas/wms-integrations|WMS Integrations Schema]]
- [[database/schemas/wms-analytics|WMS Analytics Schema]]

### Verification

```bash
dotnet test ONEVO.sln --filter Collaboration
dotnet test ONEVO.sln --filter Integrations
dotnet test ONEVO.sln --filter WorkSyncAnalytics
```

---

## Open Frontend Contracts

- [ ] Confirm exact shape of `IDEEntitlementsDto` with DEV8.
- [ ] Confirm `tag:executed` SignalR payload with DEV8.
