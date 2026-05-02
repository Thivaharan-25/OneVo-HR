# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is the **ONEVO knowledge base** — an Obsidian vault that is the single source of truth for architecture, specs, conventions, and sprint tasks for the ONEVO platform. It is not the backend or frontend code repository.

The only runnable code here is the `OneVo/` folder — a Vite + React frontend prototype.

**ONEVO** is a multi-tenant white-label SaaS with three product pillars sharing one backend and one database:
- **HR Management** — employee lifecycle, leave, performance, payroll, skills
- **Workforce Intelligence** — activity monitoring, presence, identity verification, exception engine, productivity analytics
- **WorkSync** — projects, tasks, sprints, OKR, chat, documents, roadmaps, GitHub integration (internal modules, NOT a separate system)
- **IDE Extension** — VS Code sidebar with tag-based automation for all OneVo actions a user has permission for

Platform shape: `OneVo frontend → OneVo unified backend → single PostgreSQL database`. No bridge APIs.

## Orientation — Read This Before Any Task

Before doing any work, read these files in order:

1. `AI_CONTEXT/project-context.md` — what ONEVO is, three-pillar architecture
2. `AI_CONTEXT/tech-stack.md` — .NET 9, PostgreSQL, Vite + React 19, all dependencies
3. `AI_CONTEXT/rules.md` — AI agent rules (backend + frontend + desktop agent)
4. `current-focus/README.md` — active sprint, 8-developer delivery plan
5. `AI_CONTEXT/known-issues.md` — gotchas, deprecated patterns, monitoring data quirks
6. The specific module doc in `modules/` for the module you are working on

**Do not read all module docs** — read only the one relevant to your task.

## Frontend Dev Commands

All commands run from the `OneVo/` directory:

```bash
cd OneVo
npm run dev       # Start dev server (Vite)
npm run build     # Production build
npm run lint      # ESLint
npm run preview   # Preview production build
```

## Architecture Overview

### Backend (spec only — not yet built in this repo)

- **.NET 9** — Clean Architecture, single deployable monolith (`ONEVO.Api`)
- **38 modules** in one solution, strict namespace boundaries
- **CQRS via MediatR** — every use case is a Command or Query handler
- **4-layer multi-tenancy**: JWT claim → `BaseRepository<T>` auto-filter → PostgreSQL RLS → ArchUnit boundary tests
- **Single `ApplicationDbContext`** — WorkSync tables live alongside HR tables, no bridge APIs
- **`Result<T>`** for all business logic returns — never throw exceptions for domain failures
- **Domain events** via in-process MediatR notifications — no RabbitMQ/MassTransit in Phase 1

Feature folder layout:
```
ONEVO.Domain/Features/{Feature}/Entities/  +  Events/
ONEVO.Application/Features/{Feature}/Commands/{UseCase}/  Queries/  DTOs/  Validators/  EventHandlers/
ONEVO.Infrastructure/Persistence/Configurations/{Feature}/{Entity}Configuration.cs
```

### Frontend (`OneVo/`)

- **Vite + React 19**, TypeScript strict mode, CSR SPA
- **React Router v7** — route config in `src/router.tsx`
- **TanStack Query v5** — all server state; `queryKey: ['resource', params]` pattern
- **Zustand 4** — client state (sidebar, filters, UI preferences, monitoring config cache)
- **shadcn/ui** (Radix primitives) + **Tailwind CSS** + **Framer Motion**
- **SignalR** — channels: `workforce-live`, `exception-alerts`, `notifications-{userId}`, `agent-status`
- Permission gating via `<PermissionGate permission="resource:action">` and `useAuth().hasPermission()`

### Desktop Agent (separate solution `ONEVO.Agent.sln`)

- **Windows Service** (data collection) + **.NET MAUI** tray app — communicate via Named Pipes IPC
- Device JWT stored via DPAPI; device auth is separate from user auth (`type: "agent"` claim)
- Collectors are **policy-driven** — always check policy toggles before capturing anything
- Activity data collection is **monitoring-lifecycle-gated**: only between clock-in and clock-out

### Database

- **PostgreSQL 16**, ~288 tables across 38 modules, single schema
- **EF Core 9** code-first, snake_case naming convention (EF handles C# ↔ DB mapping)
- `DateTimeOffset` for timestamps, `DateOnly` for dates, `Guid` for all PKs
- Encrypted fields via `IEncryptionService` (AES-256)
- Activity tables (`activity_snapshots`, `application_usage`, `activity_raw_buffer`) are **append-only** — never UPDATE them
- Schema files: `database/schemas/` (one file per module); authoritative table list: `database/schema-catalog.md`

## Critical Rules

### Backend
- **Every query must be tenant-scoped** — use `BaseRepository<T>`, never bypass `ITenantContext`
- **Module boundaries are non-negotiable** — only import from another module's `Public/` namespace; never `*.Internal.*`
- **`Result<T>` always** — no exceptions for business logic
- **Async all the way** — every async method takes `CancellationToken`
- **snake_case in DB, PascalCase in C#** — EF Core maps automatically
- All endpoints require `[Authorize]` + `[RequirePermission("resource:action")]`

### Frontend
- File names: `kebab-case.tsx` / `kebab-case.ts`; component names: `PascalCase`; hooks: `useCamelCase`; Zustand stores: `useCamelCaseStore`
- Default to interactive React components — CSR only, no Next.js APIs
- Use `React.lazy` + `Suspense` for heavy routes
- Forms: React Hook Form + Zod (mirrors backend FluentValidation)

### Desktop Agent
- **Count only, never content** — keyboard/mouse event counts only, never keystrokes
- **Hash window titles** via SHA-256 before touching disk
- Agent footprint: <50MB RAM, <2% CPU
- Device JWT ≠ User JWT

### Git
- Commit format: `type(scope): subject` — e.g., `feat(leave): add approval workflow`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
- Branch prefixes: `feature/`, `bugfix/`, `hotfix/`

## Task Tracking

- When a feature or acceptance criterion is implemented, mark its checkbox in `current-focus/DEV{N}-*.md`
- Update the task **Status** field: `Planned` → `In Progress` → `Complete`
- After significant work, create a changelog entry: `AI_CONTEXT/changelog/YYYY-MM-DD-<description>.md`
- Checkboxes live in individual `DEV*.md` files only — not in `current-focus/README.md`

## What NOT to Build in Phase 1

- Phase 2 modules (check `**Phase:**` marker in each module overview)
- Bridge API contracts — `backend/bridge-api-contracts.md` is **DEPRECATED**
- Separate WMS backend or WMS database
- RabbitMQ / MassTransit / IEventBus
- Meilisearch (use PostgreSQL FTS)
- JetBrains plugin (VS Code only)
- KPI targets or billable rates
- macOS agent

## Key Reference Files

| What you need | Where to look |
|:---|:---|
| All 38 modules + solution structure | `backend/module-catalog.md` |
| Cross-cutting patterns (Result<T>, ITenantContext) | `backend/shared-kernel.md` |
| Module boundary rules | `backend/module-boundaries.md` |
| All ~288 tables | `database/schema-catalog.md` |
| Foreign key map across pillars | `database/cross-module-relationships.md` |
| Frontend component system | `frontend/design-system/` |
| Frontend routing + layout | `frontend/architecture/` |
| Auth + RBAC | `security/` and `modules/auth/overview.md` |
| Desktop agent full spec | `modules/agent-gateway/` |
| IDE extension full spec | `modules/ide-extension/` |
| Current sprint tasks | `current-focus/DEV{1-8}-*.md` |
| Architecture decisions | `decisions/ADR-*.md` |
