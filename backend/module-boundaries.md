# Layer Boundary Rules: ONEVO

**Last Updated:** 2026-04-27

These rules keep the ONEVO Clean Architecture maintainable. **Non-negotiable.**

AI agents: these rules override convenience. Never generate code that violates layer dependencies.

---

## The Dependency Rule

Dependencies point inward only. Outer layers know about inner layers — never the reverse.

```
ONEVO.Api / ONEVO.Admin.Api  (outermost)
        ↓
ONEVO.Application  ←  ONEVO.Infrastructure
        ↓
ONEVO.Domain  (innermost — zero external dependencies)
```

### What each layer may reference

| Layer | May reference |
|-------|--------------|
| `ONEVO.Domain` | Nothing |
| `ONEVO.Application` | `ONEVO.Domain` only |
| `ONEVO.Infrastructure` | `ONEVO.Application` + `ONEVO.Domain` |
| `ONEVO.Api` / `ONEVO.Admin.Api` | `ONEVO.Application` + `ONEVO.Infrastructure` (DI wiring only) |

---

## Rule 1: Application defines interfaces — Infrastructure implements them

```csharp
// CORRECT: interface in Application
// ONEVO.Application/Common/Interfaces/IEmailService.cs
public interface IEmailService
{
    Task SendAsync(string to, string subject, string body, CancellationToken ct);
}

// CORRECT: implementation in Infrastructure
// ONEVO.Infrastructure/Email/SmtpEmailService.cs
public class SmtpEmailService : IEmailService { ... }

// FORBIDDEN: implementation reference in Application handler
using ONEVO.Infrastructure.Email; // ← never
```

---

## Rule 2: Domain has zero framework dependencies

Domain entities have no EF Core attributes. No `[Key]`, no `[Column]`, no `[Required]`.
All mapping is done via `IEntityTypeConfiguration<T>` in Infrastructure.

```csharp
// CORRECT
public class LeaveRequest : BaseEntity
{
    public Guid EmployeeId { get; private set; }
    public DateTime StartDate { get; private set; }
    // ...
    public void Approve()
    {
        Status = ApprovalStatus.Approved;
        AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId));
    }
}

// FORBIDDEN
[Table("leave_requests")]      // ← EF attribute in Domain
public class LeaveRequest { }
```

---

## Rule 3: Handlers return Result<T> — never throw for business failures

```csharp
// CORRECT
public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand cmd, CancellationToken ct)
{
    if (employee is null)
        return Result<LeaveRequestDto>.Failure("Employee not found");
    // ...
    return Result<LeaveRequestDto>.Success(dto);
}

// FORBIDDEN
if (employee is null)
    throw new Exception("Employee not found"); // ← only for infrastructure failures
```

---

## Rule 4: Cross-feature reads go through IApplicationDbContext

Features do not have isolated DbContexts. A handler may query any DbSet it needs.

```csharp
// CORRECT: Leave handler reading employee data
public class CreateLeaveRequestHandler : IRequestHandler<...>
{
    private readonly IApplicationDbContext _db;

    public async Task<Result<LeaveRequestDto>> Handle(CreateLeaveRequestCommand cmd, CancellationToken ct)
    {
        var employee = await _db.Employees
            .FirstOrDefaultAsync(e => e.Id == cmd.EmployeeId, ct);
        // ...
    }
}

// FORBIDDEN: direct DbContext in handler
private readonly ApplicationDbContext _db; // ← concrete, not interface
```

---

## Rule 5: Cross-feature side effects use domain events

When feature A does something that feature B should react to, feature A raises a domain event. Feature B handles it with `INotificationHandler<T>`.

```csharp
// Feature A (Leave) — entity raises event
public void Approve()
{
    Status = ApprovalStatus.Approved;
    AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId)); // ← raises event
}

// Feature B (WorkforcePresence) — reacts in EventHandlers/
public class MarkShiftAbsentOnLeaveApprovedHandler
    : INotificationHandler<LeaveApprovedEvent>
{
    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // mark shift absent
    }
}
```

Events are dispatched **after** `SaveChangesAsync` succeeds via `DomainEventDispatchInterceptor`. If the DB write fails, no events fire.

**What is gone:** `IEventBus`, `IntegrationEvent`, MassTransit, RabbitMQ, Outbox tables.

---

## Rule 6: CancellationToken everywhere

Every handler, repository call, and external HTTP call receives `CancellationToken ct`.

```csharp
// CORRECT
public async Task<Result<T>> Handle(TCommand cmd, CancellationToken ct)
{
    var entity = await _db.Set<T>().FirstOrDefaultAsync(x => x.Id == cmd.Id, ct);
    await _uow.SaveChangesAsync(ct);
}

// FORBIDDEN
await _db.Set<T>().FirstOrDefaultAsync(x => x.Id == cmd.Id); // ← no ct
```

---

## Rule 7: DevPlatform entities have no TenantId

`ApplicationDbContext` applies global tenant filters to all `BaseEntity` instances. `DevPlatformAccount`, `DevPlatformSession`, `AgentVersionRelease`, `AgentDeploymentRing`, `AgentDeploymentRingAssignment` are platform-level entities with no `TenantId` — they use a separate base class and are excluded from tenant filters.

---

## ArchUnitNET Enforcement

```csharp
[Fact]
public void Domain_Should_Not_Reference_Any_Other_Layer()
{
    Types().That().ResideInNamespace("ONEVO.Domain")
        .Should().NotDependOnAnyTypesThat()
        .ResideInNamespace("ONEVO.Application")
        .OrResideInNamespace("ONEVO.Infrastructure")
        .Check(Architecture);
}

[Fact]
public void Application_Should_Not_Reference_Infrastructure()
{
    Types().That().ResideInNamespace("ONEVO.Application")
        .Should().NotDependOnAnyTypesThat()
        .ResideInNamespace("ONEVO.Infrastructure")
        .Check(Architecture);
}

[Fact]
public void Handlers_Should_Not_Use_Concrete_DbContext()
{
    Types().That().HaveNameEndingWith("Handler")
        .Should().NotDependOnAnyTypesThat()
        .HaveExactlyName("ApplicationDbContext")
        .Check(Architecture);
}
```
