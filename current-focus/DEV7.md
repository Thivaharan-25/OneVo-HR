# DEV7: Frontend WorkSync Web UI

**Track:** Frontend
**Primary ownership:** WorkSync web UI, projects, tasks, boards, docs, time
**Current Unfinished Task:** Task 1 - WorkSync shell and projects
**Blocked By:** DEV5 app foundation; DEV3 WorkSync APIs for live data

---

## ADE Instructions

When Dev 7 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Use MSW contract mocks until DEV3 endpoints are ready.

---

## Task 1: WorkSync Shell + Projects

**Goal:** build the workspace and project experience for WorkSync.

**Requires:** DEV5 Tasks 1-4 complete  
**Live integration:** DEV3 Task 1 (use MSW until ready) - Contract: `current-focus/contracts/worksync-core.md`

### Acceptance Criteria

- [ ] Workspace switcher shows current workspace and available workspaces.
- [ ] WorkSync navigation supports Projects, My Work, Planner, Docs, Time, and Analytics.
- [ ] Project list supports search, filters, status, owner, and cursor paging.
- [ ] Project detail shows overview, members, tasks, board, roadmap, and activity tabs.
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

> **Parallel group** — Tasks 2, 3, and 4 all require DEV5 Tasks 1–4 and DEV7 Task 1, but are independent of each other. Run all three simultaneously.

## Task 2: Tasks + Boards + Planning UI

**Goal:** build task, kanban, backlog, sprint, and roadmap screens.

**Requires:** DEV5 Tasks 1-4 and DEV7 Task 1 complete  
**Live integration:** DEV3 Task 2 (use MSW until ready) - Contract: `current-focus/contracts/worksync-core.md`

### Acceptance Criteria

- [ ] My Work page groups assigned tasks by due date, status, and priority.
- [ ] Task detail supports description, assignees, status, comments, checklists, docs, and code activity.
- [ ] Board view supports columns, task cards, drag/drop shell, and quick status update.
- [ ] Backlog and sprint planning screens support moving tasks into sprints.
- [ ] Roadmap timeline shows roadmap items and milestones.
- [ ] Tests cover task detail, status update, board render, and sprint assignment.

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

## Task 3: Chat + Time + Analytics UI

**Goal:** build WorkSync chat, time tracking, timesheets, and analytics views.

**Requires:** DEV5 Tasks 1-4 and DEV7 Task 1 complete  
**Live integration:** DEV3 Tasks 2-3 (use MSW until ready) - Contract: `current-focus/contracts/signalr-events.md`

### Acceptance Criteria

- [ ] Chat screen lists channels and messages.
- [ ] Chat composer supports send, attachments shell, and realtime updates.
- [ ] Time log screen supports daily/weekly logs and task-linked entries.
- [ ] Timesheet screen supports current period summary and submit action.
- [ ] Analytics page shows productivity, capacity, task throughput, and sprint burndown cards.
- [ ] Tests cover chat message send, realtime append, time log validation, and analytics loading state.

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

## Task 4: Docs + Git Integration UI

**Goal:** build document/wiki and code activity surfaces used by web and IDE users.

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


