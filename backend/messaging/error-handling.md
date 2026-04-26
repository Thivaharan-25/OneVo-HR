# Event Error Handling: ONEVO

## Intra-Module Events (MediatR)

Domain events handled within the same module. Errors are caught and logged without crashing the publisher:

```csharp
public class DomainEventDispatcher
{
    private readonly IPublisher _publisher;
    private readonly ILogger<DomainEventDispatcher> _logger;

    public async Task DispatchEventsAsync(BaseEntity entity, CancellationToken ct)
    {
        foreach (var domainEvent in entity.DomainEvents)
        {
            try
            {
                await _publisher.Publish(domainEvent, ct);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to handle domain event {EventType} for entity {EntityId}",
                    domainEvent.GetType().Name, entity.Id);
            }
        }
        entity.ClearDomainEvents();
    }
}
```

Intra-module events are fire-and-forget within the transaction. They do not use the outbox — if the handler fails, the failure is logged.

---

## Phase 1: Cross-Module Events (RabbitMQ via MassTransit)

### Transactional Outbox

Integration events are written to `{module}_outbox_events` in the same database transaction as the business write. A background OutboxProcessor reads unprocessed events and forwards them to RabbitMQ. This guarantees at-least-once delivery even if the process crashes between the business write and the RabbitMQ publish.

```
Business write + IntegrationEvent → {module}_outbox_events (same transaction)
       ↓
OutboxProcessor (polls WHERE processed_at IS NULL)
       ↓
RabbitMQ → consumer queue
       ↓
IConsumer<T>.Consume() → processed_integration_events (idempotency check)
```

### Retry Policy (MassTransit)

| Attempt | Delay | Behaviour |
|:--------|:------|:----------|
| 1–3 | 5s, 30s, 2m | Automatic retry via MassTransit retry middleware |
| 4–5 | 10m, 1h | Extended backoff |
| 6 | — | Move to Dead Letter Exchange (DLX) |

```csharp
// MassTransit retry configuration (in module registration)
cfg.UseMessageRetry(r => r.Exponential(5, TimeSpan.FromSeconds(5), TimeSpan.FromHours(1), TimeSpan.FromSeconds(5)));
cfg.UseDelayedRedelivery(r => r.Intervals(TimeSpan.FromMinutes(10), TimeSpan.FromHours(1)));
```

### Dead Letter Exchange

After max retries, messages are routed to `onevo.events.dlx`. Each module queue has a corresponding DLX queue (`{queue-name}.dlx`). Dead-lettered messages trigger an `ExceptionAlertCreated` event via the Exception Engine for admin notification.

Monitor DLX queue depth via Prometheus metrics — see [[frontend/performance/monitoring|Monitoring]].

### Idempotency

Each consumer module has a `processed_integration_events` table. MassTransit inbox-state checks this table before processing. If `event_id` is already present, the message is silently discarded:

```csharp
public class UpdatePresenceOnLeaveApprovedConsumer : IConsumer<LeaveApproved>
{
    public async Task Consume(ConsumeContext<LeaveApproved> context)
    {
        // MassTransit inbox-state handles idempotency automatically
        // (checks processed_integration_events before executing Consume body)
        var msg = context.Message;
        // ... update presence records
    }
}
```

### Critical vs Non-Critical Events

| Category | Behaviour on Failure | Examples |
|:---------|:--------------------|:---------|
| **Integration events** | Outbox + MassTransit retry → DLX after max retries | `LeaveApproved`, `PayrollRunCompleted`, `EmployeeHired` |
| **Intra-module domain events** | Logged and skipped | `EmployeeValidated`, `BalanceRecalculated` |

---

## Related

- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/exchange-topology|Exchange Topology]]
- [[code-standards/logging-standards|Logging Standards]]
