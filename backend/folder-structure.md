# Solution Folder Structure: ONEVO

**Last Updated:** 2026-04-27

The canonical reference for ONEVO backend organisation. All other docs defer to this file for structure questions.

---

## Architecture

ONEVO follows **Clean Architecture + CQRS** (.NET 9). The solution is divided into four layer projects and two host projects. Modules from the planning docs become **feature folders** within each layer — there are no separate module `.csproj` files.

## Deployment Boundary (Definitive)

| Unit | Solution | Deployment artifact |
|:-----|:---------|:-------------------|
| HR + Work Management web backend | `ONEVO.sln` | Single ASP.NET Core host |
| Developer admin console API | `ONEVO.sln` | Second host in same solution |
| Desktop monitoring agent | `ONEVO.Agent.sln` | **Separate solution, separate MSIX release cycle** |
| VS Code IDE extension | Published to VS Code Marketplace separately | TypeScript VSIX |

`ONEVO.Agent.sln` is intentionally separate — it has its own release cadence (MSIX package signed and distributed via MDM/GPO), its own test suite, and does not share the web solution's CI pipeline. The agent communicates with `ONEVO.Api` at runtime via HTTP only.

The developer console frontend (`console.onevo.io`) is a separate SPA backed by `ONEVO.Admin.Api`, which lives **inside** `ONEVO.sln`.

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
│   │       │
│   │       │  ── WORK MANAGEMENT (Pillar 3) feature folders ──
│   │       ├── WorkManagement/Foundation/Entities/ + Events/
│   │       ├── WorkManagement/Projects/Entities/ + Events/
│   │       ├── WorkManagement/Tasks/Entities/ + Events/
│   │       ├── WorkManagement/Planning/Entities/ + Events/
│   │       ├── WorkManagement/OKR/Entities/ + Events/
│   │       ├── WorkManagement/Time/Entities/ + Events/
│   │       ├── WorkManagement/Resources/Entities/ + Events/
│   │       ├── WorkManagement/Chat/Entities/ + Events/
│   │       ├── WorkManagement/ChatAI/Entities/ + Events/
│   │       ├── WorkManagement/Collaboration/Entities/ + Events/
│   │       ├── WorkManagement/Analytics/Entities/ + Events/
│   │       ├── WorkManagement/Integrations/Entities/ + Events/
│   │       ├── Integrations/MicrosoftTeams/Entities/ + Events/
│   │       └── IDEExtension/Entities/ + Events/
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
│   │   │   │   ├── IPasswordHasher.cs
│   │   │   │   └── IIDEHubService.cs          # SignalR push to IDE: tag:executed, ai:action_pending, context:detected
│   │   │   └── Models/
│   │   │       ├── Result.cs
│   │   │       ├── PagedRequest.cs
│   │   │       └── PagedResult.cs
│   │   ├── Features/                          # ~38 feature folders (HR + WFI + Work Management + IDE)
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
│   │   │   ├── ApplicationDbContext.cs        # ALL 252 cataloged tables (HR + Work Management + IDE), global tenant + workspace + soft-delete filters
│   │   │   ├── ApplicationDbContextFactory.cs
│   │   │   ├── Migrations/                    # ONE migration set
│   │   │   ├── Interceptors/
│   │   │   │   ├── AuditableEntityInterceptor.cs
│   │   │   │   ├── SoftDeleteInterceptor.cs
│   │   │   │   └── DomainEventDispatchInterceptor.cs
│   │   │   ├── Configurations/                # IEntityTypeConfiguration<T> per entity
│   │   │   │   └── {Feature}/                 # ~38 feature folders (mirrors Domain/Features/ layout)
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
│   │   ├── Email/SmtpEmailService.cs
│   │   ├── Storage/BlobStorageService.cs
│   │   ├── Security/AesEncryptionService.cs
│   │   ├── RealTime/
│   │   │   ├── SignalRNotificationDispatcher.cs
│   │   │   ├── IDEHubService.cs               # IIDEHubService impl — pushes to IDEHub
│   │   │   └── HubRegistration.cs
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
