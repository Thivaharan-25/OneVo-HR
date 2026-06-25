# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is the **ONEVO knowledge base** - an Obsidian vault that is the single source of truth for architecture, specs, conventions, and sprint tasks for the ONEVO platform. It is not the backend or frontend code repository.

The only runnable code here is the `OneVo/` folder - a Vite + React frontend prototype.

**ONEVO** is a multi-tenant white-label SaaS with three product pillars sharing one backend and one database:
- **HR Management** - employee lifecycle, time_off, performance, payroll, skills
- **Monitoring** - activity monitoring, presence, identity verification, Phase 1 lightweight monitoring alerts, productivity analytics. Full Exception Engine is Phase 2.
- **Work** - Phase 1 simple projects, work items, basic project membership, simple project settings, worklogs, and simple docs/pages where retained. Planner, sprints/boards, OKR, Chat/Chat AI, roadmaps, GitHub/repository automation, and Teams sync are Phase 2 design references (internal modules, NOT a separate system).
- **IDE Extension (Phase 2)** - VS Code sidebar with tag-based automation for all OneVo actions a user has permission for

Platform shape: `OneVo frontend -> OneVo unified backend -> single PostgreSQL database`. No bridge APIs.

## Orientation - Read This Before Any Task

Before doing any work, read these files in order:

1. `AI_CONTEXT/project-context.md` - what ONEVO is, three-pillar architecture
2. `AI_CONTEXT/tech-stack.md` - .NET 10 / C# 14, PostgreSQL, Angular 21 merged customer app + internal dev console, all dependencies
3. `AI_CONTEXT/rules.md` - AI agent rules (backend + frontend + desktop agent)
4. `current-focus/README.md` - active sprint, 8-developer delivery plan
5. `AI_CONTEXT/known-issues.md` - gotchas, deprecated patterns, monitoring data quirks
6. The specific module doc in `modules/` for the module you are working on

**Do not read all module docs** - read only the one relevant to your task.

## Frontend Dev Commands

All commands run from the `onevo-frontend/` workspace root:

```bash
# Customer app
ng serve customer-app               # Dev server
ng build customer-app               # Production build

# Developer Platform console
ng serve dev-console                # Dev server
ng build dev-console                # Production build

# Shared library
ng build shared                # Build library (required before serving apps)

# Lint / test
ng lint                        # ESLint across workspace
ng test customer-app
ng test dev-console
ng e2e                         # Playwright E2E
```

## Architecture Overview

### Backend (implemented in sibling `../Onevo_Backend`)

- **.NET 10 / C# 14** - Clean Architecture, single deployable monolith (`ONEVO.Api`)
- **38 modules** in one solution, strict namespace boundaries
- **CQRS via MediatR** - every use case is a Command or Query handler
- **4-layer multi-tenancy**: JWT claim -> `BaseRepository<T>` auto-filter -> PostgreSQL RLS -> ArchUnit boundary tests
- **Single `ApplicationDbContext`** - WorkSync tables live alongside HR tables, no bridge APIs
- **`Result<T>`** for all business logic returns - never throw exceptions for domain failures
- **Domain events are optional** via in-process MediatR notifications; no RabbitMQ/MassTransit in Phase 1

Feature folder layout:
```text
ONEVO.Domain/Features/{Feature}/{SubFeature}/Entities/
ONEVO.Domain/Features/{Feature}/{SubFeature}/ValueObjects/
ONEVO.Domain/Features/{Feature}/{SubFeature}/Events/                 # optional only when justified

ONEVO.Application/Features/{Feature}/{SubFeature}/Commands/{UseCase}/
  {UseCase}Command.cs
  {UseCase}Handler.cs
  {UseCase}Validator.cs
ONEVO.Application/Features/{Feature}/{SubFeature}/Queries/{UseCase}/
  {UseCase}Query.cs
  {UseCase}Handler.cs
ONEVO.Application/Features/{Feature}/{SubFeature}/DTOs/{Requests,Responses}/
ONEVO.Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/
ONEVO.Application/Features/{Feature}/{SubFeature}/ServiceInterfaces/
ONEVO.Application/Features/{Feature}/{SubFeature}/Mappings/           # optional - manual entity->DTO mapping
ONEVO.Application/Features/{Feature}/{SubFeature}/Helpers/            # optional - pure utility logic, no DI
ONEVO.Application/Features/{Feature}/{SubFeature}/EventHandlers/      # optional only when justified

ONEVO.Application/Common/RepositoryInterfaces/    # cross-feature repo interfaces (e.g. IUnitOfWork)
ONEVO.Application/Common/ServiceInterfaces/       # cross-feature service interfaces
ONEVO.Application/Common/Mappings/               # cross-feature mapping helpers
ONEVO.Application/Common/Helpers/                # cross-feature utility helpers
ONEVO.Application/Common/Extensions/             # IQueryable / LINQ helpers

ONEVO.Infrastructure/Persistence/Configurations/{Feature}/{SubFeature}/{Entity}Configuration.cs
ONEVO.Infrastructure/Persistence/Repositories/{Feature}/{SubFeature}/
ONEVO.Infrastructure/Services/{Feature}/{SubFeature}/                 # non-EF service implementations
ONEVO.Infrastructure/ExternalServices/{ExternalSystem}/
```

Default request flow: `Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response`. Events are by exception, not a default template.

### Frontend (`onevo-frontend/` - Angular workspace)

Two apps in one monorepo: `customer-app` for tenant/company setup, People, Time Off, Time & Attendance, Work, Calendar, Inbox, Monitoring, and Settings; and internal `dev-console` for ONEVO platform operators. Both share a `shared` Angular library.

- **Angular 21**, TypeScript strict mode, standalone components (no NgModules), CSR SPA
- **Angular Router** - typed routes in `app.routes.ts`; functional guards (`CanActivateFn`)
- **Angular HttpClient** - `toSignal()` / `resource()` for signal-integrated async data
- **Angular Signals** - `signal()` / `computed()` / `effect()` for all reactive state (no NgRx, no RxJS BehaviorSubject for UI state)
- **Angular Material 21** + **Tailwind CSS 4** - component library and utility CSS
- **Angular Reactive Forms** + **Zod** - form state and schema validation
- **@microsoft/signalr** wrapped in Angular services - channels: `monitoring-live`, `exception-alerts`, `notifications-{userId}`, `agent-status`
- Permission gating via `*hasPermission="'resource:action'"` structural directive (from shared lib) and `AuthService.hasPermission()`
- New control flow: `@if`, `@for`, `@switch` - never use `*ngIf`, `*ngFor`
- DI via `inject()` function - never constructor injection

### Desktop Agent (separate solution `ONEVO.Agent.sln`)

- **Windows Service** (data collection) + **.NET MAUI** tray app - communicate via Named Pipes IPC
- Device JWT stored via DPAPI; device auth is separate from user auth (`type: "agent"` claim)
- Collectors are **policy-driven** - always check policy toggles before capturing anything
- Activity data collection is **monitoring-lifecycle-gated**: only between clock-in and clock-out

### Database

- **PostgreSQL 16.13 baseline / PostgreSQL 18 target after validation**, ~288 tables across 38 modules, single schema
- **EF Core 10** code-first, snake_case naming convention (EF handles C# <-> DB mapping)
- `DateTimeOffset` for timestamps, `DateOnly` for dates, `Guid` for all PKs
- Encrypted fields via `IEncryptionService` (AES-256)
- Activity tables (`activity_snapshots`, `application_usage`, `activity_raw_buffer`) are **append-only** - never UPDATE them
- Schema files: `database/schemas/` (one file per module); authoritative table list: `database/schema-catalog.md`

## Critical Rules

### Backend
- **Every query must be tenant-scoped** - use `BaseRepository<T>`, never bypass `ITenantContext`
- **Module boundaries are non-negotiable** - only import from another module's `Public/` namespace; never `*.Internal.*`
- **`Result<T>` always** - no exceptions for business logic
- **Async all the way** - every async method takes `CancellationToken`
- **snake_case in DB, PascalCase in C#** - EF Core maps automatically
- All endpoints require `[Authorize]` + `[RequirePermission("resource:action")]`
- **Interface folders**: use `RepositoryInterfaces/` and `ServiceInterfaces/` - never `Interfaces/`, `Repositories/`, or `Services/` as folder names for Application interfaces
- **No AutoMapper** - all entity->DTO mapping via static manual methods in `Mappings/`
- **DevPlatform is the Feature** for all tenant management, subscription, provisioning, billing, and role templates - `Tenancy` is a SubFeature of `DevPlatform`, not a top-level Feature

### Frontend
- File names: `kebab-case.component.ts` / `kebab-case.service.ts` / `kebab-case.guard.ts` / `kebab-case.pipe.ts`
- Component class names: `PascalCaseComponent`; services: `PascalCaseService`
- Standalone components only - `standalone: true` on every `@Component`, `@Directive`, `@Pipe`
- Use `inject()` - never constructor-inject dependencies
- Use `@if` / `@for` / `@switch` - never `*ngIf` / `*ngFor`
- Use `signal()` / `computed()` - never `BehaviorSubject` or `Subject` for component state
- Lazy-load heavy feature routes via `loadComponent` / `loadChildren`
- Forms: Angular Reactive Forms + Zod schema validation (mirrors backend FluentValidation)

### Desktop Agent
- **Count only, never content** - keyboard/mouse event counts only, never keystrokes
- **Hash window titles** via SHA-256 before touching disk
- Agent footprint: <50MB RAM, <2% CPU
- Device JWT != User JWT

### Git
- Commit format: `type(scope): subject` - e.g., `feat(time_off): add approval workflow`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
- Branch prefixes: `feature/`, `bugfix/`, `hotfix/`

## Task Tracking

- When a feature or acceptance criterion is implemented, mark its checkbox in `current-focus/DEV{N}-*.md`
- Update the task **Status** field: `Planned` -> `In Progress` -> `Complete`
- After significant work, create a changelog entry: `AI_CONTEXT/changelog/YYYY-MM-DD-<description>.md`
- Checkboxes live in individual `DEV*.md` files only - not in `current-focus/README.md`

## What NOT to Build in Phase 1

- Phase 2 modules (check `**Phase:**` marker in each module overview)
- Bridge API contracts - `backend/bridge-api-contracts.md` is **DEPRECATED**
- Separate WMS backend or WMS database
- RabbitMQ / MassTransit / IEventBus
- Meilisearch (use PostgreSQL FTS)
- KPI targets or billable rates
- macOS agent

## Key Reference Files

| What you need | Where to look |
|:---|:---|
| Canonical folder structure | `backend/folder-structure.md` |
| All 38 modules + solution structure | `backend/module-catalog.md` |
| Cross-cutting patterns (Result<T>, ITenantContext) | `backend/shared-kernel.md` |
| Module boundary rules | `backend/module-boundaries.md` |
| Backend layer guides (App/Infra/API) | `backend/layer-guide/` |
| CQRS patterns + examples | `backend/cqrs-patterns.md` |
| Backend coding standards | `code-standards/backend-standards.md` |
| All ~288 tables | `database/schema-catalog.md` |
| Foreign key map across pillars | `database/cross-module-relationships.md` |
| Frontend component system | `frontend/design-system/` |
| Frontend routing + layout | `frontend/architecture/` |
| Auth + RBAC | `security/` and `modules/auth/overview.md` |
| Desktop agent full spec | `modules/agent-gateway/` |
| IDE extension full spec | `modules/ide-extension/` |
| Current sprint tasks | `current-focus/DEV{1-8}-*.md` |
| Architecture decisions | `decisions/ADR-*.md` |
