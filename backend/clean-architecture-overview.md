# Clean Architecture Overview: ONEVO

**Last Updated:** 2026-04-27

## What is Clean Architecture

Clean Architecture organises code into concentric layers. The core rule: **dependencies point inward**. The innermost layer (Domain) knows nothing about frameworks, databases, or the web.

```
┌─────────────────────────────────────┐
│  ONEVO.Api / ONEVO.Admin.Api        │  HTTP, SignalR, JWT middleware
│  ┌───────────────────────────────┐  │
│  │  ONEVO.Infrastructure         │  │  EF Core, Redis, Hangfire, SMTP
│  │  ┌─────────────────────────┐  │  │
│  │  │  ONEVO.Application       │  │  │  CQRS handlers, interfaces, DTOs
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │  ONEVO.Domain      │  │  │  │  Entities, events, value objects
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Responsible for | Depends on |
|-------|----------------|-----------|
| Domain | Business entities, domain events, value objects, business rules | Nothing |
| Application | CQRS handlers, interface definitions, DTOs, validation | Domain |
| Infrastructure | EF Core, JWT, BCrypt, Redis, Hangfire, SMTP, SignalR | Application + Domain |
| Api/Admin.Api | HTTP routing, middleware, SignalR hubs | Application + Infrastructure (DI only) |

## Request Lifecycle

```
HTTP POST /api/v1/leave/requests
    ↓
TenantResolutionMiddleware (sets ICurrentUser from JWT)
    ↓
Controller.CreateLeaveRequest(dto)
    ↓
_mediator.Send(new CreateLeaveRequestCommand(...))
    ↓
[1] ValidationBehavior         — FluentValidation
[2] LoggingBehavior            — request name + user + tenant
[3] PerformanceBehavior        — warns if > 500ms
[4] UnhandledExceptionBehavior — safety net
    ↓
CreateLeaveRequestHandler.Handle(command, ct)
    ├── queries IApplicationDbContext for employee
    ├── calls LeaveRequest.Create(...)  — entity raises LeaveRequestSubmittedEvent
    └── await _uow.SaveChangesAsync(ct)
            ↓
        AuditableEntityInterceptor  — sets CreatedAt, UpdatedAt, CreatedById
        SoftDeleteInterceptor       — converts Delete → IsDeleted=true
        DomainEventDispatchInterceptor → IPublisher.Publish(LeaveRequestSubmittedEvent)
            ↓
        NotificationsHandler reacts — sends email notification in-process
    ↓
Result<LeaveRequestDto>.Success(dto)
    ↓
HTTP 201 Created
```

## Key Principles

**Framework independence:** Domain entities are plain C# classes. EF mapping is in Infrastructure.

**Testability:** Handlers take interface parameters. Tests mock `IApplicationDbContext`, `IUnitOfWork`, etc. No HTTP, no DB needed for unit tests.

**Single responsibility:** One Command = one use case. One Query = one read operation.

**Result pattern:** Handlers return `Result<T>` for business failures. Exceptions are for infrastructure failures only.

## Related Docs

- [[backend/folder-structure|Folder Structure]] — full solution tree
- [[backend/layer-guide/domain-layer|Domain Layer Guide]]
- [[backend/layer-guide/application-layer|Application Layer Guide]]
- [[backend/layer-guide/infrastructure-layer|Infrastructure Layer Guide]]
- [[backend/cqrs-patterns|CQRS Patterns]]
- [[backend/domain-events|Domain Events]]
- [[backend/security|Security]]
