# ADR-001: Per-Module Database Contexts + IEventBus Abstraction

**Date:** 2026-04-25
**Status:** Superseded
**Superseded by:** ADR-002 and ADR-003 on 2026-04-27

---

## Supersession Notice

This ADR is historical only and must not be used for implementation.

The accepted backend direction is:

- One Clean Architecture solution: `ONEVO.Domain`, `ONEVO.Application`, `ONEVO.Infrastructure`, and `ONEVO.Api`
- One backend deployment host: `ONEVO.Api`
- One EF Core `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`
- Database access only through Application-owned repository/reader interfaces implemented in Infrastructure
- No RabbitMQ, no MassTransit, no `IEventBus`, no integration-event broker, and no broker outbox tables in Phase 1
- Optional in-process domain events only when a completed use case needs decoupled post-save side effects

## Historical Decision

The original proposal used per-module DbContexts and a broker-backed event bus to preserve a future microservice extraction path.

That direction was rejected because Phase 1 is a single backend monolith and microservice extraction is no longer a goal. Keeping per-module DbContexts and RabbitMQ would add distributed-systems complexity without a current product requirement.

## Current Replacement

Use the current folder and dependency rules from:

- [[backend/folder-structure|Folder Structure]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]

