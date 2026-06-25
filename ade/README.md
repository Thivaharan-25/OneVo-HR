# ADE - Agentic Development Environment

## Overview

The ADE enables AI-assisted development. A developer says "I'm Dev N, finish my remaining tasks" and an AI orchestrator manages the work automatically.

The orchestrator lives in this brain repo. It reads task definitions, injects context into worker agents, and tracks progress via checkboxes.

---

## Repos

| Repo | Purpose | ADE Access |
|:-----|:--------|:-----------|
| **Brain repo** (this vault) | Knowledge base, task definitions, rules, specs | Read context + update checkboxes |
| **Backend repo** (.NET 10 / C# 14) | Backend code | Write code (Step 1) |
| **Frontend repo** (Vite + React 19 responsive SPA) | Frontend code | Write code (Step 2) |
| **Desktop Agent repo** (.NET MAUI) | Desktop agent code | Write code (DEV4 agent tasks only) |

---

## Orchestrator Flow

```
Input: dev_id, paths to brain + backend + frontend + agent repos

1. Read all task files: current-focus/DEV{dev_id}-*.md
2. Parse checkboxes - identify unchecked acceptance criteria
3. Determine task order (task # from README table)
4. For each task (SEQUENTIAL):
   a. Read the task file's "Related Tasks" section
   b. Check if cross-dev dependencies exist in the code repos
      - e.g., Does ICalendarConflictService exist in the backend repo?
   c. If dependency MISSING -> SKIP (do NOT mark checkbox)
   d. If dependencies MET -> Spawn worker agent
5. After all tasks processed:
   -> Report: completed tasks, skipped/blocked tasks with reasons
```

### Cross-Dev Dependency Check

The orchestrator checks if required interfaces/services exist in the target code repo before spawning a worker. If a dependency is missing, the task is skipped - **checkboxes are NOT marked** for skipped tasks.

Example check: Before starting DEV1's Time Off task, check if `ICalendarConflictService` exists in the backend repo. If not, skip Time Off and report: "Time Off blocked - Calendar module not found. Re-run after DEV3 delivers."

### Stop and Report

After completing all unblocked tasks, the orchestrator stops and reports:
```
Session complete.
  [done] Completed: Task 1 (Infrastructure), Task 2 (Employee Profile)
  [blocked] Blocked: Task 3 (Time Off) - needs ICalendarConflictService from DEV3 Calendar
  [blocked] Blocked: Task 4 (Productivity Analytics) - needs IActivityMonitoringService from DEV3

  Re-run after DEV3 delivers Calendar and Activity Monitoring.
```

The dev re-runs the ADE manually when blocking dependencies are delivered.

---

## Worker Agent

### Context Injection (Layered)

**Base layer (always injected):**
- `AI_CONTEXT/rules.md`
- `AI_CONTEXT/project-context.md`
- `AI_CONTEXT/tech-stack.md`
- `AI_CONTEXT/known-issues.md`

**Task-specific layer:**
- The task file (e.g., `current-focus/DEV1-time_off.md`)
- All files under the module folder (e.g., `modules/time-off/**`)
- All referenced userflows (e.g., `Userflow/Time-Off/**`)
- Related module overviews if cross-module interaction exists

### Worker Flow

```
1. Receive context (base + task layer)
2. Read unchecked acceptance criteria from task file
3. Execute Step 1: Backend
   - Write code in the BACKEND repo
   - Check off each criterion as completed
   - Commit to backend repo
4. Execute Step 2: Frontend
   - Write code in the FRONTEND repo
   - Check off each criterion as completed
   - Commit to frontend repo
5. Update checkboxes in the BRAIN repo task file
6. Return completion status to orchestrator
```

---

## Parallelism

- **Dev-scoped sequential:** Each dev's ADE session runs tasks 1 -> 2 -> 3 -> ... -> N sequentially (N = task count per dev, read from current-focus/README.md)
- **Cross-dev parallel:** Multiple devs can run their ADE sessions simultaneously (different modules, no conflicts)
- **Step-scoped sequential:** Within each task, Step 1 (backend) completes before Step 2 (frontend) starts

---

## Progress Tracking

- **Checkboxes in task files** are the single source of truth
- Workers mark `- [ ]` -> `- [x]` as they complete each criterion
- Orchestrator reads checkbox state to determine remaining work
- Skipped/blocked tasks time_off checkboxes untouched

---

## How to Run

```
$ ade run --dev {N} --brain ./onevo-hr-brain --backend ./onevo-backend --frontend ./onevo-frontend --agent ./onevo-desktop-agent
```

Where:
- `--dev {N}` - Developer number (1-4)
- `--brain` - Path to this brain repo
- `--backend` - Path to the .NET 10 backend repo
- `--frontend` - Path to the Vite + React 19 frontend repo
- `--agent` - Path to the .NET MAUI desktop agent repo (optional, only needed for DEV4)

---

## Concurrent Brain Repo Writes

When multiple dev ADE sessions run in parallel, each session edits only its own task file (`DEV1-*.md`, `DEV3-*.md`, etc.). No two sessions share a task file, so conflicts on task files are impossible.

If a conflict occurs on `current-focus/README.md` (high-level status only - no checkboxes), accept the latest version from the running session.

If a push conflict occurs: pull, resolve `current-focus/README.md` by keeping both sets of status updates, then re-push.

---

## Related

- [[current-focus/README|Current Focus]] - Task assignments and dependency chain
- [[AI_CONTEXT/rules|Rules]] - AI agent coding rules
- [[AI_CONTEXT/project-context|Project Context]] - System architecture
- [[docs/superpowers/specs/2026-04-08-phase1-restructure-and-ade-design|Design Spec]] - Full design decisions and rationale
