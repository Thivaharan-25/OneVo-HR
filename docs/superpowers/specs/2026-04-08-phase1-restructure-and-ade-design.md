# Phase 1 Restructure + ADE Architecture Design

**Date:** 2026-04-08
**Status:** Approved (pending spec review)
**Scope:** Phase 1 dev assignment restructure + Agentic Development Environment design

---

## Part 1: Phase 1 Restructure

### Phase Changes

| Module | Previous Phase | New Phase | Reason |
|:-------|:--------------|:----------|:-------|
| Payroll | 1 — Build | **2 — Deferred** | Not needed in Phase 1; full payroll engine is Phase 2 |
| Calendar | 2 — Deferred | **1 — Build** | Leave module depends on `ICalendarConflictService`; must exist before Leave |

### Phase 1 Modules (15 total)

Infrastructure, Auth, Core HR (Profile + Lifecycle), Org Structure, Leave, Calendar, Workforce Presence, Activity Monitoring, Agent Gateway, Exception Engine, Identity Verification, Notifications, Configuration, Shared Platform, Productivity Analytics

### Phase 2 Modules (7 total — do NOT build)

Payroll, Documents, Expense, Grievance, Performance, Reporting Engine, Skills

### Dev Assignments

#### DEV1

| # | Task | Module | Priority |
|:--|:-----|:-------|:---------|
| 1 | Infrastructure & Foundation | Infrastructure + SharedKernel | Critical |
| 2 | Employee Profile | CoreHR | Critical |
| 3 | Leave | Leave | High |
| 4 | Productivity Analytics | ProductivityAnalytics | High |

#### DEV2

| # | Task | Module | Priority |
|:--|:-----|:-------|:---------|
| 1 | Auth & Security | Auth | Critical |
| 2 | Employee Lifecycle | CoreHR | Critical |
| 3 | Exception Engine | ExceptionEngine | Critical |
| 4 | Notifications | Notifications | High |

#### DEV3

| # | Task | Module | Priority |
|:--|:-----|:-------|:---------|
| 1 | Org Structure | OrgStructure | Critical |
| 2 | Calendar | Calendar | High |
| 3 | Workforce Presence Setup | WorkforcePresence | Critical |
| 4 | Activity Monitoring | ActivityMonitoring | Critical |

#### DEV4

| #   | Task                            | Module                        | Priority |
| :-- | :------------------------------ | :---------------------------- | :------- |
| 1   | Shared Platform + Agent Gateway | SharedPlatform + AgentGateway | Critical |
| 2   | Configuration                   | Configuration                 | High     |
| 3   | Identity Verification           | IdentityVerification          | High     |
| 4   | Workforce Presence (Biometric)  | WorkforcePresence             | Critical |

### Dependency Chain

```
DEV1: Infra ───→ Profile ───→ Leave ───→ Productivity Analytics
                                ↑                    ↑
DEV3: Org  ───→ Calendar ──────┘                     |
          ───→ Presence Setup ───→ Activity Monitoring┘
                      ↓
DEV4: Platform ───→ Config ───→ Identity ───→ Biometric
                                              (waits for DEV3 task 3)

DEV2: Auth ───→ Lifecycle ───→ Exception Engine ───→ Notifications
```

### Critical Path

- DEV1 Infrastructure + DEV2 Auth must complete first (all other tasks depend on these)
- DEV3 Calendar must complete before DEV1 Leave starts
- DEV3 Workforce Presence Setup must complete before DEV4 Biometric starts

### Task File Labeling Fix

Rename inside every `current-focus/DEV*-*.md` file:

- `## Phase 1: Backend` → `## Step 1: Backend`
- `## Phase 2: Frontend` → `## Step 2: Frontend`

This prevents ADE agents from misinterpreting "Phase 2: Frontend" as deferred work. Both steps are part of Phase 1.

### Other Cleanup

- Remove all specific dates (e.g., "Week 2", "April 18") from current-focus files
- Remove Payroll task file (`DEV3-payroll.md`) or mark as Phase 2 deferred
- Update `current-focus/README.md` to reflect new assignments
- Update `modules/payroll/overview.md` phase marker: `**Phase:** 2 — Deferred`
- Update `modules/calendar/overview.md` phase marker: `**Phase:** 1 — Build`

---

## Part 2: ADE (Agentic Development Environment) Architecture

### Overview

The ADE enables AI-assisted development where a developer says "finish my remaining tasks" and an AI orchestrator manages the work automatically.

### Repos Involved

| Repo | Purpose | ADE Access |
|:-----|:--------|:-----------|
| **Brain repo** (this vault) | Knowledge base, task definitions, rules, specs | Read context + update checkboxes |
| **Backend repo** (.NET 9) | Backend code | Write code (Step 1) |
| **Frontend repo** (Next.js 14) | Frontend code | Write code (Step 2) |
| **Desktop Agent repo** (.NET MAUI) | Desktop agent code | Write code (DEV4 agent tasks only) |

### Architecture: Orchestrator + Worker Agents

```
┌─────────────────────────────────────────────────┐
│                  BRAIN REPO                      │
│           (orchestrator lives here)              │
│                                                  │
│  ┌──────────────┐   ┌────────────────────────┐  │
│  │ Orchestrator  │   │ current-focus/          │  │
│  │               │──→│   DEV1-*.md (checkboxes)│  │
│  │ - reads tasks │   │   DEV2-*.md             │  │
│  │ - checks deps │   │   DEV3-*.md             │  │
│  │ - spawns workers  │   DEV4-*.md             │  │
│  │ - reports     │   └────────────────────────┘  │
│  └──────┬───────┘                                │
│         │                                        │
│         │ spawns                                  │
│         ▼                                        │
│  ┌──────────────┐                                │
│  │ Worker Agent  │                                │
│  │               │                                │
│  │ Context:      │                                │
│  │ - Base layer  │──→ rules.md, project-context,  │
│  │               │   tech-stack, known-issues     │
│  │ - Task layer  │──→ task file, modules/*,       │
│  │               │   Userflow/*                   │
│  └──────┬───────┘                                │
│         │                                        │
└─────────┼────────────────────────────────────────┘
          │ writes code
          ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Backend Repo │  │ Frontend Repo│  │ Agent Repo   │
   │ (.NET 9)     │  │ (Next.js 14) │  │ (.NET MAUI)  │
   │              │  │              │  │              │
   │ Step 1 code  │  │ Step 2 code  │  │ DEV4 only    │
   └──────────────┘  └──────────────┘  └──────────────┘
```

### Orchestrator Behavior

#### Input
```
Dev says: "I'm Dev 1, finish my remaining tasks"
Orchestrator receives: dev_id = 1, paths to brain + backend + frontend repos
```

#### Orchestrator Flow

```
1. Read all task files for the dev: current-focus/DEV{id}-*.md
2. Parse checkboxes — identify unchecked acceptance criteria
3. Determine task order (task # in filename)
4. For each task (sequential):
   a. Read the task file's "Related Tasks" section
   b. Check if cross-dev dependencies exist in the code repos
      - e.g., Does ICalendarConflictService exist in the backend repo?
   c. If dependency missing → SKIP this task (do NOT mark checkbox)
   d. If dependencies met → Spawn worker agent
5. After all tasks processed:
   → Report: completed tasks, skipped/blocked tasks with reasons
   → "Completed tasks 1, 2, 4. Task 3 (Leave) blocked — Calendar module not found."
```

#### Cross-Dev Dependency Check

The orchestrator does NOT mark checkboxes for skipped tasks. It only reports what's blocked and why. The dev re-runs the ADE after the blocking dev delivers.

### Worker Agent Behavior

#### Context Injection (Layered)

**Base layer (always injected):**
- `AI_CONTEXT/rules.md`
- `AI_CONTEXT/project-context.md`
- `AI_CONTEXT/tech-stack.md`
- `AI_CONTEXT/known-issues.md`

**Task-specific layer:**
- The task file itself (e.g., `current-focus/DEV1-leave.md`)
- All files under the module folder (e.g., `modules/leave/**`)
- All referenced userflows (e.g., `Userflow/Leave/**`)
- Related module overviews if cross-module interaction exists

#### Worker Flow

```
1. Receive context (base + task layer)
2. Read unchecked acceptance criteria from task file
3. Execute Step 1: Backend
   - Write code in the backend repo
   - Check off each acceptance criterion as completed
   - Commit changes to backend repo
4. Execute Step 2: Frontend
   - Write code in the frontend repo
   - Check off each frontend criterion as completed
   - Commit changes to frontend repo
5. Update checkboxes in the brain repo task file
6. Return completion status to orchestrator
```

### Parallelism Model

- **Dev-scoped sequential:** Each dev's ADE session runs tasks 1 → 2 → 3 → 4 sequentially
- **Cross-dev parallel:** Multiple devs can run their ADE sessions simultaneously since they work on different modules
- **Step-scoped sequential:** Within each task, Step 1 (backend) completes before Step 2 (frontend) starts

### Progress Tracking

- **Checkboxes in task files** are the single source of truth for progress
- Workers check off `- [ ]` → `- [x]` as they complete each criterion
- Orchestrator reads checkbox state to determine what's remaining
- Skipped/blocked tasks leave checkboxes untouched

### Example Session

```
$ ade run --dev 1 --brain ./onevo-hr-brain --backend ./onevo-backend --frontend ./onevo-frontend

[Orchestrator] Reading tasks for Dev 1...
[Orchestrator] Found 4 tasks: Infrastructure, Employee Profile, Leave, Productivity Analytics

[Orchestrator] Task 1: Infrastructure & Foundation
  → Dependencies: none
  → Spawning worker...
[Worker] Building Step 1: Backend... (12 acceptance criteria)
[Worker] ✓ SharedKernel created
[Worker] ✓ Multi-tenancy middleware configured
[Worker] ... (completes all criteria)
[Worker] Building Step 2: Frontend... (3 criteria)
[Worker] ✓ Dashboard layout created
[Worker] ... (completes all criteria)
[Worker] Task 1 complete. Checkboxes updated.

[Orchestrator] Task 2: Employee Profile
  → Dependencies: Infrastructure (✓ exists)
  → Spawning worker...
[Worker] ... (builds backend then frontend)
[Worker] Task 2 complete.

[Orchestrator] Task 3: Leave
  → Dependencies: Calendar (checking backend repo...)
  → ICalendarConflictService NOT FOUND
  → SKIPPING — blocked by DEV3 Calendar module

[Orchestrator] Task 4: Productivity Analytics
  → Dependencies: Activity Monitoring (checking backend repo...)
  → IActivityMonitoringService NOT FOUND
  → SKIPPING — blocked by DEV3 Activity Monitoring module

[Orchestrator] Session complete.
  ✓ Completed: Task 1 (Infrastructure), Task 2 (Employee Profile)
  ✗ Blocked: Task 3 (Leave) — needs Calendar from DEV3
  ✗ Blocked: Task 4 (Productivity Analytics) — needs Activity Monitoring from DEV3
  
  Re-run after DEV3 delivers Calendar and Activity Monitoring.
```

---

## Decisions Log

| # | Decision | Choice | Alternatives Considered |
|:--|:---------|:-------|:-----------------------|
| 1 | Payroll in Phase 1? | No — deferred to Phase 2 | Schema stub, data-capture only |
| 2 | Calendar in Phase 1? | Yes — full module as specced | Minimal conflict service only, internal + basic UI |
| 3 | Agent architecture | Orchestrator + Worker agents | One agent per session, one agent per task |
| 4 | Progress tracking | Checkboxes in task files | Git history, separate status file |
| 5 | Parallelism | Dev-scoped sequential, cross-dev parallel | Fully sequential, fully parallel |
| 6 | Blocked task behavior | Skip + report (no checkbox) | Block and wait, build with stubs |
| 7 | After unblocked tasks done | Stop and report | Watch and resume, single pass |
| 8 | Context injection | Layered (base + task-specific) | Minimal (links only), full module dump |
| 9 | Orchestrator location | Brain repo | Backend repo, standalone tool |
| 10 | Repo structure | Three separate repos (backend, frontend, agent) | Monorepo, two repos |
| 11 | Task file labeling | Step 1 / Step 2 (not Phase 1 / Phase 2) | Merged single section |
