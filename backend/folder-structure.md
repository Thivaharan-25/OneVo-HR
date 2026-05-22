# ONEVO Backend Folder Structure

**Last Updated:** 2026-05-13

This is the canonical reference for ONEVO backend organization.

## Solution Structure

```text
ONEVO.sln
|
|-- src/
|   |-- ONEVO.Domain/
|   |   |-- Common/
|   |   |   |-- BaseEntity.cs
|   |   |   |-- ValueObject.cs
|   |   |   `-- IDomainEvent.cs
|   |   |
|   |   |-- Enums/
|   |   |-- Errors/
|   |   |-- ValueObjects/
|   |   |
|   |   `-- Features/
|   |       `-- {Feature}/
|   |           `-- {SubFeature}/
|   |               |-- Entities/
|   |               |-- ValueObjects/
|   |               `-- Events/                    # optional
|   |
|   |-- ONEVO.Application/
|   |   |-- Common/
|   |   |   |-- Behaviors/
|   |   |   |-- Models/
|   |   |   |-- Mappings/
|   |   |   |   `-- {Entity}MappingExtensions.cs    # static manual-mapping methods; no AutoMapper
|   |   |   |-- Helpers/
|   |   |   |   `-- {Domain}Helper.cs               # pure utility logic; no DI dependencies
|   |   |   |-- Extensions/
|   |   |   |   `-- QueryableExtensions.cs          # IQueryable / LINQ helpers used across features
|   |   |   |-- RepositoryInterfaces/
|   |   |   |   `-- IUnitOfWork.cs
|   |   |   |
|   |   |   `-- ServiceInterfaces/
|   |   |       |-- ICurrentUser.cs
|   |   |       |-- IDateTimeProvider.cs
|   |   |       |-- IEmailService.cs
|   |   |       |-- IStorageService.cs
|   |   |       |-- ICacheService.cs
|   |   |       |-- IBackgroundJobService.cs
|   |   |       |-- IEncryptionService.cs
|   |   |       |-- INotificationDispatcher.cs
|   |   |       |-- IModuleCatalogService.cs
|   |   |       |-- IModuleEntitlementService.cs
|   |   |       |-- IDefaultRoleSeeder.cs
|   |   |       `-- ITenantContext.cs
|   |   |
|   |   `-- Features/
|   |       `-- {Feature}/
|   |           `-- {SubFeature}/
|   |               |-- Commands/
|   |               |   `-- {UseCase}/
|   |               |       |-- {UseCase}Command.cs
|   |               |       |-- {UseCase}Handler.cs
|   |               |       `-- {UseCase}Validator.cs
|   |               |
|   |               |-- Queries/
|   |               |   `-- {UseCase}/
|   |               |       |-- {UseCase}Query.cs
|   |               |       `-- {UseCase}Handler.cs
|   |               |
|   |               |-- DTOs/
|   |               |   |-- Requests/
|   |               |   `-- Responses/
|   |               |
|   |               |-- RepositoryInterfaces/
|   |               |   `-- I{SubFeature}Repository.cs
|   |               |
|   |               |-- ServiceInterfaces/
|   |               |   `-- I{SubFeature}Service.cs
|   |               |
|   |               `-- EventHandlers/              # optional
|   |
|   |-- ONEVO.Infrastructure/
|   |   |-- Persistence/
|   |   |   |-- ApplicationDbContext.cs
|   |   |   |-- ApplicationDbContextFactory.cs
|   |   |   |-- UnitOfWork.cs
|   |   |   |
|   |   |   |-- Migrations/
|   |   |   |
|   |   |   |-- Interceptors/
|   |   |   |   |-- AuditableEntityInterceptor.cs
|   |   |   |   |-- SoftDeleteInterceptor.cs
|   |   |   |   |-- TenantRlsInterceptor.cs
|   |   |   |   `-- DomainEventDispatchInterceptor.cs
|   |   |   |
|   |   |   |-- Configurations/
|   |   |   |   `-- {Feature}/
|   |   |   |       `-- {SubFeature}/
|   |   |   |
|   |   |   `-- Repositories/
|   |   |       `-- {Feature}/
|   |   |           `-- {SubFeature}/
|   |   |
|   |   |-- ExternalServices/
|   |   |   |-- Email/
|   |   |   |   |-- ResendEmailService.cs
|   |   |   |   `-- SmtpEmailService.cs
|   |   |   |
|   |   |   |-- Storage/
|   |   |   |   `-- R2StorageService.cs                     # future — not yet implemented
|   |   |   |
|   |   |   |-- Payments/                               # future — not yet implemented
|   |   |   |   |-- StripePaymentService.cs             # future
|   |   |   |   `-- PayHerePaymentService.cs            # future
|   |   |   |
|   |   |   |-- Calendar/
|   |   |   |   |-- GoogleCalendarService.cs
|   |   |   |   `-- MicrosoftCalendarService.cs
|   |   |   |
|   |   |   |-- Messaging/
|   |   |   |   |-- SlackService.cs
|   |   |   |   `-- MicrosoftTeamsService.cs
|   |   |   |
|   |   |   |-- Biometric/
|   |   |   |   `-- BiometricTerminalClient.cs
|   |   |   |
|   |   |   `-- Payroll/                                # future — not yet implemented
|   |   |       |-- AdpPayrollClient.cs                 # future
|   |   |       `-- OraclePayrollClient.cs              # future
|   |   |
|   |   |-- Identity/
|   |   |   |-- AuthTokenIssuer.cs
|   |   |   |-- BCryptPasswordHasher.cs
|   |   |   |-- GoogleIdTokenValidator.cs
|   |   |   |-- JwtTokenService.cs
|   |   |   |-- OtpNetTotpService.cs
|   |   |   |-- CurrentUserService.cs
|   |   |   |-- AnonymousCurrentUser.cs
|   |   |   |-- HttpContextTenantContext.cs
|   |   |   `-- SystemDateTimeProvider.cs
|   |   |-- Caching/
|   |   |   |-- InMemoryCacheService.cs           # current — Microsoft.Extensions.Caching.Memory
|   |   |   `-- RedisCacheService.cs              # future — only if scaling to multi-instance/microservices
|   |   |-- BackgroundJobs/
|   |   |-- Security/
|   |   |   |-- PermissionResolver.cs
|   |   |   |-- PermissionVersionService.cs
|   |   |   |-- TenantPermissionCatalogService.cs
|   |   |   `-- NoOpEncryptionService.cs
|   |   |-- RealTime/
|   |   |
|   |   |-- Services/
|   |   |   |-- DevPlatform/
|   |   |   |   |-- Tenancy/
|   |   |   |   |   |-- DefaultRoleSeeder.cs
|   |   |   |   |   |-- TenantRoleStatusReader.cs
|   |   |   |   |   `-- NotConfiguredYetReaders.cs
|   |   |   |   `-- Provisioning/
|   |   |   |       `-- TenantOwnerInvitationService.cs
|   |   |   `-- SharedPlatform/
|   |   |       |-- ModuleCatalogService.cs
|   |   |       `-- ModuleEntitlementService.cs
|   |   |
|   |   `-- DependencyInjection.cs
|   |
|   |-- ONEVO.Api/
|   |   |-- Controllers/
|   |   |   |-- Admin/
|   |   |   `-- {Feature}/
|   |   |       `-- {SubFeature}/
|   |   |
|   |   |-- Extensions/
|   |   |   |-- ServiceCollectionExtensions.cs          # groups DI registrations called from Program.cs
|   |   |   `-- WebApplicationExtensions.cs             # middleware/pipeline helpers
|   |   |
|   |   |-- Hubs/
|   |   |-- Middleware/
|   |   |-- Filters/
|   |   `-- Program.cs
|
`-- tests/
    |-- ONEVO.Tests.Unit/
    |-- ONEVO.Tests.Integration/
    `-- ONEVO.Tests.Architecture/
```

## Request Lifecycle

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Optional event branch:

```text
UnitOfWork save succeeds -> DomainEventDispatchInterceptor -> EventHandler(s)
```

Domain events are optional. Do not create `Events/` or `EventHandlers/` folders unless the feature has a real decoupled post-save side effect.

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

## Placement Rules

| What                         | Correct Location                                                          |
| ---------------------------- | ------------------------------------------------------------------------- |
| Command handler              | `ONEVO.Application/Features/{Feature}/{SubFeature}/Commands/{UseCase}/`   |
| Query handler                | `ONEVO.Application/Features/{Feature}/{SubFeature}/Queries/{UseCase}/`    |
| Command validator            | `ONEVO.Application/Features/{Feature}/{SubFeature}/Commands/{UseCase}/`   |
| Common repository interface  | `ONEVO.Application/Common/RepositoryInterfaces/`                          |
| Feature repository interface | `ONEVO.Application/Features/{Feature}/{SubFeature}/RepositoryInterfaces/` |
| Common service interface     | `ONEVO.Application/Common/ServiceInterfaces/`                             |
| Feature service interface    | `ONEVO.Application/Features/{Feature}/{SubFeature}/ServiceInterfaces/`    |
| Interface implementation     | `ONEVO.Infrastructure/`                                                   |
| Entity                       | `ONEVO.Domain/Features/{Feature}/{SubFeature}/Entities/`                  |
| Optional domain event        | `ONEVO.Domain/Features/{Feature}/{SubFeature}/Events/`                    |
| Optional event handler       | `ONEVO.Application/Features/{Feature}/{SubFeature}/EventHandlers/`        |
| EF configuration             | `ONEVO.Infrastructure/Persistence/Configurations/{Feature}/{SubFeature}/` |
| Repository implementation    | `ONEVO.Infrastructure/Persistence/Repositories/{Feature}/{SubFeature}/`   |
| Migration                    | `ONEVO.Infrastructure/Persistence/Migrations/`                            |
| Customer API controller      | `ONEVO.Api/Controllers/{Feature}/{SubFeature}/`                           |
| Developer Console controller | `ONEVO.Api/Controllers/Admin/`                                            |
| DbContext                    | `ONEVO.Infrastructure/Persistence/ApplicationDbContext.cs` only           |
| Service implementation           | `ONEVO.Infrastructure/Services/{Feature}/{SubFeature}/`                   |
| Common mapping helpers           | `ONEVO.Application/Common/Mappings/`                                      |
| Feature-level mapping            | `ONEVO.Application/Features/{Feature}/{SubFeature}/Mappings/`             |
| Utility helpers                  | `ONEVO.Application/Common/Helpers/`                                       |
| Application LINQ extensions      | `ONEVO.Application/Common/Extensions/`                                    |
| API DI/pipeline extensions       | `ONEVO.Api/Extensions/`                                                   |

## Persistence Access Rule

Handlers, services, resolvers, optional event handlers, and module orchestration classes must not use EF Core or `ApplicationDbContext` directly.

Database reads and writes go through Application-owned repository/reader interfaces implemented in Infrastructure under `ONEVO.Infrastructure/Persistence/Repositories/`.

Application does not expose `IApplicationDbContext` or `DbSet<T>` abstractions. `ApplicationDbContext` is an Infrastructure detail used by repositories, EF migrations/configuration, interceptors, factories, and `IUnitOfWork`.

Use a feature-specific repository or reader for joins, projections, cross-feature reads, platform-admin flows, locking, raw SQL, or any operation that would otherwise require direct EF access.

## Host Project Rules

The active host project is a composition root only. It contains HTTP routing, middleware, filters, hubs, and DI wiring. It must not contain business logic or `DbContext` access.

Developer-console endpoints belong under `ONEVO.Api/Controllers/Admin/`.

## Related

- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/layer-guide/webapi-layer|WebApi Layer Guide]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]

