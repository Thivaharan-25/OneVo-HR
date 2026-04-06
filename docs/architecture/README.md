# Architecture Documentation: ONEVO

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [[module-catalog]] | All 22 modules, their responsibilities, tables, events, dependencies |
| [[module-boundaries]] | Strict boundary rules with .NET examples |
| [[shared-kernel]] | Cross-cutting code (BaseEntity, BaseRepository, Result<T>) |
| [[multi-tenancy]] | 4-layer tenant isolation (JWT → BaseRepo → RLS → ArchUnit) |
| [[external-integrations]] | Stripe, Resend, Biometric, WorkManage Pro bridges |
| [[notification-system]] | 6-step pipeline, 30+ events, 3 channels |
| [[search-architecture]] | PostgreSQL FTS (Phase 1), Meilisearch (Phase 2) |
| Messaging | [[event-catalog]], [[exchange-topology]], [[error-handling]] |

## Architecture Style

**Monolithic + Service-Oriented** (.NET 9 single deployable)

- 22 modules in one solution with strict namespace boundaries
- Inter-module: sync calls for queries, domain events for side effects
- 4-layer [[multi-tenancy]] with PostgreSQL RLS
- CQRS with MediatR for command/query separation
- Repository + Unit of Work patterns via EF Core (see [[coding-standards]])
