# Dev Platform Feature

**Last Updated:** 2026-04-27

The `DevPlatform` feature provides the developer console backend. It is served by `ONEVO.Admin.Api` (not `ONEVO.Api`).

## Key entities

| Entity | Tables | Notes |
|--------|--------|-------|
| `DevPlatformAccount` | 1 | Platform admin accounts — no TenantId |
| `DevPlatformSession` | 1 | Admin JWT session tracking — no TenantId |
| `AgentVersionRelease` | 1 | Agent binary releases |
| `AgentDeploymentRing` | 1 | Canary / Beta / Stable rings |
| `AgentDeploymentRingAssignment` | 1 | Tenant-to-ring assignment |

**Total: 5 tables (Phase 1)**

## Important

DevPlatform entities have **no TenantId**. They are platform-level, not tenant-level. The global tenant query filter in `ApplicationDbContext` is excluded for these entities.

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/DevPlatform/Entities/
  ONEVO.Domain/Features/DevPlatform/Events/

Application (CQRS):
  ONEVO.Application/Features/DevPlatform/Commands/
  ONEVO.Application/Features/DevPlatform/Queries/
  ONEVO.Application/Features/DevPlatform/DTOs/Requests/
  ONEVO.Application/Features/DevPlatform/DTOs/Responses/
  ONEVO.Application/Features/DevPlatform/Validators/
  ONEVO.Application/Features/DevPlatform/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/

API endpoints:
  ONEVO.Admin.Api/Controllers/DevPlatform/  ← Admin API, not customer API

## Related

- [[developer-platform/overview|Developer Platform Overview]]
- [[developer-platform/auth|Authentication]]
- [[backend/folder-structure|Folder Structure]]
