# DEV7: Frontend Work UI

**Track:** Frontend
**Primary ownership:** Work web UI: projects, work items, worklogs, simple docs/pages, membership/settings. Boards, Planner, Chat, and Analytics are Phase 2.
**Current Unfinished Task:** Task 1 - Work shell and projects
**Blocked By:** DEV5 app foundation; DEV3 Work APIs for live data

---

## ADE Instructions

When Dev 7 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Use MSW contract mocks until DEV3 endpoints are ready.

---

## Task 1: Work Shell + Projects

**Goal:** build the Phase 1 Work project experience.

**Requires:** DEV5 Tasks 1-4 complete  
**Live integration:** DEV3 Task 1 (use MSW until ready) - Contract: `current-focus/contracts/worksync-core.md`

### Acceptance Criteria

- [ ] Workspace switcher shows current workspace and available workspaces.
- [ ] Work navigation supports Projects, Work Items, Docs/Pages where retained, Worklogs, Members, and Settings. Planner, My Space, Chat, and Analytics are Phase 2.
- [ ] Project list supports search, filters, status, owner, and cursor paging.
- [ ] Project detail shows overview, members, work items, docs/pages where retained, worklogs, settings, and activity. Board and roadmap tabs are Phase 2.
- [ ] Project create/edit forms validate required fields.
- [ ] Tests cover workspace switch, project list, create validation, and detail tabs.

### References

- [[Userflow/Work-Management/wm-overview|Work Management Overview]] (Userflow/Work-Management/wm-overview.md)
- [[Userflow/Work-Management/project-flow|Project Flow]] (Userflow/Work-Management/project-flow.md)
- [[frontend/architecture/sidebar-nav|Sidebar Nav]] (frontend/architecture/sidebar-nav.md)

### Verification

```bash
npm run test -- worksync
npm run build
```

---

> **Parallel group** - Tasks 2, 3, and 4 all require DEV5 Tasks 1-4 and DEV7 Task 1, but are independent of each other. Run all three simultaneously.

## Task 2: Work Items UI (Phase 1) / Boards + Planning UI (Phase 2)

**Goal:** build Phase 1 work-item screens. Kanban, backlog, sprint, and roadmap screens are Phase 2 references.

**Requires:** DEV5 Tasks 1-4 and DEV7 Task 1 complete  
**Live integration:** DEV3 Task 2 (use MSW until ready) - Contract: `current-focus/contracts/worksync-core.md`

### Acceptance Criteria

- [ ] My Work page groups assigned tasks by due date, status, and priority.
- [ ] Task detail supports description, assignees, status, comments, checklists, docs, and code activity.
- [ ] Phase 2 only: board view with columns, cards, drag/drop shell, and quick status update.
- [ ] Phase 2 only: backlog and sprint planning screens.
- [ ] Phase 2 only: roadmap timeline.
- [ ] Tests cover work-item detail and status update. Board render and sprint assignment are Phase 2.

### References

- [[Userflow/Work-Management/task-flow|Task Flow]] (Userflow/Work-Management/task-flow.md)
- [[Userflow/Work-Management/planning-flow|Planning Flow]] (Userflow/Work-Management/planning-flow.md)
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] (frontend/design-system/patterns/layout-patterns.md)

### Verification

```bash
npm run test -- tasks
npm run test -- boards
npm run build
```

---

## Task 3: Worklogs UI + Phase 2 Chat/Analytics UI

**Goal:** build Phase 1 worklog UI. Chat, timesheets, and analytics views are Phase 2 unless explicitly reactivated.

**Requires:** DEV5 Tasks 1-4 and DEV7 Task 1 complete  
**Live integration:** DEV3 Tasks 2-3 (use MSW until ready) - Contract: `current-focus/contracts/signalr-events.md`

### Acceptance Criteria

- [ ] Phase 2 only: chat screen lists channels and messages.
- [ ] Phase 2 only: chat composer supports send, attachments shell, and realtime updates.
- [ ] Time log screen supports daily/weekly logs and task-linked entries.
- [ ] Phase 2 only: timesheet screen supports current period summary and submit action.
- [ ] Phase 2 only: analytics page shows productivity, capacity, throughput, and sprint burndown cards.
- [ ] Tests cover worklog validation. Chat message send, realtime append, and analytics loading state are Phase 2.

### References

- [[Userflow/Chat/chat-overview|Chat Overview]] (Userflow/Chat/chat-overview.md)
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] (Userflow/Work-Management/time-tracking-flow.md)
- [[modules/work-management/analytics/overview|Work Management Analytics]] (modules/work-management/analytics/overview.md)

### Verification

```bash
npm run test -- chat
npm run test -- time
npm run build
```

---

## Task 4: Simple Docs/Pages UI + Git Integration UI (Phase 2)

**Goal:** build simple document/page surfaces where retained. Code activity surfaces used by web and IDE users are Phase 2.

**Requires:** DEV5 Tasks 1-4 and DEV7 Task 1 complete  
**Live integration:** DEV3 Task 5 (use MSW until ready)

### Acceptance Criteria

- [ ] Docs list supports workspace/project filters and document status.
- [ ] Document detail supports view, edit shell, version history, and approval toolbar.
- [ ] Wiki page tree and editor shell exist.
- [ ] Repository linking screen supports provider, repo list, webhook status, and linked tasks.
- [ ] Task code activity section shows commits, branches, PRs, and CI status.
- [ ] Tests cover docs list, wiki page render, repo link flow, and code activity states.

### References

- [[Userflow/Documents/document-upload|Document Upload]] (Userflow/Documents/document-upload.md)
- [[Userflow/Documents/document-versioning|Document Versioning]] (Userflow/Documents/document-versioning.md)
- [[database/schemas/wms-integrations|WMS Integrations Schema]] (database/schemas/wms-integrations.md)

### Verification

```bash
npm run test -- docs
npm run test -- integrations
npm run build
```

---

## Open Backend Contracts

- [x] Project and task DTOs -> `current-focus/contracts/worksync-core.md`
- [x] Chat message DTO and SignalR events -> `current-focus/contracts/signalr-events.md`
- [ ] Code activity DTO from DEV3 (pending).


