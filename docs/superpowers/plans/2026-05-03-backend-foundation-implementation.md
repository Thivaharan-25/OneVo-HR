# Backend Foundation Implementation Plan

**Status:** Superseded

This plan is historical and must not be executed.

It described an older foundation that exposed `IApplicationDbContext` from Application and included a separate admin API host. That direction conflicts with the current backend architecture.

Current source of truth:

- [[backend/folder-structure|Backend Folder Structure]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[docs/decisions/ADR-002-clean-architecture-cqrs|ADR-002]]
- [[docs/decisions/ADR-003-single-applicationdbcontext|ADR-003]]

Current direction:

- `ApplicationDbContext` lives only in `ONEVO.Infrastructure/Persistence/`
- Application does not expose `IApplicationDbContext` or `DbSet<T>`
- Handlers and services use repository/reader interfaces
- `IUnitOfWork` lives under `ONEVO.Application/Common/RepositoryInterfaces/`
- Common services live under `ONEVO.Application/Common/ServiceInterfaces/`
- Developer-console endpoints live under `/admin/v1/*` inside `ONEVO.Api`

