# Clean Architecture Overview: ONEVO

**Last Updated:** 2026-05-06

Clean Architecture organises code into layers. The core rule is: dependencies point inward. Domain knows nothing about frameworks, databases, or the web.

```text
ONEVO.Api                       HTTP, SignalR, JWT middleware
  -> ONEVO.Infrastructure        EF Core, Redis, Hangfire, SMTP
      -> ONEVO.Application       CQRS handlers, interfaces, DTOs
          -> ONEVO.Domain        Entities, events, value objects
```

## Layer Responsibilities

| Layer | Responsible for | Depends on |
|---|---|---|
| Domain | Business entities, domain events, value objects, business rules | Nothing |
| Application | CQRS handlers, interface definitions, DTOs, validation | Domain |
| Infrastructure | EF Core, JWT, BCrypt, Redis, Hangfire, SMTP, SignalR | Application + Domain |
| Api | HTTP routing, middleware, SignalR hubs | Application + Infrastructure (DI only) |

## Request Lifecycle

```text
HTTP POST /api/v1/leave/requests
  -> TenantResolutionMiddleware sets current user/tenant
  -> Controller maps HTTP request to command/query
  -> MediatR pipeline runs validation, logging, performance, error safety
  -> Handler uses repository/service interfaces to load required data
  -> Domain entity method applies business rules and may raise domain events
  -> IUnitOfWork.SaveChangesAsync commits changes
  -> Infrastructure interceptors set audit fields, soft delete, dispatch domain events
  -> EventHandlers react through their own repository/service interfaces
  -> Controller maps Result<T> to HTTP response
```

## Key Principles

**Framework independence:** Domain entities are plain C# classes. EF mapping is in Infrastructure.

**Persistence boundary:** Handlers and services do not inject EF Core or `ApplicationDbContext` directly. Repositories own database access, tenant filtering, projections, locking, and any explicit platform-admin cross-tenant access.

**Testability:** Handlers take repository/service interfaces and `IUnitOfWork`. Tests mock those interfaces. No HTTP, no DB needed for unit tests.

See [[backend/repository-persistence-boundary|Repository Persistence Boundary]] for the non-negotiable persistence rule and repository placement.

**Single responsibility:** One Command = one use case. One Query = one read operation.

**Result pattern:** Handlers return `Result<T>` for business failures. Exceptions are for infrastructure failures only.

## Related Docs

- [[backend/folder-structure|Folder Structure]]
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/security|Security]]
