# Application Layer Guide

**Last Updated:** 2026-05-08

Full CQRS patterns: [[backend/cqrs-patterns|CQRS Patterns]]

The Application layer owns use cases. It contains commands, queries, handlers, validators, DTOs, and repository/service interfaces. It depends on `ONEVO.Domain` only.

## Feature Folder Structure

```text
ONEVO.Application/Features/{Feature}/{SubFeature}/
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
|-- RepositoryInterfaces/
|   `-- I{SubFeature}Repository.cs
|-- ServiceInterfaces/
|   `-- I{SubFeature}Service.cs
|-- Mappings/                   # optional - manual entity->DTO mapping; only when non-trivial
|   `-- {SubFeature}Mappings.cs
|-- Helpers/                    # optional - SubFeature-scoped utility logic with no DI deps
|   `-- {SubFeature}Helper.cs
`-- EventHandlers/              # optional - only when a justified domain event exists
```

Rules:
- SubFeature is the second level inside every Feature folder.
- Validators stay inside Commands/{UseCase}/ beside the command they validate.
- Do not create a feature-level Validators/ folder.
- Do not create EventHandlers/ by default - only when a justified domain event exists.
- Do not use Interfaces/, Repositories/, or Services/ as folder names.
  Use RepositoryInterfaces/ and ServiceInterfaces/ exactly.
- Do not use AutoMapper. All mapping is done via static manual methods in Mappings/.
- Mappings/ is optional - only add it when entity->DTO projection is non-trivial.
- Helpers/ is optional - only add it for pure utility logic that has no DI dependencies.
  If the helper needs DI, make it a service (ServiceInterfaces/ + implementation).
- Cross-feature helpers and LINQ extensions go in Common/Helpers/ and Common/Extensions/.

Optional event handler shape:

```text
ONEVO.Application/Features/{Feature}/{SubFeature}/EventHandlers/
`-- {EventName}Handler.cs
```

## Normal Request Flow

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Optional event branch:

```text
UnitOfWork save succeeds -> DomainEventDispatchInterceptor -> EventHandler(s)
```

## Persistence Access Rule

Handlers and services do not use EF Core or `ApplicationDbContext` directly. All database reads and writes go through Application-owned repository/reader interfaces implemented in Infrastructure.

Use `IRepository<T>` for simple aggregate CRUD. Create feature-specific repository or reader interfaces when a use case needs joins, projections, cross-feature reads, explicit platform-admin access, or any query that would otherwise require `IgnoreQueryFilters()`.

Application does not expose `IApplicationDbContext` or `DbSet<T>`. Repository interfaces are the persistence boundary. Infrastructure repositories own EF Core queries, tenant predicates, projections, and locking.

This is the ONEVO security default because repository boundaries centralize tenant filtering, soft-delete behavior, cancellation, and the rare places where platform-level cross-tenant access is allowed.

## Interfaces

Common interfaces are in `Application/Common/RepositoryInterfaces/` and `Application/Common/ServiceInterfaces/`.
Feature interfaces are in `Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/` and `ServiceInterfaces/`.
All interfaces are implemented in Infrastructure. Application must not reference Infrastructure.

**Common RepositoryInterfaces:**
- `IUnitOfWork` - `SaveChangesAsync` and optional post-save event dispatch

**Common ServiceInterfaces:**
- `ICurrentUser`, `ICacheService`, `IEncryptionService`, `IEmailService`, `IStorageService`, `IDateTimeProvider`, `IBackgroundJobService`, `INotificationDispatcher`, `IModuleCatalogService`, `IModuleEntitlementService`, `ITenantContext`, `IDefaultRoleSeeder`

**Feature ServiceInterfaces (examples):**
- Auth/Login: `ITokenService`, `IPasswordHasher`, `IAuthTokenIssuer`, `IGoogleIdTokenValidator`, `ITotpService`
- Auth/Permission: `IPermissionResolver`, `IPermissionVersionService`, `ITenantPermissionCatalogService`

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
