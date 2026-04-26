# Event Bus Topology: ONEVO

## Two Levels of Events

ONEVO uses two distinct event mechanisms. Never mix them up:

| Level | Type | Scope | Mechanism | Why |
|:------|:-----|:------|:----------|:----|
| 1 | **Domain Event** | Within one module | MediatR `INotification` | Fast, transactional, no broker overhead |
| 2 | **Integration Event** | Cross-module | RabbitMQ via `IEventBus` | Reliable delivery, retry, decoupled, microservice-ready |

**Rule:** Domain events never leave the module that published them. If another module needs to react, that is an integration event.

---

## Level 1: Domain Events (MediatR — intra-module only)

Used for side effects within the same module — e.g., a leave request approved triggers balance recalculation inside the Leave module.

```
Command Handler
  → saves to LeaveDbContext
  → MediatR.Publish(LeaveBalanceChangedEvent)  ← domain event, stays in Leave module
  → UpdateLeaveBalanceHandler (same module)
```

MediatR is also the CQRS dispatcher for all commands and queries. It is **not** used for cross-module communication.

---

## Level 2: Integration Events (RabbitMQ — cross-module)

Used whenever Module A needs to inform Module B of something. Always goes through RabbitMQ, even in the monolith. This is what makes microservice extraction a process split instead of a rewrite.

### Full Flow

```
Module A (Leave)
  ┌────────────────────────────────────────────────────┐
  │  ApproveLeaveHandler                               │
  │    1. leaveRequest.Approve()                       │
  │    2. LeaveDbContext.SaveChanges()  ──────────────►│ leave_requests row updated
  │       (same transaction writes to outbox)  ───────►│ leave_outbox_events row written
  └────────────────────────────────────────────────────┘
                        ↓  (5s poll)
  ┌────────────────────────────────────────────────────┐
  │  LeaveOutboxProcessor (BackgroundService)          │
  │    reads leave_outbox_events WHERE processed IS NULL│
  │    IEventBus.PublishAsync(LeaveApprovedEvent)      │
  │    marks row processed                             │
  └────────────────────────────────────────────────────┘
                        ↓
              RabbitMQ — onevo.events exchange
              routing key: leave.request.approved
                        ↓
         ┌──────────────┴──────────────┐
         ↓                             ↓
  payroll-leave-events           calendar-leave-events
         ↓                             ↓
  Module B (Payroll)            Module C (Calendar)
  ┌─────────────────────┐       ┌─────────────────────┐
  │  1. check idempotency│       │  1. check idempotency│
  │  2. process event    │       │  2. process event    │
  │  3. PayrollDbContext │       │  3. CalendarDbContext│
  │     .SaveChanges()   │       │     .SaveChanges()   │
  │  4. ACK → RabbitMQ  │       │  4. ACK → RabbitMQ  │
  └─────────────────────┘       └─────────────────────┘
```

---

## Transactional Outbox (per-module)

Every module that publishes integration events has its own outbox table inside its own `DbContext`. Writing the business data and the outbox entry happen in one transaction — guaranteed atomic.

### Per-module outbox tables

```sql
-- Each module owns its outbox. Never share across modules.
CREATE TABLE leave_outbox_events (          -- lives in Leave module schema
    id              uuid PRIMARY KEY,
    tenant_id       uuid NOT NULL,
    event_type      varchar(200) NOT NULL,
    payload         jsonb NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    processed_at    timestamptz,
    retry_count     integer DEFAULT 0,
    last_error      text
);
CREATE INDEX idx_leave_outbox_unprocessed
    ON leave_outbox_events (created_at) WHERE processed_at IS NULL;

-- Repeat pattern per module: core_hr_outbox_events, payroll_outbox_events, etc.
```

### OutboxProcessor (one per module)

```csharp
// ONEVO.Modules.Leave/Internal/Messaging/LeaveOutboxProcessor.cs
public class LeaveOutboxProcessor : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IEventBus _eventBus;

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            using var scope = _scopeFactory.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<LeaveDbContext>();

            var pending = await db.OutboxEvents
                .Where(e => e.ProcessedAt == null && e.RetryCount < 5)
                .OrderBy(e => e.CreatedAt)
                .Take(50)
                .ToListAsync(ct);

            foreach (var entry in pending)
            {
                try
                {
                    var @event = entry.Deserialize(); // IntegrationEvent
                    await _eventBus.PublishAsync(@event, ct);
                    entry.MarkProcessed();
                }
                catch (Exception ex)
                {
                    entry.RecordFailure(ex.Message);
                }
            }

            await db.SaveChangesAsync(ct);
            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}
```

---

## Exchange Topology

```
onevo.events  (topic exchange — durable)
│
├── routing key: core-hr.employee.*
│     → Queue: leave-employee-events          (Leave module)
│     → Queue: workforce-employee-events      (WorkforcePresence module)
│     → Queue: skills-employee-events         (Skills module)
│     → Queue: documents-employee-events      (Documents module)
│     → Queue: calendar-employee-events       (Calendar module)
│     → Queue: notifications-employee-events  (Notifications module)
│
├── routing key: leave.request.*
│     → Queue: payroll-leave-events           (Payroll module)
│     → Queue: calendar-leave-events          (Calendar module)
│     → Queue: workforce-leave-events         (WorkforcePresence module)
│     → Queue: notifications-leave-events     (Notifications module)
│
├── routing key: workforce.presence.*
│     → Queue: monitoring-presence-events     (ActivityMonitoring module)
│     → Queue: exception-presence-events      (ExceptionEngine module)
│
├── routing key: payroll.run.*
│     → Queue: notifications-payroll-events   (Notifications module)
│
├── routing key: performance.review.*
│     → Queue: skills-review-events           (Skills module)
│     → Queue: notifications-review-events    (Notifications module)
│
├── routing key: agent.gateway.*
│     → Queue: monitoring-agent-events        (ActivityMonitoring module)
│
└── routing key: #  (catch-all)
      → Queue: audit-all-events               (Audit module — fan-out)
```

### Dead Letter Configuration

```
Each queue has a paired dead letter queue:
  payroll-leave-events  →  (on failure × 3)  →  payroll-leave-events.dlq

DLQ messages are held for manual inspection / replay.
Retry policy: 3 attempts with exponential backoff (5s, 25s, 125s).
```

---

## Consumer Idempotency

RabbitMQ delivers at-least-once. Consumers must deduplicate.

Each module that consumes integration events has a `processed_integration_events` table:

```sql
CREATE TABLE processed_integration_events (   -- per module DbContext
    event_id     uuid PRIMARY KEY,
    event_type   varchar(200) NOT NULL,
    processed_at timestamptz NOT NULL DEFAULT now()
);
```

Consumer pattern:

```csharp
public class PayrollAdjustmentOnLeaveApprovedHandler
    : IIntegrationEventHandler<LeaveApprovedIntegrationEvent>
{
    public async Task HandleAsync(LeaveApprovedIntegrationEvent evt, CancellationToken ct)
    {
        // Idempotency check — skip if already processed
        if (await _db.ProcessedEvents.AnyAsync(e => e.EventId == evt.EventId, ct))
            return;

        // Business logic
        await _payrollService.ApplyLeaveDeduction(evt.EmployeeId, evt.Days, ct);

        // Mark processed — in same transaction as business write
        _db.ProcessedEvents.Add(new ProcessedIntegrationEvent(evt.EventId, evt.EventType));
        await _db.SaveChangesAsync(ct);
    }
}
```

---

## Docker Compose (Phase 1)

All services run together in one compose file:

```yaml
services:
  onevo-api:
    build: ./backend
    ports: ["5000:5000"]
    depends_on: [postgres, rabbitmq, redis]
    environment:
      - ConnectionStrings__Postgres=Host=postgres;Database=onevo;...
      - RabbitMq__Host=rabbitmq
      - RabbitMq__Username=onevo
      - RabbitMq__Password=${RABBITMQ_PASSWORD}

  postgres:
    image: postgres:16
    volumes: [postgres-data:/var/lib/postgresql/data]

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI (dev only)
    volumes: [rabbitmq-data:/var/lib/rabbitmq]

  redis:
    image: redis:7

volumes:
  postgres-data:
  rabbitmq-data:
```

---

## Microservice Extraction (Future — zero messaging rewrite)

When a module is ready to be extracted:

1. Create a new Docker service in compose pointing at its own Postgres instance
2. The module's code is unchanged — it still uses `IEventBus` and its own `DbContext`
3. Remove the module from the monolith's DI registration
4. The module's consumer queue already exists in RabbitMQ — it just now runs in a separate process

```
Before extraction:
  onevo-api (monolith) → publishes to RabbitMQ → onevo-api (monolith) consumes

After extraction:
  onevo-api (monolith) → publishes to RabbitMQ → payroll-service (separate container) consumes
```

No publisher changes. No consumer code changes. Just a process boundary.

---

## Related

- [[backend/messaging/event-catalog|Event Catalog]] — all 40+ integration events
- [[backend/messaging/error-handling|Error Handling]] — Result<T>, retry, DLQ policy
- [[backend/module-boundaries|Module Boundaries]] — per-module DbContext rule
- [[docs/decisions/ADR-001-per-module-database-and-event-bus|ADR-001]] — full rationale
