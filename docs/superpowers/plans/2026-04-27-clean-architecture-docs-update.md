# Clean Architecture + CQRS — Documentation Update Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update all 62 documentation files to reflect the Clean Architecture + CQRS redesign, eliminating every reference to the modular monolith, RabbitMQ, MassTransit, per-module DbContexts, IEventBus, and 24-module project structure.

**Architecture:** Documentation-only plan — no .NET code written yet. All changes are markdown files. The spec lives at `docs/superpowers/specs/2026-04-27-clean-architecture-cqrs-design.md` and is the single source of truth for content decisions.

**Tech Stack:** Markdown, Git

---

## File Map

| Action | Count | Tasks |
|---|---|---|
| DELETE | 5 | Task 1 |
| SUPERSEDE | 1 | Task 2 |
| FULL REWRITE | 5 | Tasks 3–7 |
| CREATE NEW — ADRs | 2 | Tasks 8–9 |
| CREATE NEW — Architecture docs | 8 | Tasks 10–17 |
| CREATE NEW — Agent docs | 2 | Tasks 18–19 |
| PARTIAL UPDATE — backend | 8 | Tasks 20–27 |
| PARTIAL UPDATE — dev-platform | 8 | Task 28 |
| PARTIAL UPDATE — module features | 24 | Task 29 |

---

## Task 1: Delete RabbitMQ messaging docs

**Files:**
- Delete: `backend/messaging/README.md`
- Delete: `backend/messaging/error-handling.md`
- Delete: `backend/messaging/event-catalog.md`
- Delete: `backend/messaging/module-event-matrix.md`
- Delete: `backend/messaging/exchange-topology.md`

- [ ] **Step 1: Remove all 5 files and the directory**

```bash
git rm backend/messaging/README.md
git rm backend/messaging/error-handling.md
git rm backend/messaging/event-catalog.md
git rm backend/messaging/module-event-matrix.md
git rm backend/messaging/exchange-topology.md
```

- [ ] **Step 2: Verify directory is gone**

```bash
ls backend/messaging/
```
Expected: `ls: cannot access 'backend/messaging/': No such file or directory`

- [ ] **Step 3: Commit**

```bash
git commit -m "docs: remove RabbitMQ messaging docs — replaced by domain-events.md"
```

---

## Task 2: Supersede ADR-001

**Files:**
- Modify: `docs/decisions/ADR-001-per-module-database-and-event-bus.md`

- [ ] **Step 1: Read the file, then prepend the superseded header**

Open `docs/decisions/ADR-001-per-module-database-and-event-bus.md` and add this block at the very top, before the existing title:

```markdown
> **Status: SUPERSEDED**
> Superseded by [ADR-002](ADR-002-clean-architecture-cqrs.md) and [ADR-003](ADR-003-single-applicationdbcontext.md) on 2026-04-27.
> Reason: Clean Architecture adopted. Microservice extraction path dropped. RabbitMQ removed. Per-module DbContexts consolidated into single ApplicationDbContext.

---

```

- [ ] **Step 2: Commit**

```bash
git add docs/decisions/ADR-001-per-module-database-and-event-bus.md
git commit -m "docs: supersede ADR-001 — replaced by ADR-002 and ADR-003"
```

---

## Task 3: Rewrite backend/folder-structure.md

**Files:**
- Rewrite: `backend/folder-structure.md`

- [ ] **Step 1: Replace the entire file with the following content**

```markdown
# Solution Folder Structure: ONEVO

**Last Updated:** 2026-04-27

The canonical reference for ONEVO backend organisation. All other docs defer to this file for structure questions.

---

## Architecture

ONEVO follows **Clean Architecture + CQRS** (.NET 9). The solution is divided into four layer projects and two host projects. Modules from the earlier design become **feature folders** within each layer — there are no separate module `.csproj` files.

The desktop monitoring agent is a **separate solution** (`ONEVO.Agent.sln`) with its own release cycle.

---

## ONEVO.sln — Complete Structure

```
ONEVO.sln
├── src/
│   │
│   │  ── LAYER 1: DOMAIN ──
│   ├── ONEVO.Domain/
│   │   ├── Common/
│   │   │   ├── BaseEntity.cs              # Id (UUID v7), TenantId, CreatedAt, UpdatedAt,
│   │   │   │                              #   CreatedById, IsDeleted, List<IDomainEvent>
│   │   │   ├── IDomainEvent.cs            # : INotification (MediatR) — replaces IEventBus
│   │   │   └── ValueObject.cs             # Immutable value type base class
│   │   ├── Enums/                         # EmploymentType, ApprovalStatus, Severity, WorkMode…
│   │   ├── Errors/
│   │   │   ├── DomainException.cs
│   │   │   ├── NotFoundException.cs
│   │   │   └── ForbiddenException.cs
│   │   ├── ValueObjects/
│   │   │   ├── Email.cs
│   │   │   ├── Money.cs
│   │   │   ├── PhoneNumber.cs
│   │   │   └── Address.cs
│   │   └── Features/                      # 24 feature folders — entities + domain events
│   │       ├── Auth/Entities/ + Events/
│   │       ├── InfrastructureModule/      # ← named InfrastructureModule to avoid collision
│   │       │   Entities/ + Events/        #   with ONEVO.Infrastructure layer project
│   │       ├── OrgStructure/Entities/ + Events/
│   │       ├── CoreHR/Entities/ + Events/
│   │       ├── Leave/Entities/ + Events/
│   │       ├── Payroll/Entities/ + Events/
│   │       ├── Performance/Entities/ + Events/
│   │       ├── Skills/Entities/ + Events/
│   │       ├── Documents/Entities/ + Events/
│   │       ├── WorkforcePresence/Entities/ + Events/
│   │       ├── ActivityMonitoring/Entities/ + Events/
│   │       ├── IdentityVerification/Entities/ + Events/
│   │       ├── ExceptionEngine/Entities/ + Events/
│   │       ├── DiscrepancyEngine/Entities/ + Events/
│   │       ├── ProductivityAnalytics/Entities/ + Events/
│   │       ├── SharedPlatform/Entities/ + Events/
│   │       ├── Notifications/Entities/ + Events/
│   │       ├── Configuration/Entities/ + Events/
│   │       ├── Calendar/Entities/ + Events/
│   │       ├── ReportingEngine/Entities/ + Events/
│   │       ├── Grievance/Entities/ + Events/
│   │       ├── Expense/Entities/ + Events/
│   │       ├── AgentGateway/Entities/ + Events/
│   │       └── DevPlatform/Entities/ + Events/
│   │
│   │  ── LAYER 2: APPLICATION ──
│   ├── ONEVO.Application/
│   │   ├── Common/
│   │   │   ├── Behaviors/
│   │   │   │   ├── ValidationBehavior.cs
│   │   │   │   ├── LoggingBehavior.cs
│   │   │   │   ├── PerformanceBehavior.cs
│   │   │   │   └── UnhandledExceptionBehavior.cs
│   │   │   ├── Interfaces/
│   │   │   │   ├── IApplicationDbContext.cs
│   │   │   │   ├── IRepository.cs             # IRepository<T> generic
│   │   │   │   ├── IUnitOfWork.cs
│   │   │   │   ├── ICurrentUser.cs
│   │   │   │   ├── ICacheService.cs
│   │   │   │   ├── IEncryptionService.cs
│   │   │   │   ├── IEmailService.cs
│   │   │   │   ├── IStorageService.cs
│   │   │   │   ├── IDateTimeProvider.cs
│   │   │   │   ├── IBackgroundJobService.cs
│   │   │   │   ├── INotificationDispatcher.cs
│   │   │   │   ├── ITokenService.cs
│   │   │   │   └── IPasswordHasher.cs
│   │   │   └── Models/
│   │   │       ├── Result.cs
│   │   │       ├── PagedRequest.cs
│   │   │       └── PagedResult.cs
│   │   ├── Features/                          # 24 feature folders
│   │   │   └── {Feature}/
│   │   │       ├── Commands/{UseCase}/
│   │   │       │   ├── {UseCase}Command.cs    # record : IRequest<Result<ResponseDto>>
│   │   │       │   └── {UseCase}Handler.cs
│   │   │       ├── Queries/{UseCase}/
│   │   │       │   ├── {UseCase}Query.cs
│   │   │       │   └── {UseCase}Handler.cs
│   │   │       ├── DTOs/
│   │   │       │   ├── Requests/              # HTTP request body models
│   │   │       │   └── Responses/             # handler return types
│   │   │       ├── Validators/
│   │   │       └── EventHandlers/             # INotificationHandler<IDomainEvent>
│   │   └── DependencyInjection.cs
│   │
│   │  ── LAYER 3: INFRASTRUCTURE ──
│   ├── ONEVO.Infrastructure/
│   │   ├── Persistence/
│   │   │   ├── ApplicationDbContext.cs        # ALL 176 tables, global tenant + soft-delete filters
│   │   │   ├── ApplicationDbContextFactory.cs
│   │   │   ├── Migrations/                    # ONE migration set
│   │   │   ├── Interceptors/
│   │   │   │   ├── AuditableEntityInterceptor.cs
│   │   │   │   ├── SoftDeleteInterceptor.cs
│   │   │   │   └── DomainEventDispatchInterceptor.cs
│   │   │   ├── Configurations/                # IEntityTypeConfiguration<T> per entity
│   │   │   │   └── {Feature}/                 # 24 feature folders
│   │   │   ├── Repositories/
│   │   │   │   └── GenericRepository.cs
│   │   │   └── UnitOfWork.cs
│   │   ├── Identity/
│   │   │   ├── JwtTokenService.cs
│   │   │   ├── CurrentUserService.cs
│   │   │   ├── PasswordHasher.cs              # BCrypt WorkFactor=12
│   │   │   └── PermissionService.cs
│   │   ├── Caching/
│   │   │   ├── RedisCacheService.cs
│   │   │   └── CacheKeys.cs
│   │   ├── BackgroundJobs/
│   │   │   ├── HangfireConfiguration.cs
│   │   │   ├── Queues.cs
│   │   │   └── BackgroundJobService.cs
│   │   ├── RealTime/
│   │   │   ├── SignalRNotificationDispatcher.cs
│   │   │   └── HubRegistration.cs
│   │   ├── Email/SmtpEmailService.cs
│   │   ├── Storage/BlobStorageService.cs
│   │   ├── Security/AesEncryptionService.cs
│   │   ├── ExternalServices/WmsBridgeClient.cs
│   │   └── DependencyInjection.cs
│   │
│   │  ── LAYER 4: HOSTS ──
│   │
│   ├── ONEVO.Api/                             # Customer-facing host (/api/v1/*)
│   │   ├── Controllers/                       # One per feature, all thin
│   │   ├── Hubs/
│   │   │   ├── WorkforceLiveHub.cs
│   │   │   ├── ExceptionAlertsHub.cs
│   │   │   ├── NotificationsHub.cs
│   │   │   └── AgentStatusHub.cs
│   │   ├── Middleware/
│   │   │   ├── TenantResolutionMiddleware.cs
│   │   │   ├── PermissionMiddleware.cs
│   │   │   └── ExceptionHandlerMiddleware.cs  # RFC 7807
│   │   ├── Filters/RequirePermissionAttribute.cs
│   │   └── Program.cs
│   │
│   └── ONEVO.Admin.Api/                       # Developer console host (/admin/v1/*)
│       ├── Controllers/
│       ├── Middleware/PlatformAdminAuthMiddleware.cs
│       ├── Policies/
│       └── Program.cs
│
├── tests/
│   ├── ONEVO.Tests.Unit/
│   │   └── Features/                          # Per-feature handler tests
│   ├── ONEVO.Tests.Integration/
│   │   └── Features/                          # Real DB via Testcontainers
│   └── ONEVO.Tests.Architecture/
│       └── LayerDependencyTests.cs            # ArchUnitNET — enforces dependency rule
│
└── tools/
    └── ONEVO.DbMigrator/                      # CLI — runs ApplicationDbContext migrations
```

---

## ONEVO.Agent.sln — Separate Solution

See `backend/agent/overview.md` for full detail.

```
ONEVO.Agent.sln
├── src/
│   ├── ONEVO.Agent.Core/          # Pure logic — no OS deps
│   ├── ONEVO.Agent.Windows/       # Windows tray app + capture (Phase 1)
│   └── ONEVO.Agent.Infrastructure/ # HTTP client to ONEVO.Api
└── tests/
    └── ONEVO.Agent.Tests.Unit/
```

---

## Layer Dependency Rule

```
ONEVO.Api / ONEVO.Admin.Api
        ↓
ONEVO.Application  ←  ONEVO.Infrastructure
        ↓
ONEVO.Domain

FORBIDDEN:
  Application → Infrastructure
  Domain → anything
```

Enforced by ArchUnitNET tests in `ONEVO.Tests.Architecture`.

---

## Host Project Rules

Both host projects are **composition roots only** — no business logic, no DbContext.

| What | Correct Location |
|---|---|
| MediatR handler | `ONEVO.Application/Features/{Feature}/Commands/` or `Queries/` |
| Interface definition | `ONEVO.Application/Common/Interfaces/` |
| Interface implementation | `ONEVO.Infrastructure/` |
| Entity | `ONEVO.Domain/Features/{Feature}/Entities/` |
| EF configuration | `ONEVO.Infrastructure/Persistence/Configurations/{Feature}/` |
| Migration | `ONEVO.Infrastructure/Persistence/Migrations/` |
| Controller | `ONEVO.Api/Controllers/{Feature}/` — thin only |
| DbContext | `ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs` only |

---

## Related

- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/layer-guide/webapi-layer|WebApi Layer Guide]]
- [[backend/module-catalog|Module Catalog]] — feature registry
- [[backend/security|Security Implementation]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/agent/overview|Agent Overview]]
- [[docs/decisions/ADR-002-clean-architecture-cqrs|ADR-002]]
```

- [ ] **Step 2: Commit**

```bash
git add backend/folder-structure.md
git commit -m "docs: rewrite folder-structure.md for Clean Architecture 4-layer solution"
```

---

## Task 4: Rewrite backend/module-catalog.md

**Files:**
- Rewrite: `backend/module-catalog.md`

- [ ] **Step 1: Replace the entire file with the following content**

```markdown
# Feature Catalog: ONEVO

**Last Updated:** 2026-04-27

## Architecture Overview

ONEVO follows **Clean Architecture + CQRS** (.NET 9). The 24 features that were previously separate module projects are now **feature folders** within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`.

There are **no separate module `.csproj` files**. All 176 tables live in a single `ApplicationDbContext`.

See [[backend/folder-structure|Folder Structure]] for the full solution layout.

---

## Unified Platform Model

```
ONEVO PLATFORM
  ONEVO Frontend (Next.js)
    ├── HR Sidebar        → ONEVO.Api (.NET 9)
    └── Workforce Sidebar → ONEVO.Api + WMS Backend
                                    ↕ bridge contracts
  ONEVO.Api                      WMS Backend
  All features in one host       Projects, Tasks, Sprints…
```

---

## Product Configuration Matrix

| Tier | Core | HR Pillar | Workforce Intel | WMS | Bridges |
|------|:----:|:---------:|:---------------:|:---:|:-------:|
| HR Management | ✓ | ✓ | ✗ | ✗ | — |
| Work Management | ✓ | ✗ | ✗ | ✓ | People Sync only |
| HR + Workforce Intel | ✓ | ✓ | ✓ | ✗ | — |
| HR + Work Management | ✓ | ✓ | ✗ | ✓ | All 5 bridges |
| Full Suite | ✓ | ✓ | ✓ | ✓ | All 5 bridges |

---

## Feature Registry

### Pillar 1: HR Management

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 1 | Infrastructure | `Features/InfrastructureModule` | 4 | Phase 1 |
| 2 | Auth & Security | `Features/Auth` | 9 | Phase 1 |
| 3 | Org Structure | `Features/OrgStructure` | 9 | Phase 1 |
| 4 | Core HR | `Features/CoreHR` | 13 | Phase 1 |
| 5 | Leave | `Features/Leave` | 5 | Phase 1 |
| 6 | Payroll | `Features/Payroll` | 11 | Phase 2 |
| 7 | Performance | `Features/Performance` | 7 | Phase 2 |
| 8 | Skills & Learning | `Features/Skills` | 15 (5 P1 + 10 P2) | Mixed |
| 9 | Documents | `Features/Documents` | 6 | Phase 2 |

### Pillar 2: Workforce Intelligence

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 10 | Workforce Presence | `Features/WorkforcePresence` | 12 | Phase 1 |
| 11 | Activity Monitoring | `Features/ActivityMonitoring` | 9 | Phase 1 |
| 11a | Discrepancy Engine | `Features/DiscrepancyEngine` | 2 | Phase 1 |
| 12 | Identity Verification | `Features/IdentityVerification` | 6 | Phase 1 |
| 13 | Exception Engine | `Features/ExceptionEngine` | 5 | Phase 1 |
| 14 | Productivity Analytics | `Features/ProductivityAnalytics` | 5 | Phase 1 |

### Shared Foundation

| # | Feature | Feature Folder | Tables | Phase |
|:--|:--------|:---------------|:-------|:------|
| 15 | Shared Platform | `Features/SharedPlatform` | 33 | Phase 1 |
| 16 | Notifications | `Features/Notifications` | 2 | Phase 1 |
| 17 | Configuration | `Features/Configuration` | 6 | Phase 1 |
| 18 | Calendar | `Features/Calendar` | 1 | Phase 1 |
| 19 | Reporting Engine | `Features/ReportingEngine` | 3 | Phase 2 |
| 20 | Grievance | `Features/Grievance` | 2 | Phase 2 |
| 21 | Expense | `Features/Expense` | 3 | Phase 2 |
| 22 | Agent Gateway | `Features/AgentGateway` | 4 | Phase 1 |
| 23 | Dev Platform | `Features/DevPlatform` | 5 (P1) + 1 (P2) | Mixed |

**Total: 24 features, 176 tables (133 Phase 1 · 43 Phase 2)**

---

## Feature Folder Structure

Every feature follows this exact layout within `ONEVO.Application/Features/` and `ONEVO.Domain/Features/`:

```
# Domain layer
ONEVO.Domain/Features/{Feature}/
├── Entities/       EF Core entities (no attributes — configured via Fluent API)
└── Events/         IDomainEvent implementations

# Application layer
ONEVO.Application/Features/{Feature}/
├── Commands/{UseCase}/
│   ├── {UseCase}Command.cs      record : IRequest<Result<ResponseDto>>
│   └── {UseCase}Handler.cs      IRequestHandler<Command, Result<ResponseDto>>
├── Queries/{UseCase}/
│   ├── {UseCase}Query.cs
│   └── {UseCase}Handler.cs
├── DTOs/
│   ├── Requests/                HTTP request body models
│   └── Responses/               handler return types
├── Validators/                  AbstractValidator<{UseCase}Command>
└── EventHandlers/               INotificationHandler<IDomainEvent>

# Infrastructure layer
ONEVO.Infrastructure/Persistence/Configurations/{Feature}/
└── {Entity}Configuration.cs    IEntityTypeConfiguration<T>
```

---

## Cross-Feature Communication

| Need | Mechanism |
|------|-----------|
| Read data from another feature | Inject `IApplicationDbContext` or `IRepository<T>` — query directly |
| Trigger side effect in another feature | Entity raises `IDomainEvent`; `DomainEventDispatchInterceptor` dispatches after save |
| React to another feature's event | `INotificationHandler<TEvent>` in `EventHandlers/` |
| Background processing | `IBackgroundJobService` (Hangfire) injected in handler |

No RabbitMQ. No IEventBus. No MassTransit. All communication is in-process.

---

## Developer Platform — Admin API

`ONEVO.Admin.Api` is a separate host inside `ONEVO.sln`. It is not a feature — it has no DbContext. All data access goes through `IApplicationDbContext` via the Application layer exactly like `ONEVO.Api`.

| Aspect | Detail |
|:-------|:-------|
| Host project | `ONEVO.Admin.Api` — separate `Program.cs` |
| JWT Issuer | `onevo-platform-admin` — never valid at `/api/v1/*` |
| Feature data | `Features/DevPlatform` — no TenantId on these entities |

---

## WMS — Consumed System

WMS is external. ONEVO communicates via HTTP bridge contracts only.

Full detail: [[backend/bridge-api-contracts|Bridge API Contracts]]
```

- [ ] **Step 2: Commit**

```bash
git add backend/module-catalog.md
git commit -m "docs: rewrite module-catalog.md — 24 module projects become feature folders"
```

---

## Task 5: Rewrite backend/module-boundaries.md

**Files:**
- Rewrite: `backend/module-boundaries.md`

- [ ] **Step 1: Replace the entire file with the following content**

```markdown
# Layer Boundary Rules: ONEVO

**Last Updated:** 2026-04-27

These rules keep the ONEVO Clean Architecture maintainable. **Non-negotiable.**

AI agents: these rules override convenience. Never generate code that violates layer dependencies.

---

## The Dependency Rule

Dependencies point inward only. Outer layers know about inner layers — never the reverse.

```
ONEVO.Api / ONEVO.Admin.Api  (outermost)
        ↓
ONEVO.Application  ←  ONEVO.Infrastructure
        ↓
ONEVO.Domain  (innermost — zero external dependencies)
```

### What each layer may reference

| Layer | May reference |
|-------|--------------|
| `ONEVO.Domain` | Nothing |
| `ONEVO.Application` | `ONEVO.Domain` only |
| `ONEVO.Infrastructure` | `ONEVO.Application` + `ONEVO.Domain` |
| `ONEVO.Api` / `ONEVO.Admin.Api` | `ONEVO.Application` + `ONEVO.Infrastructure` (DI wiring only) |

---

## Rule 1: Application defines interfaces — Infrastructure implements them

```csharp
// CORRECT: interface in Application
// ONEVO.Application/Common/Interfaces/IEmailService.cs
public interface IEmailService
{
    Task SendAsync(string to, string subject, string body, CancellationToken ct);
}

// CORRECT: implementation in Infrastructure
// ONEVO.Infrastructure/Email/SmtpEmailService.cs
public class SmtpEmailService : IEmailService { ... }

// FORBIDDEN: implementation reference in Application handler
using ONEVO.Infrastructure.Email; // ← never
```

---

## Rule 2: Domain has zero framework dependencies

Domain entities have no EF Core attributes. No `[Key]`, no `[Column]`, no `[Required]`.
All mapping is done via `IEntityTypeConfiguration<T>` in Infrastructure.

```csharp
// CORRECT
public class LeaveRequest : BaseEntity
{
    public Guid EmployeeId { get; private set; }
    public DateTime StartDate { get; private set; }
    // ...
    public void Approve()
    {
        Status = ApprovalStatus.Approved;
        AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId));
    }
}

// FORBIDDEN
[Table("leave_requests")]      // ← EF attribute in Domain
public class LeaveRequest { }
```

---

## Rule 3: Handlers return Result<T> — never throw for business failures

```csharp
// CORRECT
public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand cmd, CancellationToken ct)
{
    if (employee is null)
        return Result<LeaveRequestDto>.Failure("Employee not found");
    // ...
    return Result<LeaveRequestDto>.Success(dto);
}

// FORBIDDEN
if (employee is null)
    throw new Exception("Employee not found"); // ← only for infrastructure failures
```

---

## Rule 4: Cross-feature reads go through IApplicationDbContext

Features do not have isolated DbContexts. A handler may query any DbSet it needs.

```csharp
// CORRECT: Leave handler reading employee data
public class CreateLeaveRequestHandler : IRequestHandler<...>
{
    private readonly IApplicationDbContext _db;

    public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand cmd, CancellationToken ct)
    {
        var employee = await _db.Employees
            .FirstOrDefaultAsync(e => e.Id == cmd.EmployeeId, ct);
        // ...
    }
}

// FORBIDDEN: direct DbContext in handler
private readonly ApplicationDbContext _db; // ← concrete, not interface
```

---

## Rule 5: Cross-feature side effects use domain events

When feature A does something that feature B should react to, feature A raises a domain event. Feature B handles it with `INotificationHandler<T>`.

```csharp
// Feature A (Leave) — entity raises event
public void Approve()
{
    Status = ApprovalStatus.Approved;
    AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId)); // ← raises event
}

// Feature B (WorkforcePresence) — reacts in EventHandlers/
public class MarkShiftAbsentOnLeaveApprovedHandler
    : INotificationHandler<LeaveApprovedEvent>
{
    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // mark shift absent
    }
}
```

Events are dispatched **after** `SaveChangesAsync` succeeds via `DomainEventDispatchInterceptor`. If the DB write fails, no events fire.

**What is gone:** `IEventBus`, `IntegrationEvent`, MassTransit, RabbitMQ, Outbox tables.

---

## Rule 6: CancellationToken everywhere

Every handler, repository call, and external HTTP call receives `CancellationToken ct`.

```csharp
// CORRECT
public async Task<Result<T>> Handle(TCommand cmd, CancellationToken ct)
{
    var entity = await _db.Set<T>().FirstOrDefaultAsync(x => x.Id == cmd.Id, ct);
    await _uow.SaveChangesAsync(ct);
}

// FORBIDDEN
await _db.Set<T>().FirstOrDefaultAsync(x => x.Id == cmd.Id); // ← no ct
```

---

## Rule 7: DevPlatform entities have no TenantId

`ApplicationDbContext` applies global tenant filters to all `BaseEntity` instances. `DevPlatformAccount`, `DevPlatformSession`, `AgentVersionRelease`, `AgentDeploymentRing`, `AgentDeploymentRingAssignment` are platform-level entities with no `TenantId` — they use a separate base class and are excluded from tenant filters.

---

## ArchUnitNET Enforcement

```csharp
[Fact]
public void Domain_Should_Not_Reference_Any_Other_Layer()
{
    Types().That().ResideInNamespace("ONEVO.Domain")
        .Should().NotDependOnAnyTypesThat()
        .ResideInNamespace("ONEVO.Application")
        .OrResideInNamespace("ONEVO.Infrastructure")
        .Check(Architecture);
}

[Fact]
public void Application_Should_Not_Reference_Infrastructure()
{
    Types().That().ResideInNamespace("ONEVO.Application")
        .Should().NotDependOnAnyTypesThat()
        .ResideInNamespace("ONEVO.Infrastructure")
        .Check(Architecture);
}

[Fact]
public void Handlers_Should_Not_Use_Concrete_DbContext()
{
    Types().That().HaveNameEndingWith("Handler")
        .Should().NotDependOnAnyTypesThat()
        .HaveExactlyName("ApplicationDbContext")
        .Check(Architecture);
}
```
```

- [ ] **Step 2: Commit**

```bash
git add backend/module-boundaries.md
git commit -m "docs: rewrite module-boundaries.md — layer rules replace module boundary rules"
```

---

## Task 6: Rewrite backend/shared-kernel.md

**Files:**
- Rewrite: `backend/shared-kernel.md`

- [ ] **Step 1: Replace the entire file with the following content**

```markdown
# ONEVO.Domain — Layer Guide

**Last Updated:** 2026-04-27

The innermost layer. Contains pure business entities and rules. **Zero external dependencies** — no EF Core, no MediatR attributes, no framework code.

> This file replaces the former SharedKernel documentation. The `ONEVO.SharedKernel` project no longer exists. Its contents have been redistributed into `ONEVO.Domain` (entities, value objects, enums, errors) and `ONEVO.Application/Common/` (interfaces, models).

---

## What lives in ONEVO.Domain

### Common/BaseEntity.cs

```csharp
public abstract class BaseEntity
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
    public Guid CreatedById { get; set; }
    public bool IsDeleted { get; set; } = false;

    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void AddDomainEvent(IDomainEvent domainEvent)
        => _domainEvents.Add(domainEvent);

    public void ClearDomainEvents()
        => _domainEvents.Clear();
}
```

### Common/IDomainEvent.cs

```csharp
public interface IDomainEvent : INotification { } // INotification from MediatR
```

This is the **only** MediatR reference in Domain — and only because MediatR's `INotification` is a marker interface with no implementation. Domain events replace `IEventBus` + RabbitMQ entirely.

### Common/ValueObject.cs

```csharp
public abstract class ValueObject
{
    protected abstract IEnumerable<object> GetEqualityComponents();

    public override bool Equals(object? obj) { ... }
    public override int GetHashCode() { ... }
}
```

### Enums/

All shared enums used across features:
- `EmploymentType` (FullTime, PartTime, Contract, Intern)
- `EmploymentStatus` (Active, OnLeave, Suspended, Terminated)
- `ApprovalStatus` (Pending, Approved, Rejected, Cancelled)
- `Severity` (Low, Medium, High, Critical)
- `WorkMode` (OnSite, Remote, Hybrid)

### Errors/

- `DomainException` — business rule violation, maps to HTTP 422
- `NotFoundException` — entity not found, maps to HTTP 404
- `ForbiddenException` — permission denied, maps to HTTP 403

### ValueObjects/

Immutable types validated on construction:
- `Email` — validates format, normalises to lowercase
- `Money` — amount + currency code
- `PhoneNumber` — E.164 format
- `Address` — street, city, country, postal code

### Features/

24 feature sub-folders. Each contains:

```
Features/{Feature}/
├── Entities/     Business entities — POCOs, no EF attributes
└── Events/       IDomainEvent implementations
```

---

## What does NOT live in ONEVO.Domain

| Item | Where it lives |
|------|---------------|
| Repository interfaces | `ONEVO.Application/Common/Interfaces/` |
| MediatR handlers | `ONEVO.Application/Features/` |
| EF Core configurations | `ONEVO.Infrastructure/Persistence/Configurations/` |
| DTOs | `ONEVO.Application/Features/{Feature}/DTOs/` |
| Validation | `ONEVO.Application/Features/{Feature}/Validators/` |

---

## Feature entity example

```csharp
// ONEVO.Domain/Features/Leave/Entities/LeaveRequest.cs
public class LeaveRequest : BaseEntity
{
    public Guid EmployeeId { get; private set; }
    public Guid LeaveTypeId { get; private set; }
    public DateTime StartDate { get; private set; }
    public DateTime EndDate { get; private set; }
    public ApprovalStatus Status { get; private set; }

    private LeaveRequest() { } // EF constructor

    public static LeaveRequest Create(Guid employeeId, Guid leaveTypeId,
        DateTime start, DateTime end, Guid tenantId)
    {
        var request = new LeaveRequest
        {
            Id = Guid.NewGuid(),
            EmployeeId = employeeId,
            LeaveTypeId = leaveTypeId,
            StartDate = start,
            EndDate = end,
            Status = ApprovalStatus.Pending,
            TenantId = tenantId
        };
        request.AddDomainEvent(new LeaveRequestSubmittedEvent(request.Id, employeeId));
        return request;
    }

    public void Approve()
    {
        if (Status != ApprovalStatus.Pending)
            throw new DomainException("Only pending requests can be approved.");
        Status = ApprovalStatus.Approved;
        AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId));
    }
}
```
```

- [ ] **Step 2: Commit**

```bash
git add backend/shared-kernel.md
git commit -m "docs: rewrite shared-kernel.md as ONEVO.Domain layer guide"
```

---

## Task 7: Rewrite AI_CONTEXT/project-context.md

**Files:**
- Modify: `AI_CONTEXT/project-context.md`

- [ ] **Step 1: Find and replace the architecture description section**

Find every occurrence of these phrases and replace as shown:

| Find | Replace with |
|------|-------------|
| `modular monolith` | `Clean Architecture + CQRS` |
| `24 module projects` | `4 layer projects (24 features as folders)` |
| `ONEVO.Modules.{Name}` | `ONEVO.Application/Features/{Name}` |
| `per-module DbContext` | `single ApplicationDbContext` |
| `RabbitMQ` | `in-process MediatR domain events` |
| `MassTransit` | *(remove entirely)* |
| `IEventBus` | `IDomainEvent (MediatR INotification)` |
| `transactional outbox` | *(remove entirely)* |
| `Public/` folder (module public interface) | `Application/Common/Interfaces/` |
| `Internal/` folder | `feature folder within Application` |

- [ ] **Step 2: Update the solution structure section** to reference the 4-layer structure from `backend/folder-structure.md`

- [ ] **Step 3: Commit**

```bash
git add AI_CONTEXT/project-context.md
git commit -m "docs: update project-context.md architecture description to Clean Architecture"
```

---

## Task 8: Create ADR-002

**Files:**
- Create: `docs/decisions/ADR-002-clean-architecture-cqrs.md`

- [ ] **Step 1: Create the file**

```markdown
# ADR-002: Adopt Clean Architecture + CQRS

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001

---

## Context

ONEVO was designed as a modular monolith with 24 separate `.csproj` module projects. No code had been written. The May 31 delivery deadline and the dropped microservice extraction goal made the original architecture unnecessary complex.

## Decision

Adopt **Clean Architecture** with a 4-layer solution:
- `ONEVO.Domain` — entities, domain events, value objects
- `ONEVO.Application` — CQRS handlers, interfaces, DTOs, validators
- `ONEVO.Infrastructure` — EF Core, JWT, BCrypt, Redis, Hangfire, SignalR
- `ONEVO.Api` / `ONEVO.Admin.Api` — thin ASP.NET Core hosts

The 24 module projects become **feature folders** within `ONEVO.Domain/Features/` and `ONEVO.Application/Features/`.

**CQRS** is implemented with MediatR. Every write operation is a `Command`, every read is a `Query`. MediatR pipeline behaviors handle cross-cutting concerns (validation, logging, performance, exception handling).

## Consequences

**Positive:**
- Framework independence — Domain has zero external dependencies
- Testability — handlers tested without HTTP or DB
- Single deployable unit — simpler than 24 projects
- Faster to build — less boilerplate, no module registration ceremony
- No distributed systems complexity

**Negative:**
- Microservice extraction is no longer a natural path (acceptable — not a goal)
- All 176 tables in one ApplicationDbContext (managed via feature configuration folders)

## Alternatives considered

- Keep modular monolith — rejected: too complex for May 31
- Microservices — rejected: no team bandwidth, premature
```

- [ ] **Step 2: Commit**

```bash
git add docs/decisions/ADR-002-clean-architecture-cqrs.md
git commit -m "docs: add ADR-002 Clean Architecture + CQRS decision"
```

---

## Task 9: Create ADR-003

**Files:**
- Create: `docs/decisions/ADR-003-single-applicationdbcontext.md`

- [ ] **Step 1: Create the file**

```markdown
# ADR-003: Single ApplicationDbContext

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001 (per-module DbContext section)

---

## Context

The original design had 24 per-module DbContexts to facilitate future microservice extraction. With microservice extraction dropped and RabbitMQ removed, this added complexity with no benefit.

## Decision

Use a **single `ApplicationDbContext`** in `ONEVO.Infrastructure/Persistence/` for all 176 tables.

- Global query filters applied once: `TenantId == currentUser.TenantId && !IsDeleted`
- `IEntityTypeConfiguration<T>` files are grouped in feature folders under `Configurations/`
- One migration set in `Migrations/`
- `IUnitOfWork` wraps `SaveChangesAsync` — one call is atomic across all features
- `DomainEventDispatchInterceptor` runs after save and dispatches all domain events in-process

**DevPlatform exception:** `DevPlatformAccount`, `DevPlatformSession`, and agent entities have no `TenantId`. They use a separate base class and are excluded from the global tenant filter.

## Consequences

**Positive:**
- Single `SaveChangesAsync` call is atomic — no distributed transaction needed
- One migration history — simpler tooling (`ONEVO.DbMigrator`)
- Global tenant isolation guaranteed by DbContext, not per-feature code
- Cross-feature queries are simple DbSet joins

**Negative:**
- All entities are visible to all handlers via `IApplicationDbContext` (mitigated by code review convention: handlers only query their own feature's data unless explicitly needed)

## Alternatives considered

- Per-feature DbContexts within Infrastructure — rejected: adds complexity with no benefit in a monolith with no extraction plan
```

- [ ] **Step 2: Commit**

```bash
git add docs/decisions/ADR-003-single-applicationdbcontext.md
git commit -m "docs: add ADR-003 single ApplicationDbContext decision"
```

---

## Task 10: Create backend/clean-architecture-overview.md

**Files:**
- Create: `backend/clean-architecture-overview.md`

- [ ] **Step 1: Create the file**

```markdown
# Clean Architecture Overview: ONEVO

**Last Updated:** 2026-04-27

## What is Clean Architecture

Clean Architecture organises code into concentric layers. The core rule: **dependencies point inward**. The innermost layer (Domain) knows nothing about frameworks, databases, or the web.

```
┌─────────────────────────────────────┐
│  ONEVO.Api / ONEVO.Admin.Api        │  HTTP, SignalR, JWT middleware
│  ┌───────────────────────────────┐  │
│  │  ONEVO.Infrastructure         │  │  EF Core, Redis, Hangfire, SMTP
│  │  ┌─────────────────────────┐  │  │
│  │  │  ONEVO.Application       │  │  │  CQRS handlers, interfaces, DTOs
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │  ONEVO.Domain      │  │  │  │  Entities, events, value objects
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Responsible for | Depends on |
|-------|----------------|-----------|
| Domain | Business entities, domain events, value objects, business rules | Nothing |
| Application | CQRS handlers, interface definitions, DTOs, validation | Domain |
| Infrastructure | EF Core, JWT, BCrypt, Redis, Hangfire, SMTP, SignalR | Application + Domain |
| Api/Admin.Api | HTTP routing, middleware, SignalR hubs | Application + Infrastructure (DI only) |

## Request Lifecycle

```
HTTP POST /api/v1/leave/requests
    ↓
TenantResolutionMiddleware (sets ICurrentUser from JWT)
    ↓
Controller.CreateLeaveRequest(dto)
    ↓
_mediator.Send(new CreateLeaveRequestCommand(...))
    ↓
[1] ValidationBehavior         — FluentValidation
[2] LoggingBehavior            — request name + user + tenant
[3] PerformanceBehavior        — warns if > 500ms
[4] UnhandledExceptionBehavior — safety net
    ↓
CreateLeaveRequestHandler.Handle(command, ct)
    ├── queries IApplicationDbContext for employee
    ├── calls LeaveRequest.Create(...)  — entity raises LeaveRequestSubmittedEvent
    └── await _uow.SaveChangesAsync(ct)
            ↓
        AuditableEntityInterceptor  — sets CreatedAt, UpdatedAt, CreatedById
        SoftDeleteInterceptor       — converts Delete → IsDeleted=true
        DomainEventDispatchInterceptor → IPublisher.Publish(LeaveRequestSubmittedEvent)
            ↓
        NotificationsHandler reacts — sends email notification in-process
    ↓
Result<LeaveRequestDto>.Success(dto)
    ↓
HTTP 201 Created
```

## Key Principles

**Framework independence:** Domain entities are plain C# classes. EF mapping is in Infrastructure.

**Testability:** Handlers take interface parameters. Tests mock `IApplicationDbContext`, `IUnitOfWork`, etc. No HTTP, no DB needed for unit tests.

**Single responsibility:** One Command = one use case. One Query = one read operation.

**Result pattern:** Handlers return `Result<T>` for business failures. Exceptions are for infrastructure failures only.

## Related Docs

- [[backend/folder-structure|Folder Structure]] — full solution tree
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/security|Security]]
```

- [ ] **Step 2: Commit**

```bash
git add backend/clean-architecture-overview.md
git commit -m "docs: add clean-architecture-overview.md"
```

---

## Task 11: Create backend/security.md

**Files:**
- Create: `backend/security.md`

- [ ] **Step 1: Create the file**

```markdown
# Security Implementation: ONEVO

**Last Updated:** 2026-04-27

---

## Password Hashing

**Library:** `BCrypt.Net-Next`
**WorkFactor:** 12 (non-negotiable — never lower in production)
**Interface:** `IPasswordHasher` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Identity/PasswordHasher.cs`

Rule: never store plain text. Never use MD5 or SHA1. All comparisons go through `IPasswordHasher.Verify()`.

```csharp
public interface IPasswordHasher
{
    string Hash(string plainText);
    bool Verify(string plainText, string hash);
}
```

---

## JWT Authentication

**Interface:** `ITokenService` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Identity/JwtTokenService.cs`

### Mandatory validation settings (non-negotiable)

```csharp
tokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer = true,
    ValidateAudience = true,
    ValidateLifetime = true,          // ← must be true
    ValidateIssuerSigningKey = true,
    ClockSkew = TimeSpan.Zero,        // ← no grace window
    IssuerSigningKey = new SymmetricSecurityKey(
        Encoding.UTF8.GetBytes(Environment.GetEnvironmentVariable("JWT_SECRET_KEY")!))
};
```

### Secret key rule

**Never store `JWT_SECRET_KEY` in `appsettings.json`.**
- Development: environment variable
- Production: Azure Key Vault via `IConfiguration` binding

### Three token types (isolated issuers)

| Token type | Issuer | Valid at |
|---|---|---|
| Customer | `onevo-customer` | `ONEVO.Api` only |
| Platform admin | `onevo-platform-admin` | `ONEVO.Admin.Api` only |
| Agent machine | `onevo-agent` | `AgentGateway` endpoints only |

Tokens from one issuer are **rejected** at endpoints requiring another.

---

## PII Encryption

**Algorithm:** AES-256-GCM
**Interface:** `IEncryptionService` in `ONEVO.Application/Common/Interfaces/`
**Implementation:** `ONEVO.Infrastructure/Security/AesEncryptionService.cs`

```csharp
public interface IEncryptionService
{
    string Encrypt(string plainText);
    string Decrypt(string cipherText);
}
```

**Fields that must be encrypted:**
- `Employee`: NIC number, passport number, bank account number
- `SalaryHistory`: salary amount
- `VerificationRequest`: biometric hash
- `SmtpConfig`: SMTP password

Applied via EF Core **value converters** in `IEntityTypeConfiguration<T>` — encryption is transparent to handlers.

**Encryption key:** Azure Key Vault in production (`ENCRYPTION_KEY` env var in dev).

---

## Multi-Tenancy

`TenantResolutionMiddleware` reads `tenant_id` claim from JWT and populates `ICurrentUser`.

`ApplicationDbContext` applies global query filters:

```csharp
// Applied to every DbSet<T> where T : BaseEntity
modelBuilder.Entity<T>().HasQueryFilter(
    x => x.TenantId == _currentUser.TenantId && !x.IsDeleted);
```

**DevPlatform exception:** `DevPlatformAccount` and related entities have no `TenantId` and are excluded from this filter.

---

## RBAC

```csharp
// Controller endpoint
[RequirePermission("leave:approve")]
public async Task<IActionResult> ApproveLeave(...)

// Middleware reads JWT claims
// Permission format: "{resource}:{action}"
// Examples: "leave:approve", "employee:create", "payroll:run"
```

Missing permission → `ForbiddenException` → `ExceptionHandlerMiddleware` → HTTP 403 RFC 7807.

---

## Global Exception Handling

`ONEVO.Api/Middleware/ExceptionHandlerMiddleware.cs` catches all unhandled exceptions and returns RFC 7807 Problem Details:

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "Validation Error",
  "status": 422,
  "detail": "Leave request dates are invalid.",
  "instance": "/api/v1/leave/requests",
  "errors": { "StartDate": ["Must be in the future"] }
}
```

| Exception | HTTP Status |
|---|---|
| `NotFoundException` | 404 |
| `ForbiddenException` | 403 |
| `ValidationException` (FluentValidation) | 422 |
| `DomainException` | 422 |
| `System.Exception` (unhandled) | 500 (logs stack trace, returns safe message) |
```

- [ ] **Step 2: Commit**

```bash
git add backend/security.md
git commit -m "docs: add security.md — BCrypt, JWT, AES-256, RBAC, RFC 7807"
```

---

## Task 12: Create backend/cqrs-patterns.md

**Files:**
- Create: `backend/cqrs-patterns.md`

- [ ] **Step 1: Create the file**

```markdown
# CQRS Patterns: ONEVO

**Last Updated:** 2026-04-27

ONEVO uses **MediatR** for in-process CQRS. Every write is a `Command`, every read is a `Query`. Both use the same pipeline but follow different conventions.

---

## Command

A Command changes state. It returns `Result<TResponse>`.

```csharp
// ONEVO.Application/Features/Leave/Commands/ApproveLeaveRequest/
// ApproveLeaveRequestCommand.cs
public record ApproveLeaveRequestCommand(
    Guid LeaveRequestId,
    Guid ApproverId
) : IRequest<Result<LeaveRequestDto>>;

// ApproveLeaveRequestCommandHandler.cs
public class ApproveLeaveRequestCommandHandler
    : IRequestHandler<ApproveLeaveRequestCommand, Result<LeaveRequestDto>>
{
    private readonly IApplicationDbContext _db;
    private readonly IUnitOfWork _uow;

    public ApproveLeaveRequestCommandHandler(IApplicationDbContext db, IUnitOfWork uow)
    {
        _db = db;
        _uow = uow;
    }

    public async Task<Result<LeaveRequestDto>> Handle(
        ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        var request = await _db.LeaveRequests
            .FirstOrDefaultAsync(r => r.Id == cmd.LeaveRequestId, ct);

        if (request is null)
            return Result<LeaveRequestDto>.Failure("Leave request not found");

        request.Approve(); // raises LeaveApprovedEvent on the entity

        await _uow.SaveChangesAsync(ct); // interceptor dispatches domain events after save

        return Result<LeaveRequestDto>.Success(request.ToDto());
    }
}
```

---

## Query

A Query reads state. It never modifies data.

```csharp
// ONEVO.Application/Features/Leave/Queries/GetLeaveBalance/
// GetLeaveBalanceQuery.cs
public record GetLeaveBalanceQuery(
    Guid EmployeeId,
    int Year
) : IRequest<Result<LeaveBalanceDto>>;

// GetLeaveBalanceQueryHandler.cs
public class GetLeaveBalanceQueryHandler
    : IRequestHandler<GetLeaveBalanceQuery, Result<LeaveBalanceDto>>
{
    private readonly IApplicationDbContext _db;

    public GetLeaveBalanceQueryHandler(IApplicationDbContext db) => _db = db;

    public async Task<Result<LeaveBalanceDto>> Handle(
        GetLeaveBalanceQuery query, CancellationToken ct)
    {
        var balance = await _db.LeaveEntitlements
            .Where(e => e.EmployeeId == query.EmployeeId && e.Year == query.Year)
            .Select(e => new LeaveBalanceDto { ... })
            .FirstOrDefaultAsync(ct);

        if (balance is null)
            return Result<LeaveBalanceDto>.Failure("No entitlement found");

        return Result<LeaveBalanceDto>.Success(balance);
    }
}
```

---

## DTOs

```
Application/Features/Leave/DTOs/
├── Requests/
│   └── CreateLeaveRequestDto.cs    ← what the HTTP controller receives from the client
└── Responses/
    ├── LeaveRequestDto.cs           ← what handlers return to the controller
    └── LeaveBalanceDto.cs
```

Handlers **never return Domain entities** — always response DTOs.

---

## Validator

Every Command that modifies state has a FluentValidation validator:

```csharp
// ONEVO.Application/Features/Leave/Validators/
public class ApproveLeaveRequestValidator
    : AbstractValidator<ApproveLeaveRequestCommand>
{
    public ApproveLeaveRequestValidator()
    {
        RuleFor(x => x.LeaveRequestId).NotEmpty();
        RuleFor(x => x.ApproverId).NotEmpty();
    }
}
```

`ValidationBehavior` runs before every handler. If validation fails, the handler never executes.

---

## Pipeline Behaviors (run in order)

```
[1] ValidationBehavior        — FluentValidation. Returns 422 before handler if invalid.
[2] LoggingBehavior           — logs command/query name, UserId, TenantId.
[3] PerformanceBehavior       — logs warning if elapsed > 500ms.
[4] UnhandledExceptionBehavior — catches any unhandled exception, re-throws for middleware.
```

---

## Result<T>

```csharp
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }

    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}
```

Controllers map `Result<T>` to HTTP responses:
- `IsSuccess = true` → 200 / 201
- `IsSuccess = false` with `NotFoundException` message → 404
- `IsSuccess = false` with business error → 422

---

## Controller (thin)

```csharp
[ApiController]
[Route("api/v1/leave")]
public class LeaveController : ControllerBase
{
    private readonly ISender _mediator;
    public LeaveController(ISender mediator) => _mediator = mediator;

    [HttpPost("{id}/approve")]
    [RequirePermission("leave:approve")]
    public async Task<IActionResult> Approve(Guid id, ApproveLeaveRequestDto dto, CancellationToken ct)
    {
        var result = await _mediator.Send(
            new ApproveLeaveRequestCommand(id, dto.ApproverId), ct);

        return result.IsSuccess
            ? Ok(result.Value)
            : UnprocessableEntity(result.Error);
    }
}
```
```

- [ ] **Step 2: Commit**

```bash
git add backend/cqrs-patterns.md
git commit -m "docs: add cqrs-patterns.md — command/query/validator/pipeline examples"
```

---

## Task 13: Create backend/domain-events.md

**Files:**
- Create: `backend/domain-events.md`

- [ ] **Step 1: Create the file**

```markdown
# Domain Events: ONEVO

**Last Updated:** 2026-04-27

Domain events replace RabbitMQ, MassTransit, IEventBus, and the transactional outbox entirely. All cross-feature communication is **in-process via MediatR**.

---

## How it works

1. Entity method raises a business action (e.g. `LeaveRequest.Approve()`)
2. The method calls `AddDomainEvent(new LeaveApprovedEvent(...))` — stored in `BaseEntity.DomainEvents`
3. Handler calls `_uow.SaveChangesAsync(ct)` — persists DB changes
4. `DomainEventDispatchInterceptor` runs after the DB write succeeds:
   - Collects all `DomainEvents` from EF Core tracked entities
   - Calls `entity.ClearDomainEvents()`
   - Publishes each via `IPublisher.Publish(domainEvent, ct)` (MediatR)
5. Any `INotificationHandler<TEvent>` registered in DI reacts in-process

**Atomicity:** If `SaveChangesAsync` throws, the interceptor never runs — no events fire. No partial state.

---

## Defining a domain event

```csharp
// ONEVO.Domain/Features/Leave/Events/LeaveApprovedEvent.cs
public record LeaveApprovedEvent(
    Guid LeaveRequestId,
    Guid EmployeeId
) : IDomainEvent; // IDomainEvent : INotification (MediatR)
```

---

## Raising a domain event (on entity)

```csharp
// ONEVO.Domain/Features/Leave/Entities/LeaveRequest.cs
public void Approve()
{
    if (Status != ApprovalStatus.Pending)
        throw new DomainException("Only pending requests can be approved.");

    Status = ApprovalStatus.Approved;
    AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId)); // ← collected, not dispatched yet
}
```

---

## Handling a domain event (cross-feature)

```csharp
// ONEVO.Application/Features/WorkforcePresence/EventHandlers/
// LeaveApprovedEventHandler.cs
public class LeaveApprovedEventHandler : INotificationHandler<LeaveApprovedEvent>
{
    private readonly IApplicationDbContext _db;
    private readonly IUnitOfWork _uow;

    public LeaveApprovedEventHandler(IApplicationDbContext db, IUnitOfWork uow)
    {
        _db = db;
        _uow = uow;
    }

    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // Mark the employee's shift as absent during leave period
        var shifts = await _db.PresenceRecords
            .Where(p => p.EmployeeId == notification.EmployeeId)
            .ToListAsync(ct);

        foreach (var shift in shifts)
            shift.MarkAbsent();

        await _uow.SaveChangesAsync(ct);
    }
}
```

---

## Integration registry (cross-feature auto-wiring)

| Event | Published by | Handled by | Effect |
|-------|-------------|-----------|--------|
| `LeaveApprovedEvent` | Leave | WorkforcePresence | Mark shift absent |
| `LeaveApprovedEvent` | Leave | Payroll | Create deduction entry |
| `EmployeeCreatedEvent` | CoreHR | Auth | Create user account |
| `EmployeeTerminatedEvent` | CoreHR | Auth | Deactivate user |
| `EmployeeTerminatedEvent` | CoreHR | WMS bridge | Revoke WMS access |
| `SnapshotCapturedEvent` | ActivityMonitoring | ExceptionEngine | Evaluate anomaly rules |
| `PresenceRecordedEvent` | WorkforcePresence | ActivityMonitoring | Correlate agent snapshots |
| `AnomalyDetectedEvent` | ExceptionEngine | Notifications | Send alert |

---

## What is gone

| Old | New |
|-----|-----|
| `IEventBus` | `IDomainEvent` + `IPublisher` (MediatR) |
| `IntegrationEvent` base class | `IDomainEvent` interface |
| `MassTransit` NuGet | removed |
| `RabbitMQ` | removed |
| `IConsumer<T>` | `INotificationHandler<T>` |
| Per-module `OutboxMessage.cs` | removed |
| Per-module `OutboxProcessor.cs` | removed |
| `backend/messaging/` folder | deleted |
```

- [ ] **Step 2: Commit**

```bash
git add backend/domain-events.md
git commit -m "docs: add domain-events.md — MediatR replaces RabbitMQ entirely"
```

---

## Task 14: Create layer guide files

**Files:**
- Create: `backend/layer-guide/domain-layer.md`
- Create: `backend/layer-guide/application-layer.md`
- Create: `backend/layer-guide/infrastructure-layer.md`
- Create: `backend/layer-guide/webapi-layer.md`

- [ ] **Step 1: Create `backend/layer-guide/domain-layer.md`**

```markdown
# Domain Layer Guide

See [[backend/shared-kernel|ONEVO.Domain documentation]] — the full guide lives there (formerly shared-kernel.md).

Quick reference:
- `ONEVO.Domain/Common/BaseEntity.cs` — all entities extend this
- `ONEVO.Domain/Common/IDomainEvent.cs` — marker interface for domain events
- `ONEVO.Domain/Features/{Feature}/Entities/` — business entities
- `ONEVO.Domain/Features/{Feature}/Events/` — domain events
- Zero framework dependencies — no EF, no MediatR attributes
```

- [ ] **Step 2: Create `backend/layer-guide/application-layer.md`**

```markdown
# Application Layer Guide

Full CQRS patterns: [[backend/cqrs-patterns|CQRS Patterns]]
Full interface list: see `ONEVO.Application/Common/Interfaces/`

## Feature folder structure

```
ONEVO.Application/Features/{Feature}/
├── Commands/{UseCase}/
│   ├── {UseCase}Command.cs      record : IRequest<Result<ResponseDto>>
│   └── {UseCase}Handler.cs
├── Queries/{UseCase}/
│   ├── {UseCase}Query.cs
│   └── {UseCase}Handler.cs
├── DTOs/Requests/ + Responses/
├── Validators/
└── EventHandlers/               INotificationHandler<IDomainEvent>
```

## Interfaces (all defined here, implemented in Infrastructure)

| Interface | Purpose |
|---|---|
| `IApplicationDbContext` | DbSet properties — handlers query via this |
| `IRepository<T>` | Generic CRUD — GetByIdAsync, AddAsync, Update, Delete |
| `IUnitOfWork` | SaveChangesAsync — atomic save + domain event dispatch |
| `ICurrentUser` | UserId, TenantId, Permissions[] from JWT |
| `ICacheService` | Get/Set/Remove — L1+L2 abstraction |
| `IEncryptionService` | AES-256 for PII |
| `IEmailService` | SendAsync |
| `IStorageService` | UploadAsync, DownloadAsync, DeleteAsync |
| `IDateTimeProvider` | UtcNow — testable |
| `IBackgroundJobService` | Enqueue, Schedule via Hangfire |
| `INotificationDispatcher` | PushAsync — SignalR |
| `ITokenService` | GenerateToken, ValidateToken |
| `IPasswordHasher` | Hash, Verify |

## DependencyInjection.cs

```csharp
public static IServiceCollection AddApplication(this IServiceCollection services)
{
    services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(Assembly.GetExecutingAssembly()));
    services.AddValidatorsFromAssembly(Assembly.GetExecutingAssembly());
    services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
    services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
    services.AddTransient(typeof(IPipelineBehavior<,>), typeof(PerformanceBehavior<,>));
    services.AddTransient(typeof(IPipelineBehavior<,>), typeof(UnhandledExceptionBehavior<,>));
    return services;
}
```
```

- [ ] **Step 3: Create `backend/layer-guide/infrastructure-layer.md`**

```markdown
# Infrastructure Layer Guide

Implements all interfaces defined in Application. Never referenced directly by Application.

## Key files

| File | Implements | Notes |
|------|-----------|-------|
| `Persistence/ApplicationDbContext.cs` | `IApplicationDbContext` | 176 tables, global filters |
| `Persistence/UnitOfWork.cs` | `IUnitOfWork` | Wraps SaveChangesAsync |
| `Persistence/Repositories/GenericRepository.cs` | `IRepository<T>` | Tenant-filtered |
| `Identity/JwtTokenService.cs` | `ITokenService` | ValidateLifetime=true, ClockSkew=Zero |
| `Identity/PasswordHasher.cs` | `IPasswordHasher` | BCrypt WorkFactor=12 |
| `Identity/CurrentUserService.cs` | `ICurrentUser` | Reads from HttpContext JWT |
| `Caching/RedisCacheService.cs` | `ICacheService` | L1 + L2 Redis |
| `Security/AesEncryptionService.cs` | `IEncryptionService` | AES-256-GCM |
| `Email/SmtpEmailService.cs` | `IEmailService` | SMTP |
| `Storage/BlobStorageService.cs` | `IStorageService` | Azure Blob / S3 |
| `BackgroundJobs/BackgroundJobService.cs` | `IBackgroundJobService` | Hangfire |
| `RealTime/SignalRNotificationDispatcher.cs` | `INotificationDispatcher` | SignalR hubs |

## EF interceptors (run inside SaveChangesAsync)

```
AuditableEntityInterceptor    → sets CreatedAt, UpdatedAt, CreatedById automatically
SoftDeleteInterceptor         → converts Delete operations to IsDeleted=true
DomainEventDispatchInterceptor → collects entity.DomainEvents, calls IPublisher.Publish after save
```

## DependencyInjection.cs

```csharp
public static IServiceCollection AddInfrastructure(
    this IServiceCollection services, IConfiguration config)
{
    services.AddDbContext<ApplicationDbContext>(opts =>
        opts.UseNpgsql(config.GetConnectionString("DefaultConnection"))
            .AddInterceptors(
                new AuditableEntityInterceptor(),
                new SoftDeleteInterceptor(),
                new DomainEventDispatchInterceptor()));

    services.AddScoped<IApplicationDbContext>(p =>
        p.GetRequiredService<ApplicationDbContext>());
    services.AddScoped<IUnitOfWork, UnitOfWork>();
    services.AddScoped(typeof(IRepository<>), typeof(GenericRepository<>));
    services.AddScoped<ICurrentUser, CurrentUserService>();
    services.AddScoped<ITokenService, JwtTokenService>();
    services.AddScoped<IPasswordHasher, PasswordHasher>();
    services.AddScoped<IEncryptionService, AesEncryptionService>();
    services.AddScoped<ICacheService, RedisCacheService>();
    services.AddScoped<IEmailService, SmtpEmailService>();
    services.AddScoped<IStorageService, BlobStorageService>();
    services.AddScoped<IBackgroundJobService, BackgroundJobService>();
    services.AddScoped<INotificationDispatcher, SignalRNotificationDispatcher>();
    return services;
}
```
```

- [ ] **Step 4: Create `backend/layer-guide/webapi-layer.md`**

```markdown
# WebApi Layer Guide

Two host projects. Both are composition roots only — no business logic.

## ONEVO.Api (customer-facing)

**Base URL:** `/api/v1/`
**JWT issuer expected:** `onevo-customer`

### Controller pattern (all controllers are thin)

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class LeaveController : ControllerBase
{
    private readonly ISender _mediator;
    public LeaveController(ISender mediator) => _mediator = mediator;

    [HttpPost]
    [RequirePermission("leave:create")]
    public async Task<IActionResult> Create(
        [FromBody] CreateLeaveRequestDto dto, CancellationToken ct)
    {
        var result = await _mediator.Send(
            new CreateLeaveRequestCommand(dto.EmployeeId, dto.LeaveTypeId,
                dto.StartDate, dto.EndDate), ct);

        return result.IsSuccess
            ? CreatedAtAction(nameof(GetById), new { id = result.Value!.Id }, result.Value)
            : UnprocessableEntity(result.Error);
    }
}
```

### Middleware pipeline order (Program.cs)

```csharp
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseMiddleware<TenantResolutionMiddleware>();
app.UseMiddleware<PermissionMiddleware>();
app.UseAuthorization();
app.UseMiddleware<ExceptionHandlerMiddleware>(); // RFC 7807 — last
app.MapControllers();
app.MapHubs(); // SignalR
```

### Program.cs service registration

```csharp
builder.Services.AddApplication();           // MediatR + behaviors
builder.Services.AddInfrastructure(config);  // EF, JWT, BCrypt, Redis…
builder.Services.AddSignalR();
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(opts => { /* see security.md */ });
```

## ONEVO.Admin.Api (developer console)

**Base URL:** `/admin/v1/`
**JWT issuer expected:** `onevo-platform-admin`
**Same DI pattern** — calls `AddApplication()` + `AddInfrastructure(config)`

DevPlatform entities have no `TenantId` — `PlatformAdminAuthMiddleware` validates admin JWT before any endpoint runs.
```

- [ ] **Step 5: Commit all four layer guides**

```bash
git add backend/layer-guide/
git commit -m "docs: add layer guide files for Domain, Application, Infrastructure, WebApi"
```

---

## Task 15: Create agent docs

**Files:**
- Create: `backend/agent/overview.md`
- Create: `backend/agent/windows-agent.md`

- [ ] **Step 1: Create `backend/agent/overview.md`**

```markdown
# ONEVO Agent — Overview

**Last Updated:** 2026-04-27

The ONEVO Agent is a **separate solution** (`ONEVO.Agent.sln`) that runs on employee computers. It captures activity data and sends it to `ONEVO.Api` via the `AgentGateway` feature endpoints.

## Why a separate solution

- **Independent release cycle** — server deploys daily; agent uses ring-based rollout to thousands of machines via `agent_deployment_rings` and `agent_version_releases` tables in DevPlatform
- **Security boundary** — agent binary on employee machines must not contain server internals
- **Phase 2 expansion** — `ONEVO.Agent.Mac/` added without touching the server solution

## Solution structure

```
ONEVO.Agent.sln
├── src/
│   ├── ONEVO.Agent.Core/               Pure logic — no OS or framework dependencies
│   │   ├── Capture/
│   │   │   ├── IScreenshotCapture.cs
│   │   │   ├── IAppUsageCapture.cs
│   │   │   └── IBrowserActivityCapture.cs
│   │   ├── Sync/
│   │   │   ├── IAgentApiClient.cs      POSTs data to ONEVO.Api AgentGateway endpoints
│   │   │   └── IOfflineQueue.cs        Buffers data when network is unavailable
│   │   ├── Policy/
│   │   │   └── AgentPolicy.cs          Capture rules fetched from server
│   │   └── Models/
│   │       ├── ActivitySnapshot.cs
│   │       ├── AppUsageRecord.cs
│   │       └── HeartbeatPayload.cs
│   │
│   ├── ONEVO.Agent.Windows/            Windows tray app + capture implementations (Phase 1)
│   │   ├── Capture/
│   │   │   ├── WindowsScreenshotCapture.cs
│   │   │   ├── WindowsAppUsageCapture.cs
│   │   │   └── WindowsBrowserCapture.cs
│   │   ├── Tray/
│   │   │   ├── SystemTrayIcon.cs
│   │   │   └── TrayContextMenu.cs
│   │   ├── Storage/
│   │   │   └── SQLiteOfflineQueue.cs
│   │   ├── AutoUpdate/
│   │   │   └── AgentUpdater.cs
│   │   └── Program.cs                  .NET Worker Service host
│   │
│   └── ONEVO.Agent.Infrastructure/     HTTP client layer
│       ├── AgentApiClient.cs           IAgentApiClient implementation
│       ├── AgentAuthService.cs         Machine token management
│       └── PolicySyncService.cs        Fetches capture policy from AgentGateway
│
└── tests/
    └── ONEVO.Agent.Tests.Unit/
```

## Authentication

1. IT admin provisions a machine token via `AgentGateway` admin endpoint
2. Token stored in **Windows Credential Manager** (not registry, not plain file)
3. Agent uses token for all API calls — issuer: `onevo-agent`
4. Token is tenant-scoped — identifies which tenant and employee this machine belongs to

## Server-side integration

The `AgentGateway` feature in `ONEVO.Application/Features/AgentGateway/` handles:
- Agent registration
- Heartbeat ingestion
- Snapshot ingestion
- Policy delivery
- Version check (reads from `DevPlatform` feature)

## Phase roadmap

| Phase | Platform |
|-------|---------|
| Phase 1 | Windows only — `ONEVO.Agent.Windows` |
| Phase 2 | macOS — add `ONEVO.Agent.Mac` to same solution |
```

- [ ] **Step 2: Create `backend/agent/windows-agent.md`**

```markdown
# ONEVO Windows Agent

**Last Updated:** 2026-04-27
**Platform:** Windows 10/11

## Capture capabilities

| Capability | Windows API | Frequency |
|---|---|---|
| Screenshot | GDI+ `Graphics.CopyFromScreen` / `PrintWindow` | Configurable via AgentPolicy |
| Active app | `GetForegroundWindow` + `Process.GetProcessById` | Every 30s (default) |
| Browser activity | Chrome/Edge DevTools Protocol or extension | On navigation |
| Keyboard/mouse activity | Low-level hooks (presence only, no keylogging) | Continuous |

## Tray app

`ONEVO.Agent.Windows/Tray/SystemTrayIcon.cs` — uses `System.Windows.Forms.NotifyIcon`

Context menu items:
- Status (Connected / Offline)
- Pause monitoring (requires manager approval token)
- About / version
- Exit (requires IT PIN)

## Offline queue

`SQLiteOfflineQueue.cs` — SQLite database at `%APPDATA%\ONEVO\Agent\queue.db`

- Stores `ActivitySnapshot` records when network is unavailable
- Replays on reconnect in chronological order
- Max queue size: 72 hours of data (configurable)

## Auto-update

`AgentUpdater.cs` polls `AgentGateway` on startup and every 4 hours:
1. Calls `GET /api/v1/agent/version-check` with current version
2. If new version available in assigned deployment ring → downloads installer
3. Applies update on next Windows restart (MSI silent install)

Deployment rings: `Canary → Beta → Stable` — managed via DevPlatform admin console.

## Machine token storage

```csharp
// Stored in Windows Credential Manager
CredentialManager.WriteCredential(
    "ONEVO-Agent",
    Environment.MachineName,
    machineToken);

// Read on startup
var token = CredentialManager.ReadCredential("ONEVO-Agent")?.Password;
```

## Host setup (Program.cs)

```csharp
var host = Host.CreateDefaultBuilder(args)
    .UseWindowsService()           // runs as Windows Service
    .ConfigureServices(services =>
    {
        services.AddSingleton<IScreenshotCapture, WindowsScreenshotCapture>();
        services.AddSingleton<IAppUsageCapture, WindowsAppUsageCapture>();
        services.AddSingleton<IOfflineQueue, SQLiteOfflineQueue>();
        services.AddSingleton<IAgentApiClient, AgentApiClient>();
        services.AddHostedService<CaptureSchedulerService>();
        services.AddHostedService<SyncService>();
        services.AddHostedService<PolicySyncService>();
    })
    .Build();

await host.RunAsync();
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/agent/
git commit -m "docs: add agent overview and windows-agent docs"
```

---

## Task 16: Partial updates — backend docs (8 files)

**Files:**
- Modify: `backend/README.md`
- Modify: `backend/api-conventions.md`
- Modify: `backend/bridge-api-contracts.md`
- Modify: `backend/notification-system.md`
- Modify: `backend/real-time.md`
- Modify: `backend/external-integrations.md`
- Modify: `backend/monitoring-data-flow.md`
- Modify: `backend/search-architecture.md`

For each file below, open the file, apply the specified changes, and save.

- [ ] **Step 1: Update `backend/README.md`**

Replace the architecture overview paragraph with:

```markdown
ONEVO follows **Clean Architecture + CQRS** (.NET 9). Four layer projects — Domain, Application, Infrastructure, and Api/Admin.Api — with 24 features as folders within each layer. All 176 tables live in a single `ApplicationDbContext`. Cross-feature communication uses in-process MediatR domain events (no RabbitMQ).
```

Remove any links to `backend/messaging/` — replace with `[[backend/domain-events|Domain Events]]`.

- [ ] **Step 2: Update `backend/api-conventions.md`**

Find and replace:
- "module" → "feature" (when referring to code organisation)
- `ONEVO.Modules.{Name}` → `Application/Features/{Name}`
- Any reference to `{Name}Module.cs` or `Add{Name}Module()` → `DependencyInjection.cs` + `services.AddApplication()`
- Any reference to `Public/I{Name}Service.cs` → `Application/Common/Interfaces/I{Name}Service.cs`

Add at the top if not already present:

```markdown
> **Architecture:** Clean Architecture + CQRS. Controllers are thin — they call `_mediator.Send(command)` or `_mediator.Send(query)` only. No business logic in controllers.
```

- [ ] **Step 3: Update `backend/bridge-api-contracts.md`**

Remove any sections describing RabbitMQ bridges. Replace with:

```markdown
> **Bridge pattern:** WMS integration uses HTTP webhooks only. ONEVO calls WMS webhook endpoints directly from `WmsBridgeClient.cs` (Infrastructure/ExternalServices/). There is no message broker between ONEVO and WMS.
```

Keep all entity ownership tables and HTTP contract definitions — those are unchanged.

- [ ] **Step 4: Update `backend/notification-system.md`**

Find and replace:
- `IEventBus.PublishAsync` → `AddDomainEvent(new NotificationCreatedEvent(...))`
- `MassTransit` → remove
- `OutboxProcessor` → remove
- Any reference to RabbitMQ exchanges → remove

Add:

```markdown
Notifications are triggered by domain events. The `NotificationCreatedEvent` is handled by `INotificationHandler<NotificationCreatedEvent>` in `Application/Features/Notifications/EventHandlers/`, which calls `INotificationDispatcher` to push via SignalR and `IEmailService` for email channels.
```

- [ ] **Step 5: Update `backend/real-time.md`**

Find and replace:
- `ONEVO.Modules.{Name}` references → remove or replace with feature folder paths
- Module registration references → remove

Keep all SignalR hub descriptions and event push patterns — those are unchanged.

- [ ] **Step 6: Update `backend/external-integrations.md`**

Find and replace:
- `ONEVO.Infrastructure/Messaging/` → `ONEVO.Infrastructure/ExternalServices/`
- `IEventBus` → `WmsBridgeClient` (for WMS integrations) or `IDomainEvent` (for internal)
- Any outbox or MassTransit references → remove

- [ ] **Step 7: Update `backend/monitoring-data-flow.md`**

Find and replace:
- Module project names (`ONEVO.Modules.ActivityMonitoring`) → `Application/Features/ActivityMonitoring`
- RabbitMQ flow arrows → in-process domain event arrows
- `IEventBus` → `IDomainEvent`

- [ ] **Step 8: Update `backend/search-architecture.md`**

Find and replace:
- Module project names → feature folder paths
- `Internal/Queries/` → `Features/{Name}/Queries/`

- [ ] **Step 9: Commit all 8 files**

```bash
git add backend/README.md backend/api-conventions.md backend/bridge-api-contracts.md \
        backend/notification-system.md backend/real-time.md backend/external-integrations.md \
        backend/monitoring-data-flow.md backend/search-architecture.md
git commit -m "docs: partial updates to 8 backend docs — remove modular monolith references"
```

---

## Task 17: Partial updates — developer-platform docs (8 files)

**Files:**
- Modify: `developer-platform/overview.md`
- Modify: `developer-platform/system-design.md`
- Modify: `developer-platform/auth.md`
- Modify: `developer-platform/database/schema.md`
- Modify: `developer-platform/backend/admin-api-layer.md`
- Modify: `developer-platform/backend/api-contracts.md`
- Modify: `developer-platform/modules/agent-version-manager/overview.md`
- Modify: `developer-platform/modules/app-catalog-manager/overview.md`

- [ ] **Step 1: Update `developer-platform/overview.md`**

Replace any reference to `ONEVO.Modules.DevPlatform` with `Application/Features/DevPlatform`. Replace "module" with "feature" in code structure sections.

- [ ] **Step 2: Update `developer-platform/system-design.md`**

Replace architecture diagram references from modular monolith to Clean Architecture layers. Replace `ONEVO.Modules.*` references with layer paths.

- [ ] **Step 3: Update `developer-platform/auth.md`**

Find `onevo-platform-admin` JWT references — keep them, they are unchanged. Remove any MassTransit or IEventBus references.

- [ ] **Step 4: Update `developer-platform/database/schema.md`**

Replace:

```markdown
> **DbContext:** `DevPlatformDbContext` in `ONEVO.Modules.DevPlatform/Internal/Persistence/`
```

With:

```markdown
> **DbContext:** `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`. DevPlatform entities (`DevPlatformAccount`, `DevPlatformSession`, `AgentVersionRelease`, `AgentDeploymentRing`, `AgentDeploymentRingAssignment`) are configured in `ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/`. These entities have **no TenantId** and are excluded from the global tenant query filter.
```

- [ ] **Step 5: Update `developer-platform/backend/admin-api-layer.md`**

Replace:
- `ONEVO.Modules.DevPlatform` → `Application/Features/DevPlatform`
- `IDevPlatformAccountService` (from Public/) → `IApplicationDbContext` + `IUnitOfWork`
- Module project structure description → feature folder description

- [ ] **Step 6: Update `developer-platform/backend/api-contracts.md`**

Remove any module-level contract references. Keep all HTTP endpoint definitions.

- [ ] **Step 7: Update `developer-platform/modules/agent-version-manager/overview.md`**

Find the code structure section and replace module project layout with:

```markdown
**Feature folder:** `Application/Features/DevPlatform/`
**Entities:** `Domain/Features/DevPlatform/Entities/AgentVersionRelease.cs`, `AgentDeploymentRing.cs`, `AgentDeploymentRingAssignment.cs`
**EF config:** `Infrastructure/Persistence/Configurations/DevPlatform/`
```

- [ ] **Step 8: Update `developer-platform/modules/app-catalog-manager/overview.md`**

Same pattern as Step 7 — update code structure section to feature folder paths.

- [ ] **Step 9: Commit all 8 files**

```bash
git add developer-platform/
git commit -m "docs: partial updates to developer-platform docs — feature folder paths"
```

---

## Task 18: Update 24 module feature docs

**Files (all):**
```
modules/infrastructure/overview.md
modules/auth/overview.md
modules/org-structure/overview.md
modules/core-hr/overview.md
modules/leave/overview.md
modules/payroll/overview.md
modules/performance/overview.md
modules/skills/overview.md
modules/documents/overview.md
modules/workforce-presence/overview.md
modules/activity-monitoring/overview.md
modules/identity-verification/overview.md
modules/exception-engine/overview.md
modules/discrepancy-engine/overview.md
modules/productivity-analytics/overview.md
modules/shared-platform/overview.md
modules/notifications/overview.md
modules/configuration/overview.md
modules/calendar/overview.md
modules/reporting-engine/overview.md
modules/grievance/overview.md
modules/expense/overview.md
modules/agent-gateway/overview.md
modules/dev-platform/overview.md
```

**Rule:** Keep all domain/feature content (entities, business rules, user flows, table schemas). Update **only** the code structure sections.

- [ ] **Step 1: Apply this find-replace pattern to ALL 24 files**

For each file, find the section that describes the module's code structure (usually titled "Module Structure", "Project Structure", "Code Structure", or similar) and replace the old modular monolith layout:

**FIND (old pattern):**
```
ONEVO.Modules.{Name}/
├── Public/
│   ├── I{Name}Service.cs
│   ├── Dtos/
│   └── Events/
├── Internal/
│   ├── Entities/
│   ├── Persistence/
│   │   ├── {Name}DbContext.cs
│   │   ├── Migrations/
│   │   ├── Repositories/
│   │   └── EntityConfigurations/
│   ├── Services/
│   ├── Commands/
│   ├── Queries/
│   ├── Validators/
│   ├── EventHandlers/
│   ├── Jobs/
│   ├── Outbox/
│   └── Mappings/
├── Endpoints/
└── {Name}Module.cs
```

**REPLACE WITH (new pattern — substitute `{FeatureName}` for each file):**
```
# Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/{FeatureName}/Entities/
  ONEVO.Domain/Features/{FeatureName}/Events/

Application (CQRS):
  ONEVO.Application/Features/{FeatureName}/Commands/
  ONEVO.Application/Features/{FeatureName}/Queries/
  ONEVO.Application/Features/{FeatureName}/DTOs/Requests/
  ONEVO.Application/Features/{FeatureName}/DTOs/Responses/
  ONEVO.Application/Features/{FeatureName}/Validators/
  ONEVO.Application/Features/{FeatureName}/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/{FeatureName}/

API endpoints:
  ONEVO.Api/Controllers/{FeatureName}/{FeatureName}Controller.cs
```

- [ ] **Step 2: Feature name mapping for the replace above**

| File | `{FeatureName}` |
|------|----------------|
| `modules/infrastructure/overview.md` | `InfrastructureModule` |
| `modules/auth/overview.md` | `Auth` |
| `modules/org-structure/overview.md` | `OrgStructure` |
| `modules/core-hr/overview.md` | `CoreHR` |
| `modules/leave/overview.md` | `Leave` |
| `modules/payroll/overview.md` | `Payroll` |
| `modules/performance/overview.md` | `Performance` |
| `modules/skills/overview.md` | `Skills` |
| `modules/documents/overview.md` | `Documents` |
| `modules/workforce-presence/overview.md` | `WorkforcePresence` |
| `modules/activity-monitoring/overview.md` | `ActivityMonitoring` |
| `modules/identity-verification/overview.md` | `IdentityVerification` |
| `modules/exception-engine/overview.md` | `ExceptionEngine` |
| `modules/discrepancy-engine/overview.md` | `DiscrepancyEngine` |
| `modules/productivity-analytics/overview.md` | `ProductivityAnalytics` |
| `modules/shared-platform/overview.md` | `SharedPlatform` |
| `modules/notifications/overview.md` | `Notifications` |
| `modules/configuration/overview.md` | `Configuration` |
| `modules/calendar/overview.md` | `Calendar` |
| `modules/reporting-engine/overview.md` | `ReportingEngine` |
| `modules/grievance/overview.md` | `Grievance` |
| `modules/expense/overview.md` | `Expense` |
| `modules/agent-gateway/overview.md` | `AgentGateway` |
| `modules/dev-platform/overview.md` | `DevPlatform` |

- [ ] **Step 3: Also remove in every file**

Remove or update any line referencing:
- `{Name}DbContext.cs` → replace with `ApplicationDbContext (shared)`
- `OutboxMessage.cs` / `OutboxProcessor.cs` → remove entirely
- `IEventBus` → replace with `IDomainEvent (MediatR INotification)`
- `IConsumer<T>` → replace with `INotificationHandler<T>`
- `MassTransit` → remove
- `Add{Name}Module()` → remove

- [ ] **Step 4: Commit**

```bash
git add modules/
git commit -m "docs: update 24 module feature docs — feature folder paths, remove module project structure"
```

---

## Done

All 62 files updated. The documentation now fully reflects Clean Architecture + CQRS.

**Next plans (separate sessions):**
- `2026-04-27-onevo-sln-implementation.md` — build the .NET solution (Domain → Application → Infrastructure → Api layers)
- `2026-04-27-onevo-agent-implementation.md` — build ONEVO.Agent.sln (Windows tray app)
