# Messaging Architecture: ONEVO

## Overview

ONEVO uses two event buses with different scopes:

- **Cross-module events (integration events):** RabbitMQ via MassTransit — transactional outbox pattern, reliable delivery, idempotent consumers. Phase 1.
- **Intra-module events (domain events):** MediatR `INotification` — in-process, synchronous, within the same module only. No Phase label.

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [[backend/messaging/event-catalog\|Event Catalog]] | Every domain event, publishers, consumers, and payloads |
| [[backend/messaging/exchange-topology\|Exchange Topology]] | RabbitMQ topic exchange, queue bindings, routing key patterns, outbox + idempotency pattern |
| [[backend/messaging/module-event-matrix\|Module Event Matrix]] | Per-module publish/consume overview — 23 modules |
| [[backend/messaging/error-handling\|Error Handling]] | Retry policies, dead-letter handling, idempotency patterns |

## Quick Reference

### Publishing a Cross-Module Integration Event

```csharp
// In your command handler — use IEventBus for events that cross module boundaries
public class ApproveLeaveRequestHandler : IRequestHandler<ApproveLeaveRequestCommand, Result<Unit>>
{
    private readonly IEventBus _eventBus;

    public async Task<Result<Unit>> Handle(ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        // ... business logic
        await _eventBus.PublishAsync(new LeaveApproved(request.Id, request.EmployeeId, ...), ct);
        // Written to leave_outbox_events in the same transaction; forwarded to RabbitMQ by OutboxProcessor
        return Result<Unit>.Success(Unit.Value);
    }
}
```

### Publishing an Intra-Module Domain Event

```csharp
// In your service — use MediatR IPublisher for events that stay within this module
entity.AddDomainEvent(new EmployeeValidatedEvent(employee.Id));
await _unitOfWork.SaveChangesAsync(ct); // DomainEventDispatcher publishes after save
```

### Consuming a Cross-Module Integration Event

```csharp
// In your module's EventHandlers/ folder — use IConsumer<T> for cross-module events
public class UpdatePresenceOnLeaveApprovedConsumer : IConsumer<LeaveApproved>
{
    public async Task Consume(ConsumeContext<LeaveApproved> context)
    {
        // Idempotency guaranteed by MassTransit inbox-state (processed_integration_events table)
        // React to the event...
    }
}
```

### Rules

1. All handlers must be **idempotent** (see [[backend/messaging/error-handling|Error Handling]])
2. Handlers must not throw exceptions that crash the publisher
3. All cross-module integration events use the **[[backend/messaging/exchange-topology|transactional outbox pattern]]** for guaranteed delivery
4. Check [[backend/messaging/event-catalog|Event Catalog]] before publishing or consuming events
5. Always include `TenantId` in event payloads

## Related

- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/exchange-topology|Exchange Topology]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/module-boundaries|Module Boundaries]]
