# ADR-002: Adopt Clean Architecture + CQRS

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001

---

## Context

ONEVO was designed as a modular monolith with 24 separate `.csproj` module projects. No code had been written. The May 31 delivery deadline and the dropped microservice extraction goal made the original architecture unnecessary complex.

## Decision

Adopt **Clean Architecture** with a 4-layer solution:
- `ONEVO.Domain` — entities, domain events, value objects
- `ONEVO.Application` — CQRS handlers, interfaces, DTOs, validators
- `ONEVO.Infrastructure` — EF Core, JWT, BCrypt, Redis, Hangfire, SignalR
- `ONEVO.Api` / `ONEVO.Admin.Api` — thin ASP.NET Core hosts

The 24 module projects become **feature folders** within `ONEVO.Domain/Features/` and `ONEVO.Application/Features/`.

**CQRS** is implemented with MediatR. Every write operation is a `Command`, every read is a `Query`. MediatR pipeline behaviors handle cross-cutting concerns (validation, logging, performance, exception handling).

## Consequences

**Positive:**
- Framework independence — Domain has zero external dependencies
- Testability — handlers tested without HTTP or DB
- Single deployable unit — simpler than 24 projects
- Faster to build — less boilerplate, no module registration ceremony
- No distributed systems complexity

**Negative:**
- Microservice extraction is no longer a natural path (acceptable — not a goal)
- All 176 tables in one ApplicationDbContext (managed via feature configuration folders)

## Alternatives considered

- Keep modular monolith — rejected: too complex for May 31
- Microservices — rejected: no team bandwidth, premature
