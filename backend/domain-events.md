# Domain Events: ONEVO

**Last Updated:** 2026-05-08

Domain events are **optional** in ONEVO. They are not required by Clean Architecture, CQRS, MediatR, or the normal feature folder structure.

Use them only when a completed use case needs decoupled post-save side effects. Most commands should not raise an event.

## Default Rule

Start with the normal CQRS flow:

```text
Controller -> Command/Query -> Validator -> Handler -> Repository/Domain -> UnitOfWork -> Response
```

Only add the event branch when there is a real reason:

```text
UnitOfWork save succeeds -> DomainEventDispatchInterceptor -> EventHandler(s)
```

## When To Use A Domain Event

Use a domain event when all of these are true:

- The main command has already completed its own business responsibility.
- One or more secondary reactions should happen after the save succeeds.
- The original command should not need to know every downstream reaction.
- The side effect can be tested and reasoned about independently.

Examples:

- `EmployeeTerminatedEvent` triggers access revocation, workspace cleanup, and notifications.
- `IdentityVerifiedEvent` triggers onboarding progress.
- `AnomalyDetectedEvent` triggers notification enrichment.

## When Not To Use A Domain Event

Do not create events for:

- Basic CRUD operations.
- Simple logic that belongs directly in the command handler.
- Same-transaction decisions that must succeed or fail with the command.
- Architecture ceremony.
- "Because CQRS needs events." It does not.

## Folder Placement

Only create these folders when an event is justified:

```text
ONEVO.Domain/Features/{Feature}/Events/
ONEVO.Application/Features/{Feature}/EventHandlers/
```

The default feature structure does not include either folder.

## Defining A Domain Event

```csharp
// ONEVO.Domain/Features/CoreHR/Events/EmployeeTerminatedEvent.cs
public record EmployeeTerminatedEvent(
    Guid EmployeeId,
    Guid TenantId,
    DateTimeOffset OccurredAt
) : IDomainEvent;
```

`IDomainEvent` is a marker for in-process MediatR notifications. It is not an external message contract.

## Raising A Domain Event

Only raise an event from a domain method when the event represents something meaningful that already happened.

```csharp
public void Terminate(DateOnly effectiveDate, string reason)
{
    if (Status == EmploymentStatus.Terminated)
        throw new DomainException("Employee is already terminated.");

    Status = EmploymentStatus.Terminated;
    TerminationDate = effectiveDate;
    TerminationReason = reason;

    AddDomainEvent(new EmployeeTerminatedEvent(Id, TenantId, DateTimeOffset.UtcNow));
}
```

## Handling A Domain Event

```csharp
// ONEVO.Application/Features/Auth/EventHandlers/RevokeAccessOnEmployeeTerminatedHandler.cs
public class RevokeAccessOnEmployeeTerminatedHandler
    : INotificationHandler<EmployeeTerminatedEvent>
{
    private readonly IUserAccessRepository _userAccess;
    private readonly IUnitOfWork _uow;

    public RevokeAccessOnEmployeeTerminatedHandler(
        IUserAccessRepository userAccess,
        IUnitOfWork uow)
    {
        _userAccess = userAccess;
        _uow = uow;
    }

    public async Task Handle(EmployeeTerminatedEvent notification, CancellationToken ct)
    {
        await _userAccess.RevokeForEmployeeAsync(notification.EmployeeId, ct);
        await _uow.SaveChangesAsync(ct);
    }
}
```

Event handlers follow the same Application-layer persistence rule as command/query handlers: no EF Core and no `ApplicationDbContext` directly.

## Dispatch Timing

Events are dispatched after `SaveChangesAsync` succeeds. If the database write fails, event handlers do not run.

This keeps events from firing for state that was never committed.

## What Is Not In Phase 1

| Not used | Reason |
|---|---|
| `IEventBus` | No external broker abstraction in Phase 1 |
| `IntegrationEvent` | No cross-service event contracts in Phase 1 |
| MassTransit | No message broker dependency |
| RabbitMQ | No broker infrastructure |
| Outbox tables | No external async message publishing |

ONEVO Phase 1 is a single deployable backend. In-process domain events are available by exception, not as a default module pattern.
