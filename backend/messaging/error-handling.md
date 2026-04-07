# Event Error Handling: ONEVO

## Phase 1: MediatR In-Process Events

### Strategy

Since all events run in-process, errors in event handlers are caught and logged without crashing the publisher:

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
                
                // For critical events, write to outbox for retry
                if (domainEvent is ICriticalEvent)
                {
                    await _outboxRepository.AddAsync(new OutboxEvent(domainEvent), ct);
                }
            }
        }
        entity.ClearDomainEvents();
    }
}
```

### Critical vs Non-Critical Events

| Category | Behavior on Failure | Examples |
|:---------|:-------------------|:---------|
| **Critical** | Written to outbox for retry | `LeaveApproved`, `PayrollRunCompleted`, `ExpenseClaimApproved` |
| **Non-Critical** | Logged and skipped | `RecognitionGiven`, `GoalCreated`, `CalendarEventCreated` |

### Outbox Retry Policy

- Max 5 retries with exponential backoff (5s, 30s, 2m, 10m, 1h)
- After 5 failures: move to dead-letter state, alert via notification
- Dead-letter events reviewed manually by admin

### Idempotency

All event handlers must be idempotent — processing the same event twice should produce the same result:

```csharp
public class MarkLeaveInAttendanceHandler : INotificationHandler<LeaveApprovedEvent>
{
    public async Task Handle(LeaveApprovedEvent notification, CancellationToken ct)
    {
        // Idempotent: check if already processed
        var existing = await _attendanceRepo.GetByLeaveRequestIdAsync(notification.LeaveRequestId, ct);
        if (existing is not null) return; // Already processed
        
        // Process the event...
    }
}
```

## Phase 2: RabbitMQ Error Handling (Planned)

- Dead Letter Exchange (DLX) per queue
- 3-retry policy with exponential backoff
- Poison message quarantine after max retries
- Monitoring via Prometheus metrics on DLX message count (see [[monitoring]])

## Related

- [[event-catalog]]
- [[exchange-topology]]
- [[logging-standards]]
