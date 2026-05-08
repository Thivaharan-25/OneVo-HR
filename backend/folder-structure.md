# Solution Folder Structure: ONEVO

**Last Updated:** 2026-05-08

The canonical reference for ONEVO backend organisation. All other docs defer to this file for structure questions.

## Architecture

ONEVO follows **Clean Architecture + CQRS** on .NET 9. The solution is divided into layer projects and one active host project. Planning modules become feature folders inside each layer; there are no separate module `.csproj` files.

Clean Architecture and CQRS do **not** require events. Domain events are optional and should appear only when a completed use case needs decoupled post-save side effects.

## Deployment Boundary

| Unit | Solution | Deployment artifact |
|:-----|:---------|:--------------------|
| HR + Work Management web backend | `ONEVO.sln` | Single ASP.NET Core host, `ONEVO.Api` |
| Developer admin console API | `ONEVO.sln` | `/admin/v1/*` namespace inside `ONEVO.Api` |
| Desktop monitoring agent | `ONEVO.Agent.sln` | Separate solution, separate MSIX release cycle |
| VS Code IDE extension | Published to VS Code Marketplace separately | TypeScript VSIX |

`ONEVO.Agent.sln` is intentionally separate. It has its own release cadence, test suite, and deployment path. The agent communicates with `ONEVO.Api` at runtime via HTTP only.

The developer console frontend (`console.onevo.io`) is a separate SPA backed by `/admin/v1/*` endpoints inside `ONEVO.Api`. `ONEVO.Admin.Api` is deprecated scaffold only and must not be deployed as a second backend service.

## ONEVO.sln Structure

```text
ONEVO.sln
|-- src/
|   |-- ONEVO.Domain/
|   |   |-- Common/
|   |   |   |-- BaseEntity.cs
|   |   |   |-- ValueObject.cs
|   |   |   `-- IDomainEvent.cs                  # optional post-save event marker
|   |   |-- Enums/
|   |   |-- Errors/
|   |   |-- ValueObjects/
|   |   `-- Features/
|   |       `-- {Feature}/
|   |           |-- Entities/
|   |           `-- Events/                       # optional; create only when justified
|   |
|   |-- ONEVO.Application/
|   |   |-- Common/
|   |   |   |-- Behaviors/
|   |   |   |   |-- ValidationBehavior.cs
|   |   |   |   |-- LoggingBehavior.cs
|   |   |   |   |-- PerformanceBehavior.cs
|   |   |   |   `-- UnhandledExceptionBehavior.cs
|   |   |   |-- Interfaces/
|   |   |   `-- Models/
|   |   |       |-- Result.cs
|   |   |       |-- PagedRequest.cs
|   |   |       `-- PagedResult.cs
|   |   `-- Features/
|   |       `-- {Feature}/
|   |           |-- Commands/
|   |           |   `-- {UseCase}/
|   |           |       |-- {UseCase}Command.cs
|   |           |       |-- {UseCase}Handler.cs
|   |           |       `-- {UseCase}Validator.cs
|   |           |-- Queries/
|   |           |   `-- {UseCase}/
|   |           |       |-- {UseCase}Query.cs
|   |           |       `-- {UseCase}Handler.cs
|   |           |-- DTOs/
|   |           |   |-- Requests/
|   |           |   `-- Responses/
|   |           |-- Interfaces/
|   |           `-- EventHandlers/                 # optional; only for justified events
|   |
|   |-- ONEVO.Infrastructure/
|   |   |-- Persistence/
|   |   |   |-- ApplicationDbContext.cs
|   |   |   |-- ApplicationDbContextFactory.cs
|   |   |   |-- Migrations/
|   |   |   |-- Interceptors/
|   |   |   |   |-- AuditableEntityInterceptor.cs
|   |   |   |   |-- SoftDeleteInterceptor.cs
|   |   |   |   `-- DomainEventDispatchInterceptor.cs # optional event dispatch
|   |   |   |-- Configurations/{Feature}/
|   |   |   |-- Repositories/{Feature}/
|   |   |   `-- UnitOfWork.cs
|   |   |-- Identity/
|   |   |-- Caching/
|   |   |-- BackgroundJobs/
|   |   |-- Email/
|   |   |-- Storage/
|   |   |-- Security/
|   |   |-- RealTime/
|   |   `-- DependencyInjection.cs
|   |
|   |-- ONEVO.Api/
|   |   |-- Controllers/
|   |   |   |-- Admin/
|   |   |   `-- {Feature}/
|   |   |-- Hubs/
|   |   |-- Middleware/
|   |   |-- Filters/
|   |   `-- Program.cs
|   |
|   `-- ONEVO.Admin.Api/                           # deprecated scaffold only
|
|-- tests/
|   |-- ONEVO.Tests.Unit/
|   |-- ONEVO.Tests.Integration/
|   `-- ONEVO.Tests.Architecture/
|
`-- tools/
    `-- ONEVO.DbMigrator/
```

## Application Feature Rule

Use-case files stay together:

```text
ONEVO.Application/Features/{Feature}/
|-- Commands/
|   `-- {UseCase}/
|       |-- {UseCase}Command.cs
|       |-- {UseCase}Handler.cs
|       `-- {UseCase}Validator.cs
|-- Queries/
|   `-- {UseCase}/
|       |-- {UseCase}Query.cs
|       `-- {UseCase}Handler.cs
|-- DTOs/
|   |-- Requests/
|   `-- Responses/
`-- Interfaces/
```

Do not create feature-level `Validators/` folders. A validator belongs to the command it validates. Queries may have validators only when they accept meaningful user input such as filters, date ranges, pagination, or identifiers that need format checks.

Do not create `EventHandlers/` by default. Add it only when the feature handles a real domain event.

## Request Lifecycle

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Optional event branch:

```text
UnitOfWork save succeeds -> DomainEventDispatchInterceptor -> EventHandler(s)
```

That branch exists only for justified post-save side effects. It is not part of the normal use-case template.

## Layer Dependency Rule

```text
ONEVO.Api
    -> ONEVO.Application <- ONEVO.Infrastructure
           -> ONEVO.Domain
```

Forbidden dependencies:

```text
Application -> Infrastructure
Domain -> Application
Domain -> Infrastructure
Domain -> Api
```

## Host Project Rules

The active host project is a composition root only: no business logic, no `DbContext`. `ONEVO.Admin.Api` is deprecated scaffold only.

| What | Correct Location |
|---|---|
| Command handler | `ONEVO.Application/Features/{Feature}/Commands/{UseCase}/` |
| Query handler | `ONEVO.Application/Features/{Feature}/Queries/{UseCase}/` |
| Command validator | `ONEVO.Application/Features/{Feature}/Commands/{UseCase}/` |
| Interface definition | `ONEVO.Application/Common/Interfaces/` or `ONEVO.Application/Features/{Feature}/Interfaces/` |
| Interface implementation | `ONEVO.Infrastructure/` |
| Entity | `ONEVO.Domain/Features/{Feature}/Entities/` |
| Optional domain event | `ONEVO.Domain/Features/{Feature}/Events/` |
| Optional event handler | `ONEVO.Application/Features/{Feature}/EventHandlers/` |
| EF configuration | `ONEVO.Infrastructure/Persistence/Configurations/{Feature}/` |
| Repository implementation | `ONEVO.Infrastructure/Persistence/Repositories/{Feature}/` |
| Migration | `ONEVO.Infrastructure/Persistence/Migrations/` |
| Customer API controller | `ONEVO.Api/Controllers/{Feature}/` |
| Developer Console controller | `ONEVO.Api/Controllers/Admin/` |
| DbContext | `ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs` only |

## Persistence Access Rule

Handlers, services, resolvers, optional event handlers, and module orchestration classes must not use EF Core or `ApplicationDbContext` directly. Database reads and writes go through Application-owned repository/reader interfaces implemented in Infrastructure.

Use the generic `IRepository<T>` for simple aggregate access. Add feature-specific repositories/readers for joins, projections, cross-feature reads, platform-admin flows, or any operation that would otherwise require `IgnoreQueryFilters()`.

Application does not expose `IApplicationDbContext` or `DbSet<T>` abstractions. `ApplicationDbContext` is an Infrastructure detail used by repositories, EF migrations/configuration, and `IUnitOfWork`.

## Related

- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/layer-guide/webapi-layer|WebApi Layer Guide]]
- [[backend/module-catalog|Module Catalog]]
- [[backend/security|Security Implementation]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/agent/overview|Agent Overview]]
- [[docs/decisions/ADR-002-clean-architecture-cqrs|ADR-002]]
