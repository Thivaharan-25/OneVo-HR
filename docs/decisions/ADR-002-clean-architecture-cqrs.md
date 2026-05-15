# ADR-002: Adopt Clean Architecture + CQRS

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001

---

## Context

ONEVO was designed as a modular monolith with separate module projects. No production backend code had been written for that direction. The delivery timeline and the dropped microservice extraction goal made the original architecture unnecessarily complex.

## Decision

Adopt Clean Architecture with a 4-layer solution:

- `ONEVO.Domain` - entities, value objects, errors, enums, and optional domain events
- `ONEVO.Application` - CQRS handlers, DTOs, validators, repository interfaces, and service interfaces
- `ONEVO.Infrastructure` - EF Core, repositories, unit of work, security, background jobs, caching, identity, and external service implementations
- `ONEVO.Api` - the single ASP.NET Core host for customer APIs and `/admin/v1/*` developer-console APIs

The planning modules become feature folders inside the layer projects. There are no separate module `.csproj` files.

CQRS is implemented with MediatR. Every write operation is a command and every read operation is a query. MediatR pipeline behaviors handle validation, logging, performance, and exception safety.

Domain events are optional. They are not required by Clean Architecture or CQRS and should only be added when a completed use case needs decoupled post-save side effects.

## Consequences

**Positive:**

- Domain remains framework independent.
- Handlers are testable without HTTP or a real database.
- One deployable backend host is simpler than module services or multiple API hosts.
- Repository interfaces keep persistence behind Application-owned contracts.
- No RabbitMQ, MassTransit, or integration-event broker is required in Phase 1.

**Negative:**

- Microservice extraction is no longer a natural path. This is acceptable because it is not a Phase 1 goal.
- All feature persistence shares one `ApplicationDbContext`; repository boundaries and architecture tests must prevent handlers and services from bypassing repositories.

## Alternatives Considered

- Keep the modular monolith with separate module projects - rejected as too complex for the current delivery target.
- Microservices - rejected because there is no current product need or team bandwidth.
- Separate `ONEVO.Admin.Api` host - rejected. Developer-console endpoints live under `/admin/v1/*` inside `ONEVO.Api`.

