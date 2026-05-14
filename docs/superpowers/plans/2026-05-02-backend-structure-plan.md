# Backend Folder Structure Implementation Plan

**Status:** Superseded

This plan is historical and must not be executed.

It was written for an older backend layout that included a separate `ONEVO.Admin.Api` host and older generic interface placement. The current source of truth is:

- [[backend/folder-structure|Backend Folder Structure]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[docs/decisions/ADR-002-clean-architecture-cqrs|ADR-002]]
- [[docs/decisions/ADR-003-single-applicationdbcontext|ADR-003]]

Current direction:

- Single backend host: `ONEVO.Api`
- Developer-console controllers under `ONEVO.Api/Controllers/Admin/`
- Application repository contracts under `RepositoryInterfaces/`
- Application service contracts under `ServiceInterfaces/`
- No separate module projects
- No direct `ApplicationDbContext` access from handlers or services
