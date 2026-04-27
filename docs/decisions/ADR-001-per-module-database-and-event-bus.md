> **Status: SUPERSEDED**
> Superseded by [ADR-002](ADR-002-clean-architecture-cqrs.md) and [ADR-003](ADR-003-single-applicationdbcontext.md) on 2026-04-27.
> Reason: Clean Architecture adopted. Microservice extraction path dropped. RabbitMQ removed. Per-module DbContexts consolidated into single ApplicationDbContext.

---

# ADR-001: Per-Module Database Contexts + IEventBus Abstraction

**Date:** 2026-04-25  
**Status:** Accepted  
**Deciders:** Thivaharan (Product Owner + Lead)

---

## Context

ONEVO is currently built as a **modular monolith** — one deployable .NET 9 application with 23 modules, all sharing a single PostgreSQL instance.

The original design used a single `ApplicationDbContext` that registered all module entities together. While simple to start, this creates a **hard coupling at the data layer** that makes future microservice extraction significantly harder:

- Splitting a module into its own service requires untangling shared DbContext, EF migrations, and cross-module FK references
- Transactions that span multiple modules become impossible to isolate
- Each module cannot be independently scaled, replicated, or replaced

Additionally, cross-module async communication was implemented directly with MediatR `INotification`, which is **in-process only** — it cannot be replaced with a message broker without rewriting all event publishers and consumers.

RabbitMQ and Docker are **Phase 1 requirements**, not future plans. Only the microservice split (separate processes, separate DB instances per module) is deferred.

---

## Decision

### 1. Per-Module DbContext (Database Schema Isolation)

Each module owns its own `{Module}DbContext`. There is **no shared ApplicationDbContext** that spans multiple modules.

```
ONEVO.Modules.Leave/
  Internal/
    Persistence/
      LeaveDbContext.cs         ← Only maps leave_* tables
      LeaveDbContextFactory.cs  ← For EF migrations

ONEVO.Modules.CoreHR/
  Internal/
    Persistence/
      CoreHRDbContext.cs        ← Only maps employees, salary_history, etc.
```

All module DbContexts connect to the **same PostgreSQL instance** (single deployment) but are logically isolated. Migrations are per-module.

**Microservice extraction path:** When a module is split out, its `{Module}DbContext` becomes the service's own database. No rewriting — just point it at a dedicated PostgreSQL instance and remove the module from the monolith.

Cross-module data access goes through **Public service interfaces** (sync) or **IEventBus** (async). Modules never query each other's tables directly, even within the monolith.

### 2. IEventBus + RabbitMQ for Integration Events (Phase 1)

All cross-module async communication uses an `IEventBus` interface backed by **RabbitMQ in Phase 1**. MediatR is kept only for CQRS (commands/queries) and domain events within a single module.

```csharp
// SharedKernel — cross-module async contract
public interface IEventBus
{
    Task PublishAsync<T>(T integrationEvent, CancellationToken ct = default)
        where T : IntegrationEvent;
}

public abstract record IntegrationEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; } = DateTimeOffset.UtcNow;
    public string EventType => GetType().Name;
}
```

**Phase 1 (monolith + RabbitMQ):** `IEventBus` is implemented with RabbitMQ (MassTransit). All modules run in one process but communicate through the broker — this is intentional. The same topology that runs in the monolith is the topology that microservices will use.

```csharp
// Infrastructure.Messaging.RabbitMq
public class RabbitMqEventBus : IEventBus
{
    private readonly IBus _bus; // MassTransit
    public Task PublishAsync<T>(T evt, CancellationToken ct)
        where T : IntegrationEvent
        => _bus.Publish(evt, ct);
}
```

**Future (microservices):** No messaging code changes. Extract the module to its own container, point its `DbContext` at a dedicated DB instance. It still connects to the same RabbitMQ broker and subscribes to the same queues — already working.

### 3. Domain Events vs Integration Events

| Type | Scope | Mechanism | Lives in |
|:-----|:------|:----------|:---------|
| **Domain Event** | Within a module | MediatR `INotification` (direct) | Module internal |
| **Integration Event** | Cross-module (or cross-service) | `IEventBus` abstraction | SharedKernel + Module Public/Events/ |

Domain events never leave the module. Only integration events cross module boundaries. This maps cleanly to microservices: domain events stay in-process, integration events go over RabbitMQ.

### 4. Docker Compose — Phase 1 Topology

All services run together in one `docker-compose.yml`:
- `onevo-api` — the .NET 9 monolith (all modules in one process)
- `postgres` — single PostgreSQL instance (all module schemas co-located)
- `rabbitmq` — active in Phase 1, used for all cross-module integration events
- `redis` — caching, rate limiting, feature flag cache

When a module is extracted to a microservice, it gets its own Docker service entry and its own Postgres service. The monolith removes the module's DI registration. RabbitMQ topology is unchanged.

---

## Consequences

### Positive
- Modules are independently extractable into microservices without rewriting data or messaging layers
- Module migrations are isolated — one module's schema change cannot break another's
- `IEventBus` lets the team swap RabbitMQ in **without touching business logic**
- Docker Compose already mirrors the future microservice topology

### Negative / Trade-offs
- **No cross-module transactions.** Operations that previously used a shared DbContext in one `SaveChanges()` call must now use the **Saga pattern** or **eventual consistency via integration events** for cross-module writes.
- **More DbContext registrations** — DI setup is slightly more complex. Mitigated by each module registering its own DbContext in `{Name}Module.cs`.
- **Module migrations are separate** — `dotnet ef migrations add` must be run per-module project. Scripted via CI.

---

## Migration from Shared DbContext

If any shared `ApplicationDbContext` was scaffolded during early development:

1. Identify which entities belong to which module (follow table ownership in `module-boundaries.md`)
2. Create `{Module}DbContext` per module, moving only that module's entity configurations
3. Move EF migrations to the module's `Internal/Persistence/Migrations/` folder
4. Remove entities from the shared context
5. Replace any cross-module direct DB queries with Public interface calls

---

## Related

- [[backend/module-boundaries|Module Boundaries]] — Rule 3: Each Module Owns Its Data
- [[backend/messaging/exchange-topology|Exchange Topology]] — Transactional outbox pattern
- [[backend/messaging/event-catalog|Event Catalog]] — Integration events published per module
- [[backend/shared-kernel|Shared Kernel]] — IEventBus, IntegrationEvent base types
- [[AI_CONTEXT/tech-stack|Tech Stack]] — Docker, RabbitMQ, PostgreSQL
