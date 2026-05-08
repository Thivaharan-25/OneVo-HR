# Application Layer Guide

**Last Updated:** 2026-05-08

Full CQRS patterns: [[backend/cqrs-patterns|CQRS Patterns]]

The Application layer owns use cases. It contains commands, queries, handlers, validators, DTOs, and repository/service interfaces. It depends on `ONEVO.Domain` only.

## Feature Folder Structure

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

Rules:

- Command validators live beside the command they validate.
- Do not create a feature-level `Validators/` folder.
- Query validators are allowed only when the query accepts user input that needs validation.
- Do not create `EventHandlers/` by default.
- Add `EventHandlers/` only when a justified domain event exists.

Optional event handler shape:

```text
ONEVO.Application/Features/{Feature}/EventHandlers/
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

All interfaces are defined in Application and implemented in Infrastructure.

| Interface | Purpose |
|---|---|
| Repository/reader interfaces | Persistence contracts for handlers and services |
| `IRepository<T>` | Generic tenant-safe CRUD when present |
| `IUnitOfWork` | `SaveChangesAsync` and optional post-save event dispatch |
| `ICurrentUser` | UserId, TenantId, Permissions from JWT |
| `ICacheService` | Get/Set/Remove cache abstraction |
| `IEncryptionService` | AES-256 for PII |
| `IEmailService` | Email delivery abstraction |
| `IStorageService` | File upload/download/delete abstraction |
| `IDateTimeProvider` | Testable time source |
| `IBackgroundJobService` | Enqueue and schedule background work |
| `INotificationDispatcher` | SignalR notification abstraction |
| `ITokenService` | Token generation and validation |
| `IPasswordHasher` | Hash and verify passwords |

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
