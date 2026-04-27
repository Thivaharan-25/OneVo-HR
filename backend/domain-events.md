# Domain Events: ONEVO

**Last Updated:** 2026-04-27

Domain events replace RabbitMQ, MassTransit, IEventBus, and the transactional outbox entirely. All cross-feature communication is **in-process via MediatR**.

---

## How it works

1. Entity method raises a business action (e.g. `LeaveRequest.Approve()`)
2. The method calls `AddDomainEvent(new LeaveApprovedEvent(...))` — stored in `BaseEntity.DomainEvents`
3. Handler calls `_uow.SaveChangesAsync(ct)` — persists DB changes
4. `DomainEventDispatchInterceptor` runs after the DB write succeeds:
   - Collects all `DomainEvents` from EF Core tracked entities
   - Calls `entity.ClearDomainEvents()`
   - Publishes each via `IPublisher.Publish(domainEvent, ct)` (MediatR)
5. Any `INotificationHandler<TEvent>` registered in DI reacts in-process

**Atomicity:** If `SaveChangesAsync` throws, the interceptor never runs — no events fire. No partial state.

---

## Defining a domain event

```csharp
// ONEVO.Domain/Features/Leave/Events/LeaveApprovedEvent.cs
public record LeaveApprovedEvent(
    Guid LeaveRequestId,
    Guid EmployeeId
) : IDomainEvent; // IDomainEvent : INotification (MediatR)
```

---

## Raising a domain event (on entity)

```csharp
// ONEVO.Domain/Features/Leave/Entities/LeaveRequest.cs
public void Approve()
{
    if (Status != ApprovalStatus.Pending)
        throw new DomainException("Only pending requests can be approved.");

    Status = ApprovalStatus.Approved;
    AddDomainEvent(new LeaveApprovedEvent(Id, EmployeeId)); // ← collected, not dispatched yet
}
```

---

## Handling a domain event (cross-feature)

```csharp
// ONEVO.Application/Features/WorkforcePresence/EventHandlers/
// LeaveApprovedEventHandler.cs
public class LeaveApprovedEventHandler : INotificationHandler<LeaveApprovedEvent>
{
    private readonly IApplicationDbContext _db;
    private readonly IUnitOfWork _uow;

    public LeaveApprovedEventHandler(IApplicationDbContext db, IUnitOfWork uow)
    {
        _db = db;
        _uow = uow;
    }

    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // Mark the employee's shift as absent during leave period
        var shifts = await _db.PresenceRecords
            .Where(p => p.EmployeeId == notification.EmployeeId)
            .ToListAsync(ct);

        foreach (var shift in shifts)
            shift.MarkAbsent();

        await _uow.SaveChangesAsync(ct);
    }
}
```

---

## Integration registry (cross-feature auto-wiring)

| Event | Published by | Handled by | Effect |
|-------|-------------|-----------|--------|
| `LeaveApprovedEvent` | Leave | WorkforcePresence | Mark shift absent |
| `LeaveApprovedEvent` | Leave | Payroll | Create deduction entry |
| `EmployeeCreatedEvent` | CoreHR | Auth | Create user account |
| `EmployeeTerminatedEvent` | CoreHR | Auth | Deactivate user |
| `EmployeeTerminatedEvent` | CoreHR | WMS bridge | Revoke WMS access |
| `SnapshotCapturedEvent` | ActivityMonitoring | ExceptionEngine | Evaluate anomaly rules |
| `PresenceRecordedEvent` | WorkforcePresence | ActivityMonitoring | Correlate agent snapshots |
| `AnomalyDetectedEvent` | ExceptionEngine | Notifications | Send alert |

---

## What is gone

| Old | New |
|-----|-----|
| `IEventBus` | `IDomainEvent` + `IPublisher` (MediatR) |
| `IntegrationEvent` base class | `IDomainEvent` interface |
| `MassTransit` NuGet | removed |
| `RabbitMQ` | removed |
| `IConsumer<T>` | `INotificationHandler<T>` |
| Per-module `OutboxMessage.cs` | removed |
| Per-module `OutboxProcessor.cs` | removed |
| `backend/messaging/` folder | deleted |
