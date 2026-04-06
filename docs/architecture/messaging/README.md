# Messaging Architecture: ONEVO

## Overview

ONEVO uses a two-phase messaging strategy:

- **Phase 1 (current):** In-process domain events via MediatR `INotification`
- **Phase 2 (future):** RabbitMQ for cross-module events requiring reliability at scale

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [[event-catalog]] | Every domain event, publishers, consumers, and payloads |
| [[exchange-topology]] | How events flow between modules (MediatR now, RabbitMQ later) |
| [[error-handling]] | Retry policies, dead-letter handling, idempotency patterns |

## Quick Reference

### Publishing an Event

```csharp
// In your service/handler:
entity.AddDomainEvent(new EmployeeHiredEvent(employee.Id, employee.TenantId, employee.DepartmentId));
await _unitOfWork.SaveChangesAsync(ct); // DomainEventDispatcher publishes after save
```

### Consuming an Event

```csharp
// In your module's EventHandlers/ folder:
public class HandleEmployeeHired : INotificationHandler<EmployeeHiredEvent>
{
    public async Task Handle(EmployeeHiredEvent notification, CancellationToken ct)
    {
        // React to the event (must be idempotent)
    }
}
```

### Rules

1. All handlers must be **idempotent** (see [[error-handling]])
2. Handlers must not throw exceptions that crash the publisher
3. Critical events use the **[[exchange-topology|outbox pattern]]** for guaranteed delivery
4. Check [[event-catalog]] before publishing or consuming events
5. Always include `TenantId` in event payloads

## Related

- [[module-boundaries]] — sync vs async communication rules
- [[module-catalog]] — which modules publish/consume which events
- [[shared-kernel]] — DomainEvent base class
