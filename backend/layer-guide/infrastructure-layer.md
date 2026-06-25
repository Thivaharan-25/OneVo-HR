# Infrastructure Layer Guide

Implements all interfaces defined in Application. Never referenced directly by Application.

## Key files

| File | Implements | Notes |
|------|-----------|-------|
| `Persistence/ApplicationDbContext.cs` | `IUnitOfWork` | Single EF Core context, global filters; used by repositories, EF tooling, and DI |
| `Persistence/UnitOfWork.cs` | `IUnitOfWork` | Wraps SaveChangesAsync |
| `Persistence/Repositories/GenericRepository.cs` | `IRepository<T>` | Tenant-filtered persistence boundary |
| `Identity/JwtTokenService.cs` | `ITokenService` | ValidateLifetime=true, ClockSkew=Zero |
| `Identity/BCryptPasswordHasher.cs` | `IPasswordHasher` | BCrypt WorkFactor=12 |
| `Identity/CurrentUserService.cs` | `ICurrentUser` | Reads from HttpContext JWT |
| `Identity/SystemDateTimeProvider.cs` | `IDateTimeProvider` | Wraps DateTimeOffset.UtcNow |
| `Caching/InMemoryCacheService.cs` | `ICacheService` | Current - Microsoft.Extensions.Caching.Memory |
| `Caching/RedisCacheService.cs` | `ICacheService` | Future - distributed/multi-instance only |
| `Security/NoOpEncryptionService.cs` | `IEncryptionService` | Stub - AES-256 pending |
| `ExternalServices/Email/ResendSmtpEmailService.cs` | `IEmailService` | Resend SMTP |
| `ExternalServices/Storage/R2StorageService.cs` | `IStorageService` | Future - Cloudflare R2 |
| `BackgroundJobs/BackgroundJobService.cs` | `IBackgroundJobService` | Future - Hangfire; not yet implemented |
| `RealTime/SignalRNotificationDispatcher.cs` | `INotificationDispatcher` | Future - SignalR; not yet implemented |
| `Security/PermissionResolver.cs` | `IPermissionResolver` | Resolves user permissions |
| `Security/PermissionVersionService.cs` | `IPermissionVersionService` | Tracks permission version |
| `Security/TenantPermissionCatalogService.cs` | `ITenantPermissionCatalogService` | Tenant permission catalog |
| `Services/SharedPlatform/ModuleCatalogService.cs` | `IModuleCatalogService` | Module registry |
| `Services/SharedPlatform/ModuleEntitlementService.cs` | `IModuleEntitlementService` | Tenant module access |
| `Services/DevPlatform/Tenancy/DefaultRoleSeeder.cs` | `IDefaultRoleSeeder` | Seeds default roles |
| `Services/DevPlatform/Provisioning/TenantOwnerInvitationService.cs` | `ITenantOwnerInvitationService` | Owner invite flow |

## EF interceptors (run inside SaveChangesAsync)

```
AuditableEntityInterceptor    -> sets CreatedAt, UpdatedAt, CreatedById automatically
SoftDeleteInterceptor         -> converts Delete operations to IsDeleted=true
TenantRlsInterceptor          -> sets app.current_tenant_id RLS variable on every connection open
DomainEventDispatchInterceptor -> collects entity.DomainEvents, calls IPublisher.Publish after save
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
                new TenantRlsInterceptor(),
                new DomainEventDispatchInterceptor()));

    services.AddScoped<IUnitOfWork>(p =>
        p.GetRequiredService<ApplicationDbContext>());

    // Identity
    services.AddScoped<ITokenService, JwtTokenService>();
    services.AddScoped<IPasswordHasher, BCryptPasswordHasher>();
    services.AddScoped<ICurrentUser, CurrentUserService>();
    services.AddScoped<IDateTimeProvider, SystemDateTimeProvider>();
    services.AddScoped<IGoogleIdTokenValidator, GoogleIdTokenValidator>();
    services.AddScoped<ITotpService, OtpNetTotpService>();
    services.AddScoped<IAuthTokenIssuer, AuthTokenIssuer>();

    // Security
    services.AddScoped<IPermissionResolver, PermissionResolver>();
    services.AddScoped<IPermissionVersionService, PermissionVersionService>();
    services.AddScoped<ITenantPermissionCatalogService, TenantPermissionCatalogService>();
    services.AddScoped<IEncryptionService, NoOpEncryptionService>(); // stub - AES pending

    // Email
    services.AddScoped<IEmailService, ResendSmtpEmailService>();

    // Services
    services.AddScoped<IModuleCatalogService, ModuleCatalogService>();
    services.AddScoped<IModuleEntitlementService, ModuleEntitlementService>();
    services.AddScoped<IDefaultRoleSeeder, DefaultRoleSeeder>();
    services.AddScoped<ITenantOwnerInvitationService, TenantOwnerInvitationService>();

    // In-memory caching (current - Microsoft.Extensions.Caching.Memory):
    services.AddScoped<ICacheService, InMemoryCacheService>();

    // Pending (not yet implemented):
    // services.AddScoped<ICacheService, RedisCacheService>(); // replace above if scaling to multi-instance
    // services.AddScoped<IBackgroundJobService, BackgroundJobService>();
    // services.AddScoped<INotificationDispatcher, SignalRNotificationDispatcher>();
    // services.AddScoped<IStorageService, R2StorageService>();
    return services;
}
```
