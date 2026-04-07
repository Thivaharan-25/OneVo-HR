# Event Bus Topology: ONEVO

## Phase 1: In-Process Domain Events (MediatR)

In Phase 1, all domain events are dispatched in-process via MediatR `INotification`:

```
Publisher Module → MediatR.Publish(event) → All registered INotificationHandler<T>
```

### Advantages
- Zero infrastructure overhead (no message broker needed)
- Synchronous execution within the same transaction (consistency)
- Simple debugging and tracing

### Limitations
- No retry/dead-letter handling (handled by try-catch + logging)
- Events lost if process crashes mid-publish
- All handlers run in the same thread/transaction

### Mitigation: Transactional Outbox (for critical events)

For events that MUST be delivered (e.g., `PayrollRunCompleted`, `LeaveApproved`), use the outbox pattern:

```csharp
// 1. Save entity + outbox event in same transaction
await _context.SaveChangesAsync(ct); // Saves LeaveRequest + OutboxEvent atomically

// 2. Background worker polls outbox and dispatches events
public class OutboxProcessor : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var events = await _outboxRepository.GetUnprocessedAsync(batchSize: 50, ct);
            foreach (var evt in events)
            {
                await _publisher.Publish(evt.Deserialize(), ct);
                evt.MarkProcessed();
            }
            await _unitOfWork.SaveChangesAsync(ct);
            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}
```

### Outbox Table

```sql
CREATE TABLE outbox_events (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL,
    event_type varchar(200) NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz,
    retry_count integer DEFAULT 0,
    last_error text
);

CREATE INDEX idx_outbox_unprocessed ON outbox_events (created_at) WHERE processed_at IS NULL;
```

## Phase 2: RabbitMQ (Future)

When scale requires it, migrate critical events to RabbitMQ:

### Exchange Topology (Planned)

```
onevo.events (topic exchange)
├── core-hr.employee.*     → Queue: attendance-employee-events
│                          → Queue: leave-employee-events
│                          → Queue: skills-employee-events
├── leave.request.*        → Queue: payroll-leave-events
│                          → Queue: calendar-leave-events
│                          → Queue: attendance-leave-events
├── attendance.record.*    → Queue: payroll-attendance-events
├── payroll.run.*          → Queue: notifications-payroll-events
├── performance.review.*   → Queue: skills-review-events
│                          → Queue: notifications-review-events
└── *.*.created|updated    → Queue: audit-all-events (fan-out for audit)
```

### Migration Strategy

1. Keep MediatR for intra-module events (fast, transactional)
2. Add RabbitMQ for cross-module events that need reliability
3. Use the `IntegrationEvent` base class (already in SharedKernel) for RabbitMQ events
4. Dual-publish during migration: MediatR + RabbitMQ
5. Once stable, remove MediatR cross-module handlers

## Related

- [[event-catalog]]
- [[error-handling]]
