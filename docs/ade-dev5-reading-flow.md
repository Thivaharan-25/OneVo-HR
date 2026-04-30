# ADE Reading Flow: Dev 5 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 5. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 5's
5 tasks across WorkSync Pillar 3 foundation.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ADE-START-HERE.md                   ← Platform overview, all 3 pillars, IDE Extension
2. current-focus/README.md             ← Task assignment table: Dev 5 has 5 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | Module | Key Tables |
|:-------|:-------|:-----------|
| 1 | WorkSync Foundation | workspaces, workspace_roles, workspace_members |
| 2 | Project Management | projects, project_members, epics, milestones, versions, labels |
| 3 | OKR & Goals | objectives, key_results, okr_check_ins |
| 4 | Time Management | time_logs, time_entries, timers |
| 5 | Resource Management | resource_allocations, capacity_overrides |

Tasks run **sequentially** (1 → 2 → 3 → 4 → 5). Task 1 (workspaces) is the hardest
dependency — DEV6 and DEV7 cannot start their foundation work until Task 1 is done.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

Before any task starts, every worker agent receives these 4 files:

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**Key concepts DEV5 must absorb:**

- WorkSync is **Pillar 3** — same backend, same ApplicationDbContext, no bridge APIs
- Workspace scoping: all WMS entities carry both `tenant_id` AND `workspace_id`
- `workspace_members` is the join table for user ↔ workspace (many-to-many)
- `employees.user_id` is how an HR employee maps to a workspace member
- Workspace roles (Admin/Member/Viewer) are separate from HR RBAC roles
- A workspace can bind to a `legal_entity_id` — when bound, WMS visibility respects the HR topbar legal entity scope
- Feature folder path: `ONEVO.Application/Features/WorkSync/{SubFeature}/`

---

## Phase 2: Task 1 — WorkSync Foundation

**Task file:** `current-focus/DEV5-wms-foundation.md` (Task 1 section)

**Schema files to read:**
```
database/schemas/wms-project-management.md   ← workspaces, workspace_roles, workspace_members
database/schema-catalog.md                  ← WorkSync Foundation section
onevo-unified-entity-map.md                 ← Section 1 (workspaces) + Scoping Rules
```

**User flows to read:**
```
Userflow/Work-Management/wm-overview.md
```

**Key invariants:**
- Three system workspace roles (Admin/Member/Viewer) seeded per workspace on creation
- Tenant provisioning creates a default workspace if tenant has WorkSync enabled
- Global query filter must enforce both `tenant_id` AND `workspace_id` on all workspace-scoped entities
- Workspace switcher: active workspace carried in JWT claims or `X-Workspace-Id` header

---

## Phase 3: Task 2 — Project Management

**Task file:** `current-focus/DEV5-wms-foundation.md` (Task 2 section)

**Schema files to read:**
```
database/schemas/wms-project-management.md   ← projects, project_members, epics, milestones, versions, labels
```

**User flows to read:**
```
Userflow/Work-Management/project-flow.md
```

**Key invariants:**
- `projects.workspace_id` FK — project always belongs to one workspace
- Project members have roles: Owner / Admin / Member / Viewer
- Labels are workspace-scoped, not project-scoped (reusable across projects)
- Epics link to projects; milestones are project-level date targets

---

## Phase 4: Task 3 — OKR & Goals

**Task file:** `current-focus/DEV5-wms-foundation.md` (Task 3 section)

**Schema files to read:**
```
onevo-unified-entity-map.md                 ← Section 28 (WMS — OKR)
```

**User flows to read:**
```
Userflow/Work-Management/goals-okr-flow.md
```

**Key invariants:**
- OKRs are workspace-scoped (`workspace_id`) — not tenant-scoped
- Key results carry `current_value`, `target_value`, `unit` for progress calculation
- Check-ins are time-series updates to key result current_value
- OKR progress cascades: key_results → objective % complete

---

## Phase 5: Task 4 — Time Management

**Task file:** `current-focus/DEV5-wms-foundation.md` (Task 4 section)

**Schema files to read:**
```
onevo-unified-entity-map.md                 ← Section 31 (WMS — Time Management)
```

**User flows to read:**
```
Userflow/Work-Management/time-tracking-flow.md
```

**Key invariants:**
- `time_logs.task_id` FK → `tasks` — this is the WMS→HR correlation point
- Active timer: one row per user with `ended_at = null` enforced at application layer
- Time logs feed `wms_daily_time_logs` in the Discrepancy Engine (Pillar 2)
- Overtime correlation: `overtime_records.task_id` (nullable) references `tasks.id`

---

## Phase 6: Task 5 — Resource Management

**Task file:** `current-focus/DEV5-wms-foundation.md` (Task 5 section)

**Schema files to read:**
```
onevo-unified-entity-map.md                 ← Section 32 (WMS — Resource Management)
```

**User flows to read:**
```
Userflow/Work-Management/resource-flow.md
```

**Key invariants:**
- Resource allocations are project + user + date_range based
- Capacity overrides allow temporary changes to a user's available hours
- Allocation percentage + leave_requests feed into availability calculation
