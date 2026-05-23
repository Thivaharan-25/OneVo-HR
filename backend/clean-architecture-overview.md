# Clean Architecture Overview: ONEVO

**Canonical folder structure source:** `ONEVO-backend-folder-structure.md` — when this file and the folder structure file conflict, the folder structure file wins.

**Last Updated:** 2026-05-13

Clean Architecture organises code into layers. The core rule is: dependencies point inward. Domain knows nothing about frameworks, databases, or the web.

```text
ONEVO.Api
  -> ONEVO.Application
  -> ONEVO.Infrastructure

ONEVO.Infrastructure
  -> ONEVO.Application
  -> ONEVO.Domain

ONEVO.Application
  -> ONEVO.Domain

ONEVO.Domain
  -> no project dependencies
```

Current implementation target: .NET 10 / C# 14.

Domain events are optional. They are not required by Clean Architecture or CQRS.

## Layer Responsibilities

| Layer | Responsible for | Depends on |
|---|---|---|
| Domain | Business entities, value objects, business rules, optional domain events | Nothing |
| Application | CQRS handlers, interface definitions, DTOs, validation | Domain |
| Infrastructure | EF Core, JWT, BCrypt, Redis, Hangfire, SMTP, SignalR | Application + Domain |
| Api | HTTP routing, middleware, SignalR hubs | Application + Infrastructure for DI |

## Request Lifecycle

```text
HTTP request
  -> TenantResolutionMiddleware sets current user/tenant
  -> Controller maps HTTP request to command/query
  -> MediatR pipeline runs validation, logging, performance, error safety
  -> Handler uses repository/service interfaces to load required data
  -> Domain entity method applies business rules
  -> IUnitOfWork.SaveChangesAsync commits changes
  -> Controller maps Result<T> to HTTP response
```

Short form:

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Optional event branch:

```text
UnitOfWork save succeeds -> DomainEventDispatchInterceptor -> EventHandler(s)
```

Use that optional branch only when a completed use case needs decoupled post-save side effects.

## Key Principles

**Framework independence:** Domain entities are plain C# classes. EF mapping is in Infrastructure.

**Persistence boundary:** Handlers and services do not inject EF Core or `ApplicationDbContext` directly. Repositories own database access, tenant filtering, projections, locking, and explicit platform-admin cross-tenant access.

**Testability:** Handlers take repository/service interfaces and `IUnitOfWork`. Tests mock those interfaces. No HTTP or database is needed for normal handler unit tests.

**Single responsibility:** One Command = one write use case. One Query = one read operation.

**Result pattern:** Handlers return `Result<T>` for business failures. Exceptions are for infrastructure failures only.

**Events by exception:** Do not create `Events/` or `EventHandlers/` folders as a default template. Add them only when there is a real side effect that benefits from decoupling.

## Related Docs

- [[backend/folder-structure|Folder Structure]]
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/security|Security]]
