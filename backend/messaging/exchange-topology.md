# Event Bus Topology: ONEVO

## Intra-Module Events (MediatR)

Domain events published and handled **within the same module only**. They never cross a module boundary.

```
Publisher Handler → MediatR.Publish(DomainEvent) → INotificationHandler<T> (same module only)
```

- Zero infrastructure overhead (no message broker needed)
- Executes synchronously within the same transaction (strong consistency)
- Simple debugging and tracing

---

## Phase 1: Cross-Module Events (RabbitMQ via MassTransit)

All integration events that cross module boundaries are delivered via **RabbitMQ** using **MassTransit** with the transactional outbox pattern.

```
Publisher Module
  → IEventBus.PublishAsync(IntegrationEvent)
  → Written to {module}_outbox_events in same DB transaction
  → MassTransit OutboxProcessor polls & forwards to RabbitMQ
  → onevo.events topic exchange
  → Bound queues
  → Consumer module IConsumer<T>
  → Idempotency check (processed_integration_events)
  → Handler logic
```

### Exchange Topology

```
onevo.events (topic exchange)
├── infrastructure.*          → Queue: auth-infrastructure-events
│                             → Queue: configuration-infrastructure-events
│                             → Queue: org-structure-infrastructure-events
├── auth.*                    → Queue: shared-platform-auth-events
├── core-hr.employee.*        → Queue: workforce-presence-employee-events
│                             → Queue: leave-employee-events
│                             → Queue: skills-employee-events
│                             → Queue: documents-employee-events
│                             → Queue: performance-employee-events
│                             → Queue: calendar-employee-events
│                             → Queue: agent-gateway-employee-events
├── workforce.presence.*      → Queue: activity-monitoring-presence-events
│                             → Queue: exception-engine-presence-events
│                             → Queue: payroll-presence-events
│                             → Queue: workforce-presence-leave-events
├── leave.request.*           → Queue: payroll-leave-events
│                             → Queue: calendar-leave-events
│                             → Queue: workforce-presence-leave-events
│                             → Queue: notifications-leave-events
├── activity.*                → Queue: exception-engine-activity-events
│                             → Queue: identity-verification-activity-events
│                             → Queue: productivity-analytics-activity-events
│                             → Queue: discrepancy-engine-activity-events
├── agent.gateway.*           → Queue: exception-engine-agent-events
│                             → Queue: agent-gateway-employee-events
├── exception.*               → Queue: notifications-exception-events
│                             → Queue: productivity-analytics-exception-events
├── payroll.run.*             → Queue: notifications-payroll-events
├── performance.review.*      → Queue: skills-review-events
│                             → Queue: calendar-review-events
│                             → Queue: notifications-review-events
├── analytics.*               → Queue: notifications-analytics-events
├── skills.*                  → Queue: notifications-skills-events
├── documents.*               → Queue: notifications-documents-events
├── grievance.*               → Queue: notifications-grievance-events
├── expense.*                 → Queue: payroll-expense-events
│                             → Queue: notifications-expense-events
├── platform.*                → Queue: notifications-platform-events
├── identity.*                → Queue: notifications-identity-events
├── org.department.*          → Queue: notifications-org-events
└── discrepancy.*             → Queue: notifications-discrepancy-events
```

### Routing Key Patterns

> Routing keys follow `<module>.<aggregate>.<verb_past>` where applicable. See [[backend/messaging/event-catalog|Event Catalog]] for per-event routing keys.

| Module Group | Pattern | Example |
|:------------|:--------|:--------|
| Infrastructure | `infrastructure.<aggregate>.<verb>` | `infrastructure.tenant.created` |
| Auth | `auth.<verb>` | `auth.login` |
| Core HR | `core-hr.employee.<verb>` | `core-hr.employee.hired` |
| Workforce Presence | `workforce.presence.<verb>` | `workforce.presence.started` |
| Leave | `leave.request.<verb>` | `leave.request.approved` |
| Activity Monitoring | `activity.<noun>` | `activity.snapshot` |
| Exception Engine | `exception.<verb>` | `exception.alert` |
| Payroll | `payroll.run.<verb>` | `payroll.run.completed` |
| Performance | `performance.review.<verb>` | `performance.review.started` |
| Skills | `skills.<verb>` | `skills.validated` |

### Transactional Outbox Pattern

Each publisher module has a `{module}_outbox_events` table. Integration events are written to this table in the same database transaction as the business write. MassTransit's OutboxProcessor polls the table and forwards messages to RabbitMQ.

```csharp
// Publisher: IEventBus wraps MassTransit outbox publish
public class ApproveLeaveRequestHandler : IRequestHandler<ApproveLeaveRequestCommand, Result<Unit>>
{
    private readonly IEventBus _eventBus;

    public async Task<Result<Unit>> Handle(ApproveLeaveRequestCommand cmd, CancellationToken ct)
    {
        // ... approve the leave request
        await _eventBus.PublishAsync(new LeaveApproved(leaveRequest.Id, leaveRequest.EmployeeId, ...), ct);
        // LeaveApproved written to leave_outbox_events in same transaction as business write
        return Result<Unit>.Success(Unit.Value);
    }
}

// Consumer: MassTransit IConsumer<T> with idempotency guard
public class UpdatePresenceOnLeaveApprovedConsumer : IConsumer<LeaveApproved>
{
    public async Task Consume(ConsumeContext<LeaveApproved> context)
    {
        // MassTransit inbox-state handles idempotency via processed_integration_events
        // Mark leave days in workforce presence records
    }
}
```

### Idempotency

Each consumer module has a `processed_integration_events` table. MassTransit's inbox-state middleware checks this table before processing — if `event_id` is already present, the message is silently discarded. This prevents double-processing when RabbitMQ redelivers after a transient failure.

---

## Related

- [[backend/messaging/event-catalog|Event Catalog]] — full event list with routing keys
- [[backend/messaging/error-handling|Error Handling]] — retry policies and dead-letter queues
- [[backend/messaging/module-event-matrix|Module Event Matrix]] — per-module publish/consume overview
