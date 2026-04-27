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
