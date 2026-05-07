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

## Persistence Access Rule

Handlers and services do not use EF Core or `ApplicationDbContext` directly. All database reads and writes go through Application-owned repository/reader interfaces, implemented in Infrastructure.

Use `IRepository<T>` for simple aggregate CRUD. Create feature-specific repository or reader interfaces when a use case needs joins, projections, cross-feature reads, explicit platform-admin access, or any query that would otherwise require `IgnoreQueryFilters()`.

Application does not expose `IApplicationDbContext` or `DbSet<T>`. Repository interfaces are the persistence boundary; Infrastructure repositories own EF Core queries, tenant predicates, projections, and locking.

This is the ONEVO security default because repository boundaries centralize tenant filtering, soft-delete behavior, cancellation, and the rare places where platform-level cross-tenant access is allowed.

## Interfaces (all defined here, implemented in Infrastructure)

| Interface | Purpose |
|---|---|
| Repository/reader interfaces | Persistence contracts for handlers and services; implemented in Infrastructure repositories |
| `IRepository<T>` | Generic tenant-safe CRUD, when present; GetByIdAsync, AddAsync, Update, Delete |
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
