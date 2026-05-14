# Tenant + Entitlement Foundation Implementation Plan

**Status:** Superseded

This plan is historical and must not be executed.

It contains older provisioning and persistence guidance, including direct `IApplicationDbContext` usage. The current implementation direction requires repository/reader interfaces and `IUnitOfWork`; handlers and services must not directly use EF Core or `ApplicationDbContext`.

Current source of truth:

- [[developer-platform/userflow/provisioning-flow|Provisioning Flow]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[backend/folder-structure|Backend Folder Structure]]
- [[current-focus/DEV1|DEV1]]

Current direction:

- Tenant provisioning is operator-driven through `/admin/v1/*` endpoints inside `ONEVO.Api`
- Tenant owner access is invite/set-password based, not direct `adminPassword` creation
- Entitlement reads and provisioning writes go through Application-owned repository/reader interfaces
- Infrastructure implements those interfaces under `ONEVO.Infrastructure/Persistence/Repositories/`
- No `IApplicationDbContext` in Application contracts

