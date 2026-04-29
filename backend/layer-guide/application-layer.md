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
