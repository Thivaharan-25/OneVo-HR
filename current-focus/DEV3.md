# DEV3: Backend Work + Phase 2 IDE APIs

**Track:** Backend
**Primary ownership:** Work backend: projects, work items, worklogs, simple docs/pages, project membership/settings. Boards, planning, OKR, resources, chat, Chat AI, integrations, analytics, IDE backend APIs, and tag execution are Phase 2 references.
**Current Unfinished Task:** Task 1 - Work foundation
**Blocked By:** DEV1 tenant/auth foundation

---

## ADE Instructions

When Dev 3 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Keep Work inside the main backend and database; internal `Features/WorkSync/*` names may remain as implementation folders.

---

## Task 1: Work Foundation + Projects

**Goal:** create the project, membership, role, and basic work foundation for Phase 1 Work.

**Requires:** DEV1 Tasks 1-3 complete

### Acceptance Criteria

- [ ] Workspaces table and APIs exist.
- [ ] Workspace members and roles exist.
- [ ] Workspace members store both `user_id` and `employee_id`, and reject users without an active employee record in Phase 1.
- [ ] Workspace role permissions can be resolved for a user.
- [ ] Projects can be created, listed, updated, archived, and assigned members.
- [ ] Project members are represented. Epics, milestones, versions, and repository links are Phase 2.
- [ ] Phase 2 resource planning is not implemented in Phase 1.
- [ ] Workspace provisioning can be triggered from tenant module activation.
- [ ] Workspace APIs are tenant-scoped.
- [ ] Tests cover workspace membership, role permissions, project CRUD, and tenant isolation.

### References

- [[modules/work-management/foundation/overview|Work Management Foundation]] (modules/work-management/foundation/overview.md)
- [[modules/work-management/projects/overview|Projects]] (modules/work-management/projects/overview.md)
- [[modules/work-management/resources/overview|Resources]] (modules/work-management/resources/overview.md)
- [[Userflow/Work-Management/wm-overview|Work Management Overview]] (Userflow/Work-Management/wm-overview.md)
- [[database/schemas/wms-project-management|WMS Project Management Schema]] (database/schemas/wms-project-management.md)

### Verification

```bash
dotnet test ONEVO.sln --filter WorkSync
```

---

> **Parallel group** - Tasks 2, 3, and 5 all depend only on Task 1 and are independent of each other. Task 4 depends on Tasks 1-3. After Task 1 is done, Tasks 2, 3, and 5 can start simultaneously.

## Task 2: Work Items + Worklogs (Phase 1) / Boards + Planning + OKR (Phase 2)

**Goal:** implement Phase 1 work-item and worklog APIs. Board, sprint, roadmap, OKR, and IDE task APIs are Phase 2 references.

**Requires:** DEV3 Task 1 complete  
**Live integration:** DEV2 Task 3 for time_off-aware assignment warnings (use MSW stub returning `availability_status: null` until ready)

### Acceptance Criteria

- [ ] Task create/list/detail/update APIs exist.
- [ ] Task assignments, comments, checklists, labels, and status transitions exist.
- [ ] Task assignments store both `user_id` and `employee_id`, reject inactive/deleted employees, and resolve HR profile data without application-only joins.
- [ ] Task assignment checks Time Off + Calendar availability and writes `availability_status`, `availability_checked_at`, and `availability_warning`.
- [ ] Phase 2 only: boards, columns, and task positions.
- [ ] Phase 2 only: sprint planning APIs for backlog, sprint assignment, start, complete, and burndown snapshots.
- [ ] Phase 2 only: sprint planning assignment availability warnings.
- [ ] Phase 2 only: sprint reports and typed contributor metrics.
- [ ] Phase 2 only: roadmap APIs.
- [ ] Phase 2 only: OKR APIs for objectives, key results, check-ins, and progress updates.
- [ ] Time management APIs exist for time logs, timers, timesheets, and current period summary.
- [ ] WorkSync time can provide daily logged minutes to the Discrepancy Engine.
- [ ] Phase 2 only: `GET /api/v1/ide/tasks/assigned`.
- [ ] Tests cover Phase 1 work-item lifecycle and worklogs. Board moves, sprint assignment, and IDE assigned-task feed are Phase 2.
- [ ] Tests cover time_off-aware assignment warnings, offboarded employee assignment rejection, and typed sprint contributor reporting.

### References

- [[modules/work-management/tasks/overview|Tasks]] (modules/work-management/tasks/overview.md)
- [[modules/work-management/planning/overview|Planning]] (modules/work-management/planning/overview.md)
- [[modules/work-management/okr/overview|OKR]] (modules/work-management/okr/overview.md)
- [[modules/work-management/time/overview|Time]] (modules/work-management/time/overview.md)
- [[Userflow/Work-Management/task-flow|Task Flow]] (Userflow/Work-Management/task-flow.md)
- [[Userflow/Work-Management/planning-flow|Planning Flow]] (Userflow/Work-Management/planning-flow.md)
- [[database/cross-module-relationships|Cross-Module Relationships]] (database/cross-module-relationships.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Tasks
dotnet test ONEVO.sln --filter Planning
dotnet test ONEVO.sln --filter OKR
dotnet test ONEVO.sln --filter Time
```

---

## Task 3: Chat + Chat AI (Phase 2)

**Goal:** Phase 2 reference for Work chat, Microsoft Teams sync hooks, and the first-party Semantic Kernel assistant/action pipeline.

**Requires:** DEV3 Task 1 complete

### Acceptance Criteria

- [ ] Channels, channel members, messages, reactions, and attachments exist.
- [ ] Chat APIs support channel list, message page, send message, and mark read.
- [ ] SignalR publishes `chat:message`, `chat:typing`, and unread update events.
- [ ] AI action job flow supports pending, finalized, and undone states.
- [ ] Chat AI is implemented as ONEVO-owned Semantic Kernel orchestration with permission-filtered Kernel Functions.
- [ ] Chat AI can detect HR/WorkSync query and task/action intents, answer read-only questions, and produce undoable action jobs.
- [ ] Chat AI suggestions are filtered by backend permissions and active modules.
- [ ] Microsoft Teams inbound messages can be imported into ONEVO chat and invoke assistant only after sender mapping to a ONEVO user.
- [ ] Microsoft Teams outbound sync records `teams_message_sync_state` and never blocks local ONEVO message delivery.
- [ ] Undo window is server-enforced.
- [ ] Tests cover message send, realtime event contract, and undo state transitions.

### References

- [[modules/work-management/chat/overview|Chat]] (modules/work-management/chat/overview.md)
- [[modules/work-management/chat-ai/overview|Chat AI]] (modules/work-management/chat-ai/overview.md)
- [[Userflow/Chat/chat-overview|Chat Overview]] (Userflow/Chat/chat-overview.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Chat
dotnet test ONEVO.sln --filter AiAction
```

---

## Task 4: IDE Backend APIs + Tag Execution (Phase 2)

**Goal:** provide backend source of truth for the VS Code extension.

**Requires:** DEV3 Tasks 1-3 complete  
**Contract:** `current-focus/contracts/ide-entitlements.md` (see IAgentEntitlementProvider note - ship with no-op stub; DEV4 Task 7 registers the real implementation)

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

- [[modules/ide-extension/overview|IDE Extension Spec]] (modules/ide-extension/overview.md)
- [[database/schemas/ide-extension|IDE Extension Schema]] (database/schemas/ide-extension.md)
- [[backend/real-time|Real-Time Architecture]] (backend/real-time.md)

### Verification

```bash
dotnet test ONEVO.sln --filter IDE
```

---

## Task 5: Work Collaboration + Phase 2 Integrations + Analytics

**Goal:** build simple Phase 1 documents/pages where retained. Git/code integration, automation, and Work analytics APIs are Phase 2.

**Requires:** DEV3 Tasks 1-3 complete  
**Live integration:** DEV1 Task 5 for document approval workflow (use no-op stub until ready)

### Acceptance Criteria

- [ ] Documents and document versions support workspace/project scope.
- [ ] Phase 1 document/task approvals use direct reviewer routing and Notifications; Shared Platform workflow engine is Phase 2.
- [ ] Wiki pages support tree structure and versioning.
- [ ] Task-document links exist and enforce uniqueness.
- [ ] Phase 2 only: repository records, task repository links, and code activity events.
- [ ] Phase 2 only: GitHub webhook endpoint validates signatures and extracts task refs from commits and PRs.
- [ ] Phase 2 only: commit records, pull request records, CI pipeline runs, and task automation rules.
- [ ] Phase 2 only: automation rules after code events.
- [ ] Phase 2 only: Work analytics exposes sprint reports, dashboard widgets, saved views, and throughput/capacity data.
- [ ] Tests cover document version, document approval workflow, wiki update, repo link, webhook signature, task ref extraction, PR/CI record update, automation rule execution, and analytics query.

### References

- [[modules/work-management/collaboration/overview|Collaboration]] (modules/work-management/collaboration/overview.md)
- [[modules/work-management/integrations/overview|Integrations]] (modules/work-management/integrations/overview.md)
- [[modules/work-management/analytics/overview|Analytics]] (modules/work-management/analytics/overview.md)
- [[Userflow/Documents/document-versioning|Document Versioning]] (Userflow/Documents/document-versioning.md)
- [[Userflow/Documents/document-upload|Document Upload]] (Userflow/Documents/document-upload.md)
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]] (database/schemas/wms-collaboration.md)
- [[database/schemas/wms-integrations|WMS Integrations Schema]] (database/schemas/wms-integrations.md)
- [[database/schemas/wms-analytics|WMS Analytics Schema]] (database/schemas/wms-analytics.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Collaboration
dotnet test ONEVO.sln --filter Integrations
dotnet test ONEVO.sln --filter WorkSyncAnalytics
```

---

## Open Frontend Contracts

- [x] `IDEEntitlementsDto` shape -> `current-focus/contracts/ide-entitlements.md`
- [x] `tag:executed` SignalR payload -> `current-focus/contracts/signalr-events.md`
- [x] WorkSync project and task DTOs -> `current-focus/contracts/worksync-core.md`
- [x] Chat message and SignalR events -> `current-focus/contracts/signalr-events.md`

---

## Early Pickup: DEV1 Task 7 - Developer Platform Admin API Foundation

**Execute this during the wait window before DEV3 Task 1.**

Dev 3 cannot start DEV3 Task 1 until DEV1 Tasks 1, 2, and 3 are all complete - the longest backend wait window. DEV1 Task 7 (Dev Platform Admin API Foundation) only requires DEV1 Tasks 1, 2, and 4. Since Dev 4 is building Task 4 in parallel with Task 2, Task 7 unlocks for Dev 3 as soon as Task 2 lands.

Dev 3 building Task 7 frees Dev 1 to run the critical chain T1 -> T2 -> T3 -> T5 -> T6 without detours.

**Acceptance criteria and verification:** see `current-focus/DEV1.md` Task 7.

---

## Overflow Assignment: DEV1 Task 9

After DEV3 Tasks 1-5 are complete, Dev 3 picks up **DEV1 Task 9 - Developer Platform Operations Backend**.

**Requires:** DEV1 Tasks 4, 5, and 7 complete before starting (T4 by Dev 4, T5 by Dev 1, T7 already built by Dev 3 earlier).  
**Acceptance criteria and verification:** see `current-focus/DEV1.md` Task 9.


