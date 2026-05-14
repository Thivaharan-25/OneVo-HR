# ADR-003: Single ApplicationDbContext

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001 per-module DbContext section

---

## Context

The original design had per-module DbContexts to support future microservice extraction. With microservice extraction dropped and RabbitMQ removed, that design adds complexity without a current benefit.

## Decision

Use a single EF Core `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`.

- EF configurations are grouped under `ONEVO.Infrastructure/Persistence/Configurations/{Feature}/{SubFeature}/`
- Repository implementations live under `ONEVO.Infrastructure/Persistence/Repositories/{Feature}/{SubFeature}/`
- One migration set lives under `ONEVO.Infrastructure/Persistence/Migrations/`
- `IUnitOfWork` wraps `SaveChangesAsync`
- Optional `DomainEventDispatchInterceptor` dispatches in-process domain events after a successful save

`ApplicationDbContext` is an Infrastructure detail. It must not be injected into command handlers, query handlers, application services, domain services, event handlers, resolvers, or module orchestration classes.

Application owns repository and reader interfaces. Infrastructure implements those interfaces and is the only normal layer that queries EF Core.

## Consequences

**Positive:**

- One migration history is simpler to operate.
- One unit of work can commit cross-feature changes atomically.
- EF configuration remains centralized in Infrastructure.
- Repository implementations centralize tenant filtering, locking, projections, raw SQL, and cross-feature reads.

**Negative:**

- A single DbContext can tempt handlers and services to bypass repositories. This must be blocked by code review and architecture tests.
- Feature-specific repository/read interfaces are required for joins, projections, platform-admin flows, and any operation that would otherwise need direct EF access.

## Alternatives Considered

- Per-feature DbContexts within Infrastructure - rejected because it adds complexity with no Phase 1 extraction plan.
- Exposing `IApplicationDbContext` from Application - rejected because it leaks EF concepts into the application layer and allows direct database access from handlers/services.

