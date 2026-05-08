# Layer Boundary Rules: ONEVO

**Last Updated:** 2026-05-08

These rules keep the ONEVO Clean Architecture maintainable. AI agents must follow these rules over convenience.

## The Dependency Rule

Dependencies point inward only. Outer layers know about inner layers; inner layers never know about outer layers.

```text
ONEVO.Api
    -> ONEVO.Application <- ONEVO.Infrastructure
           -> ONEVO.Domain
```

| Layer | May reference |
|---|---|
| `ONEVO.Domain` | Nothing |
| `ONEVO.Application` | `ONEVO.Domain` only |
| `ONEVO.Infrastructure` | `ONEVO.Application` + `ONEVO.Domain` |
| `ONEVO.Api` | `ONEVO.Application` + `ONEVO.Infrastructure` for DI |

## Rule 1: Application Defines Interfaces, Infrastructure Implements Them

```csharp
// Correct: interface in Application
public interface IEmailService
{
    Task SendAsync(string to, string subject, string body, CancellationToken ct);
}

// Correct: implementation in Infrastructure
public class SmtpEmailService : IEmailService
{
    // ...
}
```

Application handlers must not reference Infrastructure implementations directly.

## Rule 2: Domain Has Zero Framework Dependencies

Domain entities have no EF Core attributes and no framework dependencies. All mapping is done through `IEntityTypeConfiguration<T>` in Infrastructure.

```csharp
// Correct
public class LeaveRequest : BaseEntity
{
    public Guid EmployeeId { get; private set; }
    public DateOnly StartDate { get; private set; }

    public void Approve(Guid approverId)
    {
        Status = ApprovalStatus.Approved;
        ApprovedById = approverId;
    }
}
```

```csharp
// Forbidden
[Table("leave_requests")]
public class LeaveRequest
{
}
```

## Rule 3: Handlers Return Result<T>

Handlers return `Result<T>` for business failures. Exceptions are for infrastructure failures and truly unexpected states.

```csharp
public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand command, CancellationToken ct)
{
    var employee = await _employees.GetByIdAsync(command.EmployeeId, ct);

    if (employee is null)
        return Result<LeaveRequestDto>.Failure("Employee not found");

    return Result<LeaveRequestDto>.Success(dto);
}
```

## Rule 4: Persistence Access Goes Through Repositories

Handlers, services, optional event handlers, permission resolvers, tenant provisioning services, and module orchestration classes do not query EF Core directly.

```csharp
// Correct
public class CreateLeaveRequestHandler : IRequestHandler<CreateLeaveRequestCommand, Result<LeaveRequestDto>>
{
    private readonly IEmployeeReader _employees;
    private readonly ILeaveRequestRepository _leaveRequests;
}
```

```csharp
// Forbidden
private readonly ApplicationDbContext _db;

// Forbidden
private readonly IApplicationDbContext _db;
```

Repository implementations live in `ONEVO.Infrastructure/Persistence/Repositories/{Feature}/` and are the normal place for EF Core, `IgnoreQueryFilters()`, raw SQL, tenant predicates, projections, and locking.

## Rule 5: Events Are Optional, Not Default

Clean Architecture and CQRS do not require events or event handlers.

Use direct command-handler logic, repositories, readers, and Application services for normal use-case work. Use domain events only when a saved business action needs decoupled post-save side effects.

Good event candidates:

- A completed employee termination should trigger multiple independent cleanup reactions.
- A persisted anomaly should trigger notification enrichment.
- A successful identity verification should trigger onboarding progress.

Poor event candidates:

- Basic CRUD operations.
- Logic that belongs to the current command transaction.
- Side effects added only because every feature template has `Events/`.

If a domain event is justified:

```text
ONEVO.Domain/Features/{Feature}/Events/{EventName}.cs
ONEVO.Application/Features/{Feature}/EventHandlers/{EventName}Handler.cs
```

Events are dispatched only after `SaveChangesAsync` succeeds. If the database write fails, no event handlers run.

RabbitMQ, MassTransit, `IEventBus`, `IntegrationEvent`, and Outbox tables are not part of Phase 1.

## Rule 6: CancellationToken Everywhere

Every handler, repository call, and external HTTP call receives `CancellationToken ct`.

```csharp
await _repository.GetByIdAsync(command.Id, ct);
await _uow.SaveChangesAsync(ct);
```

Do not use `CancellationToken.None` inside request-scoped code.

## Rule 7: DevPlatform Entities Have No TenantId

`ApplicationDbContext` applies global tenant filters to tenant-owned entities. Platform-level DevPlatform entities use a separate base class and are excluded from tenant filters.

## ArchUnitNET Enforcement

Architecture tests enforce at least:

- Domain must not reference Application, Infrastructure, or Api.
- Application must not reference Infrastructure.
- Handlers must not depend on `ApplicationDbContext`.
- Handlers must not depend on `IApplicationDbContext`.
