# ADR-003: Single ApplicationDbContext

**Date:** 2026-04-27
**Status:** Accepted
**Supersedes:** ADR-001 (per-module DbContext section)

---

## Context

The original design had 24 per-module DbContexts to facilitate future microservice extraction. With microservice extraction dropped and RabbitMQ removed, this added complexity with no benefit.

## Decision

Use a **single `ApplicationDbContext`** in `ONEVO.Infrastructure/Persistence/` for all 176 tables.

- Global query filters applied once: `TenantId == currentUser.TenantId && !IsDeleted`
- `IEntityTypeConfiguration<T>` files are grouped in feature folders under `Configurations/`
- One migration set in `Migrations/`
- `IUnitOfWork` wraps `SaveChangesAsync` — one call is atomic across all features
- `DomainEventDispatchInterceptor` runs after save and dispatches all domain events in-process

**DevPlatform exception:** `DevPlatformAccount`, `DevPlatformSession`, and agent entities have no `TenantId`. They use a separate base class and are excluded from the global tenant filter.

## Consequences

**Positive:**
- Single `SaveChangesAsync` call is atomic — no distributed transaction needed
- One migration history — simpler tooling (`ONEVO.DbMigrator`)
- Global tenant isolation guaranteed by DbContext, not per-feature code
- Cross-feature queries are simple DbSet joins

**Negative:**
- All entities are visible to all handlers via `IApplicationDbContext` (mitigated by code review convention: handlers only query their own feature's data unless explicitly needed)

## Alternatives considered

- Per-feature DbContexts within Infrastructure — rejected: adds complexity with no benefit in a monolith with no extraction plan
