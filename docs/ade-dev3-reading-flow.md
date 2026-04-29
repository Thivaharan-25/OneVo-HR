# ADE Reading Flow: Dev 3 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 3. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 3's
**5 tasks** (more than the other devs), and the known issues flagged below.

> **âš ï¸ ADE IMPLEMENTATION NOTE — Dev 3 has 5 tasks, not 4.**
> The orchestrator must handle a variable task count. Dev 3's task list:
> 1→2→3→4→5 (Org Structure → Skills Core → Calendar → Workforce Presence → Activity Monitoring).
> The orchestrator sequential loop must not assume a fixed count of 4 tasks.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ade/README.md                        â† How the orchestrator works, what repos to use
2. current-focus/README.md             â† Task assignment table: Dev 3 has 5 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | File | Module |
|:-------|:-----|:-------|
| 1 | `current-focus/DEV3-org-structure.md` | OrgStructure |
| 2 | `current-focus/DEV3-skills-core.md` | Skills (5 tables) |
| 3 | `current-focus/DEV3-calendar.md` | Calendar |
| 4 | `current-focus/DEV3-workforce-presence-setup.md` | WorkforcePresence |
| 5 | `current-focus/DEV3-activity-monitoring.md` | ActivityMonitoring |

The orchestrator reads each task file's `## Related Tasks` section to check cross-dev
dependencies. If a dependency is missing in the code repo, the task is skipped. Tasks run
**sequentially** (1 → 2 → 3 → 4 → 5), never in parallel.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

Before any task starts, every worker agent receives these 4 files:

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**What the agent learns from each:**

### `AI_CONTEXT/rules.md`
The agent's operating constitution. Key rules absorbed:
- Clean Architecture + CQRS with strict layer boundaries
- Domain events for side effects, direct calls for sync queries
- `ITenantContext` injection in every repository — never skip
- `Result<T>` pattern instead of exceptions
- async + CancellationToken everywhere
- Naming: snake_case columns, PascalCase C#, kebab-case API routes
- Phase 2 guard: never build courses/assessments/LMS tables (those are Phase 2 Skills)
- Activity data: never log window titles or app names — only hashed or counts
- Checkbox tracking: mark `- [ ]` → `- [x]` as each criterion is completed

### `AI_CONTEXT/project-context.md`
System architecture map. Key concepts absorbed:
- Workforce Intelligence pillar: Agent Gateway → Activity Monitoring → Exception Engine pipeline
- Activity data: buffer → aggregate pattern (raw buffer 48h, summaries 2 years)
- Monitoring Lifecycle: data only captured when employee is clocked in (GDPR)
- Cross-module: `ICalendarConflictService` is a public sync interface, called directly by Leave module
- Three-tier App Allowlist: tenant → role → employee; most specific wins

### `AI_CONTEXT/tech-stack.md`
Technology choices. Key items absorbed:
- PostgreSQL 16 partitioned tables (`pg_partman`) for activity data
- EF Core 9 snake_case naming convention
- Hangfire for background jobs (multiple queues: High, Default, Low)
- SignalR for real-time workforce presence push
- Azure Blob Storage via `IFileService` for screenshots
- SHA-256 for window title hashing

### `AI_CONTEXT/known-issues.md`
Gotchas. Key ones absorbed for Dev 3's work:
- Activity data volume: 240 rows/employee/day — must use partitioned tables
- `activity_daily_summary`: INSERT OR UPDATE on conflict `(tenant_id, employee_id, date)`
- Reporting data: use `activity_daily_summary`, never raw `activity_raw_buffer`
- Self-referencing departments: `parent_department_id` — use CTE for tree queries
- Screenshots are RESTRICTED data — serve via SAS tokens, never permanent blob URLs
- Cursor-based pagination only — no offset pagination

---

## Phase 2: ADE Entry Point Scan (First File Read)

The agent reads:

```
ADE-START-HERE.md
```

**What the agent learns:**
- Phase 1: 16 modules to build (Org Structure, Calendar, Workforce Presence, Activity Monitoring, Discrepancy Engine all in scope)
- Skills: only 5 core tables are Phase 1 — courses, LMS, assessments, certifications are Phase 2
- `ICalendarConflictService` is the sync interface consumed by Leave (DEV1)
- Monitoring Lifecycle is a hard GDPR constraint — data collection tied to clock-in/clock-out
- Activity Monitoring is the data pipeline from Agent Gateway ingest through to daily summaries
- Discrepancy Engine is a Phase 1 module (2 tables: `discrepancy_events`, `wms_daily_time_logs`)

---

## Phase 3: Task 1 — Org Structure

### Dependency check
```
DEV1 Infrastructure Setup  â† checks: Does ONEVO.SharedKernel exist in backend repo?
```
No other cross-dev dependencies. If Infrastructure is done, agent proceeds immediately.

### Files read for Task 1

```
current-focus/DEV3-org-structure.md            â† Task spec: acceptance criteria, pages to build
```

Task-specific context injected by orchestrator:

```
modules/org-structure/overview.md              â† OrgStructure module spec: tables, events
backend/shared-kernel.md                       â† BaseEntity, BaseRepository, ITenantContext
infrastructure/multi-tenancy.md               â† Tenant-scoped hierarchy queries
backend/module-catalog.md                     â† Module ownership + namespace boundaries
code-standards/backend-standards.md           â† Naming conventions
```

Userflows:
```
Userflow/Org-Structure/department-hierarchy.md â† Create and manage department tree
Userflow/Org-Structure/team-creation.md        â† Create teams and manage members
Userflow/Org-Structure/job-family-setup.md     â† Configure job families, levels, titles
Userflow/Org-Structure/legal-entity-setup.md   â† Manage legal entities
Userflow/Org-Structure/cost-center-setup.md    â† Cost center configuration
```

Frontend references:
```
frontend/design-system/components/component-catalog.md   â† DataTable, Dialog, DropdownMenu
frontend/design-system/patterns/layout-patterns.md       â† Tree view layout
frontend/data-layer/api-integration.md
```

### What the agent builds

**Step 1 — Backend:**
1. Legal entity CRUD (name, registration number, country)
2. Office location CRUD (linked to legal entity + country)
3. Department CRUD with hierarchical tree (unlimited nesting via `parent_department_id`)
4. Department tree query: CTE to return full hierarchy for a tenant
5. Job family CRUD (taxonomy root for job structure)
6. Job levels CRUD (`job_levels` table — rank ordering: Junior/Senior/Lead/Director)
7. Job title CRUD (linked to job family + job level)
8. Job skill requirements CRUD — BUT this endpoint is stubbed only in Task 1; it calls into
   `ISkillService` which doesn't exist yet (Skills Core is Task 2). The endpoint returns 501 until
   Task 2 completes.
9. Team CRUD (linked to department)
10. Team member management (add/remove employees from teams)
11. All entities tenant-scoped with indexes: `(tenant_id, parent_department_id)`, etc.

**Step 2 — Frontend:**
1. `org/page.tsx`: `OrgChart.tsx` — visual org hierarchy (click to drill down)
2. `org/departments/page.tsx`: `DepartmentTree.tsx` — interactive expand/collapse tree, drag-and-drop reorder, create dialog (name, parent, head), employee count per department
3. `org/teams/page.tsx`: DataTable + `TeamMemberList.tsx` — team detail with add/remove
4. `org/job-families/page.tsx`: `JobFamilyAccordion.tsx` — family → levels → titles, CRUD at each level; "Required Skills" tab (rendered but empty until Task 2 unblocks it)
5. `org/legal-entities/page.tsx`: DataTable + CRUD dialogs
6. `org/locations/page.tsx`: DataTable + CRUD dialogs
7. Colocated: `DepartmentTree.tsx`, `TeamMemberList.tsx`, `JobFamilyAccordion.tsx`, `OrgChart.tsx`

**After Step 2:** Marks all checkboxes in `DEV3-org-structure.md`. Commits.

---

## Phase 4: Task 2 — Skills Core (Phase 1)

### Dependency check
```
DEV1 Infrastructure Setup  â† checks: Does ONEVO.SharedKernel exist?
DEV2 Auth & Security       â† checks: Do skills:* permissions exist in the permissions table?
DEV1 Core HR Profile       â† checks: Does employees table exist?
DEV3 Org Structure         â† checks: Do job_families table exist? (just completed in Task 1)
```
Since Task 1 just completed, DEV3 Org Structure is met. The other dependencies should be
met (DEV1 + DEV2 are Week 1 foundations). If permissions are missing → skip, report blocked.

### Files read for Task 2

```
current-focus/DEV3-skills-core.md              â† Task spec
```

Task-specific context:

```
modules/skills/overview.md                     â† Skills module: Phase 1 scope, public API
modules/skills/employee-skills/overview.md     â† Write path: self-declare, manager-add, validate
modules/skills/skill-taxonomy/overview.md      â† Taxonomy data model
database/schemas/skills.md                     â† Full table schemas for the 5 Phase 1 tables
infrastructure/multi-tenancy.md
```

Userflows:
```
Userflow/Skills-Learning/skill-taxonomy-setup.md       â† Admin configures categories + skills
Userflow/Skills-Learning/employee-skill-declaration.md â† Self-declare + manager direct-add variation
Userflow/Skills-Learning/skill-assessment.md           â† Manager validates pending declarations
```

> **âš ï¸ SCOPE GUARD:** Task 2 builds ONLY 5 tables: `skill_categories`, `skills`,
> `employee_skills`, `job_skill_requirements`, `skill_validation_requests`.
> Do NOT build courses, LMS, assessments, certifications, development plans — those are Phase 2.

### What the agent builds

**Step 1 — Backend:**

Skill Taxonomy:
1. `skill_categories` CRUD (name, `is_active`, tenant-scoped)
2. `skills` CRUD (linked to category, `proficiency_levels` jsonb — 5 levels with label+description, `evidence_required` flag)
3. Skill search typeahead: min 2 chars, searches active skills (PostgreSQL FTS or ILIKE)
4. Deactivate skill: hides from new declarations, existing `employee_skills` retained

Employee Skills:
5. `employee_skills` CRUD with three write paths:
   - Self-declare: `POST /api/v1/employees/me/skills` → `status = 'pending'`
   - Manager direct-add: `POST /api/v1/employees/{id}/skills` → `status = 'validated'`
   - Manager validate/reject: `PUT /api/v1/employees/{id}/skills/{skillId}/validate`
6. `proficiency_level` is integer 1–5 (check constraint `BETWEEN 1 AND 5`)
7. `last_assessed_in_review_id` always null in Phase 1 (FK to review_cycles — Phase 2)
8. Unique constraint on `(employee_id, skill_id)` — no duplicate declarations
9. Skill gap analysis: `GET /api/v1/skills/gap-analysis/{employeeId}` — compares validated skills vs `job_skill_requirements` for their job family

Skill Validation Requests:
10. `skill_validation_requests` CRUD — employee requests proficiency upgrade (`from_level` → `to_level`)
11. Manager approve → updates `employee_skills.proficiency_level`, status = `validated`
12. Manager reject → `skill_validation_requests.status = 'rejected'`, no change to employee_skills

Now activates the Job Skill Requirements endpoint stubbed in Task 1 (calls `ISkillService` which now exists).

**Step 2 — Frontend:**
1. `skills/taxonomy/page.tsx` (admin, `skills:manage`):
   - `SkillCategoryList.tsx`: category accordion with skill count
   - `SkillForm.tsx`: create/edit skill modal (name, category, proficiency labels)
   - `ProficiencyLevelEditor.tsx`: edit 5 level labels per skill
2. `employees/[id]/skills/page.tsx` (manager view, `skills:validate` or `skills:write-team`):
   - `SkillProfileCard.tsx`: skill + proficiency bar + validation status badge
   - `AddSkillModal.tsx`: manager direct-add (creates as Validated)
   - `SkillGapPanel.tsx`: gap vs job family requirements
   - Pending skills highlighted → click to validate (set proficiency) or reject
3. `me/skills/page.tsx` (employee self-service, `skills:write`):
   - Grid of declared skills: name, category, proficiency bar, status badge (Pending/Validated)
   - `DeclareSkillModal.tsx`: search taxonomy typeahead → set proficiency slider (1–5) → save
   - `SkillCard.tsx`: own skill card with status badge
4. Also activates the "Required Skills" tab on the Job Families page (built in Task 1, now unlocked)

> **âš ï¸ PHANTOM ASSIGNMENT NOTE:** `DEV3-skills-core.md` lists "Assignee: Dev 3 (+ Dev 4 for
> employee skills frontend)". However, there is NO `DEV4-skills-core.md` task file. Dev 4's
> ADE session will not automatically build any Skills Core frontend. Dev 3 must build
> all Skills Core frontend pages. See flagged issues at end of this document.

**After Step 2:** Marks all checkboxes in `DEV3-skills-core.md`. Commits.

---

## Phase 5: Task 3 — Calendar

### Dependency check
```
DEV1 Infrastructure Setup  â† checks: Does ONEVO.SharedKernel exist?
```
Only Infrastructure required. No other cross-dev dependencies. Agent proceeds.

### Files read for Task 3

```
current-focus/DEV3-calendar.md                 â† Task spec
```

Task-specific context:

```
modules/calendar/overview.md                   â† Calendar module spec: public interface
modules/calendar/calendar-events/overview.md   â† Table schema, API endpoints
modules/calendar/conflict-detection/overview.md â† ICalendarConflictService, conflict rules
infrastructure/multi-tenancy.md               â† Tenant-scoped events
```

Userflows:
```
Userflow/Calendar/calendar-event-creation.md   â† Create calendar events
Userflow/Calendar/conflict-detection.md        â† Detect scheduling conflicts
```

### What the agent builds

**Step 1 — Backend:**
1. `calendar_events` table — unified calendar, polymorphic `source_type` + `source_id`
2. Event types: `company`, `team`, `personal`, `leave`, `holiday`, `review`
3. Source types: `manual`, `leave_request`, `holiday`, `review_cycle`
4. Visibility levels: `public`, `team`, `private`
5. CRUD endpoints: `GET/POST/PUT/DELETE /api/v1/calendar`
6. `ICalendarConflictService` — detect overlapping events for employee + date range
7. Conflict detection excludes `leave` and `holiday` types
8. Conflict severity: `review` + `company` = high, `team` + `personal` = medium
9. `GET /api/v1/calendar/conflicts` — requires `leave:create` or `leave:approve`
10. Domain events: `CalendarEventCreated`, `CalendarEventUpdated`, `CalendarEventDeleted`
11. Listen for `LeaveApproved` → auto-create calendar event with `source_type = 'leave_request'`
12. Listen for `LeaveCancelled` → auto-delete corresponding calendar event
13. Company holiday seeding via tenant setup
14. Unit tests ≥ 80% coverage

This task **unblocks DEV1 Leave (Task 3)**: `ICalendarConflictService` is now available in the backend repo.

**Step 2 — Frontend:**
1. `calendar/page.tsx`: unified monthly calendar, color-coded by event type (leave=blue, holiday=green, review=orange, company=purple, team=teal, personal=gray)
2. Create manual events: dialog for company/team/personal types
3. Edit/delete own events
4. Filter by event type
5. Conflict warning display for date ranges with overlapping events
6. `PermissionGate`: authenticated (all users view), event creation based on role

**After Step 2:** Marks all checkboxes in `DEV3-calendar.md`. Commits.

---

## Phase 6: Task 4 — Workforce Presence Setup

### Dependency check
```
DEV1 Infrastructure Setup  â† checks: Does ONEVO.SharedKernel exist?
DEV4 Shared Platform       â† checks: Do workflow_definitions + workflow_instances exist?
```
If DEV4 Shared Platform is missing → orchestrator skips Task 4 and reports:
"Workforce Presence Setup blocked — workflow engine missing. Re-run after DEV4 delivers Shared Platform."

If dependencies are met, agent proceeds.

### Files read for Task 4

```
current-focus/DEV3-workforce-presence-setup.md â† Task spec
```

Task-specific context:

```
modules/workforce-presence/overview.md         â† WorkforcePresence module spec
modules/configuration/monitoring-toggles/overview.md â† Toggles gate monitoring features
infrastructure/multi-tenancy.md               â† Tenant-scoped presence data
```

Userflows:
```
Userflow/Workforce-Intelligence/live-dashboard.md       â† Real-time workforce status monitoring
Userflow/Workforce-Presence/shift-schedule-setup.md     â† Configure shifts and schedules
Userflow/Workforce-Presence/presence-session-view.md    â† View employee presence detail
Userflow/Workforce-Presence/break-tracking.md           â† View and manage break records
```

### What the agent builds

**Step 1 — Backend:**
1. `shifts` CRUD (morning, evening, night, flexible with start/end times)
2. `work_schedules` CRUD (weekly patterns)
3. `schedule_templates` — reusable templates
4. `employee_shift_assignments` — assign employees to shifts
5. `employee_work_schedules` — per-employee schedule overrides
6. `holidays` CRUD (company + country holidays, recurring flag)
7. `presence_sessions` table — **one row per employee per day**, unified from all sources
8. Presence status computation: `present`, `absent`, `partial`, `on_leave`
9. `device_sessions` table — multiple rows per employee per day (one per active/idle cycle)
10. `break_records` table — with `auto_detected` flag for agent-detected breaks
11. Break auto-detection: agent idle > configurable threshold (default 15 min) → create break record
12. `ReconcilePresenceSessions` Hangfire job (every 5 min during work hours)
13. `FlagUnresolvedAbsences` Hangfire job (daily 10 AM)
14. `CloseOpenSessions` Hangfire job (daily 11:59 PM)
15. `IWorkforcePresenceService` public interface implementation
16. `GET /api/v1/workforce/presence/live` — real-time workforce status snapshot
17. Unit tests ≥ 80% coverage

This task **unblocks DEV2 Exception Engine (Task 3)**: `IWorkforcePresenceService` is now available.
This task **unblocks DEV4 Biometric (Task 4)**: presence session schema is now defined.

**Step 2 — Frontend:**
1. `workforce/presence/page.tsx` (`LiveStatusBoard.tsx`):
   - Summary cards: total active, idle, on break, absent, on leave (real-time via SignalR `workforce-live`)
   - Employee DataTable: name, status badge (color-coded), current activity, check-in time, device
   - Filter by department, team, status
2. Presence session detail on employee row click:
   - `TimelineBar`: full-day view — active/idle/break/meeting segments
   - Device sessions list + break records
3. `workforce/presence/shifts/page.tsx` (`ShiftCalendar.tsx`):
   - CRUD shifts, schedule templates
   - Bulk assign shifts by department/team
4. `workforce/presence/holidays/page.tsx`: calendar view + CRUD holidays
5. Colocated: `LiveStatusBoard.tsx`, `AttendanceTable.tsx`, `ShiftCalendar.tsx`, `OvertimeTable.tsx`, `BiometricDeviceCard.tsx` (placeholder for DEV4 Biometric to populate)

**After Step 2:** Marks all checkboxes in `DEV3-workforce-presence-setup.md`. Commits.

---

## Phase 7: Task 5 — Activity Monitoring

### Dependency check
```
DEV4 Shared Platform + Agent Gateway  â† checks: Does POST /api/v1/agent/ingest endpoint exist?
                                        (also checks: does registered_agents table exist?)
```
If Agent Gateway ingest is missing → orchestrator skips Task 5 and reports:
"Activity Monitoring blocked — Agent Gateway ingest endpoint missing. Re-run after DEV4 delivers Shared Platform + Agent Gateway."

If dependency is met, agent proceeds.

### Files read for Task 5

```
current-focus/DEV3-activity-monitoring.md      â† Task spec
```

Task-specific context:

```
modules/activity-monitoring/overview.md        â† ActivityMonitoring module spec: data pipeline
modules/agent-gateway/overview.md              â† Agent ingest data format, batch types
modules/configuration/monitoring-toggles/overview.md â† Feature toggles gate processing
security/data-classification.md               â† Screenshots are RESTRICTED data
infrastructure/multi-tenancy.md               â† Tenant-configurable app categories
database/schemas/activity-monitoring.md       â† Full table schemas with partitioning notes
```

Userflows:
```
Userflow/Workforce-Intelligence/activity-snapshot-view.md  â† View activity data + screenshots
Userflow/Workforce-Intelligence/monitoring-configuration.md â† Configure monitoring categories
```

Frontend references:
```
frontend/design-system/components/component-catalog.md   â† TimelineBar, ActivityHeatmap
frontend/design-system/patterns/data-visualization.md   â† Heatmaps, charts
frontend/design-system/foundations/color-tokens.md      â† Productive/unproductive colors
```

### What the agent builds

**Step 1 — Backend:**

Data Pipeline:
1. `activity_raw_buffer` table — partitioned daily via `pg_partman`, batch INSERT via `COPY`/`unnest()`
2. `ProcessRawBufferJob` Hangfire job (every 2 min) — parse raw → snapshots + app usage + meetings + document + communication usage
3. `activity_snapshots` table — partitioned monthly, 90-day retention
4. Intensity score: `(keyboard + mouse) / max_expected * 100`, capped at 100
5. `application_usage` table — time per app per day, with `app_category_type` + optional `browser_domain`
6. Window title hashing: SHA-256 — never store raw titles
7. `meeting_sessions` table — Phase 1: process name matching (`Teams.exe`, `zoom.exe`); `meet_browser`, `teams_browser` platform enum values
8. Camera/mic detection via process inspection
9. `device_tracking` table — laptop active minutes, estimated mobile
10. `activity_daily_summary` table — `INSERT OR UPDATE` on conflict `(tenant_id, employee_id, date)`
11. New columns on `activity_daily_summary`: `document_time_minutes`, `communication_time_minutes`, `deep_focus_sessions_count`, `data_source`
12. `browser_activity` table — domain + classification + seconds + source (browser extension, nullable)

Discrepancy Engine (within this task):
13. `discrepancy_events` table — populated by `DiscrepancyEngineJob` (daily EOD)
14. Manager-only visibility enforced at query level
15. `wms_daily_time_logs` table — WMS Work Activity bridge writes here (Bridge 3 endpoint)

Screenshots:
16. `screenshots` table — metadata only, files in blob storage via `IFileService`
17. Screenshot trigger types: `scheduled`, `random`, `manual`
18. `PurgeExpiredScreenshotsJob` (daily 4 AM) — per-tenant retention policy
19. Screenshots are RESTRICTED data — served via time-limited SAS tokens (15 min expiry)

Application Categories:
20. `application_categories` table — tenant-configurable with glob pattern matching
21. `is_productive` flag (nullable — uncategorized apps)

Aggregation & Retention:
22. `AggregateDailySummaryJob` (every 30 min + EOD)
23. `PurgeRawBufferJob` (daily 3 AM) — drop partitions > 48h
24. `PurgeExpiredSnapshotsJob` (monthly) — drop partitions > 90 days
25. `IActivityMonitoringService` public interface implementation
26. Feature toggle check before processing via `IConfigurationService`
27. Domain events: `ActivitySnapshotReceived`, `DailySummaryAggregated`
28. Unit tests ≥ 80% coverage

This task **unblocks DEV2 Exception Engine (Task 3)**: `IActivityMonitoringService` is now available.
This task **unblocks DEV1 Productivity Analytics (Task 4)**: `activity_daily_summary` and `IActivityMonitoringService` are now available.

**Step 2 — Frontend:**
1. `workforce/activity/page.tsx` (`ActivityFeed.tsx`): team activity feed
2. `workforce/activity/[employeeId]/page.tsx`:
   - `ActivityHeatmap`: hourly intensity grid for selected date range
   - `AppUsageChart.tsx`: stacked bar chart — productive/unproductive/uncategorized
   - `ActivityTimeline.tsx`: minute-by-minute active/idle/meeting segments
   - Meeting sessions list with duration
   - Screenshot gallery (thumbnails, click to expand with timestamp)
   - Date picker to navigate days
3. `workforce/activity/screenshots/page.tsx`: `ScreenshotGrid.tsx` — review queue
4. `settings/monitoring/page.tsx` (admin):
   - `application_categories` DataTable + CRUD dialogs
   - Uncategorized apps list with quick-assign
   - Screenshot settings: enable/disable, interval, retention period
5. `loading.tsx` skeleton for employee detail page
6. Colocated: `ActivityFeed.tsx`, `ActivityTimeline.tsx`, `ScreenshotGrid.tsx`, `AppUsageChart.tsx`

**After Step 2:** Marks all checkboxes in `DEV3-activity-monitoring.md`. Commits.

---

## Phase 8: Orchestrator Final Report

After all tasks complete (or are blocked), the orchestrator outputs:

```
Session complete.
  ✓ Completed: Task 1 (Org Structure), Task 2 (Skills Core), Task 3 (Calendar)
  ✗ Blocked: Task 4 (Workforce Presence Setup) — needs DEV4 Shared Platform workflow engine
  ✗ Blocked: Task 5 (Activity Monitoring) — needs DEV4 Agent Gateway ingest endpoint

  Re-run after DEV4 delivers Shared Platform + Agent Gateway.
```

---

## Full File Read Order (Canonical Sequence)

```
## ORCHESTRATOR PHASE
ade/README.md
current-focus/README.md

## BASE CONTEXT (every task)
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md

## ENTRY POINT
ADE-START-HERE.md

## TASK 1 — Org Structure
current-focus/DEV3-org-structure.md
modules/org-structure/overview.md
backend/shared-kernel.md
infrastructure/multi-tenancy.md
backend/module-catalog.md
code-standards/backend-standards.md
Userflow/Org-Structure/department-hierarchy.md
Userflow/Org-Structure/team-creation.md
Userflow/Org-Structure/job-family-setup.md
Userflow/Org-Structure/legal-entity-setup.md
Userflow/Org-Structure/cost-center-setup.md
frontend/design-system/components/component-catalog.md
frontend/design-system/patterns/layout-patterns.md
frontend/data-layer/api-integration.md

## TASK 2 — Skills Core
current-focus/DEV3-skills-core.md
modules/skills/overview.md
modules/skills/employee-skills/overview.md
modules/skills/skill-taxonomy/overview.md
database/schemas/skills.md
Userflow/Skills-Learning/skill-taxonomy-setup.md
Userflow/Skills-Learning/employee-skill-declaration.md
Userflow/Skills-Learning/skill-assessment.md

## TASK 3 — Calendar
current-focus/DEV3-calendar.md
modules/calendar/overview.md
modules/calendar/calendar-events/overview.md
modules/calendar/conflict-detection/overview.md
Userflow/Calendar/calendar-event-creation.md
Userflow/Calendar/conflict-detection.md

## TASK 4 — Workforce Presence Setup
current-focus/DEV3-workforce-presence-setup.md
modules/workforce-presence/overview.md
modules/configuration/monitoring-toggles/overview.md
Userflow/Workforce-Intelligence/live-dashboard.md
Userflow/Workforce-Presence/shift-schedule-setup.md
Userflow/Workforce-Presence/presence-session-view.md
Userflow/Workforce-Presence/break-tracking.md
frontend/design-system/foundations/color-tokens.md   â† status colors
frontend/design-system/patterns/data-visualization.md â† timeline visualization

## TASK 5 — Activity Monitoring
current-focus/DEV3-activity-monitoring.md
modules/activity-monitoring/overview.md
modules/agent-gateway/overview.md                   â† data source
security/data-classification.md                     â† screenshots are RESTRICTED
database/schemas/activity-monitoring.md
Userflow/Workforce-Intelligence/activity-snapshot-view.md
Userflow/Workforce-Intelligence/monitoring-configuration.md
frontend/design-system/patterns/data-visualization.md
```

**Total unique files read: ~44**

---

## Known Issues Flagged During Read Flow Analysis

### ISSUE 1 — Dev 3 Has 5 Tasks (ADE Orchestrator Must Handle Variable Count)

The `ade/README.md` orchestrator flow documentation implies sequential 1→4 execution. Dev 3
has **5 tasks**. The orchestrator implementation must not hardcode 4 as the task count — it
must read the task assignment table from `current-focus/README.md` and process however many
tasks a dev has.

**Impact:** If orchestrator assumes exactly 4 tasks per dev, Task 5 (Activity Monitoring)
will never run for Dev 3. `IActivityMonitoringService` will never be built, which blocks
Dev 2's Exception Engine and Dev 1's Productivity Analytics permanently.

**Fix needed:** Orchestrator reads task count dynamically from `current-focus/README.md`,
not from a hardcoded loop limit.

---

### ISSUE 2 — Skills Core Phantom Dev 4 Assignment

`DEV3-skills-core.md` header says: `Assignee: Dev 3 (+ Dev 4 for employee skills frontend)`.

There is **no `DEV4-skills-core.md`** task file. Dev 4's ADE session has no task to dispatch
for this claimed work. If Dev 3's ADE skips the frontend pages expecting Dev 4 to build them,
those pages will not be built.

**Impact:** Employee Skills tab on employee detail page and My Skills self-service page may
be incomplete.

**Fix options:**
- (A) Remove `(+ Dev 4)` from the assignee line — Dev 3 owns all Skills Core frontend
- (B) Create `current-focus/DEV4-skills-core.md` with only the employee skills frontend pages

**Recommended:** Option A. Dev 3 builds all 3 frontend pages (`skills/taxonomy`, `employees/[id]/skills`, `me/skills`). They are self-contained and do not conflict with Dev 4's work.

---

## Notes for ADE Implementation

1. **Task 3 (Calendar) is independent of Tasks 2 and 4.** It only requires DEV1 Infrastructure.
   The orchestrator could in theory run Calendar before Skills Core — but since tasks run
   sequentially 1→5, Calendar will always wait for Skills Core to finish. This is fine.

2. **Task 3 (Calendar) is a cross-dev unblocking event.** When `ICalendarConflictService` is
   committed to the backend repo, the orchestrator running DEV1's session can re-evaluate
   whether DEV1 Leave (Task 3) is now unblocked.

3. **The `discrepancy_events` and `wms_daily_time_logs` tables are built in Task 5.**
   Even though they belong to the "Discrepancy Engine" module namespace, they are physically
   built inside this task file. The agent must place them under `ONEVO.Modules.DiscrepancyEngine`
   namespace, not `ActivityMonitoring`.

4. **Screenshots are RESTRICTED data.** Never serve raw blob URLs to the frontend. Always
   use time-limited SAS tokens (15 min) via `IFileService.GetTemporaryUrlAsync()`.

5. **Step 1 (Backend) always completes before Step 2 (Frontend).** Backend commit happens first.
